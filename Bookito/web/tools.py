import requests
from bs4 import BeautifulSoup
from database.query_manager import QueryManager

_qm = None

def get_query_manager():
    global _qm
    if _qm is None:
        _qm = QueryManager()
    return _qm

def web_search(query: str) -> str:
    """Performs a web search using DuckDuckGo Lite."""
    if not query:
        return "Error: Query parameter is required."
    
    url = "https://lite.duckduckgo.com/lite/"
    data = {"q": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for tr in soup.find_all('tr'):
            td = tr.find('td', class_='result-snippet')
            if td:
                results.append(td.get_text(strip=True))
                
        if not results:
            return "No results found."
        
        return "\n\n".join(results[:5])
    except Exception as e:
        return f"Error executing web search: {str(e)}"

def url_get(url: str) -> str:
    """Fetches text content from a URL."""
    if not url:
        return "Error: URL parameter is required."
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        return text[:8000]
    except Exception as e:
        return f"Error executing url get: {str(e)}"

def semantic_chapter_search(query: str) -> str:
    """Performs a semantic + lexical search for chapters."""
    qm = get_query_manager()
    
    query_vectors = qm.embedder.embed_texts([query])
    if not query_vectors:
        return "Failed to generate embeddings."
    query_vector = query_vectors[0]
    
    # Hybrid search: Lexical MUST match all words AND Vector KNN
    search_body = {
        "size": 50,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "chunk_text": {
                                "query": query,
                                "operator": "and"
                            }
                        }
                    },
                    {
                        "knn": {
                            "chunk_vector": {
                                "vector": query_vector,
                                "k": 50
                            }
                        }
                    }
                ]
            }
        },
        "_source": {"excludes": ["chunk_vector"]}
    }
    
    try:
        resp = qm.client.search(index=qm.util.chunks_index, body=search_body)
        hits = resp.get("hits", {}).get("hits", [])
        
        if not hits:
            return "No matching chapters found."
        
        seen_chapters = set()
        chapter_contents = []
        
        for hit in hits:
            source = hit.get("_source", {})
            chapter_id = source.get("chapter_id")
            
            if chapter_id and chapter_id not in seen_chapters:
                seen_chapters.add(chapter_id)
                
                chap_query = {
                    "size": 1000,
                    "query": {
                        "term": {
                            "chapter_id.keyword": chapter_id
                        }
                    },
                    "sort": [
                        {"chunk_index": {"order": "asc"}}
                    ],
                    "_source": {"excludes": ["chunk_vector"]}
                }
                
                chap_resp = qm.client.search(index=qm.util.chunks_index, body=chap_query)
                chap_hits = chap_resp.get("hits", {}).get("hits", [])
                
                chunks_text = [h.get("_source", {}).get("chunk_text", "") for h in chap_hits]
                chapter_text = "\n".join(chunks_text)
                
                chapter_title = source.get("chapter_title", f"Chapter {source.get('chapter_number', 'Unknown')}")
                book_name = source.get("book_name", "Unknown Book")
                
                chapter_contents.append(f"Book: {book_name}\nChapter: {chapter_title}\nContent:\n{chapter_text}")
                
        final_output = "\n\n---\n\n".join(chapter_contents[:3]) # Top 3 distinct chapters
        return final_output[:20000]
    except Exception as e:
        return f"Error executing semantic chapter search: {str(e)}"
