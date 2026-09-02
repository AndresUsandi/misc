import os
import re
import json
import math
import spacy
import yake
import torch
from typing import List, Dict, Any, Tuple, Set
from collections import Counter, defaultdict
from keybert import KeyBERT
from nltk.stem import SnowballStemmer
from sklearn.metrics.pairwise import cosine_similarity

# ==============================================================================
# CONFIGURATION CONSTANTS (YAKE, POS TAGGING & KEYBERT DEDUPLICATION)
# ==============================================================================

DEFAULT_YAKE_TOP_K = 1000
DEFAULT_YAKE_DEDUP_LIM = 0.9
DEFAULT_YAKE_MAX_NGRAM = 4

DEFAULT_KEYBERT_SIMILARITY_THRESHOLD = 0.82
DEFAULT_DEDUP_TOP_CANDIDATES = 1000
DEFAULT_FINAL_TOP_N_CONCEPTS = 250
DEFAULT_EXTRACT_TOP_N = 10
DEFAULT_KEYBERT_MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_YAKE_LANGUAGE = "en"
SPACY_MODEL_NAME = "en_core_web_sm"
SNOWBALL_STEMMER_LANGUAGE = "english"

DEFAULT_EXCLUDE_ACTION_VERBS = True
DEFAULT_ENABLE_DF_FILTERING = True
DEFAULT_MAX_DF_THRESHOLD = 0.90
DEFAULT_USE_WORD_SCORING = True
DEFAULT_USE_MULTI_INSTANCE_BOOST = True

WORD_DF_CACHE_FILENAME = "word_df_cache.json"
KEY_BOOK_COUNT = "book_count"
KEY_DF = "df"
KEY_WORDS = "words"
KEY_METADATA = "_metadata"
KEY_TOTAL_BOOKS = "total_books"
AGG_BOOK_COUNT_NAME = "book_count"
AGG_CARDINALITY = "cardinality"
FIELD_METADATA_BOOK_ID = "metadata.book_id"

POS_TAG_NOUN = "NOUN"
POS_TAG_PROPN = "PROPN"
POS_TAG_VERB = "VERB"
POS_INVALID_START_TAGS_SEMANTIC = ("VERB", "AUX", "DET", "ADP", "CCONJ", "SCONJ", "PART", "ADV")
POS_INVALID_START_TAGS_DEFAULT = ("ADP", "CCONJ", "SCONJ", "PART")

DEFAULT_USE_SEMANTIC_BOOST = True
SYNTACTIC_DOBJ_BOOST_FACTOR = 2.5
SYNTACTIC_NOUN_CHUNK_BOOST_FACTOR = 1.8

KEY_SCORE = "score"
KEY_OCCURRENCES = "occurrences"
KEY_EXCLUDED = "excluded"
EXCLUDE_REASON_HIGH_DF = "Word Score > 0.90"
EXCLUDE_REASON_REPEATING_SINGLE_WORD = "Sentence-Repeating Single Word"
EXCLUDE_REASON_CONTAINED_IN_MULTI_WORD = "Contained in Multi-Word Concept"
EXCLUDE_REASON_SUBSUMED_SUBPHRASE = "Subsumed into Larger Concept"
EXCLUDE_REASON_SINGLE_WORD_CONCEPT = "single word concept"

GERUND_VERB_PENALTY_FACTOR = 0.15
DEFAULT_SENTENCE_REPEATING_BOOST_ALPHA = 0.80
DEFAULT_MIN_SENTENCE_OCCURRENCES = 2
NON_NOUN_START_TAGS = ("VERB", "ADP", "SCONJ", "CCONJ", "ADJ", "ADV", "PART")

YAKE_SCORE_EPSILON = 1e-6
SCORE_ROUND_DECIMALS = 4

DEFAULT_MIN_TEXT_WORDS = 5
DEFAULT_MIN_SINGLE_WORD_OCCURRENCES = 1
DEFAULT_MIN_MULTI_WORD_OCCURRENCES = 1
SPACY_PIPE_BATCH_SIZE = 512

ENV_HF_HUB_OFFLINE = "HF_HUB_OFFLINE"
ENV_HF_HUB_OFFLINE_VALUE = "1"
ENV_TOKENIZERS_PARALLELISM = "TOKENIZERS_PARALLELISM"
ENV_TOKENIZERS_PARALLELISM_VALUE = "false"

_nlp_parser_enabled_instance = None
_nlp_parser_disabled_instance = None
_stemmer_instance = None

def get_spacy_nlp(use_semantic_boost: bool = True):
    """Returns singleton SpaCy NLP instance. Enables parser when use_semantic_boost is True for noun_chunks."""
    global _nlp_parser_enabled_instance, _nlp_parser_disabled_instance
    os.environ[ENV_HF_HUB_OFFLINE] = ENV_HF_HUB_OFFLINE_VALUE
    os.environ[ENV_TOKENIZERS_PARALLELISM] = ENV_TOKENIZERS_PARALLELISM_VALUE

    if use_semantic_boost:
        if _nlp_parser_enabled_instance is None:
            _nlp_parser_enabled_instance = spacy.load(SPACY_MODEL_NAME, disable=["ner", "lemmatizer"])
            _nlp_parser_enabled_instance.add_pipe("sentencizer")
        return _nlp_parser_enabled_instance
    else:
        if _nlp_parser_disabled_instance is None:
            _nlp_parser_disabled_instance = spacy.load(SPACY_MODEL_NAME, disable=["parser", "ner", "lemmatizer"])
            _nlp_parser_disabled_instance.add_pipe("sentencizer")
        return _nlp_parser_disabled_instance

def get_stemmer() -> SnowballStemmer:
    """Returns singleton SnowballStemmer instance for English word stemming."""
    global _stemmer_instance
    if _stemmer_instance is None:
        _stemmer_instance = SnowballStemmer(SNOWBALL_STEMMER_LANGUAGE)
    return _stemmer_instance

def normalize_base_word(w: str) -> str:
    """Normalizes word to its morphological stem using NLTK SnowballStemmer for cross-sentence tracking."""
    if not w:
        return ""
    return get_stemmer().stem(w.lower().strip())

def is_subphrase(sub: str, super_p: str) -> bool:
    """Checks if candidate sub-phrase is a word token constituent of a larger super-phrase."""
    sub_words = [w.lower() for w in re.findall(r'\b\w+\b', sub)]
    super_words = [w.lower() for w in re.findall(r'\b\w+\b', super_p)]
    if len(sub_words) >= len(super_words):
        return False
    sub_len = len(sub_words)
    for i in range(len(super_words) - sub_len + 1):
        if super_words[i:i+sub_len] == sub_words:
            return True
    return False

def is_valid_pos_sequence(
    pos_tags: List[str],
    exclude_action_verbs: bool = True,
    use_semantic_boost: bool = True
) -> bool:
    """Validates whether a candidate keyphrase's POS tag sequence forms a valid concept phrase."""
    if not pos_tags:
        return False

    invalid_start_tags = POS_INVALID_START_TAGS_SEMANTIC if use_semantic_boost else POS_INVALID_START_TAGS_DEFAULT

    if len(pos_tags) == 1:
        if pos_tags[0] not in (POS_TAG_NOUN, POS_TAG_PROPN):
            return False
        if exclude_action_verbs and pos_tags[0] == POS_TAG_VERB:
            return False
        return True

    if not any(p in (POS_TAG_NOUN, POS_TAG_PROPN) for p in pos_tags):
        return False
    if pos_tags[0] in invalid_start_tags:
        return False
    if pos_tags[-1] not in (POS_TAG_NOUN, POS_TAG_PROPN):
        return False
    return True

class WordDFCalculator:
    """Computes and caches Document Frequency (DF = books containing word / total books)
    for single-word concepts using OpenSearch index aggregations.
    """
    def __init__(self, cache_file_path: str = None):
        if cache_file_path is None:
            cache_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), WORD_DF_CACHE_FILENAME)
        self.cache_file_path = cache_file_path
        self.opensearch_util = None
        self.client = None
        self.total_books = 0
        self.cache = self._load_cache()
        self._init_opensearch()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_file_path):
            try:
                with open(self.cache_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {KEY_METADATA: {KEY_TOTAL_BOOKS: 0}, KEY_WORDS: {}}

    def _save_cache(self):
        try:
            with open(self.cache_file_path, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass

    def _init_opensearch(self):
        try:
            from database.opensearch_manager import OpenSearchManager
            self.opensearch_util = OpenSearchManager()
            self.client = self.opensearch_util.connect()
            cnt_resp = self.client.count(index=self.opensearch_util.books_index)
            self.total_books = cnt_resp.get("count", 0)
            self.cache[KEY_METADATA][KEY_TOTAL_BOOKS] = self.total_books
        except Exception:
            self.client = None

    def get_word_df(self, word: str) -> float:
        """Returns the Document Frequency (0.0 to 1.0) of a single-word concept across books.
        Checks bookito_words OpenSearch index first, falling back to local cache or cardinality aggregation.
        """
        word_clean = word.lower().strip()
        if not word_clean:
            return 0.0

        if self.client is not None:
            try:
                res = self.client.get(index=self.opensearch_util.words_index, id=word_clean)
                if res.get("found"):
                    score = res.get("_source", {}).get("score", 0.0)
                    return float(score)
            except Exception:
                pass

        words_cache = self.cache.get(KEY_WORDS, {})
        if word_clean in words_cache:
            return words_cache[word_clean].get(KEY_DF, 0.0)

        if self.client is None or self.total_books == 0:
            return 0.0

        try:
            body = {
                "size": 0,
                "query": {"match": {"chunk_text": word_clean}},
                "aggs": {
                    AGG_BOOK_COUNT_NAME: {
                        AGG_CARDINALITY: {"field": FIELD_METADATA_BOOK_ID}
                    }
                }
            }
            res = self.client.search(index=self.opensearch_util.chunks_index, body=body)
            book_cnt = res.get("aggregations", {}).get(AGG_BOOK_COUNT_NAME, {}).get("value", 0)
            df = round(book_cnt / self.total_books, 4) if self.total_books > 0 else 0.0

            words_cache[word_clean] = {KEY_BOOK_COUNT: book_cnt, KEY_DF: df}
            self.cache[KEY_WORDS] = words_cache
            self._save_cache()
            return df
        except Exception:
            return 0.0

    def get_high_score_words(self, max_df_threshold: float = DEFAULT_MAX_DF_THRESHOLD) -> Set[str]:
        """Queries bookito_words OpenSearch index for all single words with score > max_df_threshold."""
        word_set = set()
        if self.client is None:
            return word_set
        try:
            query = {
                "size": 10000,
                "query": {
                    "range": {
                        "score": {
                            "gt": max_df_threshold
                        }
                    }
                }
            }
            res = self.client.search(index=self.opensearch_util.words_index, body=query)
            for hit in res.get("hits", {}).get("hits", []):
                word_val = hit.get("_source", {}).get("word", "")
                if word_val:
                    word_set.add(word_val.lower().strip())
        except Exception:
            pass
        return word_set

class ConceptExtractor:
    """Extracts keyphrase concepts from text using YAKE, SpaCy POS tag sequence filtering,
    n-gram frequency counting, and KeyBERT semantic embedding deduplication.
    """
    def __init__(
        self,
        yake_top_k: int = DEFAULT_YAKE_TOP_K,
        yake_dedup_lim: float = DEFAULT_YAKE_DEDUP_LIM,
        yake_max_ngram: int = DEFAULT_YAKE_MAX_NGRAM,
        keybert_similarity_threshold: float = DEFAULT_KEYBERT_SIMILARITY_THRESHOLD,
        dedup_top_candidates: int = DEFAULT_DEDUP_TOP_CANDIDATES,
        final_top_n: int = DEFAULT_FINAL_TOP_N_CONCEPTS,
        keybert_model_name: str = DEFAULT_KEYBERT_MODEL_NAME,
        exclude_action_verbs: bool = DEFAULT_EXCLUDE_ACTION_VERBS,
        enable_df_filtering: bool = DEFAULT_ENABLE_DF_FILTERING,
        max_df_threshold: float = DEFAULT_MAX_DF_THRESHOLD,
        use_word_scoring: bool = DEFAULT_USE_WORD_SCORING,
        use_multi_instance_boost: bool = DEFAULT_USE_MULTI_INSTANCE_BOOST,
        use_semantic_boost: bool = DEFAULT_USE_SEMANTIC_BOOST
    ):
        self.yake_top_k = yake_top_k
        self.yake_dedup_lim = yake_dedup_lim
        self.yake_max_ngram = yake_max_ngram
        self.keybert_similarity_threshold = keybert_similarity_threshold
        self.dedup_top_candidates = dedup_top_candidates
        self.final_top_n = final_top_n
        self.keybert_model_name = keybert_model_name
        self.exclude_action_verbs = exclude_action_verbs
        self.enable_df_filtering = enable_df_filtering
        self.max_df_threshold = max_df_threshold
        self.use_word_scoring = use_word_scoring
        self.use_multi_instance_boost = use_multi_instance_boost
        self.use_semantic_boost = use_semantic_boost
        self._kw_model = None
        self.df_calculator = WordDFCalculator() if (enable_df_filtering and use_word_scoring) else None

    def _get_keybert_model(self) -> KeyBERT:
        if self._kw_model is None:
            os.environ[ENV_HF_HUB_OFFLINE] = ENV_HF_HUB_OFFLINE_VALUE
            os.environ[ENV_TOKENIZERS_PARALLELISM] = ENV_TOKENIZERS_PARALLELISM_VALUE
            self._kw_model = KeyBERT(model=self.keybert_model_name)
        return self._kw_model

    def extract_raw_candidates(
        self,
        text: str,
        min_single_word_occurrences: int = DEFAULT_MIN_SINGLE_WORD_OCCURRENCES,
        min_multi_word_occurrences: int = DEFAULT_MIN_MULTI_WORD_OCCURRENCES
    ) -> Dict[str, Dict[str, Any]]:
        """Extracts raw candidate keyphrases using YAKE, SpaCy POS tag validation, and n-gram frequency counting."""
        if not text or len(text.strip().split()) < DEFAULT_MIN_TEXT_WORDS:
            return {}

        extractor = yake.KeywordExtractor(
            lan=DEFAULT_YAKE_LANGUAGE,
            n=self.yake_max_ngram,
            dedupLim=self.yake_dedup_lim,
            top=self.yake_top_k
        )
        raw_yake = extractor.extract_keywords(text)

        yake_dict = {
            kw.lower(): 1.0 / (score + YAKE_SCORE_EPSILON)
            for kw, score in raw_yake
            if 1 <= len(kw.split()) <= self.yake_max_ngram
        }
        candidate_list = list(yake_dict.keys())

        if not candidate_list:
            return {}

        nlp = get_spacy_nlp(use_semantic_boost=self.use_semantic_boost)
        pos_cands = []
        docs = list(nlp.pipe(candidate_list, batch_size=SPACY_PIPE_BATCH_SIZE))
        for cand_text, doc in zip(candidate_list, docs):
            tags = [t.pos_ for t in doc]
            if is_valid_pos_sequence(tags, exclude_action_verbs=self.exclude_action_verbs, use_semantic_boost=self.use_semantic_boost):
                pos_cands.append(cand_text)

        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        word_counts = Counter(words)
        bigrams = Counter(" ".join(words[i:i+2]) for i in range(len(words)-1))
        trigrams = Counter(" ".join(words[i:i+3]) for i in range(len(words)-2))
        fourgrams = Counter(" ".join(words[i:i+4]) for i in range(len(words)-3))

        ngram_counters = {1: word_counts, 2: bigrams, 3: trigrams, 4: fourgrams}

        freq_cands = []
        excluded_cands = {}
        for c in pos_cands:
            c_clean = c.lower().strip()
            n_words = len(c_clean.split())
            count_in_text = ngram_counters.get(n_words, word_counts).get(c_clean, 0)

            if n_words == 1:
                if count_in_text >= min_single_word_occurrences:
                    if self.use_word_scoring and self.enable_df_filtering and self.df_calculator is not None:
                        df_val = self.df_calculator.get_word_df(c_clean)
                        if df_val > self.max_df_threshold:
                            excluded_cands[c_clean] = {
                                KEY_SCORE: df_val,
                                KEY_OCCURRENCES: count_in_text,
                                "reason": EXCLUDE_REASON_HIGH_DF
                            }
                            continue
                    freq_cands.append(c_clean)
            else:
                if count_in_text >= min_multi_word_occurrences:
                    freq_cands.append(c_clean)

        freq_cands = list(set(freq_cands))

        results = {}
        for kw in freq_cands:
            kw_clean = kw.lower().strip()
            score = yake_dict.get(kw_clean, 1.0)
            n_words = len(kw_clean.split())
            count = ngram_counters.get(n_words, word_counts).get(kw_clean, 0)
            results[kw_clean] = {KEY_SCORE: score, KEY_OCCURRENCES: count}

        return results, excluded_cands

    def deduplicate_candidates(
        self,
        candidate_tuples: List[Tuple],
        similarity_threshold: float = None,
        top_n: int = None
    ) -> List[Tuple]:
        """Deduplicates candidates using KeyBERT embeddings & cosine similarity matrix.

        Args:
            candidate_tuples: List of tuples where item[0] is phrase, item[1] is score, followed by metadata.
            similarity_threshold: Cosine similarity threshold for deduplication.
            top_n: Maximum number of concepts to return.

        Returns:
            List of deduplicated tuples sorted by score descending.
        """
        if not candidate_tuples:
            return []

        thresh = similarity_threshold if similarity_threshold is not None else self.keybert_similarity_threshold
        max_n = top_n if top_n is not None else self.final_top_n

        sorted_candidates = sorted(candidate_tuples, key=lambda x: x[1], reverse=True)
        top_candidates = sorted_candidates[:self.dedup_top_candidates]
        if not top_candidates:
            return []

        candidate_phrases = [x[0] for x in top_candidates]

        kw_model = self._get_keybert_model()
        embeddings = kw_model.model.embed(candidate_phrases)
        sim_matrix = cosine_similarity(embeddings)

        final_list = []
        dropped = set()

        for i in range(len(candidate_phrases)):
            if i in dropped:
                continue
            final_list.append(top_candidates[i])
            if len(final_list) >= max_n:
                break

            for j in range(i + 1, len(candidate_phrases)):
                if j not in dropped and sim_matrix[i, j] > thresh:
                    dropped.add(j)

        final_list.sort(key=lambda x: x[1], reverse=True)
        return final_list

    def extract_from_text(
        self,
        text: str,
        min_single_word_occurrences: int = DEFAULT_MIN_SINGLE_WORD_OCCURRENCES,
        min_multi_word_occurrences: int = DEFAULT_MIN_MULTI_WORD_OCCURRENCES
    ) -> List[Tuple[str, float, int]]:
        """Extracts keyphrase concepts from a text string.

        Returns:
            List of tuples: [(phrase, score, total_occurrences), ...] sorted by score descending.
        """
    def extract_with_details(
        self,
        text: str,
        min_single_word_occurrences: int = DEFAULT_MIN_SINGLE_WORD_OCCURRENCES,
        min_multi_word_occurrences: int = DEFAULT_MIN_MULTI_WORD_OCCURRENCES,
        top_n: int = DEFAULT_EXTRACT_TOP_N
    ) -> Tuple[List[Tuple[str, float, int]], List[Tuple[str, float, int, str]]]:
        """Extracts keyphrase concepts and returns both kept concepts and excluded single-word concepts.

        Returns:
            Tuple of (kept_concepts, excluded_concepts) where:
            - kept_concepts: [(phrase, score, occurrences), ...]
            - excluded_concepts: [(phrase, df_score, occurrences, reason), ...]
        """
        raw_cands_res = self.extract_raw_candidates(
            text,
            min_single_word_occurrences=min_single_word_occurrences,
            min_multi_word_occurrences=min_multi_word_occurrences
        )
        if isinstance(raw_cands_res, tuple):
            raw_candidates, excluded_dict = raw_cands_res
        else:
            raw_candidates, excluded_dict = raw_cands_res, {}

        excluded_list = [
            (kw, round(data[KEY_SCORE], SCORE_ROUND_DECIMALS), data[KEY_OCCURRENCES], data["reason"])
            for kw, data in excluded_dict.items()
        ]

        if not raw_candidates:
            excluded_list.sort(key=lambda x: x[1], reverse=True)
            return [], excluded_list

        if self.use_multi_instance_boost or self.use_semantic_boost:
            nlp = get_spacy_nlp(use_semantic_boost=self.use_semantic_boost)
            doc = nlp(text)
            sentences = list(doc.sents)
            total_sentences = max(len(sentences), 1)

            word_sent_counts = defaultdict(set)
            for idx, sent in enumerate(sentences):
                sent_words = set(re.findall(r'\b\w+\b', sent.text.lower()))
                for w in sent_words:
                    word_sent_counts[normalize_base_word(w)].add(idx)

            repeating_single_words = {
                w: len(s_set) for w, s_set in word_sent_counts.items()
                if len(s_set) >= DEFAULT_MIN_SENTENCE_OCCURRENCES
            }

            syntactic_boost_map = {}
            if self.use_semantic_boost:
                for chunk in doc.noun_chunks:
                    words = [t for t in chunk if t.pos_ not in ("DET", "PRON")]
                    if not words:
                        continue
                    clean_chunk = " ".join(w.text.lower() for w in words).strip()
                    dep = chunk.root.dep_
                    boost_val = SYNTACTIC_DOBJ_BOOST_FACTOR if dep in ("dobj", "nsubj") else SYNTACTIC_NOUN_CHUNK_BOOST_FACTOR
                    syntactic_boost_map[clean_chunk] = boost_val

                    if clean_chunk and clean_chunk not in raw_candidates:
                        count_in_text = text.lower().count(clean_chunk)
                        raw_candidates[clean_chunk] = {
                            KEY_SCORE: 1.0,
                            KEY_OCCURRENCES: max(count_in_text, 1)
                        }
        else:
            repeating_single_words = {}
            syntactic_boost_map = {}
            total_sentences = 1

        scores_map = {}
        occurrences_map = {}
        is_clause_map = {}
        for kw, data in raw_candidates.items():
            kw_clean = kw.lower().strip()
            words_in_kw = re.findall(r'\b\w+\b', kw_clean)
            n_words = len(words_in_kw)
            score = data[KEY_SCORE]
            occurrences = data[KEY_OCCURRENCES]

            kw_doc = nlp(kw_clean)
            is_clause = False
            if any(t.pos_ in ("ADP", "SCONJ", "CCONJ") for t in kw_doc):
                is_clause = True
            elif any(t.tag_ in ("VB", "VBZ", "VBP", "VBG") or t.pos_ in ("ADV",) for t in kw_doc):
                is_clause = True

            if is_clause:
                score = score * GERUND_VERB_PENALTY_FACTOR

            if self.use_semantic_boost and kw_clean in syntactic_boost_map:
                score = score * syntactic_boost_map[kw_clean]

            if self.use_multi_instance_boost and n_words >= 2:
                boost = 1.0
                for w in words_in_kw:
                    base_w = normalize_base_word(w)
                    if base_w in repeating_single_words:
                        s_cnt = repeating_single_words[base_w]
                        boost += DEFAULT_SENTENCE_REPEATING_BOOST_ALPHA * math.log(1.0 + (s_cnt / total_sentences))
                score = score * boost

            is_clause_map[kw_clean] = is_clause
            scores_map[kw_clean] = score
            occurrences_map[kw_clean] = occurrences

        all_phrases = sorted(scores_map.keys(), key=lambda x: len(re.findall(r'\b\w+\b', x)), reverse=True)

        accumulated_scores = dict(scores_map)
        subsumed_phrases = set()

        for p in reversed(all_phrases):
            if p in subsumed_phrases:
                continue
            targets = [
                t for t in all_phrases
                if t != p and t not in subsumed_phrases and is_subphrase(p, t)
                and not (not is_clause_map[p] and is_clause_map[t])
            ]
            if targets:
                best_target = max(targets, key=lambda t: (len(re.findall(r'\b\w+\b', t)), scores_map[t]))
                accumulated_scores[best_target] += accumulated_scores[p]
                subsumed_phrases.add(p)

                df_val = self.df_calculator.get_word_df(p) if (self.df_calculator and len(p.split()) == 1) else 0.0
                reason_msg = EXCLUDE_REASON_CONTAINED_IN_MULTI_WORD if len(p.split()) == 1 else EXCLUDE_REASON_SUBSUMED_SUBPHRASE
                excluded_list.append((
                    p,
                    round(df_val, SCORE_ROUND_DECIMALS),
                    occurrences_map[p],
                    reason_msg
                ))

        candidate_tuples = [
            (p, accumulated_scores[p], occurrences_map[p])
            for p in all_phrases
            if p not in subsumed_phrases
        ]

        deduped = self.deduplicate_candidates(candidate_tuples)
        raw_final_list = [(phrase, round(score, SCORE_ROUND_DECIMALS), occurrences) for phrase, score, occurrences in deduped]

        final_kept_list = []
        for phrase, score, occurrences in raw_final_list:
            word_count = len(re.findall(r'\b\w+\b', phrase))
            if word_count <= 1:
                df_val = self.df_calculator.get_word_df(phrase) if (self.df_calculator and len(phrase.split()) == 1) else 0.0
                excluded_list.append((
                    phrase,
                    round(df_val, SCORE_ROUND_DECIMALS),
                    occurrences,
                    EXCLUDE_REASON_SINGLE_WORD_CONCEPT
                ))
            else:
                final_kept_list.append((phrase, score, occurrences))

        if top_n is not None and top_n > 0:
            final_kept_list = final_kept_list[:top_n]

        excluded_list.sort(key=lambda x: x[1], reverse=True)
        return final_kept_list, excluded_list

    def extract_from_text(
        self,
        text: str,
        min_single_word_occurrences: int = DEFAULT_MIN_SINGLE_WORD_OCCURRENCES,
        min_multi_word_occurrences: int = DEFAULT_MIN_MULTI_WORD_OCCURRENCES,
        top_n: int = DEFAULT_EXTRACT_TOP_N
    ) -> List[Tuple[str, float, int]]:
        """Extracts keyphrase concepts from a text string.

        Returns:
            List of tuples: [(phrase, score, total_occurrences), ...] sorted by score descending.
        """
        kept_list, _ = self.extract_with_details(
            text,
            min_single_word_occurrences=min_single_word_occurrences,
            min_multi_word_occurrences=min_multi_word_occurrences,
            top_n=top_n
        )
        return kept_list

    def extractFromText(
        self,
        text: str,
        min_single_word_occurrences: int = DEFAULT_MIN_SINGLE_WORD_OCCURRENCES,
        min_multi_word_occurrences: int = DEFAULT_MIN_MULTI_WORD_OCCURRENCES,
        top_n: int = DEFAULT_EXTRACT_TOP_N
    ) -> List[Tuple[str, float, int]]:
        """CamelCase alias for extract_from_text."""
        return self.extract_from_text(
            text,
            min_single_word_occurrences=min_single_word_occurrences,
            min_multi_word_occurrences=min_multi_word_occurrences,
            top_n=top_n
        )
