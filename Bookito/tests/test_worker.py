import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.worker import BookParserWorker

class TestBookParserWorker(unittest.TestCase):
    def setUp(self):
        self.worker = BookParserWorker()

    @patch('parsers.worker.PdfBookParser')
    def test_parse_book_pdf(self, mock_pdf_parser_class):
        mock_pdf_parser = MagicMock()
        mock_pdf_parser_class.return_value = mock_pdf_parser
        
        # Instantiate worker after patching class
        worker = BookParserWorker()
        
        worker.parse_book("book.pdf")
        mock_pdf_parser.parse.assert_called_once_with("book.pdf", "book.pdf", max_items=None)

    def test_parse_book_unsupported_raises(self):
        with self.assertRaises(ValueError):
            self.worker.parse_book("book.xyz")

if __name__ == '__main__':
    unittest.main()
