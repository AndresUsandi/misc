from opensearchpy import OpenSearch

# Top-of-file Constants
INDEX_BOOKS_SUFFIX = "bookito_books"
INDEX_CHAPTERS_SUFFIX = "bookito_chapters"
INDEX_CHUNKS_SUFFIX = "bookito_chunks"
INDEX_CONCEPTS_SUFFIX = "bookito_concepts"
INDEX_WORDS_SUFFIX = "bookito_words"

VECTOR_DIMENSION = 384
HNSW_EF_CONSTRUCTION = 128
HNSW_M = 16

KEY_MAPPINGS = "mappings"
KEY_PROPERTIES = "properties"
KEY_SETTINGS = "settings"
KEY_INDEX = "index"
KEY_KNN = "knn"
SETTING_EF_SEARCH_KEY = "index.knn.algo_param.ef_search"
SETTING_KNN_ALGO_PARAM_EF_SEARCH = "knn.algo_param.ef_search"
DEFAULT_EF_SEARCH_VALUE = 512

TYPE_INTEGER = "integer"
TYPE_KEYWORD = "keyword"
TYPE_TEXT = "text"
TYPE_FLOAT = "float"
TYPE_KNN_VECTOR = "knn_vector"
ENGINE_FAISS = "faiss"

FIELD_BOOK_ID = "book_id"
FIELD_BOOK_NAME = "book_name"
FIELD_FILE_LINK = "file_link"
FIELD_CHAPTER_ID = "chapter_id"
FIELD_CHAPTER_TITLE = "chapter_title"
FIELD_CHAPTER_NUMBER = "chapter_number"
FIELD_CHAPTER_TEXT = "chapter_text"
FIELD_CHUNK_ID = "chunk_id"
FIELD_CHUNK_TEXT = "chunk_text"
FIELD_CHUNK_VECTOR = "chunk_vector"
FIELD_METADATA = "metadata"
FIELD_CHUNK_INDEX = "chunk_index"
FIELD_CONCEPT_ID = "concept_id"
FIELD_PHRASE = "phrase"
FIELD_SCORE = "score"
FIELD_CHAPTERS_COUNT = "chapters_count"
FIELD_TOTAL_OCCURRENCES = "total_occurrences"
FIELD_WORD = "word"
FIELD_BOOK_COUNT = "book_count"
FIELD_TOTAL_BOOKS = "total_books"

METHOD_NAME_HNSW = "hnsw"
SPACE_TYPE_L2 = "l2"

LOG_CREATED_INDEX_FORMAT = "Created index: {index_name}"

def create_indices(client: OpenSearch, index_prefix: str = ""):
    """Creates the OpenSearch index mappings for books, chapters, chunks, and concepts if they do not exist."""
    books_index = f"{index_prefix}{INDEX_BOOKS_SUFFIX}"
    chapters_index = f"{index_prefix}{INDEX_CHAPTERS_SUFFIX}"
    chunks_index = f"{index_prefix}{INDEX_CHUNKS_SUFFIX}"
    concepts_index = f"{index_prefix}{INDEX_CONCEPTS_SUFFIX}"

    books_mapping = {
        KEY_MAPPINGS: {
            KEY_PROPERTIES: {
                FIELD_BOOK_ID: {"type": TYPE_INTEGER},
                FIELD_BOOK_NAME: {"type": TYPE_KEYWORD},
                FIELD_FILE_LINK: {"type": TYPE_KEYWORD}
            }
        }
    }

    chapters_mapping = {
        KEY_MAPPINGS: {
            KEY_PROPERTIES: {
                FIELD_CHAPTER_ID: {"type": TYPE_INTEGER},
                FIELD_BOOK_ID: {"type": TYPE_INTEGER},
                FIELD_CHAPTER_TITLE: {"type": TYPE_TEXT},
                FIELD_CHAPTER_NUMBER: {"type": TYPE_INTEGER},
                FIELD_CHAPTER_TEXT: {"type": TYPE_TEXT}
            }
        }
    }
    
    chunks_mapping = {
        KEY_SETTINGS: {
            KEY_INDEX: {
                KEY_KNN: True,
                SETTING_KNN_ALGO_PARAM_EF_SEARCH: DEFAULT_EF_SEARCH_VALUE
            }
        },
        KEY_MAPPINGS: {
            KEY_PROPERTIES: {
                FIELD_CHUNK_ID: {"type": TYPE_INTEGER},
                FIELD_CHAPTER_ID: {"type": TYPE_INTEGER},
                FIELD_CHUNK_TEXT: {"type": TYPE_TEXT},
                FIELD_CHUNK_VECTOR: {
                    "type": TYPE_KNN_VECTOR,
                    "dimension": VECTOR_DIMENSION,
                    "method": {
                        "name": METHOD_NAME_HNSW,
                        "space_type": SPACE_TYPE_L2,
                        "engine": ENGINE_FAISS,
                        "parameters": {
                            "ef_construction": HNSW_EF_CONSTRUCTION,
                            "m": HNSW_M
                        }
                    }
                },
                FIELD_METADATA: {
                    KEY_PROPERTIES: {
                        FIELD_BOOK_ID: {"type": TYPE_INTEGER},
                        FIELD_CHAPTER_NUMBER: {"type": TYPE_INTEGER},
                        FIELD_CHUNK_INDEX: {"type": TYPE_INTEGER}
                    }
                }
            }
        }
    }
    
    concepts_mapping = {
        KEY_MAPPINGS: {
            KEY_PROPERTIES: {
                FIELD_CONCEPT_ID: {"type": TYPE_INTEGER},
                FIELD_BOOK_ID: {"type": TYPE_INTEGER},
                FIELD_PHRASE: {"type": TYPE_KEYWORD},
                FIELD_SCORE: {"type": TYPE_FLOAT},
                FIELD_CHAPTERS_COUNT: {"type": TYPE_INTEGER},
                FIELD_TOTAL_OCCURRENCES: {"type": TYPE_INTEGER}
            }
        }
    }
    
    words_index = f"{index_prefix}{INDEX_WORDS_SUFFIX}"

    words_mapping = {
        KEY_MAPPINGS: {
            KEY_PROPERTIES: {
                FIELD_WORD: {"type": TYPE_KEYWORD},
                FIELD_BOOK_COUNT: {"type": TYPE_INTEGER},
                FIELD_TOTAL_BOOKS: {"type": TYPE_INTEGER},
                FIELD_SCORE: {"type": TYPE_FLOAT}
            }
        }
    }
    
    for idx_name, mapping in [
        (books_index, books_mapping),
        (chapters_index, chapters_mapping),
        (chunks_index, chunks_mapping),
        (concepts_index, concepts_mapping),
        (words_index, words_mapping)
    ]:
        try:
            if not client.indices.exists(index=idx_name):
                client.indices.create(index=idx_name, body=mapping)
                print(LOG_CREATED_INDEX_FORMAT.format(index_name=idx_name))
        except Exception:
            pass

    try:
        if client.indices.exists(index=chunks_index):
            client.indices.put_settings(index=chunks_index, body={SETTING_EF_SEARCH_KEY: DEFAULT_EF_SEARCH_VALUE})
    except Exception:
        pass
