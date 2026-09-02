import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database.opensearch_manager import BookitoOpenSearchUtil

def print_doc(doc):
    print(json.dumps(doc, indent=2))

def main():
    util = BookitoOpenSearchUtil()
    client = util.connect()
    
    print("### Bookito Books")
    res = client.search(index=util.books_index, body={"size": 1})
    if res["hits"]["hits"]:
        print("```json")
        print_doc(res["hits"]["hits"][0]["_source"])
        print("```")
        
    print("\n### Bookito Chapters")
    res = client.search(index=util.chapters_index, body={"size": 1})
    if res["hits"]["hits"]:
        print("```json")
        print_doc(res["hits"]["hits"][0]["_source"])
        print("```")
        
    print("\n### Bookito Chunks")
    res = client.search(index=util.chunks_index, body={"size": 1, "_source": {"excludes": ["chunk_vector"]}})
    if res["hits"]["hits"]:
        print("```json")
        print_doc(res["hits"]["hits"][0]["_source"])
        print("```")

    print("\n### Bookito Concepts")
    res = client.search(index=util.concepts_index, body={"size": 1})
    if res["hits"]["hits"]:
        print("```json")
        print_doc(res["hits"]["hits"][0]["_source"])
        print("```")

if __name__ == "__main__":
    main()
