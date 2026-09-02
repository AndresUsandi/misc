import os
import re
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
from .base_parser import BaseBookParser
from book import Book, Chapter, Chunk

class EpubBookParser(BaseBookParser):
    def __init__(self, unwrap: bool = False):
        super().__init__(unwrap=unwrap)

    def parse(self, file_path: str, book_name: str, max_items: int = None) -> Book:
        ebook = epub.read_epub(file_path)
        
        book = Book()
        book.Title = book_name
        
        def parse_epub_toc(toc_list, depth=1):
            items = []
            for item in toc_list:
                if isinstance(item, epub.Link):
                    items.append({
                        "title": item.title,
                        "local": item.href.split('#')[0],
                        "depth": depth
                    })
                elif isinstance(item, tuple) and len(item) == 2:
                    section_link = item[0]
                    sub_links = item[1]
                    items.append({
                        "title": section_link.title,
                        "local": section_link.href.split('#')[0],
                        "depth": depth
                    })
                    items.extend(parse_epub_toc(sub_links, depth + 1))
            return items
            
        all_items = list(ebook.get_items())
        toc_items = parse_epub_toc(ebook.toc)
        existing_locals = {item["local"] for item in toc_items if item.get("local")}
        
        for item in all_items:
            if item.get_type() == ebooklib.ITEM_DOCUMENT or (hasattr(item, 'file_name') and item.file_name.lower().endswith(('.html', '.xhtml', '.htm'))):
                fname = item.file_name
                if not any(x in fname.lower() for x in ["nav", "sitemap"]) and fname not in existing_locals and not any(fname.endswith("/" + loc) or loc.endswith("/" + fname) for loc in existing_locals):
                    toc_items.append({
                        "title": os.path.basename(fname),
                        "local": fname,
                        "depth": 1
                    })
                    existing_locals.add(fname)
                
        if max_items is not None:
            toc_items = toc_items[:max_items]
            
        current_chapter = None
        chapter_count = 0
        
        processed_files = set()
        file_texts = {}
        soups = {}
        
        for item in toc_items:
            title = item["title"]
            local = item["local"]
            depth = item["depth"]
            
            doc_item = None
            if local:
                for b_item in all_items:
                    if b_item.file_name == local or b_item.file_name.endswith("/" + local) or local.endswith("/" + b_item.file_name):
                        doc_item = b_item
                        break
                        
            file_text = ""
            soup = None
            if doc_item:
                if local in soups:
                    soup = soups[local]
                    file_text = file_texts[local]
                else:
                    try:
                        html_content = doc_item.get_content()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        file_text = soup.get_text()
                        soups[local] = soup
                        file_texts[local] = file_text
                    except Exception:
                        pass
            
            if (not title or title == local) and soup:
                try:
                    h1 = soup.find('h1')
                    if h1:
                        title = h1.get_text().strip()
                except Exception:
                    pass
            if not title:
                title = f"Section {local}" if local else f"Chapter {chapter_count + 1}"
                
            if depth == 1 or not current_chapter:
                chapter_count += 1
                current_chapter = Chapter()
                current_chapter.Title = title
                current_chapter.Number = chapter_count
                book.Chapters.append(current_chapter)
                
            if soup:
                body = soup.find('body')
                target = body if body else soup
                
                p_tags = target.find_all('p')
                if p_tags:
                    for p in p_tags:
                        chunks = self.create_chunks_from_raw_text(p.get_text())
                        current_chapter.Chunks.extend(chunks)
                        
                if not current_chapter.Chunks:
                    raw_text = target.get_text()
                    chunks = self.create_chunks_from_raw_text(raw_text)
                    current_chapter.Chunks.extend(chunks)
                if not current_chapter.Chunks and file_text:
                    if local not in processed_files:
                        if local:
                            processed_files.add(local)
                        raw_paras = file_text.split("\n\n")
                        for rp in raw_paras:
                            chunks = self.create_chunks_from_raw_text(rp)
                            current_chapter.Chunks.extend(chunks)
            elif file_text:
                if local not in processed_files:
                    if local:
                        processed_files.add(local)
                    raw_paras = file_text.split("\n\n")
                    for rp in raw_paras:
                        chunks = self.create_chunks_from_raw_text(rp)
                        current_chapter.Chunks.extend(chunks)
                            
        return book
