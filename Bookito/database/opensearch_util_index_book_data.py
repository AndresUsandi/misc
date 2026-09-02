import os
from opensearchpy import OpenSearch, helpers

# Top-of-file Constants
BULK_INDEX_REQUEST_TIMEOUT = 180

INDEX_BOOKS_SUFFIX = "bookito_books"
INDEX_CHAPTERS_SUFFIX = "bookito_chapters"
INDEX_CHUNKS_SUFFIX = "bookito_chunks"
INDEX_CONCEPTS_SUFFIX = "bookito_concepts"

FILE_URL_PREFIX = "file:///"
BACKSLASH_CHAR = "\\"
FORWARD_SLASH_CHAR = "/"

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
FIELD_PHRASE = "phrase"
FIELD_SCORE = "score"
FIELD_CHAPTERS_COUNT = "chapters_count"
FIELD_TOTAL_OCCURRENCES = "total_occurrences"

KEY_BULK_INDEX = "_index"
KEY_BULK_ID = "_id"
KEY_BULK_SOURCE = "_source"

LOG_INDEXED_CHAPTERS_FORMAT = "Indexed {count} chapters"
LOG_GENERATING_EMBEDDINGS_FORMAT = "Generating embeddings for {count} chunks..."
LOG_INDEXED_CHUNKS_FORMAT = "Indexed {count} chunks"
LOG_INDEXED_CONCEPTS_FORMAT = "Indexed {count} concepts"

def index_book_data(client: OpenSearch, index_prefix: str, book, book_name: str, book_id: int, file_path: str, embedder, concepts: list = None):
    """Indexes a parsed Book entity into OpenSearch books, chapters, chunks, and concepts indices."""
    books_index = f"{index_prefix}{INDEX_BOOKS_SUFFIX}"
    chapters_index = f"{index_prefix}{INDEX_CHAPTERS_SUFFIX}"
    chunks_index = f"{index_prefix}{INDEX_CHUNKS_SUFFIX}"
    concepts_index = f"{index_prefix}{INDEX_CONCEPTS_SUFFIX}"

    abs_path = os.path.abspath(file_path).replace(BACKSLASH_CHAR, FORWARD_SLASH_CHAR)
    file_link = f"{FILE_URL_PREFIX}{abs_path}"
    
    book_doc = {
        FIELD_BOOK_ID: book_id,
        FIELD_BOOK_NAME: book_name,
        FIELD_FILE_LINK: file_link
    }
    client.index(index=books_index, id=str(book_id), body=book_doc, request_timeout=BULK_INDEX_REQUEST_TIMEOUT)
    
    # 1. Index Chapters
    chapter_actions = []
    for ch in book.Chapters:
        doc = {
            FIELD_CHAPTER_ID: ch.Id,
            FIELD_BOOK_ID: book_id,
            FIELD_CHAPTER_TITLE: ch.Title,
            FIELD_CHAPTER_NUMBER: ch.Number,
            FIELD_CHAPTER_TEXT: ch.getFullText()
        }
        chapter_actions.append({
            KEY_BULK_INDEX: chapters_index,
            KEY_BULK_ID: str(ch.Id),
            KEY_BULK_SOURCE: doc
        })
        
    if chapter_actions:
        helpers.bulk(client, chapter_actions, raise_on_error=True, request_timeout=BULK_INDEX_REQUEST_TIMEOUT)
        print(LOG_INDEXED_CHAPTERS_FORMAT.format(count=len(chapter_actions)))
        
    # 2. Index Chunks with Vectors
    all_chunks = []
    for ch in book.Chapters:
        for chunk in ch.Chunks:
            all_chunks.append((ch, chunk))
                
    if all_chunks:
        texts = [chunk.Text for ch, chunk in all_chunks]
        print(LOG_GENERATING_EMBEDDINGS_FORMAT.format(count=len(texts)))
        vectors = embedder.embed_texts(texts)
        
        chunk_actions = []
        for i, (ch, chunk) in enumerate(all_chunks):
            doc = {
                FIELD_CHUNK_ID: chunk.Id,
                FIELD_CHAPTER_ID: ch.Id,
                FIELD_CHUNK_TEXT: chunk.Text,
                FIELD_CHUNK_VECTOR: vectors[i],
                FIELD_METADATA: {
                    FIELD_BOOK_ID: book_id,
                    FIELD_CHAPTER_NUMBER: ch.Number,
                    FIELD_CHUNK_INDEX: chunk.Index
                }
            }
            chunk_actions.append({
                KEY_BULK_INDEX: chunks_index,
                KEY_BULK_ID: str(chunk.Id),
                KEY_BULK_SOURCE: doc
            })
            
        helpers.bulk(client, chunk_actions, chunk_size=100, raise_on_error=True, request_timeout=BULK_INDEX_REQUEST_TIMEOUT)
        try:
            client.indices.refresh(index=chunks_index, request_timeout=BULK_INDEX_REQUEST_TIMEOUT)
            c_cnt = client.count(index=chunks_index, request_timeout=BULK_INDEX_REQUEST_TIMEOUT).get("count", 0)
            print(LOG_INDEXED_CHUNKS_FORMAT.format(count=len(chunk_actions)) + f" (OpenSearch chunk count: {c_cnt})")
        except Exception:
            print(LOG_INDEXED_CHUNKS_FORMAT.format(count=len(chunk_actions)))

    # 3. Index Concepts if provided
    if concepts:
        concept_actions = []
        for phrase, score, chapters_count, total_occurrences in concepts:
            doc = {
                FIELD_BOOK_ID: book_id,
                FIELD_PHRASE: phrase,
                FIELD_SCORE: score,
                FIELD_CHAPTERS_COUNT: chapters_count,
                FIELD_TOTAL_OCCURRENCES: total_occurrences
            }
            concept_actions.append({
                KEY_BULK_INDEX: concepts_index,
                KEY_BULK_SOURCE: doc
            })
            
        if concept_actions:
            helpers.bulk(client, concept_actions, raise_on_error=True, request_timeout=BULK_INDEX_REQUEST_TIMEOUT)
            print(LOG_INDEXED_CONCEPTS_FORMAT.format(count=len(concept_actions)))
