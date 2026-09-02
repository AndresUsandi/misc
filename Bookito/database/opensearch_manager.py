from opensearchpy import OpenSearch
from database.opensearch_util_connect import connect_opensearch, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TIMEOUT
from database.opensearch_util_get_max_id import get_max_id as util_get_max_id
from database.opensearch_util_create_indices import (
    create_indices as util_create_indices,
    INDEX_BOOKS_SUFFIX,
    INDEX_CHAPTERS_SUFFIX,
    INDEX_CHUNKS_SUFFIX,
    INDEX_CONCEPTS_SUFFIX,
    INDEX_WORDS_SUFFIX
)
from database.opensearch_util_index_book_data import index_book_data as util_index_book_data

# Top-of-file Constants
EMPTY_PREFIX = ""

class OpenSearchManager:
    """Consolidated high-level OpenSearch Manager that delegates operations to modular utility functions."""
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, index_prefix: str = EMPTY_PREFIX):
        self.host = host
        self.port = port
        self.index_prefix = index_prefix
        self.books_index = f"{index_prefix}{INDEX_BOOKS_SUFFIX}"
        self.chapters_index = f"{index_prefix}{INDEX_CHAPTERS_SUFFIX}"
        self.chunks_index = f"{index_prefix}{INDEX_CHUNKS_SUFFIX}"
        self.concepts_index = f"{index_prefix}{INDEX_CONCEPTS_SUFFIX}"
        self.words_index = f"{index_prefix}{INDEX_WORDS_SUFFIX}"
        self.client = None

    def connect(self) -> OpenSearch:
        self.client = connect_opensearch(host=self.host, port=self.port, timeout=DEFAULT_TIMEOUT)
        return self.client

    def get_max_id(self, index_name: str, id_field: str) -> int:
        if not self.client:
            self.connect()
        return util_get_max_id(self.client, index_name, id_field)

    def create_indices(self):
        if not self.client:
            self.connect()
        return util_create_indices(self.client, index_prefix=self.index_prefix)

    def index_book_data(self, book, book_name: str, book_id: int, file_path: str, embedder, concepts: list = None):
        if not self.client:
            self.connect()
        return util_index_book_data(
            client=self.client,
            index_prefix=self.index_prefix,
            book=book,
            book_name=book_name,
            book_id=book_id,
            file_path=file_path,
            embedder=embedder,
            concepts=concepts
        )

# Backward Compatibility Alias for existing imports
BookitoOpenSearchUtil = OpenSearchManager
