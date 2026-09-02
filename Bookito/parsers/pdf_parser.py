import re
from collections import Counter
import fitz  # PyMuPDF
from .base_parser import BaseBookParser
from book import Book, Chapter, Chunk

class PdfBookParser(BaseBookParser):
    def __init__(self, unwrap: bool = False):
        super().__init__(unwrap=unwrap)

    def parse(self, file_path: str, book_name: str, max_items: int = None) -> Book:
        doc = fitz.open(file_path)
        toc = doc.get_toc()  # [[level, title, page], ...]
        
        book = Book()
        book.Title = book_name
        
        total_pages = len(doc)
        if max_items is not None:
            total_pages = min(total_pages, max_items)
        
        if toc:
            headings = []
            for item in toc:
                level, title, page = item
                if page > 0 and page <= len(doc):
                    headings.append({"level": level, "title": title, "page": page})
            
            headings.sort(key=lambda x: x["page"])
            
            chapter_count = 0
            chapter_id_map = {}  # heading_idx -> Chapter object
            
            min_level = min(h["level"] for h in headings) if headings else 1
            for idx, h in enumerate(headings):
                if h["level"] == min_level:
                    chapter_count += 1
                    current_chapter = Chapter()
                    current_chapter.Title = h["title"]
                    current_chapter.Number = chapter_count
                    book.Chapters.append(current_chapter)
                    chapter_id_map[idx] = current_chapter
            
            if not book.Chapters:
                current_chapter = Chapter()
                current_chapter.Title = "Chapter 1"
                current_chapter.Number = 1
                book.Chapters.append(current_chapter)
            
            for page_idx in range(total_pages):
                page_num = page_idx + 1
                active_ch = book.Chapters[0]
                
                last_ch_heading_idx = None
                for idx, h in enumerate(headings):
                    if h["page"] <= page_num:
                        if h["level"] == min_level:
                            last_ch_heading_idx = idx
                    else:
                        break
                
                if last_ch_heading_idx is not None:
                    active_ch = chapter_id_map.get(last_ch_heading_idx) or book.Chapters[0]
                
                page = doc[page_idx]
                res = page.get_text("blocks")
                if isinstance(res, list):
                    for b in res:
                        block_text = b[4] if (isinstance(b, (list, tuple)) and len(b) >= 5) else (str(b) if not isinstance(b, (list, tuple)) else "")
                        chunks = self.create_chunks_from_raw_text(block_text)
                        active_ch.Chunks.extend(chunks)
                else:
                    page_text = str(res) if res else ""
                    chunks = self.create_chunks_from_raw_text(page_text)
                    active_ch.Chunks.extend(chunks)
        else:
            # Fallback for PDFs without outline: scan physical table of contents pages using regex
            toc_pages = []
            toc_line_regex = re.compile(
                r'^(.*?)'
                r'(?:[\s\.\-\_\~·•]{3,}|(?<=\s)\s{2,})'
                r'[\-\s]*?(\d+|[ivxldcmIVXLDCM]+)[\-\s]*?$',
                re.IGNORECASE
            )
            
            scan_limit = min(50, len(doc))
            page_text_cache = {}
            for p_idx in range(scan_limit):
                try:
                    page = doc[p_idx]
                    text = page.get_text()
                    page_text_cache[p_idx] = text
                    matching_lines = 0
                    lines = text.split('\n')
                    for line in lines:
                        if toc_line_regex.match(line.strip()):
                            matching_lines += 1
                    
                    is_toc = matching_lines >= 3 or bool(re.search(r'\b(table\s+of\s+contents|contents\s+at\s+a\s+glance|contents)\b', text, re.IGNORECASE))
                    if is_toc:
                        toc_pages.append(p_idx)
                except Exception:
                    pass
            
            chapter_prefix_regex = re.compile(
                r'^(?:Chapter|Book|Part|Hour|Section|Book\s+\d+|Part\s+[IVXLCDM]+|Chapter\s+\d+|Hour\s+\d+)\b',
                re.IGNORECASE
            )
            single_digit_prefix_regex = re.compile(r'^\d+[\.\s]+')
            nested_digit_prefix_regex = re.compile(r'^\d+\.\d+')
            
            raw_entries = []
            seen_entries = set()
            has_prefixes = False
            
            for p_idx in toc_pages:
                try:
                    text = page_text_cache.get(p_idx) or doc[p_idx].get_text()
                    lines = text.split('\n')
                    
                    accumulated_title = ""
                    for line in lines:
                        line_clean = line.strip()
                        if not line_clean:
                            continue
                            
                        if line_clean.lower().startswith(('table of contents', 'contents at a glance', 'dummies')) and not toc_line_regex.match(line_clean):
                            continue
                            
                        match = toc_line_regex.match(line_clean)
                        
                        is_standalone_page = False
                        standalone_page_str = ""
                        if not match and accumulated_title:
                            roman_regex = r'^(?=[MDCLXVI])M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})$'
                            page_str_clean = line_clean.strip(' -.')
                            if page_str_clean.isdigit():
                                is_standalone_page = True
                                standalone_page_str = page_str_clean
                            elif re.match(roman_regex, page_str_clean, re.IGNORECASE):
                                is_standalone_page = True
                                standalone_page_str = page_str_clean

                        if match or is_standalone_page:
                            if match:
                                matched_title = match.group(1).strip()
                                page_str = match.group(2).strip()
                                if accumulated_title:
                                    full_title = accumulated_title + " " + matched_title
                                else:
                                    full_title = matched_title
                            else:
                                full_title = accumulated_title
                                page_str = standalone_page_str

                            accumulated_title = ""
                            full_title = re.sub(r'[\s\.\-]+$', '', full_title).strip()
                            
                            if not re.search(r'[a-zA-Z]', full_title):
                                continue
                            if len(full_title) < 4:
                                continue
                                
                            entry_key = (full_title.lower(), page_str.lower())
                            if entry_key in seen_entries:
                                continue
                            seen_entries.add(entry_key)
                            
                            is_arabic = page_str.isdigit()
                            printed_page = int(page_str) if is_arabic else 0
                            
                            is_chapter_prefix = bool(chapter_prefix_regex.match(full_title) or (single_digit_prefix_regex.match(full_title) and not nested_digit_prefix_regex.match(full_title)))
                            if is_chapter_prefix:
                                has_prefixes = True
                                
                            raw_entries.append({
                                "title": full_title,
                                "printed_page": printed_page,
                                "is_arabic": is_arabic,
                                "is_chapter_prefix": is_chapter_prefix
                            })
                        else:
                            if re.search(r'[a-zA-Z]', line_clean) and len(line_clean) > 3:
                                if accumulated_title:
                                    accumulated_title += " " + line_clean
                                else:
                                    accumulated_title = line_clean
                            else:
                                accumulated_title = ""
                except Exception:
                    pass
            
            page_offset = 0
            if raw_entries:
                offsets = []
                for entry in raw_entries:
                    if not entry["is_arabic"] or entry["printed_page"] <= 0:
                        continue
                    printed_page = entry["printed_page"]
                    title = entry["title"]
                    for offset in range(0, 50):
                        target_abs_idx = printed_page + offset
                        if target_abs_idx < len(doc):
                            try:
                                page_text = page_text_cache.get(target_abs_idx)
                                if page_text is None:
                                    page_text = doc[target_abs_idx].get_text()
                                    page_text_cache[target_abs_idx] = page_text
                                page_text = page_text.lower()
                                title_clean = re.sub(r'[^a-z0-9\s]', '', title.lower()).strip()
                                title_words = title_clean.split()
                                if len(title_words) >= 3:
                                    search_term = " ".join(title_words[:3])
                                    if search_term in page_text:
                                        offsets.append(offset)
                                        break
                            except Exception:
                                pass
                if offsets:
                    page_offset = Counter(offsets).most_common(1)[0][0]
                    
            final_entries = []
            for entry in raw_entries:
                if not entry["is_arabic"]:
                    continue
                abs_page = entry["printed_page"] + page_offset
                if abs_page < 0 or abs_page >= len(doc):
                    continue
                    
                is_chapter = entry["is_chapter_prefix"] if has_prefixes else True
                final_entries.append({
                    "title": entry["title"],
                    "abs_page": abs_page,
                    "is_chapter": is_chapter
                })
                
            final_entries.sort(key=lambda x: x["abs_page"])
            
            current_chapter = None
            chapter_count = 0
            
            if max_items is not None:
                final_entries = final_entries[:max_items]
                
            for idx, entry in enumerate(final_entries):
                title = entry["title"]
                abs_page = entry["abs_page"]
                is_chapter = entry["is_chapter"]
                
                next_page = len(doc)
                if idx < len(final_entries) - 1:
                    next_page = final_entries[idx + 1]["abs_page"]
                next_page = max(abs_page, next_page)
                
                text_content = ""
                for p in range(abs_page, next_page):
                    try:
                        p_text = page_text_cache.get(p)
                        if p_text is None:
                            p_text = doc[p].get_text()
                            page_text_cache[p] = p_text
                        text_content += p_text + "\n"
                    except Exception:
                        pass
                        
                if is_chapter or not current_chapter:
                    chapter_count += 1
                    current_chapter = Chapter()
                    current_chapter.Title = title if is_chapter else "Introduction"
                    current_chapter.Number = chapter_count
                    book.Chapters.append(current_chapter)
                    
                if text_content.strip():
                    raw_paras = text_content.split("\n\n")
                    for rp in raw_paras:
                        chunks = self.create_chunks_from_raw_text(rp)
                        current_chapter.Chunks.extend(chunks)
            
            if not book.Chapters:
                doc.close()
                raise ValueError("No TOC or valid chapter headings found in PDF. Parsing rejected.")

        doc.close()
        return book
