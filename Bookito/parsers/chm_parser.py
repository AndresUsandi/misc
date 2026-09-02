import os
import re
import tempfile
import subprocess
import shutil
from bs4 import BeautifulSoup
from .base_parser import BaseBookParser
from book import Book, Chapter, Chunk

class ChmBookParser(BaseBookParser):
    def __init__(self, unwrap: bool = False):
        super().__init__(unwrap=unwrap)

    def parse(self, file_path: str, book_name: str, max_items: int = None) -> Book:
        book = Book()
        book.Title = book_name
        
        temp_dir = tempfile.mkdtemp(prefix="chm_extract_")
        try:
            temp_chm_path = os.path.join(temp_dir, "book.chm")
            shutil.copy(file_path, temp_chm_path)
            
            subprocess.run(['hh.exe', '-decompile', temp_dir, temp_chm_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            hhc_file = None
            for root, dirs, files in os.walk(temp_dir):
                for f in files:
                    if f.lower().endswith('.hhc'):
                        hhc_file = os.path.join(root, f)
                        break
                if hhc_file:
                    break
            
            sitemap_items = []
            if hhc_file:
                try:
                    with open(hhc_file, 'r', encoding='utf-8', errors='ignore') as f:
                        hhc_content = f.read()
                    
                    pattern = re.compile(r'(<ul[^>]*>|</ul>|<object\s+[^>]*>.*?</object>)', re.IGNORECASE | re.DOTALL)
                    matches = pattern.findall(hhc_content)
                    
                    depth = 0
                    for m in matches:
                        m_lower = m.lower()
                        if m_lower.startswith('<ul'):
                            depth += 1
                        elif m_lower.startswith('</ul'):
                            depth -= 1
                        elif m_lower.startswith('<object'):
                            soup = BeautifulSoup(m, 'html.parser')
                            name_param = soup.find('param', attrs={"name": "Name"})
                            local_param = soup.find('param', attrs={"name": "Local"})
                            title = name_param.get('value', '').strip() if name_param else ""
                            local_file = local_param.get('value', '').strip().replace('\\', '/') if local_param else ""
                            local_file_norm = local_file.split('#')[0] if local_file else ""
                            
                            if title or local_file_norm:
                                sitemap_items.append({
                                    "title": title,
                                    "local": local_file_norm,
                                    "depth": depth
                                })
                except Exception as e:
                    print(f"Error parsing .hhc file: {e}")
                    
            if not sitemap_items:
                html_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for f in files:
                        if f.lower().endswith(('.html', '.htm')):
                            full_path = os.path.join(root, f)
                            rel_path = full_path[len(temp_dir):].lstrip('/\\').replace('\\', '/')
                            html_files.append((full_path, rel_path))
                html_files.sort(key=lambda x: x[1])
                for full_path, rel_path in html_files:
                    if not any(x in rel_path.lower() for x in ["sitemap", "index"]):
                        sitemap_items.append({
                            "title": "",
                            "local": rel_path,
                            "depth": 1
                        })
                        
            if max_items is not None:
                sitemap_items = sitemap_items[:max_items]
                
            current_chapter = None
            chapter_count = 0
            
            processed_files = set()
            
            for item in sitemap_items:
                title = item["title"]
                local = item["local"]
                depth = item["depth"]
                
                file_text = ""
                soup_html = None
                if local:
                    full_path = os.path.join(temp_dir, local)
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f_html:
                            html_content = f_html.read()
                        soup_html = BeautifulSoup(html_content, 'html.parser')
                        file_text = soup_html.get_text()
                    except Exception:
                        pass
                            
                if local in processed_files and not file_text:
                    continue
                if local:
                    processed_files.add(local)
                    
                if not title:
                    title = f"Section {local}" if local else f"Chapter {chapter_count + 1}"
                    
                if depth == 1 or not current_chapter:
                    chapter_count += 1
                    current_chapter = Chapter()
                    current_chapter.Title = title
                    current_chapter.Number = chapter_count
                    book.Chapters.append(current_chapter)
                    
                if soup_html:
                    body = soup_html.find('body')
                    target = body if body else soup_html
                    p_tags = target.find_all('p')
                    if p_tags:
                        for p in p_tags:
                            chunks = self.create_chunks_from_raw_text(p.get_text())
                            current_chapter.Chunks.extend(chunks)
                    if not current_chapter.Chunks:
                        raw_text = target.get_text()
                        chunks = self.create_chunks_from_raw_text(raw_text)
                        current_chapter.Chunks.extend(chunks)
                elif file_text:
                    raw_paras = file_text.split("\n\n")
                    for rp in raw_paras:
                        chunks = self.create_chunks_from_raw_text(rp)
                        current_chapter.Chunks.extend(chunks)
                    
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        return book
