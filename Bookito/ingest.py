import sys
import os

# Add current script directory to sys.path to resolve subpackages correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from processors.file_processor import FileProcessor

def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <directory_path_or_file_path> [rejection_folder]")
        sys.exit(1)
        
    target_path = sys.argv[1]
    rejection_folder = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("=========================================================")
    print("Bookito Ingestion Engine")
    print("=========================================================")
    print(f"Target Path: {target_path}")
    print("=========================================================")

    try:
        processor = FileProcessor(rejection_folder=rejection_folder)
        processor.process(target_path)
        print("=========================================================")
        print("Ingestion Run Completed.")
        print("=========================================================")
    except Exception as e:
        print(f"[FATAL ERROR] Ingestion failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
