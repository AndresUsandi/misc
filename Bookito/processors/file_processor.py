import os
import shutil
from parsers.worker import BookParserWorker
from embeddings.embedding_generator import EmbeddingGenerator
from database.opensearch_manager import BookitoOpenSearchUtil
from processors.concept_processor import ConceptProcessor

# Top-of-file Constants
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9200
DEFAULT_INDEX_PREFIX = ""

FIELD_BOOK_ID = "book_id"
FIELD_CHAPTER_ID = "chapter_id"
FIELD_CHUNK_ID = "chunk_id"

EXT_PDF = ".pdf"
EXT_EPUB = ".epub"
EXT_CHM = ".chm"
SUPPORTED_EXTENSIONS = {EXT_PDF, EXT_EPUB, EXT_CHM}

LOG_LIMIT_MODE_WARNING_FORMAT = "\n[WARNING] Ingestion is running in LIMIT MODE (max {max_items} items per book). This is intended ONLY for fast integration testing!\n"
LOG_CONNECTING_FORMAT = "Connecting to OpenSearch at {host}:{port}..."
LOG_COPIED_REJECTED_FORMAT = "Copied rejected file to {dest}"
LOG_FAILED_COPY_REJECTED_FORMAT = "Failed to copy rejected file {f_path}: {error}"
LOG_FOUND_BOOKS_FORMAT = "Found {count} books to process."
LOG_PROCESSING_BOOK_FORMAT = "\nProcessing book: {book_name}"
LOG_PARSED_DETAILS_FORMAT = "Parsed structure details:\n  - Chapters: {chapters}\n  - Chunks: {chunks}"
LOG_EXTRACTING_CONCEPTS_FORMAT = "Extracting concepts/keyphrases for {book_name}..."
LOG_EXTRACTED_CONCEPTS_FORMAT = "Extracted {count} concepts for {book_name}"
LOG_FINISHED_INDEXING_FORMAT = "Successfully finished indexing {book_name}"
LOG_FAILED_INGESTION_FORMAT = "Failed to ingest book {f_path}: {error}"

def _safe_print(msg: str):
    """Safely prints strings that may contain non-CP1252 unicode characters to Windows stdout."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))

class FileProcessor:
    def __init__(self, opensearch_host=DEFAULT_HOST, opensearch_port=DEFAULT_PORT, index_prefix=DEFAULT_INDEX_PREFIX, rejection_folder=None, opensearch_util_class=None, embedder=None, parser=None, concept_processor=None):
        util_cls = opensearch_util_class or BookitoOpenSearchUtil
        self.db_util = util_cls(host=opensearch_host, port=opensearch_port, index_prefix=index_prefix)
        self.embedder = embedder
        self.parser = parser or BookParserWorker()
        self.concept_processor = concept_processor or ConceptProcessor()
        self.supported_exts = SUPPORTED_EXTENSIONS
        self.rejection_folder = rejection_folder

    def _handle_rejection(self, f_path: str):
        if self.rejection_folder:
            try:
                os.makedirs(self.rejection_folder, exist_ok=True)
                dest = os.path.join(self.rejection_folder, os.path.basename(f_path))
                shutil.copy2(f_path, dest)
                _safe_print(LOG_COPIED_REJECTED_FORMAT.format(dest=dest))
            except Exception as ce:
                _safe_print(LOG_FAILED_COPY_REJECTED_FORMAT.format(f_path=f_path, error=ce))

    def process(self, target_path: str, max_items_per_book: int = None):
        if max_items_per_book is not None:
            _safe_print(LOG_LIMIT_MODE_WARNING_FORMAT.format(max_items=max_items_per_book))
        # 1. Connect and Setup OpenSearch indexes
        _safe_print(LOG_CONNECTING_FORMAT.format(host=self.db_util.host, port=self.db_util.port))
        self.db_util.connect()
        self.db_util.create_indices()

        self.next_book_id = self.db_util.get_max_id(self.db_util.books_index, FIELD_BOOK_ID) + 1
        self.next_chapter_id = self.db_util.get_max_id(self.db_util.chapters_index, FIELD_CHAPTER_ID) + 1
        self.next_chunk_id = self.db_util.get_max_id(self.db_util.chunks_index, FIELD_CHUNK_ID) + 1

        # 2. Setup Embedder
        if self.embedder is None:
            self.embedder = EmbeddingGenerator()

        # 3. Locate files recursively
        files_to_process = []
        if os.path.isfile(target_path):
            ext = os.path.splitext(target_path)[1].lower()
            if ext in self.supported_exts:
                files_to_process.append(target_path)
            else:
                self._handle_rejection(target_path)
        elif os.path.isdir(target_path):
            for root, dirs, files in os.walk(target_path):
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in self.supported_exts:
                        files_to_process.append(os.path.join(root, f))
                    else:
                        full_path = os.path.join(root, f)
                        self._handle_rejection(full_path)

        _safe_print(LOG_FOUND_BOOKS_FORMAT.format(count=len(files_to_process)))

        # 4. Ingest each file
        for f_path in files_to_process:
            book_name = os.path.basename(f_path)
            _safe_print(LOG_PROCESSING_BOOK_FORMAT.format(book_name=book_name))
            try:
                book_data = self.parser.parse_book(f_path, max_items=max_items_per_book)
                
                total_chapters = len(book_data.Chapters)
                total_chunks = sum(len(ch.Chunks) for ch in book_data.Chapters)
                
                _safe_print(LOG_PARSED_DETAILS_FORMAT.format(chapters=total_chapters, chunks=total_chunks))
                
                book_id = self.next_book_id
                self.next_book_id += 1
                book_data.Id = book_id
                
                for ch in book_data.Chapters:
                    ch.Id = self.next_chapter_id
                    self.next_chapter_id += 1
                    for chunk in ch.Chunks:
                        chunk.Id = self.next_chunk_id
                        chunk.Index = self.next_chunk_id
                        self.next_chunk_id += 1
                
                _safe_print(LOG_EXTRACTING_CONCEPTS_FORMAT.format(book_name=book_name))
                concepts = self.concept_processor.processBook(book_data)
                _safe_print(LOG_EXTRACTED_CONCEPTS_FORMAT.format(count=len(concepts), book_name=book_name))

                self.db_util.index_book_data(
                    book=book_data,
                    book_name=book_name,
                    book_id=book_id,
                    file_path=f_path,
                    embedder=self.embedder,
                    concepts=concepts
                )
                _safe_print(LOG_FINISHED_INDEXING_FORMAT.format(book_name=book_name))
            except Exception as e:
                _safe_print(LOG_FAILED_INGESTION_FORMAT.format(f_path=f_path, error=e))
                self._handle_rejection(f_path)
                import traceback
                traceback.print_exc()
