import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processors.file_processor import FileProcessor

# Top-of-file Constants for Tests
TEST_INDEX_PREFIX = "test_file_proc_"
TEST_BOOK_NAME = "book1.pdf"
TEST_FOLDER_PATH = "/path/to/books"
TEST_FILE_PATH = os.path.join(TEST_FOLDER_PATH, TEST_BOOK_NAME)
TEST_CONCEPT_PHRASE = "sql server"
TEST_CONCEPT_SCORE = 100.0
TEST_CHAPTERS_COUNT = 5
TEST_TOTAL_OCCURRENCES = 20

class TestFileProcessor(unittest.TestCase):
    def test_process_directory(self):
        mock_db_class = MagicMock()
        mock_db = MagicMock()
        mock_db.get_max_id.return_value = 0
        mock_db_class.return_value = mock_db

        with patch('processors.file_processor.os.path.isfile') as mock_isfile, \
             patch('processors.file_processor.os.path.isdir') as mock_isdir, \
             patch('processors.file_processor.os.walk') as mock_walk:

            mock_worker = MagicMock()
            mock_embedder = MagicMock()
            mock_concept = MagicMock()
            mock_concept.processBook.return_value = [(TEST_CONCEPT_PHRASE, TEST_CONCEPT_SCORE, TEST_CHAPTERS_COUNT, TEST_TOTAL_OCCURRENCES)]
            
            mock_isfile.return_value = False
            mock_isdir.return_value = True
            
            mock_walk.return_value = [
                (TEST_FOLDER_PATH, [], [TEST_BOOK_NAME, 'other.txt'])
            ]
            
            mock_book_data = MagicMock()
            mock_book_data.Chapters = []
            mock_worker.parse_book.return_value = mock_book_data
            
            processor = FileProcessor(
                index_prefix=TEST_INDEX_PREFIX,
                opensearch_util_class=mock_db_class,
                embedder=mock_embedder,
                parser=mock_worker,
                concept_processor=mock_concept
            )
            processor.process(TEST_FOLDER_PATH)
            
            mock_db.connect.assert_called_once()
            mock_db.create_indices.assert_called_once()
            mock_worker.parse_book.assert_called_once_with(TEST_FILE_PATH, max_items=None)
            mock_concept.processBook.assert_called_once_with(mock_book_data)
            mock_db.index_book_data.assert_called_once_with(
                book=mock_book_data,
                book_name=TEST_BOOK_NAME,
                book_id=1,
                file_path=TEST_FILE_PATH,
                embedder=mock_embedder,
                concepts=[(TEST_CONCEPT_PHRASE, TEST_CONCEPT_SCORE, TEST_CHAPTERS_COUNT, TEST_TOTAL_OCCURRENCES)]
            )

if __name__ == '__main__':
    unittest.main()

