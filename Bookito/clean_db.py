import sys
import os

# Add current script directory to sys.path to resolve subpackages correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.opensearch_manager import BookitoOpenSearchUtil

def main():
    print("=========================================================")
    print("Bookito Database Cleanup")
    print("=========================================================")
    
    try:
        util = BookitoOpenSearchUtil()
        client = util.connect()
        
        indices_to_delete = [
            util.books_index,
            util.chapters_index,
            util.chunks_index,
            util.concepts_index
        ]
        
        for idx in indices_to_delete:
            if client.indices.exists(index=idx):
                client.indices.delete(index=idx)
                print(f"Deleted index: {idx}")
            else:
                print(f"Index {idx} does not exist.")
                
        print("=========================================================")
        print("Database successfully restored to initial state.")
        print("=========================================================")
    except Exception as e:
        print(f"[FATAL ERROR] Cleanup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
