import os
import sys
import time
import re
import statistics
import concurrent.futures
from collections import defaultdict
from typing import List, Dict, Any, Tuple, Set
from nltk.stem.snowball import SnowballStemmer

# Ensure parent directory is in sys.path for relative/absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.query_manager import (
    QueryManager,
    DEFAULT_TOP_K,
    RESULT_KEY_SCORE,
    RESULT_KEY_CHUNK_ID,
    RESULT_KEY_CHUNK_INDEX,
    RESULT_KEY_CHUNK_TEXT,
    RESULT_KEY_CHAPTER_ID,
    RESULT_KEY_CHAPTER_NUMBER,
    RESULT_KEY_CHAPTER_TITLE,
    RESULT_KEY_BOOK_ID,
    RESULT_KEY_BOOK_NAME,
    RESULT_KEY_FILE_LINK
)
from visualization.constants import (
    DEFAULT_MAX_CONCURRENT_QUERIES,
    DEFAULT_CONTEXT_EXPANSION_CHUNKS,
    MATCH_TYPE_SYNTACTIC,
    MATCH_TYPE_SEMANTIC,
    FORMAT_MATCHED_CONCEPT
)

# Top-of-File Constants
DEFAULT_INITIAL_PAGE = 1
SEARCH_PAGE_SIZE = 50
SCORE_ROUND_DECIMALS = 4
EXPANDED_SEARCH_SIZE = 500
OPENSEARCH_RANGE_TIMEOUT = 30
SNOWBALL_STEMMER_LANGUAGE = "english"
MIN_VECTOR_SEARCH_WORD_COUNT = 2

# Adaptive Score Threshold Tuning Constants
# MAD (Median Absolute Deviation) method: threshold = median + MAD_SENSITIVITY_FACTOR * MAD
MAD_SENSITIVITY_FACTOR = 3.5  # Increased from 1.0 to make the MAD threshold much stricter
# Elbow detection: a gap is significant if it exceeds mean_gap + ELBOW_GAP_STDDEV_MULTIPLIER * stddev_gap
ELBOW_GAP_STDDEV_MULTIPLIER = 1.0  # Decreased from 1.5 to detect gaps/drop-offs sooner
# Minimum number of top items to keep before allowing an elbow cut
ELBOW_MIN_ITEMS_BEFORE_CUT = 2
# Fraction of the gap value to add above the score just below the gap (softens the cutoff)
ELBOW_SCORE_RETENTION_FACTOR = 0.6  # Increased from 0.1 to set the cutoff higher in the gap
# Minimum number of results required to apply thresholding (below this, keep all)
MIN_RESULTS_FOR_THRESHOLD = 3

BOOK_SECTION_DELIMITER = "--------------------------------"
ELLIPSIS_GAP_INDICATOR = "..."
EMPTY_STRING = ""
NEWLINE = "\n"
NO_RESULTS_MESSAGE = "No aggregated search results found."

FIELD_CHUNK_VECTOR = "chunk_vector"
KEY_SIZE = "size"
KEY_SOURCE = "_source"
KEY_EXCLUDES = "excludes"
KEY_QUERY = "query"
KEY_BOOL = "bool"
KEY_MUST = "must"
KEY_TERM = "term"
KEY_RANGE = "range"
KEY_GTE = "gte"
KEY_LTE = "lte"
FIELD_METADATA_BOOK_ID = "metadata.book_id"
FIELD_METADATA_CHUNK_INDEX = "metadata.chunk_index"
KEY_HITS = "hits"

KEY_CONCEPT_INTERNAL = "_concept"
KEY_MATCH_TYPE_INTERNAL = "_match_type"
KEY_MATCHED_CONCEPTS_INTERNAL = "_matched_concepts"
KEY_IS_DIRECT_HIT_INTERNAL = "_is_direct_hit"

RESULT_KEY_TOTAL_AGGREGATED_SCORE = "total_aggregated_score"
RESULT_KEY_CHUNKS = "chunks"
RESULT_KEY_MATCHED_CONCEPTS = "matched_concepts"

FALLBACK_BOOK_NAME_PREFIX = "Book "
FALLBACK_CHAPTER_TITLE_DEFAULT = "Chapter 1"

LOG_SEARCH_ERROR_PREFIX = "Search error for "
LOG_RANGE_FETCH_ERROR_PREFIX = "Error fetching expanded chunks for book "

def is_valid_syntactic_match(concept: str, chunk_text: str, stemmer: SnowballStemmer) -> bool:
    """Verifies that all words of the concept phrase are present in the chunk text, matching via word stems."""
    if not concept or not chunk_text:
        return False

    concept_words = [w.lower() for w in re.findall(r'\b\w+\b', concept)]
    if not concept_words:
        return False

    concept_stems = set(stemmer.stem(w) for w in concept_words)
    chunk_words = [w.lower() for w in re.findall(r'\b\w+\b', chunk_text)]
    chunk_stems = set(stemmer.stem(w) for w in chunk_words)

    return concept_stems.issubset(chunk_stems)

def compute_adaptive_threshold(scores: List[float]) -> float:
    """Computes an adaptive score threshold using the higher of two methods:

    Method A (MAD): median + MAD_SENSITIVITY_FACTOR * MAD
        - Robust to outliers; captures the central tendency of scores.
    Method B (Elbow): Detects the first significant gap in sorted scores
        - Finds the natural breakpoint where scores drop sharply.

    Returns the threshold value. Scores at or above this value should be kept.
    """
    if len(scores) < MIN_RESULTS_FOR_THRESHOLD:
        return 0.0

    sorted_desc = sorted(scores, reverse=True)

    # Method A: Median + MAD
    median_val = statistics.median(sorted_desc)
    deviations = [abs(s - median_val) for s in sorted_desc]
    mad = statistics.median(deviations)
    mad_threshold = median_val + mad * MAD_SENSITIVITY_FACTOR

    # Method B: Elbow/Knee detection via gap analysis
    elbow_threshold = sorted_desc[-1]  # fallback: keep everything
    gaps = []
    for i in range(len(sorted_desc) - 1):
        gap = sorted_desc[i] - sorted_desc[i + 1]
        gaps.append((gap, i, sorted_desc[i + 1]))

    if gaps:
        mean_gap = sum(g[0] for g in gaps) / len(gaps)
        std_gap = (sum((g[0] - mean_gap) ** 2 for g in gaps) / len(gaps)) ** 0.5
        elbow_gap_cutoff = mean_gap + ELBOW_GAP_STDDEV_MULTIPLIER * std_gap

        for gap_val, idx, score_below in gaps:
            if gap_val > elbow_gap_cutoff and idx >= ELBOW_MIN_ITEMS_BEFORE_CUT:
                elbow_threshold = score_below + (gap_val * ELBOW_SCORE_RETENTION_FACTOR)
                break

    return max(mad_threshold, elbow_threshold)

class AugmentedContentGenerator:
    """Processes a list of concept strings by executing concurrent syntactic (lexical)
    and semantic (vector) queries against OpenSearch, expanding chunk context (+/- 5 chunks),
    deduplicating chunks globally, accumulating match scores, and aggregating result groups.
    """
    def __init__(self, query_manager: QueryManager = None):
        self.qm = query_manager if query_manager is not None else QueryManager()
        self.stemmer = SnowballStemmer(SNOWBALL_STEMMER_LANGUAGE)

    def generate_augmented_content(
        self,
        concepts: List[str],
        context_expansion: int = DEFAULT_CONTEXT_EXPANSION_CHUNKS,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT_QUERIES,
        top_k: int = DEFAULT_TOP_K
    ) -> List[Dict[str, Any]]:
        """Executes full search, context expansion, chunk deduplication, score accumulation,
        and result group aggregation across the provided list of concepts.

        Args:
            concepts: List of concept strings (e.g. ['workflow engine', 'business processes']).
            context_expansion: Number of contiguous context chunks to fetch before and after each hit (default: 5).
            max_concurrent: Maximum allowed concurrent OpenSearch queries (default: 3).

        Returns:
            List of aggregated result dictionaries sorted by total_aggregated_score descending.
        """
        if not concepts:
            return []

        # Filter out empty concept strings
        clean_concepts = [c.strip() for c in concepts if c and c.strip()]
        if not clean_concepts:
            return []

        self.qm.set_max_concurrent_queries(max_concurrent)

        # ----------------------------------------------------------------------
        # Step 1: Multi-concept Syntactic & Semantic Search with Concurrency Limit
        # ----------------------------------------------------------------------
        raw_hits = []
        # Intermediate collection grouped by (concept, match_type) for threshold filtering
        concept_results = defaultdict(list)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_info = {}
            for c_clean in clean_concepts:
                # Submit Syntactic (Lexical Match) Search
                f_syn = executor.submit(self.qm.lexical_search, c_clean, DEFAULT_INITIAL_PAGE, top_k, top_k)
                future_to_info[f_syn] = (c_clean, MATCH_TYPE_SYNTACTIC)
                # Submit Semantic (Vector KNN) Search
                f_sem = executor.submit(self.qm.vector_search, c_clean, DEFAULT_INITIAL_PAGE, top_k, top_k)
                future_to_info[f_sem] = (c_clean, MATCH_TYPE_SEMANTIC)

            for future in concurrent.futures.as_completed(future_to_info):
                c_clean, match_type = future_to_info[future]
                try:
                    results = future.result()
                    for r in results:
                        hit_item = dict(r)
                        chunk_text = hit_item.get(RESULT_KEY_CHUNK_TEXT, "")

                        # Syntactic matches must contain ALL stemmed concept words
                        if match_type == MATCH_TYPE_SYNTACTIC:
                            if not is_valid_syntactic_match(c_clean, chunk_text, self.stemmer):
                                continue

                        # Semantic matches must match on concepts with 2 or more words
                        if match_type == MATCH_TYPE_SEMANTIC:
                            if len(re.findall(r'\b\w+\b', c_clean)) < MIN_VECTOR_SEARCH_WORD_COUNT:
                                continue

                        hit_item[KEY_CONCEPT_INTERNAL] = c_clean
                        hit_item[KEY_MATCH_TYPE_INTERNAL] = match_type
                        concept_results[(c_clean, match_type)].append(hit_item)
                except Exception as e:
                    print(f"{LOG_SEARCH_ERROR_PREFIX}{c_clean} ({match_type}): {e}")

        # Apply adaptive score thresholds per (concept, match_type) group
        for (c_clean, match_type), hits in concept_results.items():
            scores = [h.get(RESULT_KEY_SCORE, 0.0) for h in hits]
            threshold = compute_adaptive_threshold(scores)
            for hit in hits:
                if hit.get(RESULT_KEY_SCORE, 0.0) >= threshold:
                    raw_hits.append(hit)

        if not raw_hits:
            return []

        # ----------------------------------------------------------------------
        # Step 2: Identify Matched Chunks and Range Bounds per Book
        # ----------------------------------------------------------------------
        raw_chunk_hits_map = defaultdict(list)
        for hit in raw_hits:
            b_id = hit.get(RESULT_KEY_BOOK_ID)
            c_idx = hit.get(RESULT_KEY_CHUNK_INDEX)
            if b_id is not None and c_idx is not None:
                chunk_key = (b_id, c_idx)
                raw_chunk_hits_map[chunk_key].append(hit)

        # Calculate overall score per chunk to apply adaptive threshold before expansion
        chunk_scores = {
            chunk_key: sum(h.get(RESULT_KEY_SCORE, 0.0) for h in hits)
            for chunk_key, hits in raw_chunk_hits_map.items()
        }

        book_matched_chunks = defaultdict(set)
        chunk_hits_map = defaultdict(list)

        if chunk_scores:
            overall_threshold = compute_adaptive_threshold(list(chunk_scores.values()))
            for chunk_key, score in chunk_scores.items():
                if score >= overall_threshold:
                    chunk_hits_map[chunk_key] = raw_chunk_hits_map[chunk_key]
                    b_id, c_idx = chunk_key
                    book_matched_chunks[b_id].add(c_idx)

        if not book_matched_chunks:
            return []

        # ----------------------------------------------------------------------
        # Step 3: Fetch Contiguous Expanded Context Chunks (+/- 5 chunks)
        # ----------------------------------------------------------------------
        book_expanded_chunks = {}
        for b_id, matched_indexes in book_matched_chunks.items():
            if not matched_indexes:
                continue
            min_idx = max(0, min(matched_indexes) - context_expansion)
            max_idx = max(matched_indexes) + context_expansion
            expanded_docs = self._fetch_book_chunks_in_range(b_id, min_idx, max_idx)
            book_expanded_chunks[b_id] = expanded_docs

        # ----------------------------------------------------------------------
        # Step 4: Global Deduplication & Score Accumulation
        # ----------------------------------------------------------------------
        # Map: (book_id, chunk_index) -> aggregated chunk record
        deduped_chunks = {}

        for b_id, expanded_list in book_expanded_chunks.items():
            for chunk_doc in expanded_list:
                c_idx = chunk_doc.get(RESULT_KEY_CHUNK_INDEX)
                chunk_key = (b_id, c_idx)

                hits_for_chunk = chunk_hits_map.get(chunk_key, [])
                matched_concepts_set = set()
                score_sum = 0.0

                for hit in hits_for_chunk:
                    score_sum += hit.get(RESULT_KEY_SCORE, 0.0)
                    concept = hit.get(KEY_CONCEPT_INTERNAL)
                    m_type = hit.get(KEY_MATCH_TYPE_INTERNAL)
                    if concept and m_type:
                        fmt_concept = FORMAT_MATCHED_CONCEPT.format(concept=concept, match_type=m_type)
                        matched_concepts_set.add(fmt_concept)

                chunk_doc_copy = dict(chunk_doc)
                chunk_doc_copy[RESULT_KEY_SCORE] = score_sum
                chunk_doc_copy[KEY_MATCHED_CONCEPTS_INTERNAL] = matched_concepts_set
                chunk_doc_copy[KEY_IS_DIRECT_HIT_INTERNAL] = len(hits_for_chunk) > 0
                deduped_chunks[chunk_key] = chunk_doc_copy

        # ----------------------------------------------------------------------
        # Step 5: Construct Aggregated Result Objects
        # ----------------------------------------------------------------------
        # Group chunks by book_id to form Master Result Items
        book_groups = defaultdict(list)
        for (b_id, c_idx), chunk_rec in deduped_chunks.items():
            book_groups[b_id].append(chunk_rec)

        aggregated_results = []
        for b_id, group_chunks in book_groups.items():
            # Sort chunks by chunk_index
            group_chunks.sort(key=lambda x: x.get(RESULT_KEY_CHUNK_INDEX, 0))

            total_score = sum(c[RESULT_KEY_SCORE] for c in group_chunks)
            all_concepts_set = set()
            for c in group_chunks:
                all_concepts_set.update(c.get(KEY_MATCHED_CONCEPTS_INTERNAL, set()))

            first_c = group_chunks[0]
            b_name = first_c.get(RESULT_KEY_BOOK_NAME, f"{FALLBACK_BOOK_NAME_PREFIX}{b_id}")
            ch_title = first_c.get(RESULT_KEY_CHAPTER_TITLE, FALLBACK_CHAPTER_TITLE_DEFAULT)
            ch_num = first_c.get(RESULT_KEY_CHAPTER_NUMBER, 1)
            f_link = first_c.get(RESULT_KEY_FILE_LINK, "")

            # Formatted list of matched concepts
            matched_concepts_list = sorted(list(all_concepts_set))

            aggregated_results.append({
                RESULT_KEY_TOTAL_AGGREGATED_SCORE: round(total_score, SCORE_ROUND_DECIMALS),
                RESULT_KEY_BOOK_ID: b_id,
                RESULT_KEY_BOOK_NAME: b_name,
                RESULT_KEY_CHAPTER_TITLE: ch_title,
                RESULT_KEY_CHAPTER_NUMBER: ch_num,
                RESULT_KEY_FILE_LINK: f_link,
                RESULT_KEY_CHUNKS: group_chunks,
                RESULT_KEY_MATCHED_CONCEPTS: matched_concepts_list
            })

        # Rank master list by total_aggregated_score descending
        aggregated_results.sort(key=lambda x: x[RESULT_KEY_TOTAL_AGGREGATED_SCORE], reverse=True)
        return aggregated_results

    def _fetch_book_chunks_in_range(self, book_id: int, min_idx: int, max_idx: int) -> List[Dict[str, Any]]:
        """Queries OpenSearch for chunks belonging to book_id within chunk_index range [min_idx, max_idx]."""
        search_body = {
            KEY_SIZE: EXPANDED_SEARCH_SIZE,
            KEY_SOURCE: {
                KEY_EXCLUDES: [FIELD_CHUNK_VECTOR]
            },
            KEY_QUERY: {
                KEY_BOOL: {
                    KEY_MUST: [
                        {KEY_TERM: {FIELD_METADATA_BOOK_ID: book_id}},
                        {KEY_RANGE: {FIELD_METADATA_CHUNK_INDEX: {KEY_GTE: min_idx, KEY_LTE: max_idx}}}
                    ]
                }
            }
        }
        try:
            resp = self.qm.client.search(index=self.qm.util.chunks_index, body=search_body, request_timeout=OPENSEARCH_RANGE_TIMEOUT)
            hits = resp.get(KEY_HITS, {}).get(KEY_HITS, [])
            return self.qm._enrich_chunk_hits(hits)
        except Exception as e:
            print(f"{LOG_RANGE_FETCH_ERROR_PREFIX}{book_id}: {e}")
            return []

def format_augmented_results_to_text(results: list) -> str:
    """Formats the aggregated search results into a clean text string containing
    book titles, all chunks ordered from lowest to highest chunk_index/chunk_id,
    with '...' inserted whenever there is a gap between sequential chunks.
    """
    if not results:
        return NO_RESULTS_MESSAGE

    output_blocks = []

    for group_idx, result_group in enumerate(results):
        book_title = str(result_group.get(RESULT_KEY_BOOK_NAME, "")).strip()
        chunks = result_group.get(RESULT_KEY_CHUNKS, [])

        if not chunks:
            continue

        group_lines = []
        if group_idx > 0:
            group_lines.append(BOOK_SECTION_DELIMITER)
            group_lines.append(EMPTY_STRING)

        group_lines.append(f"[{book_title}]")
        group_lines.append(EMPTY_STRING)

        # Sort chunks by chunk_index ascending (lowest to highest)
        sorted_chunks = sorted(chunks, key=lambda c: c.get(RESULT_KEY_CHUNK_INDEX, 0))

        prev_idx = None
        for chunk in sorted_chunks:
            curr_idx = chunk.get(RESULT_KEY_CHUNK_INDEX, 0)
            chunk_text = str(chunk.get(RESULT_KEY_CHUNK_TEXT, "")).strip()

            if not chunk_text:
                continue

            if prev_idx is not None and curr_idx > prev_idx + 1:
                group_lines.append(ELLIPSIS_GAP_INDICATOR)

            group_lines.append(chunk_text)
            prev_idx = curr_idx

        output_blocks.append(NEWLINE.join(group_lines))

    return NEWLINE.join(output_blocks)
