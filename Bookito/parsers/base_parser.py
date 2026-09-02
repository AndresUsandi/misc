import re
from abc import ABC, abstractmethod
from book import Book, Chunk

class BaseBookParser(ABC):
    def __init__(self, unwrap: bool = False):
        self.unwrap = unwrap

    @abstractmethod
    def parse(self, file_path: str, book_name: str, max_items: int = None) -> Book:
        """
        Parses a book file and returns a Book instance.
        """
        pass

    def create_chunks_from_raw_text(self, raw_text: str) -> list[Chunk]:
        chunks = []
        if not raw_text or not raw_text.strip():
            return chunks

        if self.unwrap:
            # 1. Unwrap text: replace newlines with space and collapse whitespace
            unwrapped = raw_text.replace('\r', '').replace('\n', ' ')
            unwrapped = re.sub(r'\s+', ' ', unwrapped).strip()
            
            # 2. Split unwrapped text by sentences
            raw_sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"\'(])', unwrapped)
            for s in raw_sentences:
                clean_s = s.strip()
                if len(clean_s) >= 5:
                    c = Chunk()
                    c.Text = clean_s
                    chunks.append(c)
            # Fallback if sentence regex split didn't yield items but text is long enough
            if not chunks and len(unwrapped) >= 5:
                c = Chunk()
                c.Text = unwrapped
                chunks.append(c)
        else:
            # Keep original newlines and formatting intact, split paragraphs by \n\n
            paras = [p.strip() for p in raw_text.replace('\r', '').split('\n\n') if p.strip()]
            for p in paras:
                lines = [line.strip() for line in p.split('\n')]
                clean_p = "\n".join(lines).strip()
                if len(clean_p) >= 5:
                    c = Chunk()
                    c.Text = clean_p
                    chunks.append(c)

        return chunks
