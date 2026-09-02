import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.opensearch_manager import BookitoOpenSearchUtil

# Top-of-file Constants for Tests
TEST_HOST = "localhost"
TEST_PORT = 9200
TEST_PREFIX = "test_"
TEST_BOOK_NAME = "Test Book.pdf"
TEST_BOOK_PATH = "path/to/Test Book.pdf"
TEST_CHAPTER_TITLE = "Ch 1"
TEST_CHAPTER_TEXT = "Text"
TEST_CHUNK_TEXT = "Chunk text"
TEST_CONCEPT_PHRASE = "sql server"
TEST_CONCEPT_SCORE = 100.0
TEST_CHAPTERS_COUNT = 5
TEST_TOTAL_OCCURRENCES = 20

class TestBookitoOpenSearchUtil(unittest.TestCase):
    def setUp(self):
        self.db_util = BookitoOpenSearchUtil(host=TEST_HOST, port=TEST_PORT, index_prefix=TEST_PREFIX)
        self.mock_client = MagicMock()
        self.db_util.client = self.mock_client

    def test_connect(self):
        with patch('database.opensearch_util_connect.OpenSearch') as mock_opensearch:
            mock_client = MagicMock()
            mock_opensearch.return_value = mock_client
            
            db = BookitoOpenSearchUtil(host=TEST_HOST, port=TEST_PORT, index_prefix=TEST_PREFIX)
            client = db.connect()
            
            self.assertEqual(client, mock_client)
            mock_client.info.assert_called_once()

    def test_create_indices(self):
        self.mock_client.indices.exists.return_value = False
        
        self.db_util.create_indices()
        
        self.assertEqual(self.mock_client.indices.create.call_count, 4)
        self.mock_client.indices.create.assert_any_call(index="test_bookito_chapters", body=unittest.mock.ANY)
        self.mock_client.indices.create.assert_any_call(index="test_bookito_chunks", body=unittest.mock.ANY)
        self.mock_client.indices.create.assert_any_call(index="test_bookito_concepts", body=unittest.mock.ANY)

    @patch('database.opensearch_util_index_book_data.helpers')
    def test_index_book_data(self, mock_helpers):
        mock_ch = MagicMock()
        mock_ch.Id = 1
        mock_ch.Title = TEST_CHAPTER_TITLE
        mock_ch.Number = 1
        mock_ch.getFullText.return_value = TEST_CHAPTER_TEXT

        mock_chunk = MagicMock()
        mock_chunk.Id = 1
        mock_chunk.Text = TEST_CHUNK_TEXT
        mock_chunk.Index = 1

        mock_ch.Chunks = [mock_chunk]
        
        mock_book = MagicMock()
        mock_book.Chapters = [mock_ch]
        
        mock_embedder = MagicMock()
        mock_embedder.embed_texts.return_value = [[0.1] * 384]
        
        concepts = [(TEST_CONCEPT_PHRASE, TEST_CONCEPT_SCORE, TEST_CHAPTERS_COUNT, TEST_TOTAL_OCCURRENCES)]
        self.db_util.index_book_data(mock_book, TEST_BOOK_NAME, 1, TEST_BOOK_PATH, mock_embedder, concepts=concepts)
        
        self.assertEqual(mock_helpers.bulk.call_count, 3)

if __name__ == '__main__':
    unittest.main()
