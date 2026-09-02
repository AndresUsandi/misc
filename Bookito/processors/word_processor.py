import os
import sys
import re
import time
import json
import argparse
from collections import defaultdict
from typing import Dict, Set, Any
from opensearchpy import helpers

# Ensure parent directory is in sys.path for Bookito module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.opensearch_manager import OpenSearchManager

# ==============================================================================
# TOP-OF-FILE CONFIGURATION & LOG CONSTANTS
# ==============================================================================

CHUNK_BATCH_SIZE = 1000
DEFAULT_CHUNK_FETCH_SIZE = 1000
WORD_TOKEN_REGEX = r"\b[a-zA-Z]+\b"
SCORE_ROUND_DECIMALS = 4
DEFAULT_TOTAL_BOOKS_FALLBACK = 1
SCROLL_TIMEOUT = "10m"

CHECKPOINT_FILE_NAME = "word_processor_checkpoint.json"
KEY_LAST_PROCESSED_CHUNK_ID = "last_processed_chunk_id"
KEY_TOTAL_CHUNKS_PROCESSED = "total_chunks_processed"
KEY_UNIQUE_BOOKS = "unique_books"
KEY_WORD_BOOKS_MAP = "word_books_map"

CLI_ARG_RESET = "--reset"
CLI_ARG_RESET_SHORT = "-r"
CLI_HELP_RESET = "Reset word processor state and clear OpenSearch words index to start from scratch."

KEY_INDEX = "_index"
KEY_ID = "_id"
KEY_SOURCE = "_source"
KEY_OP_TYPE = "_op_type"
OP_TYPE_INDEX = "index"

FIELD_WORD = "word"
FIELD_BOOK_COUNT = "book_count"
FIELD_TOTAL_BOOKS = "total_books"
FIELD_SCORE = "score"
FIELD_CHUNK_TEXT = "chunk_text"
FIELD_METADATA = "metadata"
FIELD_BOOK_ID = "book_id"
FIELD_CHUNK_ID = "chunk_id"

LOG_START_PROCESSING = "Starting WordProcessor batch processing from OpenSearch chunks index..."
LOG_CLEAR_INDEX_FORMAT = "Clearing existing contents of OpenSearch index '{index_name}' for a clean slate restart..."
LOG_PROGRESS_FORMAT = "Processed {chunk_count} chunks across {book_count} unique books ({word_count} unique words tracked). Bulk upserting word scores..."
LOG_COMPLETED_FORMAT = "Completed WordProcessor execution in {elapsed:.2f}s. Processed {chunk_count} total chunks, tracked {word_count} words across {book_count} books."
LOG_BULK_SUCCESS_FORMAT = "Successfully indexed {count} word scores into '{index_name}'."
LOG_SCAN_ERROR_FORMAT = "Error scanning chunks from OpenSearch: {error}"
LOG_BULK_ERROR_FORMAT = "Error during bulk indexing of words: {error}"

LOG_CHUNK_PROCESSED_FORMAT = "[Chunk #{chunk_num}] ID: {chunk_id} | Book ID: {book_id} | Extracted: {token_count} words"
LOG_RECALC_HEADER_FORMAT = "--- Recalculated Scores after {chunk_count} Chunks (Unique Words: {word_count}, Total Books: {total_books}) ---"
LOG_SCORE_SAMPLE_HEADER_FORMAT = "Sample Top {sample_size} Calculated Word Scores:"
LOG_SCORE_ITEM_FORMAT = "   Word: '{word}' -> Book Count: {book_count}/{total_books} | Calculated Score: {score:.4f}"
LOG_RESUMING_FORMAT = "Resuming WordProcessor from last checkpoint: Chunk ID {last_chunk_id}, {chunk_count} total chunks processed so far across {book_count} books."
LOG_SAVED_CHECKPOINT_FORMAT = "Saved WordProcessor checkpoint (Last Chunk ID: {last_chunk_id}, Total Chunks: {chunk_count})."
LOG_NO_CHECKPOINT_FOUND = "No existing checkpoint found. Starting fresh WordProcessor scan..."
SAMPLE_SCORES_LOG_COUNT = 10

class WordProcessor:
    """Processes OpenSearch chunk documents in batches of 1,000, tokenizes words,
    tracks unique book identifiers per word, calculates standardized document frequency scores,
    and bulk-upserts word scores into the bookito_words OpenSearch index. Supports checkpoint resumption.
    """
    def __init__(self, chunk_batch_size: int = CHUNK_BATCH_SIZE, host: str = None, port: int = None, index_prefix: str = ""):
        self.chunk_batch_size = chunk_batch_size
        if host is not None and port is not None:
            self.osm = OpenSearchManager(host=host, port=port, index_prefix=index_prefix)
        else:
            self.osm = OpenSearchManager(index_prefix=index_prefix)
        self.client = self.osm.connect()
        self.osm.create_indices()

        # Word -> set of unique book identifiers (book_id)
        self.word_books_map: Dict[str, Set[Any]] = defaultdict(set)
        # Set of all unique book identifiers encountered
        self.unique_books: Set[Any] = set()
        self.total_chunks_processed = 0

    def get_checkpoint_path(self) -> str:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), CHECKPOINT_FILE_NAME)

    def load_checkpoint(self) -> Dict[str, Any]:
        checkpoint_path = self.get_checkpoint_path()
        if os.path.exists(checkpoint_path):
            try:
                with open(checkpoint_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.total_chunks_processed = data.get(KEY_TOTAL_CHUNKS_PROCESSED, 0)
                    self.unique_books = set(data.get(KEY_UNIQUE_BOOKS, []))
                    raw_map = data.get(KEY_WORD_BOOKS_MAP, {})
                    self.word_books_map = defaultdict(set, {k.lower().strip(): set(v) for k, v in raw_map.items()})
                    return data
            except Exception:
                pass
        return {}

    def save_checkpoint(self, last_chunk_id: Any):
        checkpoint_path = self.get_checkpoint_path()
        try:
            data = {
                KEY_LAST_PROCESSED_CHUNK_ID: last_chunk_id,
                KEY_TOTAL_CHUNKS_PROCESSED: self.total_chunks_processed,
                KEY_UNIQUE_BOOKS: list(self.unique_books),
                KEY_WORD_BOOKS_MAP: {k: list(v) for k, v in self.word_books_map.items()}
            }
            with open(checkpoint_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(LOG_SAVED_CHECKPOINT_FORMAT.format(last_chunk_id=last_chunk_id, chunk_count=self.total_chunks_processed))
        except Exception:
            pass

    def clear_checkpoint(self):
        checkpoint_path = self.get_checkpoint_path()
        if os.path.exists(checkpoint_path):
            try:
                os.remove(checkpoint_path)
            except Exception:
                pass

    def clear_words_index(self):
        """Deletes and recreates the bookito_words index to ensure a clean slate upon restart."""
        try:
            if self.client.indices.exists(index=self.osm.words_index):
                print(LOG_CLEAR_INDEX_FORMAT.format(index_name=self.osm.words_index))
                self.client.indices.delete(index=self.osm.words_index, ignore=[400, 404])
                time.sleep(0.5)
        except Exception:
            pass
        self.osm.create_indices()

    def process_all_chunks(self, reset: bool = False):
        """Scans all chunks from chunks_index 1,000 at a time, tracks word-to-book associations,
        and periodically recalculates & stores word scores in OpenSearch every 1,000 chunks.

        Args:
            reset: If True, clears the bookito_words index and deletes checkpoint to start fresh.
        """
        if reset:
            self.clear_words_index()
            self.clear_checkpoint()
            self.word_books_map = defaultdict(set)
            self.unique_books = set()
            self.total_chunks_processed = 0
            last_chunk_id = None
        else:
            checkpoint_data = self.load_checkpoint()
            last_chunk_id = checkpoint_data.get(KEY_LAST_PROCESSED_CHUNK_ID)
            if last_chunk_id is not None:
                print(LOG_RESUMING_FORMAT.format(
                    last_chunk_id=last_chunk_id,
                    chunk_count=self.total_chunks_processed,
                    book_count=len(self.unique_books)
                ))
            else:
                print(LOG_NO_CHECKPOINT_FOUND)

        print(LOG_START_PROCESSING)
        start_time = time.time()

        try:
            total_books_in_db = self.client.count(index=self.osm.books_index).get("count", 0)
        except Exception:
            total_books_in_db = 0

        if last_chunk_id is not None:
            scan_query = {
                "query": {
                    "range": {
                        FIELD_CHUNK_ID: {"gt": last_chunk_id}
                    }
                },
                "sort": [{FIELD_CHUNK_ID: "asc"}],
                KEY_SOURCE: [FIELD_CHUNK_TEXT, FIELD_METADATA, FIELD_CHUNK_ID]
            }
        else:
            scan_query = {
                "sort": [{FIELD_CHUNK_ID: "asc"}],
                KEY_SOURCE: [FIELD_CHUNK_TEXT, FIELD_METADATA, FIELD_CHUNK_ID]
            }

        chunk_batch_counter = 0
        current_chunk_id = last_chunk_id

        try:
            scroll = helpers.scan(
                self.client,
                index=self.osm.chunks_index,
                query=scan_query,
                scroll=SCROLL_TIMEOUT,
                size=DEFAULT_CHUNK_FETCH_SIZE
            )

            for hit in scroll:
                source = hit.get(KEY_SOURCE, {})
                meta = source.get(FIELD_METADATA, {})
                chunk_id = source.get(FIELD_CHUNK_ID) or hit.get(KEY_ID, "")
                chunk_text = source.get(FIELD_CHUNK_TEXT, "")
                book_id = meta.get(FIELD_BOOK_ID) or source.get(FIELD_BOOK_ID)
                current_chunk_id = chunk_id

                if book_id is not None:
                    self.unique_books.add(book_id)

                tokens = []
                if chunk_text:
                    raw_tokens = re.findall(WORD_TOKEN_REGEX, chunk_text)
                    for token in raw_tokens:
                        token_clean = token.lower().strip()
                        if book_id is not None and token_clean:
                            self.word_books_map[token_clean].add(book_id)
                            tokens.append(token_clean)

                self.total_chunks_processed += 1
                chunk_batch_counter += 1

                print(LOG_CHUNK_PROCESSED_FORMAT.format(
                    chunk_num=self.total_chunks_processed,
                    chunk_id=chunk_id,
                    book_id=book_id if book_id is not None else "N/A",
                    token_count=len(tokens)
                ))

                if chunk_batch_counter >= self.chunk_batch_size:
                    effective_total_books = max(len(self.unique_books), DEFAULT_TOTAL_BOOKS_FALLBACK)
                    self._flush_word_scores_to_opensearch(effective_total_books)
                    self.save_checkpoint(current_chunk_id)
                    chunk_batch_counter = 0

            if chunk_batch_counter > 0:
                effective_total_books = max(len(self.unique_books), DEFAULT_TOTAL_BOOKS_FALLBACK)
                self._flush_word_scores_to_opensearch(effective_total_books)
                self.save_checkpoint(current_chunk_id)

        except Exception as e:
            print(LOG_SCAN_ERROR_FORMAT.format(error=str(e)))

        elapsed = time.time() - start_time
        print(LOG_COMPLETED_FORMAT.format(
            elapsed=elapsed,
            chunk_count=self.total_chunks_processed,
            word_count=len(self.word_books_map),
            book_count=len(self.unique_books)
        ))

    def _flush_word_scores_to_opensearch(self, total_books: int):
        """Recalculates scores (books appeared in / total books) for all tracked words
        and bulk-upserts the records to the bookito_words OpenSearch index.
        """
        if not self.word_books_map or total_books <= 0:
            return

        actions = []
        scores_list = []
        for word, book_set in self.word_books_map.items():
            word_clean = word.lower().strip()
            book_count = len(book_set)
            score = round(book_count / total_books, SCORE_ROUND_DECIMALS)
            scores_list.append((word_clean, book_count, score))

            action = {
                KEY_OP_TYPE: OP_TYPE_INDEX,
                KEY_INDEX: self.osm.words_index,
                KEY_ID: word_clean,
                KEY_SOURCE: {
                    FIELD_WORD: word_clean,
                    FIELD_BOOK_COUNT: book_count,
                    FIELD_TOTAL_BOOKS: total_books,
                    FIELD_SCORE: score
                }
            }
            actions.append(action)

        if actions:
            try:
                success_count, _ = helpers.bulk(self.client, actions, raise_on_error=False)
                print(LOG_PROGRESS_FORMAT.format(
                    chunk_count=self.total_chunks_processed,
                    book_count=len(self.unique_books),
                    word_count=len(self.word_books_map)
                ))
                print(LOG_BULK_SUCCESS_FORMAT.format(count=success_count, index_name=self.osm.words_index))

                scores_list.sort(key=lambda x: x[1], reverse=True)
                sample_size = min(SAMPLE_SCORES_LOG_COUNT, len(scores_list))
                print(LOG_RECALC_HEADER_FORMAT.format(
                    chunk_count=self.total_chunks_processed,
                    word_count=len(self.word_books_map),
                    total_books=total_books
                ))
                print(LOG_SCORE_SAMPLE_HEADER_FORMAT.format(sample_size=sample_size))
                for w, b_cnt, sc in scores_list[:sample_size]:
                    print(LOG_SCORE_ITEM_FORMAT.format(
                        word=w,
                        book_count=b_cnt,
                        total_books=total_books,
                        score=sc
                    ))
            except Exception as e:
                print(LOG_BULK_ERROR_FORMAT.format(error=str(e)))

def main():
    parser = argparse.ArgumentParser(description="WordProcessor for OpenSearch term document frequency calculations.")
    parser.add_argument(CLI_ARG_RESET_SHORT, CLI_ARG_RESET, action="store_true", help=CLI_HELP_RESET)
    args = parser.parse_args()

    processor = WordProcessor()
    processor.process_all_chunks(reset=args.reset)

if __name__ == "__main__":
    main()
