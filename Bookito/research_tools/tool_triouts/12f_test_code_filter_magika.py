from huggingface_hub.inference._generated.types import zero_shot_image_classification
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import re
import spacy
import yake
import torch
from collections import Counter
from magika import Magika
from keybert import KeyBERT
from sklearn.metrics.pairwise import cosine_similarity
import concurrent.futures

from parsers.pdf_parser import PdfBookParser

# ==============================================================================
# CONFIGURATION CONSTANTS (HEURISTICS, CONTEXT WINDOWS & DEDUPLICATION)
# ==============================================================================

LINE_TYPE_CODE = "CODE"
LINE_TYPE_TEXT = "TEXT"
LINE_TYPE_AMBIGUOUS = "AMBIGUOUS"

# --- Pass 1: Single Sentence / Line Heuristic Thresholds ---
PASS1_TEXT_MIN_WORDS = 8              # Sentence length threshold (>= 8 words) for confident TEXT
PASS1_TEXT_MAX_CODE_KW = 1           # Max code keyword matches permitted for confident TEXT
PASS1_CODE_MIN_KW = 2                # Code keyword match count to classify line as CODE immediately
PASS1_CODE_SHORT_LINE_WORDS = 5       # Word count threshold for short lines where 1 code keyword triggers CODE
PASS1_MIN_CHAR_LENGTH = 3

# Keywords used to identify code/programming lines in Pass 1
CODE_KEYWORDS_LIST = [
    "public", "private", "protected", "dim", "as", "integer", "string", "boolean", "double",
    "class", "sub", "function", "end sub", "end class", "end function", "end if", "inherits",
    "mybase", "directcast", "create", "select", "insert", "update", "delete", "from", "where",
    "join", "group by", "order by", "exec", "create table", "create view", "create procedure",
    "create trigger", "returns", "return", "namespace", "using", "try", "catch", "finally",
    "import", "go"
]

CODE_SYMBOLS_REGEX_PATTERN = r'[{};=<>+*/\\\[\]()]'

# Build compiled regex for code keywords and symbols
CODE_KEYWORDS_REGEX = re.compile(
    r'\b(' + '|'.join(re.escape(kw) for kw in CODE_KEYWORDS_LIST) + r')\b|' + CODE_SYMBOLS_REGEX_PATTERN,
    re.IGNORECASE
)

# Common English prose function words (articles, prepositions, conjunctions, pronouns)
ENGLISH_PROSE_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "about",
    "against", "between", "into", "through", "during", "before", "after", "above", "below",
    "from", "up", "down", "of", "off", "over", "under", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "can", "will", "just", "should", "now", "this", "that",
    "these", "those", "which", "who", "whom", "you", "your", "yours", "we", "our", "ours",
    "they", "their", "theirs", "he", "him", "his", "she", "her", "it", "its", "would",
    "could", "because", "also", "however", "therefore", "discuss", "show", "shows", "chapter"
}

PROSE_PREFIXES = (
    "figure ", "table ", "note:", "tip:", "warning:", "chapter ", "section ", 
    "listing ", "example ", "see ", "refer to ", "in this ", "for example", "the following"
)

VB_CODE_PATTERNS = re.compile(
    r'\b(dim\s+\w+\s+as|public\s+(sub|function|class|property|enum|structure)|'
    r'private\s+(sub|function|class|property)|protected\s+overrides|'
    r'end\s+(sub|function|class|if|select|property|with|try)|'
    r'imports\s+\w+|inherits\s+\w+|implements\s+\w+|'
    r'select\s+case|catch\s+\w+\s+as|console\.write|msgbox|system\.data|system\.xml)\b',
    re.IGNORECASE
)

def is_definitive_text(line):
    """Heuristic to identify lines as TEXT for sure, distinguishing prose from code (including Visual Basic)."""
    clean_line = line.strip()
    if not clean_line:
        return True
    
    line_lower = clean_line.lower()
    
    # 1. Prose callouts / structural prefixes
    if line_lower.startswith(PROSE_PREFIXES):
        return True
        
    # 2. Check for explicit VB / C# code declaration patterns
    if VB_CODE_PATTERNS.search(clean_line):
        return False
        
    words = re.findall(r'\b[a-zA-Z]+\b', clean_line)
    word_count = len(words)
    if word_count == 0:
        return False
        
    prose_word_count = sum(1 for w in words if w.lower() in ENGLISH_PROSE_STOPWORDS)
    ends_with_prose_punct = clean_line.endswith(('.', '?', '!', ':', '."'))
    starts_with_cap = clean_line[0].isupper()
    
    # Heuristic A: Standard prose sentence (>=6 words, starts with capital, ends with sentence punctuation, >=2 prose function words)
    if word_count >= 6 and starts_with_cap and ends_with_prose_punct and prose_word_count >= 2:
        if not re.search(r'=\s*[\w"\'\(\[\{]', clean_line) and not clean_line.endswith(';'):
            return True
            
    # Heuristic B: High prose word density (>= 30% of words are function words, min 2 prose words)
    if word_count >= 5 and prose_word_count >= 2 and (prose_word_count / word_count) >= 0.30:
        code_kw_matches = CODE_KEYWORDS_REGEX.findall(clean_line)
        if len(code_kw_matches) <= 1:
            return True
            
    # Heuristic C: Long prose sentence (>= 10 words, >= 3 prose function words, not code comment)
    if word_count >= 10 and prose_word_count >= 3:
        if not (clean_line.startswith('//') or clean_line.startswith("'") or clean_line.startswith('#')):
            return True

    return False

DEFINITIVE_CODE_PATTERNS = re.compile(
    r'(\b(dim\s+\w+\s+as|public\s+(sub|function|class|property|enum|structure)|'
    r'private\s+(sub|function|class|property)|protected\s+overrides|'
    r'end\s+(sub|function|class|if|select|property|with|try)|'
    r'imports\s+\w+|inherits\s+\w+|implements\s+\w+|'
    r'select\s+case|catch\s+\w+\s+as|console\.write|msgbox|system\.data|system\.xml|'
    r'using\s+system|namespace\s+\w+|public\s+void|private\s+int|new\s+\w+\(|'
    r'create\s+(table|procedure|view|trigger)|insert\s+into|delete\s+from|'
    r'exec\s+\w+|group\s+by|order\s+by)\b)|'
    r'(\b\w+\.\w+\()|'
    r'(\s*[{};]\s*$)',
    re.IGNORECASE
)

def is_definitive_code(line, has_indent=False):
    """Heuristic to identify lines as CODE for sure, covering Visual Basic, C#, SQL, etc."""
    clean_line = line.strip()
    if not clean_line:
        return False
        
    # 1. Indented code blocks in books are code
    if has_indent:
        return True
        
    # 2. Check regex patterns for explicit code signatures
    if DEFINITIVE_CODE_PATTERNS.search(clean_line):
        return True
        
    # 3. Check for code syntax / assignment operators
    if re.search(r'\b\w+\s*=\s*(\w+|\d+|"|\')', clean_line) and not is_definitive_text(line):
        return True
        
    # 4. Keyword density in short lines
    code_kw_matches = CODE_KEYWORDS_REGEX.findall(clean_line)
    words = clean_line.split()
    if len(words) <= 6 and len(code_kw_matches) >= 2:
        return True

    return False

# --- Pass 2: Contextual Neighbor & Outlier Smoothing ---
CONTEXT_RADIUS = 2                    # Radius of context window (total window size = 2 * CONTEXT_RADIUS + 1 = 5)
SMOOTH_CODE_MIN_NEIGHBORS = 3         # Min CODE neighbors in window to flip non-CODE line to CODE
SMOOTH_TEXT_MIN_NEIGHBORS = 4         # Min TEXT neighbors in window to flip CODE line to TEXT
SMOOTH_AMBIGUOUS_TEXT_NEIGHBORS = 2   # Min TEXT neighbors in window to flip AMBIGUOUS line to TEXT

# Maximum acceptable percentage of sentences/units sent to Magika
MAGIKA_MAX_TARGET_PCT = 20.0

# --- Phase 1 Candidate Mining ---
YAKE_TOP_K = 1000                     # Max YAKE candidates to extract per chapter
YAKE_DEDUP_LIM = 0.9                  # YAKE candidate deduplication limit
YAKE_MAX_NGRAM = 4                    # Max phrase n-gram length (1 to 4 words)

# --- Phase 2 Deduplication ---
KEYBERT_SIMILARITY_THRESHOLD = 0.82   # Cosine similarity threshold for deduplicating concepts
DEDUP_TOP_CANDIDATES = 1000           # Number of consolidated concepts to pass into KeyBERT GPU deduplicator
FINAL_TOP_N_CONCEPTS = 250            # Final concept list target size

# System Device
device = "cuda" if torch.cuda.is_available() else "cpu"

nlp = None
magika = None

class Line:
    def __init__(self, text, type):
        self.text = text
        self.type = type

def init_worker():
    global nlp, magika
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner", "lemmatizer"])
    magika = Magika()

def is_valid_pos_sequence(pos_tags):
    if not any(p in ('NOUN', 'PROPN') for p in pos_tags):
        return False
    if pos_tags[0] in ('ADP', 'CCONJ', 'SCONJ', 'PART'):
        return False
    if pos_tags[-1] not in ('NOUN', 'PROPN'):
        return False
    if any(p == 'VERB' for p in pos_tags):
        return False
    return True

def process_chapter(args):
    chapter, index, total = args
    t_ch_start = time.perf_counter()
    
    t_class_start = time.perf_counter()
    raw_units = []
    
    p1_counts = {LINE_TYPE_CODE: 0, LINE_TYPE_TEXT: 0, LINE_TYPE_AMBIGUOUS: 0}
    for chunk in chapter.Chunks:
        p_text = chunk.Text
        if not p_text or len(p_text.strip()) <= 10:
            continue
            
            lines = p_text.split('\n')
            for line in lines:
                has_indent = bool(re.match(r'^\s{4,}|\t', line))
                code_kw_count = len(CODE_KEYWORDS_REGEX.findall(line))
                word_count = len(line.split(" "))
                is_tiny = len(line) <= PASS1_MIN_CHAR_LENGTH

                if is_definitive_code(line, has_indent):
                    line_type = LINE_TYPE_CODE
                elif is_definitive_text(line):
                    line_type = LINE_TYPE_TEXT
                elif (code_kw_count > PASS1_CODE_MIN_KW and word_count <= PASS1_CODE_SHORT_LINE_WORDS):
                    line_type = LINE_TYPE_CODE
                elif word_count >= PASS1_TEXT_MIN_WORDS or is_tiny:
                    line_type = LINE_TYPE_TEXT
                else:
                    line_type = LINE_TYPE_AMBIGUOUS

                raw_units.append(Line(line, line_type))
                p1_counts[line_type] += 1

    total_units = len(raw_units)

    # ----------------------------------------------------
    # PASS 2: Contextual Neighbor / Outlier Smoothing
    # ----------------------------------------------------
    n = len(raw_units)

    for i in range(n):
        prev_prev = raw_units[max(0, i - 2)]
        prev = raw_units[max(0, i - 1)]
        current = raw_units[i]
        next = raw_units[min(n - 1, i + 1)]
        next_next = raw_units[min(n - 1, i + 2)]

        if (prev_prev.type == prev.type and next.type == next_next.type and prev.type == next.type and prev.type != LINE_TYPE_AMBIGUOUS):
            current.type = prev.type

    for i in range(n):
        prev_prev = raw_units[max(0, i - 2)]
        prev = raw_units[max(0, i - 1)]
        current = raw_units[i]
        next = raw_units[min(n - 1, i + 1)]
        next_next = raw_units[min(n - 1, i + 2)]

        if(current.type == LINE_TYPE_CODE and prev.type != LINE_TYPE_CODE and prev_prev.type != LINE_TYPE_CODE):
            prev.type = LINE_TYPE_AMBIGUOUS
            prev_prev.type = LINE_TYPE_AMBIGUOUS

        if(current.type == LINE_TYPE_CODE and next.type != LINE_TYPE_CODE and next_next.type != LINE_TYPE_CODE):
            next.type = LINE_TYPE_AMBIGUOUS
            next_next.type = LINE_TYPE_AMBIGUOUS

    p2_counts = {LINE_TYPE_CODE: 0, LINE_TYPE_TEXT: 0, LINE_TYPE_AMBIGUOUS: 0}
    for i, item in enumerate(raw_units):
        p2_counts[item.type] += 1
    t_class_end = time.perf_counter()

    # ----------------------------------------------------
    # PASS 3: Selective Magika Verification (AMBIGUOUS lines ONLY)
    # ----------------------------------------------------
    t_magika_start = time.perf_counter()
    magika_count = 0
    for i in range(n):
        if raw_units[i].type == LINE_TYPE_AMBIGUOUS:
            magika_count += 1
            if magika is not None:
                magika_results = magika.identify_bytes(raw_units[i].text.encode('utf-8'))
                if magika_results.output.group in ('code', 'markup') and magika_results.output.label not in ('txt', 'markdown'):
                    raw_units[i].type = LINE_TYPE_CODE
                else:
                    raw_units[i].type = LINE_TYPE_TEXT

    p3_counts = {LINE_TYPE_CODE: 0, LINE_TYPE_TEXT: 0, LINE_TYPE_AMBIGUOUS: 0}
    for i, item in enumerate(raw_units):
        p3_counts[item.type] += 1
    t_magika_end = time.perf_counter()

    magika_pct = (magika_count / total_units * 100.0) if total_units > 0 else 0.0
    warning_flag = " [WARNING: >20% Magika!]" if magika_pct > MAGIKA_MAX_TARGET_PCT else ""

    t_prep_start = time.perf_counter()
    clean_sentences = [item.text for item in raw_units if item.type == LINE_TYPE_TEXT]
    if not clean_sentences:
        t_ch_end = time.perf_counter()
        ch_timings = {
            'classification': t_class_end - t_class_start,
            'magika': t_magika_end - t_magika_start,
            'prep': t_prep_start - t_class_end,
            'yake': 0.0,
            'spacy': 0.0,
            'ngram': 0.0,
            'total': t_ch_end - t_ch_start
        }
        return {}, ch_timings, index

    ch_text = "\n".join(clean_sentences)
    ch_text_lower = ch_text.lower()
    t_prep_end = time.perf_counter()

    # 1. YAKE candidate generation
    t_yake_start = time.perf_counter()
    extractor = yake.KeywordExtractor(lan="en", n=YAKE_MAX_NGRAM, dedupLim=YAKE_DEDUP_LIM, top=YAKE_TOP_K)
    raw_yake = extractor.extract_keywords(ch_text)
    
    yake_dict = {kw.lower(): 1.0 / (score + 1e-6) for kw, score in raw_yake if 1 <= len(kw.split()) <= YAKE_MAX_NGRAM}
    candidate_list = list(yake_dict.keys())
    t_yake_end = time.perf_counter()
    
    if not candidate_list:
        t_ch_end = time.perf_counter()
        ch_timings = {
            'classification': t_class_end - t_class_start,
            'magika': t_magika_end - t_magika_start,
            'prep': t_prep_end - t_prep_start,
            'yake': t_yake_end - t_yake_start,
            'spacy': 0.0,
            'ngram': 0.0,
            'total': t_ch_end - t_ch_start
        }
        return {}, ch_timings, index
        
    # 2. BATCH POS Filtering
    t_spacy_start = time.perf_counter()
    pos_cands = []
    docs = list(nlp.pipe(candidate_list, batch_size=512))
    for cand_text, doc in zip(candidate_list, docs):
        tags = [t.pos_ for t in doc]
        if is_valid_pos_sequence(tags):
            pos_cands.append(cand_text)
    t_spacy_end = time.perf_counter()
            
    # 3. Pre-tokenized Counter frequency lookup
    t_ngram_start = time.perf_counter()
    words = re.findall(r'\b\w+\b', ch_text_lower)
    word_counts = Counter(words)
    
    bigrams = Counter(" ".join(words[i:i+2]) for i in range(len(words)-1))
    trigrams = Counter(" ".join(words[i:i+3]) for i in range(len(words)-2))
    fourgrams = Counter(" ".join(words[i:i+4]) for i in range(len(words)-3))
    
    ngram_counters = {1: word_counts, 2: bigrams, 3: trigrams, 4: fourgrams}
    
    freq_cands = []
    for c in pos_cands:
        n_words = len(c.split())
        count_in_ch = ngram_counters.get(n_words, word_counts).get(c, 0)
        
        if n_words == 1:
            if count_in_ch >= 2:
                freq_cands.append(c)
        else:
            if count_in_ch >= 1:
                freq_cands.append(c)
                
    freq_cands = list(set(freq_cands))
    
    ch_results = {}
    for kw in freq_cands:
        score = yake_dict.get(kw, 1.0)
        n_words = len(kw.split())
        count = ngram_counters.get(n_words, word_counts).get(kw, 0)
        ch_results[kw] = {'score': score, 'occurrences': count}
    t_ngram_end = time.perf_counter()
    t_ch_end = time.perf_counter()

    ch_timings = {
        'classification': t_class_end - t_class_start,
        'magika': t_magika_end - t_magika_start,
        'prep': t_prep_end - t_prep_start,
        'yake': t_yake_end - t_yake_start,
        'spacy': t_spacy_end - t_spacy_start,
        'ngram': t_ngram_end - t_ngram_start,
        'total': t_ch_end - t_ch_start
    }
        
    print(f"  Chapter {index:2d}/{total:2d}: {total_units:4d} units | P1: [T:{p1_counts['TEXT']:4d}, C:{p1_counts['CODE']:3d}, A:{p1_counts['AMBIGUOUS']:3d}] | P2: [T:{p2_counts['TEXT']:4d}, C:{p2_counts['CODE']:3d}, A:{p2_counts['AMBIGUOUS']:3d}] | P3: [T:{p3_counts['TEXT']:4d}, C:{p3_counts['CODE']:3d}, A:{p3_counts['AMBIGUOUS']:3d}] | Magika: {magika_count:3d} ({magika_pct:4.1f}%){warning_flag}")
    return ch_results, ch_timings, index

def main():
    print(f"=== 12F. Configurable 3-Pass Classification with Diagnostic Auditing (Device: {device.upper()}) ===")
    t_start_main = time.perf_counter()
    
    t_pdf_start = time.perf_counter()
    parser = PdfBookParser()
    path = r'e:\Development\GitHub\MachineLarning\Bookito\tests\integrations\files\Professional ADO NET 2 Programming With SQL Server 2005, Oracle, & MySQL 2006.pdf'
    print("Parsing PDF into chapters...")
    book = parser.parse(path, "test_book")
    t_pdf_end = time.perf_counter()

    t_filter_start = time.perf_counter()
    valid_chapters = [ch for ch in book.Chapters if len(ch.getFullText().strip().split()) > 200]
    print(f"Found {len(valid_chapters)} valid chapters. (PDF Parse: {t_pdf_end - t_pdf_start:.2f}s)")
    t_filter_end = time.perf_counter()

    all_chapter_keywords = {}

    print("\n--- Phase 1: 3-Pass Parallel Multiprocess Extraction ---")
    t_phase1_start = time.perf_counter()
    args_list = [(ch, i+1, len(valid_chapters)) for i, ch in enumerate(valid_chapters)]
    
    phase1_worker_sums = {
        'classification': 0.0,
        'magika': 0.0,
        'prep': 0.0,
        'yake': 0.0,
        'spacy': 0.0,
        'ngram': 0.0,
        'total': 0.0
    }
    
    num_workers = min(6, os.cpu_count() or 4)
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers, initializer=init_worker) as executor:
        results = executor.map(process_chapter, args_list)
        for ch_results, ch_timings, index in results:
            for k in phase1_worker_sums:
                phase1_worker_sums[k] += ch_timings.get(k, 0.0)
            for kw, data in ch_results.items():
                if kw in all_chapter_keywords:
                    all_chapter_keywords[kw]['score'] += data['score']
                    all_chapter_keywords[kw]['freq'] += 1
                    all_chapter_keywords[kw]['occurrences'] += data['occurrences']
                else:
                    all_chapter_keywords[kw] = {'score': data['score'], 'freq': 1, 'occurrences': data['occurrences']}
    t_phase1_end = time.perf_counter()

    print("\n--- Phase 2: Consolidation & GPU KeyBERT Deduplication ---")
    t_phase2_start = time.perf_counter()
    t_cons_start = time.perf_counter()
    sorted_keywords = []
    for kw, data in all_chapter_keywords.items():
        if data['occurrences'] < 3: continue
        weighted_score = data['score'] * data['freq']
        sorted_keywords.append((kw, weighted_score, data['freq'], data['occurrences']))
        
    sorted_keywords.sort(key=lambda x: x[1], reverse=True)
    
    top_candidates = sorted_keywords[:DEDUP_TOP_CANDIDATES]
    candidate_phrases = [kw for kw, _, _, _ in top_candidates]
    t_cons_end = time.perf_counter()
    print(f"Consolidated down to {len(candidate_phrases)} unique candidate concepts.")
    
    print(f"\nDeduplicating using KeyBERT GPU embeddings ({device.upper()}) to keep top {FINAL_TOP_N_CONCEPTS} concepts...")
    
    t_kb_init_start = time.perf_counter()
    kw_model_main = KeyBERT(model="all-MiniLM-L6-v2")
    t_kb_init_end = time.perf_counter()

    t_embed_start = time.perf_counter()
    embeddings = kw_model_main.model.embed(candidate_phrases)
    t_embed_end = time.perf_counter()

    t_sim_matrix_start = time.perf_counter()
    sim_matrix = cosine_similarity(embeddings)
    t_sim_matrix_end = time.perf_counter()
    
    t_dedup_loop_start = time.perf_counter()
    final_list = []
    dropped = set()
    
    for i in range(len(candidate_phrases)):
        if i in dropped: continue
        final_list.append(top_candidates[i])
        if len(final_list) >= FINAL_TOP_N_CONCEPTS: break
            
        for j in range(i + 1, len(candidate_phrases)):
            if j not in dropped and sim_matrix[i, j] > KEYBERT_SIMILARITY_THRESHOLD:
                dropped.add(j)
                
    t_dedup_loop_end = time.perf_counter()
    t_phase2_end = time.perf_counter()
    
    t_main_total = time.perf_counter() - t_start_main

    # Print Timing Summary Table
    pdf_time = t_pdf_end - t_pdf_start
    filter_time = t_filter_end - t_filter_start
    phase1_wall = t_phase1_end - t_phase1_start
    phase2_wall = t_phase2_end - t_phase2_start
    cons_time = t_cons_end - t_cons_start
    kb_init_time = t_kb_init_end - t_kb_init_start
    embed_time = t_embed_end - t_embed_start
    sim_matrix_time = t_sim_matrix_end - t_sim_matrix_start
    dedup_loop_time = t_dedup_loop_end - t_dedup_loop_start

    print("\n" + "=" * 80)
    print("                    DETAILED SCRIPT EXECUTION TIMING BREAKDOWN                   ")
    print("=" * 80)
    print(f"  1. PDF File Parsing (PdfBookParser)             : {pdf_time:6.2f}s  ({(pdf_time/t_main_total)*100:5.1f}%)")
    print(f"  2. Chapter Filtering & Setup                    : {filter_time:6.2f}s  ({(filter_time/t_main_total)*100:5.1f}%)")
    print(f"  3. Phase 1 Parallel Extraction (Wall Clock)     : {phase1_wall:6.2f}s  ({(phase1_wall/t_main_total)*100:5.1f}%)")
    print(f"     |- Line Classification (Pass 1 & Pass 2)     : {phase1_worker_sums['classification']:6.2f}s (worker CPU sum)")
    print(f"     |- Pass 3 Magika Verification                : {phase1_worker_sums['magika']:6.2f}s (worker CPU sum)")
    print(f"     |- Clean Text Assembly                       : {phase1_worker_sums['prep']:6.2f}s (worker CPU sum)")
    print(f"     |- YAKE Keyword Extraction                   : {phase1_worker_sums['yake']:6.2f}s (worker CPU sum)")
    print(f"     |- SpaCy POS Batch Tagging                   : {phase1_worker_sums['spacy']:6.2f}s (worker CPU sum)")
    print(f"     \\- N-Gram Counter Frequency Lookup           : {phase1_worker_sums['ngram']:6.2f}s (worker CPU sum)")
    print(f"  4. Phase 2 KeyBERT GPU Deduplication (Wall Clock): {phase2_wall:6.2f}s  ({(phase2_wall/t_main_total)*100:5.1f}%)")
    print(f"     |- Keyword Consolidation & Sorting           : {cons_time:6.2f}s")
    print(f"     |- KeyBERT Model Initialization              : {kb_init_time:6.2f}s")
    print(f"     |- Phrase Embedding Generation               : {embed_time:6.2f}s")
    print(f"     |- Cosine Similarity Matrix Computation      : {sim_matrix_time:6.2f}s")
    print(f"     \\- Matrix Deduplication Selection Loop       : {dedup_loop_time:6.2f}s")
    print("-" * 80)
    print(f"  TOTAL SCRIPT EXECUTION TIME                     : {t_main_total:6.2f}s  (100.0%)")
    print("=" * 80 + "\n")

    print(f"Final Deduplicated Top {len(final_list)} Concepts [Total Script Time: {t_main_total:.2f}s]:")
    final_list.sort(key=lambda x: (len(x[0].split()), -x[1]))
    
    print(f"{'Keyphrase':<45} | {'Total Score':<15} | {'Chapters':<10} | {'Total Occurrences':<15}")
    print("-" * 95)
    for kw, score, freq, occurrences in final_list:
        print(f"{kw:<45} | {score:.4f}          | {freq:<10} | {occurrences}")

if __name__ == "__main__":
    main()
