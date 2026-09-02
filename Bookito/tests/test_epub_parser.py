import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.epub_parser import EpubBookParser

class TestEpubBookParser(unittest.TestCase):
    def setUp(self):
        self.parser = EpubBookParser()

    @patch('parsers.epub_parser.epub')
    def test_parse_epub(self, mock_epub):
        mock_book = MagicMock()
        mock_epub.read_epub.return_value = mock_book
        
        mock_item_1 = MagicMock()
        mock_item_1.file_name = "chapter1.html"
        mock_item_1.get_type.return_value = 9 # ITEM_DOCUMENT
        mock_item_1.get_content.return_value = b"""
        <html>
            <body>
                <h1>Chapter 1: The Beginning</h1>
                <p>This is first paragraph text that is long enough to pass the filters.</p>
                <p>This is second chunk text that is long enough to pass the filters.</p>
            </body>
        </html>
        """
        
        mock_book.get_items.return_value = [mock_item_1]
        mock_book.toc = []
        
        book = self.parser.parse("fake.epub", "Test Book.epub")
        
        self.assertEqual(len(book.Chapters), 1)
        self.assertEqual(book.Chapters[0].Title, "Chapter 1: The Beginning")
        self.assertTrue(len(book.Chapters[0].Chunks) >= 1)
        self.assertEqual(book.Chapters[0].Chunks[0].Text, "This is first paragraph text that is long enough to pass the filters.")

if __name__ == '__main__':
    unittest.main()
