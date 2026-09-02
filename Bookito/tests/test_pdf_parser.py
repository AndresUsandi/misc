import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.pdf_parser import PdfBookParser

class TestPdfBookParser(unittest.TestCase):
    def setUp(self):
        self.parser = PdfBookParser()

    @patch('parsers.pdf_parser.fitz')
    def test_parse_with_toc(self, mock_fitz):
        mock_doc = MagicMock()
        mock_fitz.open.return_value = mock_doc
        
        mock_doc.get_toc.return_value = [
            [1, "Chapter 1", 1],
            [1, "Chapter 2", 2]
        ]
        
        mock_page_1 = MagicMock()
        mock_page_1.get_text.return_value = "This is Chapter 1 text that is long enough to pass the filter.\n\nParagraph 2 text here is also long enough."
        mock_page_2 = MagicMock()
        mock_page_2.get_text.return_value = "This is Chapter 2 text that is long enough to pass the filter.\n\nParagraph 4 text here is also long enough."
        
        mock_doc.__len__.return_value = 2
        mock_doc.__getitem__.side_effect = [mock_page_1, mock_page_2]
        
        book = self.parser.parse("fake_path.pdf", "Test Book.pdf")
        
        self.assertEqual(len(book.Chapters), 2)
        self.assertEqual(book.Chapters[0].Title, "Chapter 1")
        self.assertTrue(len(book.Chapters[0].Chunks) >= 2)
        self.assertIn("This is Chapter 1 text", book.Chapters[0].Chunks[0].Text)

    def test_unwrap_sentence_splitting(self):
        parser = PdfBookParser(unwrap=True)
        raw_text = "This is sentence one in the paragraph.\nThis is sentence two in the same paragraph! Is this sentence three?"
        chunks = parser.create_chunks_from_raw_text(raw_text)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0].Text, "This is sentence one in the paragraph.")
        self.assertEqual(chunks[1].Text, "This is sentence two in the same paragraph!")
        self.assertEqual(chunks[2].Text, "Is this sentence three?")

if __name__ == '__main__':
    unittest.main()
