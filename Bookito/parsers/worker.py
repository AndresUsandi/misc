import os
from .registry import BookParserRegistry
from .pdf_parser import PdfBookParser
from .epub_parser import EpubBookParser
from .chm_parser import ChmBookParser
from book import Book

class BookParserWorker:
    def __init__(self, unwrap: bool = True):
        self.unwrap = unwrap
        self.registry = BookParserRegistry()
        self.registry.register_parser('.pdf', PdfBookParser, unwrap)
        self.registry.register_parser('.epub', EpubBookParser, unwrap)
        self.registry.register_parser('.chm', ChmBookParser, unwrap)
        
    def parse_book(self, file_path: str, max_items: int = None, unwrap: bool = None) -> Book:
        ext = os.path.splitext(file_path)[1].lower()
        parser = self.registry.get_parser(ext)
        if not parser:
            raise ValueError(f"No parser registered for file extension: {ext}")
            
        parser.unwrap = self.unwrap if unwrap is None else unwrap
        book_name = os.path.basename(file_path)
        return parser.parse(file_path, book_name, max_items=max_items)
