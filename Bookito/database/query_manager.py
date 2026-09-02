import os
import sys
import threading
from typing import List, Dict, Any

# Ensure parent directory is in sys.path for relative/absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.opensearch_manager import OpenSearchManager
from embeddings.embedding_generator import EmbeddingGenerator

# Top-of-file Constants: Defaults & Connection Settings
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9200
DEFAULT_INDEX_PREFIX = ""
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 100
DEFAULT_TOP_K = 100
DEFAULT_SCORE = 0.0
DEFAULT_DEFAULT_ID = -1
FIRST_ELEMENT_INDEX = 0
DEFAULT_MAX_CONCURRENT_QUERIES = 3
MIN_CONCURRENT_QUERIES_LIMIT = 1
MIN_VECTOR_SEARCH_WORD_COUNT = 2

SEARCH_BODY_LEXICAL_TIMEOUT = "30s"
SEARCH_BODY_VECTOR_TIMEOUT = "30s"
OPENSEARCH_SEARCH_REQUEST_TIMEOUT = 30
OPENSEARCH_MGET_REQUEST_TIMEOUT = 30

# OpenSearch Query Structure & Cluster Settings Keys
KEY_PERSISTENT = "persistent"
SETTING_KNN_MEMORY_CB_LIMIT = "knn.memory.circuit_breaker.limit"
SETTING_KNN_CB_TRIGGERED = "knn.circuit_breaker.triggered"
VAL_KNN_MEMORY_CB_LIMIT_48G = "48g"
VAL_FALSE_STRING = "false"

KEY_FROM = "from"
KEY_SIZE = "size"
KEY_TIMEOUT = "timeout"
KEY_QUERY = "query"
KEY_MATCH = "match"
KEY_OPERATOR = "operator"
OPENSEARCH_OPERATOR_AND = "and"
KEY_KNN = "knn"
KEY_VECTOR = "vector"
KEY_FIELD = "field"
KEY_QUERY_VECTOR = "query_vector"
KEY_K = "k"
KEY_FILTER = "filter"
KEY_BOOL = "bool"
KEY_MUST = "must"
KEY_TERMS = "terms"
CANDIDATE_SEARCH_SIZE = 100
CANDIDATE_CHUNK_SEARCH_SIZE = 200
MAX_CANDIDATE_BOOKS = 10
KEY_SCRIPT_SCORE = "script_score"
KEY_SCRIPT = "script"
KEY_LANG = "lang"
KEY_PARAMS = "params"
KEY_QUERY_VALUE = "query_value"
KEY_SPACE_TYPE = "space_type"
VAL_KNN_SCORE = "knn_score"
VAL_KNN_LANG = "knn"
VAL_SPACE_TYPE_L2 = "l2"
KEY_HITS = "hits"
KEY_SOURCE = "_source"
KEY_SCORE = "_score"
KEY_IDS = "ids"
KEY_DOCS = "docs"
KEY_FOUND = "found"

# OpenSearch Schema Field Names
FIELD_CHUNK_ID = "chunk_id"
FIELD_CHAPTER_ID = "chapter_id"
FIELD_CHUNK_TEXT = "chunk_text"
FIELD_CHUNK_VECTOR = "chunk_vector"
FIELD_METADATA = "metadata"
FIELD_BOOK_ID = "book_id"
FIELD_CHAPTER_NUMBER = "chapter_number"
FIELD_CHUNK_INDEX = "chunk_index"
FIELD_CHAPTER_TITLE = "chapter_title"
FIELD_BOOK_NAME = "book_name"
FIELD_FILE_LINK = "file_link"

# Enriched Result Dictionary Keys
RESULT_KEY_SCORE = "score"
RESULT_KEY_CHUNK_ID = "chunk_id"
RESULT_KEY_CHUNK_INDEX = "chunk_index"
RESULT_KEY_CHUNK_TEXT = "chunk_text"
RESULT_KEY_VECTOR_DIM = "vector_dim"
RESULT_KEY_CHAPTER_ID = "chapter_id"
RESULT_KEY_CHAPTER_NUMBER = "chapter_number"
RESULT_KEY_CHAPTER_TITLE = "chapter_title"
RESULT_KEY_BOOK_ID = "book_id"
RESULT_KEY_BOOK_NAME = "book_name"
RESULT_KEY_FILE_LINK = "file_link"

# Default Formats & Messages
FALLBACK_CHAPTER_TITLE_PREFIX = "Chapter "
FALLBACK_BOOK_NAME_PREFIX = "Book "
EMPTY_STRING = ""

LOG_LEXICAL_ERROR_PREFIX = "Lexical search warning/error: "
LOG_VECTOR_ERROR_PREFIX = "Vector search warning/error: "
LOG_CHAPTER_FETCH_ERROR_PREFIX = "Error fetching chapters for enrichment: "
LOG_BOOK_FETCH_ERROR_PREFIX = "Error fetching books for enrichment: "

class QueryManager:
    """Manages search queries against OpenSearch indices (lexical & vector search)
    and joins chunk hits with their parent Chapter and Book metadata.
    """
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, index_prefix: str = DEFAULT_INDEX_PREFIX, embedder: EmbeddingGenerator = None, max_concurrent_queries: int = DEFAULT_MAX_CONCURRENT_QUERIES):
        self.util = OpenSearchManager(host=host, port=port, index_prefix=index_prefix)
        self.client = self.util.connect()
        self.util.create_indices()
        self._ensure_knn_circuit_breaker_settings()
        self.embedder = embedder if embedder is not None else EmbeddingGenerator()

        self.max_concurrent_queries = max_concurrent_queries
        self.query_semaphore = threading.Semaphore(max_concurrent_queries)

        threading.Thread(target=self.warmup_knn_index, daemon=True).start()

    def set_max_concurrent_queries(self, limit: int):
        """Dynamically updates the maximum allowed concurrent OpenSearch queries."""
        if limit >= MIN_CONCURRENT_QUERIES_LIMIT:
            self.max_concurrent_queries = limit
            self.query_semaphore = threading.Semaphore(limit)

    def _ensure_knn_circuit_breaker_settings(self):
        """Ensures KNN memory circuit breaker is set to 48g and not triggered so graphs remain resident in native RAM."""
        try:
            body = {
                KEY_PERSISTENT: {
                    SETTING_KNN_MEMORY_CB_LIMIT: VAL_KNN_MEMORY_CB_LIMIT_48G,
                    SETTING_KNN_CB_TRIGGERED: VAL_FALSE_STRING
                }
            }
            self.client.cluster.put_settings(body=body)
        except Exception:
            pass

    def warmup_knn_index(self):
        """Asynchronously pre-loads HNSW graph index files off disk into native C++ RAM in a background thread."""
        try:
            self.client.transport.perform_request("GET", f"/_plugins/_knn/warmup/{self.util.chunks_index}")
        except Exception:
            pass

    def lexical_search(self, query_text: str, page: int = DEFAULT_PAGE, page_size: int = DEFAULT_PAGE_SIZE, top_k: int = DEFAULT_TOP_K) -> List[Dict[str, Any]]:
        """Performs a text match search on chunk_text in OpenSearch chunks_index with pagination."""
        if not query_text or not query_text.strip():
            return []

        actual_size = top_k if top_k is not None else page_size
        from_offset = (page - 1) * actual_size

        search_query = {
            KEY_FROM: from_offset,
            KEY_SIZE: actual_size,
            KEY_TIMEOUT: SEARCH_BODY_LEXICAL_TIMEOUT,
            KEY_QUERY: {
                KEY_MATCH: {
                    FIELD_CHUNK_TEXT: {
                        KEY_QUERY: query_text,
                        KEY_OPERATOR: OPENSEARCH_OPERATOR_AND
                    }
                }
            }
        }
        
        with self.query_semaphore:
            try:
                response = self.client.search(index=self.util.chunks_index, body=search_query, _source_excludes=[FIELD_CHUNK_VECTOR], request_timeout=OPENSEARCH_SEARCH_REQUEST_TIMEOUT)
                hits = response.get(KEY_HITS, {}).get(KEY_HITS, [])
                return self._enrich_chunk_hits(hits)
            except Exception as e:
                print(f"{LOG_LEXICAL_ERROR_PREFIX}{e}")
                return []

    def vector_search(self, query_text: str, page: int = DEFAULT_PAGE, page_size: int = DEFAULT_PAGE_SIZE, top_k: int = DEFAULT_TOP_K) -> List[Dict[str, Any]]:
        """Generates embedding for query_text and performs KNN vector search on chunk_vector with pagination."""
        if not query_text or not query_text.strip():
            return []

        import re
        word_count = len(re.findall(r'\b\w+\b', query_text))
        if word_count < MIN_VECTOR_SEARCH_WORD_COUNT:
            return []

        query_vectors = self.embedder.embed_texts([query_text])
        if not query_vectors:
            return []
            
        query_vector = query_vectors[FIRST_ELEMENT_INDEX]

        actual_size = top_k if top_k is not None else page_size
        from_offset = (page - 1) * actual_size
        knn_k = from_offset + actual_size

        search_query = {
            KEY_FROM: from_offset,
            KEY_SIZE: actual_size,
            KEY_TIMEOUT: SEARCH_BODY_VECTOR_TIMEOUT,
            KEY_QUERY: {
                KEY_KNN: {
                    FIELD_CHUNK_VECTOR: {
                        KEY_VECTOR: query_vector,
                        KEY_K: knn_k
                    }
                }
            }
        }

        with self.query_semaphore:
            try:
                response = self.client.search(
                    index=self.util.chunks_index,
                    body=search_query,
                    _source_excludes=[FIELD_CHUNK_VECTOR],
                    request_timeout=OPENSEARCH_SEARCH_REQUEST_TIMEOUT
                )
                hits = response.get(KEY_HITS, {}).get(KEY_HITS, [])
                return self._enrich_chunk_hits(hits)
            except Exception as e:
                print(f"{LOG_VECTOR_ERROR_PREFIX}{e}")
                return []

    def _enrich_chunk_hits(self, hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Joins chunk search hits with Chapter and Book documents from OpenSearch."""
        if not hits:
            return []

        chapter_ids = set()
        book_ids = set()

        for hit in hits:
            source = hit.get(KEY_SOURCE, {})
            ch_id = source.get(FIELD_CHAPTER_ID)
            if ch_id is not None:
                chapter_ids.add(str(ch_id))

            meta = source.get(FIELD_METADATA, {})
            b_id = meta.get(FIELD_BOOK_ID) or source.get(FIELD_BOOK_ID)
            if b_id is not None:
                book_ids.add(str(b_id))

        # Batch fetch Chapters
        chapters_map = {}
        if chapter_ids:
            try:
                ch_resp = self.client.mget(index=self.util.chapters_index, body={KEY_IDS: list(chapter_ids)}, request_timeout=OPENSEARCH_MGET_REQUEST_TIMEOUT)
                for doc in ch_resp.get(KEY_DOCS, []):
                    if doc.get(KEY_FOUND):
                        src = doc.get(KEY_SOURCE, {})
                        c_id = src.get(FIELD_CHAPTER_ID)
                        if c_id is not None:
                            chapters_map[c_id] = src
            except Exception as e:
                print(f"{LOG_CHAPTER_FETCH_ERROR_PREFIX}{e}")

        # Batch fetch Books
        books_map = {}
        if book_ids:
            try:
                bk_resp = self.client.mget(index=self.util.books_index, body={KEY_IDS: list(book_ids)}, request_timeout=OPENSEARCH_MGET_REQUEST_TIMEOUT)
                for doc in bk_resp.get(KEY_DOCS, []):
                    if doc.get(KEY_FOUND):
                        src = doc.get(KEY_SOURCE, {})
                        b_id = src.get(FIELD_BOOK_ID)
                        if b_id is not None:
                            books_map[b_id] = src
            except Exception as e:
                print(f"{LOG_BOOK_FETCH_ERROR_PREFIX}{e}")

        enriched_results = []
        for hit in hits:
            score = hit.get(KEY_SCORE, DEFAULT_SCORE)
            source = hit.get(KEY_SOURCE, {})

            c_id = source.get(FIELD_CHAPTER_ID, DEFAULT_DEFAULT_ID)
            chunk_id = source.get(FIELD_CHUNK_ID, DEFAULT_DEFAULT_ID)
            chunk_text = source.get(FIELD_CHUNK_TEXT, EMPTY_STRING)
            chunk_vector = source.get(FIELD_CHUNK_VECTOR, [])

            meta = source.get(FIELD_METADATA, {})
            b_id = meta.get(FIELD_BOOK_ID, DEFAULT_DEFAULT_ID)
            ch_num_meta = meta.get(FIELD_CHAPTER_NUMBER, DEFAULT_DEFAULT_ID)
            chunk_idx = meta.get(FIELD_CHUNK_INDEX, DEFAULT_DEFAULT_ID)

            chapter_data = chapters_map.get(c_id, {})
            book_data = books_map.get(b_id, {})

            default_ch_title = f"{FALLBACK_CHAPTER_TITLE_PREFIX}{ch_num_meta}"
            default_b_name = f"{FALLBACK_BOOK_NAME_PREFIX}{b_id}"

            ch_title = chapter_data.get(FIELD_CHAPTER_TITLE, default_ch_title)
            ch_num = chapter_data.get(FIELD_CHAPTER_NUMBER, ch_num_meta)
            b_name = book_data.get(FIELD_BOOK_NAME, default_b_name)
            f_link = book_data.get(FIELD_FILE_LINK, EMPTY_STRING)

            enriched_results.append({
                RESULT_KEY_SCORE: score,
                RESULT_KEY_CHUNK_ID: chunk_id,
                RESULT_KEY_CHUNK_INDEX: chunk_idx,
                RESULT_KEY_CHUNK_TEXT: chunk_text,
                RESULT_KEY_VECTOR_DIM: len(chunk_vector) if chunk_vector else 0,
                RESULT_KEY_CHAPTER_ID: c_id,
                RESULT_KEY_CHAPTER_NUMBER: ch_num,
                RESULT_KEY_CHAPTER_TITLE: ch_title,
                RESULT_KEY_BOOK_ID: b_id,
                RESULT_KEY_BOOK_NAME: b_name,
                RESULT_KEY_FILE_LINK: f_link
            })

        return enriched_results
