import os
import time
import re
from magika import Magika
import concurrent.futures
from typing import List, Tuple, Dict, Any

from book import Book, Chapter
from processors.concept_extractor import (
    ConceptExtractor,
    get_spacy_nlp,
    DEFAULT_YAKE_TOP_K,
    DEFAULT_YAKE_DEDUP_LIM,
    DEFAULT_YAKE_MAX_NGRAM,
    DEFAULT_KEYBERT_SIMILARITY_THRESHOLD,
    DEFAULT_DEDUP_TOP_CANDIDATES,
    DEFAULT_FINAL_TOP_N_CONCEPTS,
    SCORE_ROUND_DECIMALS,
    ENV_HF_HUB_OFFLINE,
    ENV_HF_HUB_OFFLINE_VALUE,
    ENV_TOKENIZERS_PARALLELISM,
    ENV_TOKENIZERS_PARALLELISM_VALUE
)

# ==============================================================================
# CONFIGURATION CONSTANTS (HEURISTICS, CONTEXT WINDOWS & DEDUPLICATION)
# ==============================================================================

LINE_TYPE_CODE = "CODE"
LINE_TYPE_TEXT = "TEXT"
LINE_TYPE_AMBIGUOUS = "AMBIGUOUS"

PASS1_TEXT_MIN_WORDS = 8
PASS1_TEXT_MAX_CODE_KW = 1
PASS1_CODE_MIN_KW = 2
PASS1_CODE_SHORT_LINE_WORDS = 5
PASS1_MIN_CHAR_LENGTH = 3

CODE_KEYWORDS_LIST = [
    "public", "private", "protected", "dim", "as", "integer", "string", "boolean", "double",
    "class", "sub", "function", "end sub", "end class", "end function", "end if", "inherits",
    "mybase", "directcast", "create", "select", "insert", "update", "delete", "from", "where",
    "join", "group by", "order by", "exec", "create table", "create view", "create procedure",
    "create trigger", "returns", "return", "namespace", "using", "try", "catch", "finally",
    "import", "go"
]

CODE_SYMBOLS_REGEX_PATTERN = r'[{};=<>+*/\\\[\]()]'

CODE_KEYWORDS_REGEX = re.compile(
    r'\b(' + '|'.join(re.escape(kw) for kw in CODE_KEYWORDS_LIST) + r')\b|' + CODE_SYMBOLS_REGEX_PATTERN,
    re.IGNORECASE
)

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

YAKE_TOP_K = DEFAULT_YAKE_TOP_K
YAKE_DEDUP_LIM = DEFAULT_YAKE_DEDUP_LIM
YAKE_MAX_NGRAM = DEFAULT_YAKE_MAX_NGRAM

KEYBERT_SIMILARITY_THRESHOLD = DEFAULT_KEYBERT_SIMILARITY_THRESHOLD
DEDUP_TOP_CANDIDATES = DEFAULT_DEDUP_TOP_CANDIDATES
FINAL_TOP_N_CONCEPTS = DEFAULT_FINAL_TOP_N_CONCEPTS

CHAPTER_MIN_WORD_COUNT = 200
CHAPTER_SINGLE_WORD_MIN_OCCURRENCES = 2
CHAPTER_MULTI_WORD_MIN_OCCURRENCES = 2
BOOK_CONCEPT_MIN_OCCURRENCES = 2

DEFAULT_INGESTION_USE_WORD_SCORING = False
DEFAULT_INGESTION_USE_MULTI_INSTANCE_BOOST = False
DEFAULT_INGESTION_USE_SEMANTIC_BOOST = False

MAX_WORKERS_LIMIT = 6
DEFAULT_WORKERS_FALLBACK = 4

MAGIKA_GROUP_CODE = "code"
MAGIKA_GROUP_MARKUP = "markup"
MAGIKA_LABEL_TXT = "txt"
MAGIKA_LABEL_MARKDOWN = "markdown"
UTF8_ENCODING = "utf-8"

magika = None

def init_worker():
    """Initializes SpaCy and Magika worker environment."""
    global magika
    os.environ[ENV_HF_HUB_OFFLINE] = ENV_HF_HUB_OFFLINE_VALUE
    os.environ[ENV_TOKENIZERS_PARALLELISM] = ENV_TOKENIZERS_PARALLELISM_VALUE

    get_spacy_nlp()
    if magika is None:
        magika = Magika()

def is_definitive_text(line: str) -> bool:
    clean_line = line.strip()
    if not clean_line:
        return True

    line_lower = clean_line.lower()
    if line_lower.startswith(PROSE_PREFIXES):
        return True

    if VB_CODE_PATTERNS.search(clean_line):
        return False

    words = re.findall(r'\b[a-zA-Z]+\b', clean_line)
    word_count = len(words)
    if word_count == 0:
        return False

    prose_word_count = sum(1 for w in words if w.lower() in ENGLISH_PROSE_STOPWORDS)
    ends_with_prose_punct = clean_line.endswith(('.', '?', '!', ':', '."'))
    starts_with_cap = clean_line[0].isupper()

    if word_count >= 6 and starts_with_cap and ends_with_prose_punct and prose_word_count >= 2:
        if not re.search(r'=\s*[\w"\'\(\[\{]', clean_line) and not clean_line.endswith(';'):
            return True

    if word_count >= 5 and prose_word_count >= 2 and (prose_word_count / word_count) >= 0.30:
        code_kw_matches = CODE_KEYWORDS_REGEX.findall(clean_line)
        if len(code_kw_matches) <= 1:
            return True

    if word_count >= 10 and prose_word_count >= 3:
        if not (clean_line.startswith('//') or clean_line.startswith("'") or clean_line.startswith('#')):
            return True

    return False

def is_definitive_code(line: str, has_indent: bool = False) -> bool:
    clean_line = line.strip()
    if not clean_line:
        return False

    if has_indent:
        return True

    if DEFINITIVE_CODE_PATTERNS.search(clean_line):
        return True

    if re.search(r'\b\w+\s*=\s*(\w+|\d+|"|\')', clean_line) and not is_definitive_text(line):
        return True

    code_kw_matches = CODE_KEYWORDS_REGEX.findall(clean_line)
    words = clean_line.split()
    if len(words) <= 6 and len(code_kw_matches) >= 2:
        return True

    return False

def process_chapter(args: Tuple[Any, int, int]) -> Dict[str, Dict[str, Any]]:
    """Filters code vs text lines in a chapter and extracts raw candidate keyphrases using ConceptExtractor."""
    chapter, index, total = args
    valid_chunks = []

    for chunk in chapter.Chunks:
        p_text = chunk.Text
        if not p_text or len(p_text.strip()) <= 10:
            chunk.Type = LINE_TYPE_TEXT
            continue

        has_indent = bool(re.match(r'^\s{4,}|\t', p_text))
        code_kw_count = len(CODE_KEYWORDS_REGEX.findall(p_text))
        word_count = len(p_text.split(" "))
        is_tiny = len(p_text) <= PASS1_MIN_CHAR_LENGTH

        if is_definitive_code(p_text, has_indent):
            chunk.Type = LINE_TYPE_CODE
        elif is_definitive_text(p_text):
            chunk.Type = LINE_TYPE_TEXT
        elif (code_kw_count > PASS1_CODE_MIN_KW and word_count <= PASS1_CODE_SHORT_LINE_WORDS):
            chunk.Type = LINE_TYPE_CODE
        elif word_count >= PASS1_TEXT_MIN_WORDS or is_tiny:
            chunk.Type = LINE_TYPE_TEXT
        else:
            chunk.Type = LINE_TYPE_AMBIGUOUS

        valid_chunks.append(chunk)

    # Pass 2 Context Smoothing
    n = len(valid_chunks)
    for i in range(n):
        prev_prev = valid_chunks[max(0, i - 2)]
        prev = valid_chunks[max(0, i - 1)]
        current = valid_chunks[i]
        next_item = valid_chunks[min(n - 1, i + 1)]
        next_next = valid_chunks[min(n - 1, i + 2)]

        if (prev_prev.Type == prev.Type and next_item.Type == next_next.Type and prev.Type == next_item.Type and prev.Type != LINE_TYPE_AMBIGUOUS):
            current.Type = prev.Type

    for i in range(n):
        prev_prev = valid_chunks[max(0, i - 2)]
        prev = valid_chunks[max(0, i - 1)]
        current = valid_chunks[i]
        next_item = valid_chunks[min(n - 1, i + 1)]
        next_next = valid_chunks[min(n - 1, i + 2)]

        if (current.Type == LINE_TYPE_CODE and prev.Type != LINE_TYPE_CODE and prev_prev.Type != LINE_TYPE_CODE):
            prev.Type = LINE_TYPE_AMBIGUOUS
            prev_prev.Type = LINE_TYPE_AMBIGUOUS

        if (current.Type == LINE_TYPE_CODE and next_item.Type != LINE_TYPE_CODE and next_next.Type != LINE_TYPE_CODE):
            next_item.Type = LINE_TYPE_AMBIGUOUS
            next_next.Type = LINE_TYPE_AMBIGUOUS

    # Pass 3 Magika Verification (Ambiguous chunks only)
    for chunk in valid_chunks:
        if chunk.Type == LINE_TYPE_AMBIGUOUS:
            if magika is not None:
                magika_results = magika.identify_bytes(chunk.Text.encode(UTF8_ENCODING))
                if magika_results.output.group in (MAGIKA_GROUP_CODE, MAGIKA_GROUP_MARKUP) and magika_results.output.label not in (MAGIKA_LABEL_TXT, MAGIKA_LABEL_MARKDOWN):
                    chunk.Type = LINE_TYPE_CODE
                else:
                    chunk.Type = LINE_TYPE_TEXT

    clean_sentences = [chunk.Text for chunk in valid_chunks if chunk.Type == LINE_TYPE_TEXT]
    if not clean_sentences or len(chapter.getFullText().strip().split()) <= CHAPTER_MIN_WORD_COUNT:
        return {}

    ch_text = "\n".join(clean_sentences)
    extractor = ConceptExtractor(
        yake_top_k=YAKE_TOP_K,
        yake_dedup_lim=YAKE_DEDUP_LIM,
        yake_max_ngram=YAKE_MAX_NGRAM,
        use_word_scoring=DEFAULT_INGESTION_USE_WORD_SCORING,
        use_multi_instance_boost=DEFAULT_INGESTION_USE_MULTI_INSTANCE_BOOST,
        use_semantic_boost=DEFAULT_INGESTION_USE_SEMANTIC_BOOST
    )
    return extractor.extract_raw_candidates(
        ch_text,
        min_single_word_occurrences=CHAPTER_SINGLE_WORD_MIN_OCCURRENCES,
        min_multi_word_occurrences=CHAPTER_MULTI_WORD_MIN_OCCURRENCES
    )

class ConceptProcessor:
    """Processes Book objects by filtering prose text per chapter, extracting candidates,
    and deduplicating keyphrases using ConceptExtractor.
    """
    def __init__(
        self,
        yake_top_k: int = YAKE_TOP_K,
        keybert_similarity_threshold: float = KEYBERT_SIMILARITY_THRESHOLD,
        final_top_n: int = FINAL_TOP_N_CONCEPTS,
        extractor: ConceptExtractor = None
    ):
        self.yake_top_k = yake_top_k
        self.keybert_similarity_threshold = keybert_similarity_threshold
        self.final_top_n = final_top_n
        self.extractor = extractor if extractor is not None else ConceptExtractor(
            yake_top_k=yake_top_k,
            keybert_similarity_threshold=keybert_similarity_threshold,
            final_top_n=final_top_n,
            use_word_scoring=DEFAULT_INGESTION_USE_WORD_SCORING,
            use_multi_instance_boost=DEFAULT_INGESTION_USE_MULTI_INSTANCE_BOOST,
            use_semantic_boost=DEFAULT_INGESTION_USE_SEMANTIC_BOOST
        )

    def processBook(self, book: Book) -> List[Tuple[str, float, int, int]]:
        """Processes a Book object and extracts keyphrases/concepts.

        Returns:
            List of tuples: [(phrase, score, chapters_count, total_occurrences), ...]
            sorted by score in descending order.
        """
        if not book.Chapters:
            return []

        init_worker()

        all_chapter_keywords = {}
        args_list = [(ch, i+1, len(book.Chapters)) for i, ch in enumerate(book.Chapters)]
        num_workers = min(MAX_WORKERS_LIMIT, os.cpu_count() or DEFAULT_WORKERS_FALLBACK)

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            results = executor.map(process_chapter, args_list)
            for ch_results in results:
                for kw, data in ch_results.items():
                    kw_clean = kw.lower().strip()
                    if kw_clean in all_chapter_keywords:
                        all_chapter_keywords[kw_clean]['score'] += data['score']
                        all_chapter_keywords[kw_clean]['freq'] += 1
                        all_chapter_keywords[kw_clean]['occurrences'] += data['occurrences']
                    else:
                        all_chapter_keywords[kw_clean] = {
                            'score': data['score'],
                            'freq': 1,
                            'occurrences': data['occurrences']
                        }

        sorted_keywords = []
        for kw, data in all_chapter_keywords.items():
            if data['occurrences'] < BOOK_CONCEPT_MIN_OCCURRENCES:
                continue
            weighted_score = data['score'] * data['freq']
            sorted_keywords.append((kw, weighted_score, data['freq'], data['occurrences']))

        sorted_keywords.sort(key=lambda x: x[1], reverse=True)

        if not sorted_keywords:
            return []

        deduped = self.extractor.deduplicate_candidates(
            sorted_keywords,
            similarity_threshold=self.keybert_similarity_threshold,
            top_n=self.final_top_n
        )

        return [(kw, round(score, SCORE_ROUND_DECIMALS), freq, occurrences) for kw, score, freq, occurrences in deduped]
