import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.chm_parser import ChmBookParser

class TestChmBookParser(unittest.TestCase):
    def setUp(self):
        self.parser = ChmBookParser(unwrap=False)

    @patch('parsers.chm_parser.tempfile')
    @patch('parsers.chm_parser.shutil')
    @patch('parsers.chm_parser.subprocess')
    @patch('parsers.chm_parser.os.walk')
    @patch('parsers.chm_parser.open', create=True)
    def test_parse_chm(self, mock_open_func, mock_walk, mock_subproc, mock_shutil, mock_tempfile):
        mock_tempfile.mkdtemp.return_value = '/tmp/chm'
        mock_walk.return_value = [
            ('/tmp/chm', [], ['test.hhc', 'ch1.html'])
        ]
        
        hhc_content = """
        <UL>
            <LI><OBJECT type="text/sitemap">
                <param name="Name" value="Chapter 1: Intro">
                <param name="Local" value="ch1.html">
            </OBJECT>
        </UL>
        """
        html_content = """
        <html>
            <head><title>ch1</title></head>
            <body>
                <p>Paragraph content is here. This is a very long paragraph that has more than one hundred characters to pass the initial CHM document validation check and make sure it is parsed correctly.</p>
            </body>
        </html>
        """
        
        mock_open_func.side_effect = [
            mock_open(read_data=hhc_content).return_value,
            mock_open(read_data=html_content).return_value
        ]
        
        book = self.parser.parse("fake.chm", "Test Book.chm")
        
        self.assertEqual(len(book.Chapters), 1)
        self.assertEqual(book.Chapters[0].Title, "Chapter 1: Intro")
        self.assertEqual(len(book.Chapters[0].Chunks), 1)
        self.assertEqual(book.Chapters[0].Chunks[0].Text, "Paragraph content is here. This is a very long paragraph that has more than one hundred characters to pass the initial CHM document validation check and make sure it is parsed correctly.")
        
        mock_subproc.run.assert_called_once()
        mock_shutil.rmtree.assert_called_once()

if __name__ == '__main__':
    unittest.main()
