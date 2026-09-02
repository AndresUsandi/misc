import sys
import os
import time

# Ensure the root of the project is on the python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parsers.pdf_parser import PdfBookParser

# KeyBERT uses BERT embeddings to find keywords
from keybert import KeyBERT

def main():
    print("=== KeyBERT Tutorial ===")
    print("KeyBERT is a minimal and easy-to-use keyword extraction technique that leverages BERT embeddings.")
    print("It finds sub-phrases in a document that are the most similar (using cosine similarity) to the document itself.\n")
    
    # 1. Get sample text from our book corpus
    parser = PdfBookParser()
    path = r'e:\Development\GitHub\MachineLarning\Bookito\tests\integrations\files\Professional ADO NET 2 Programming With SQL Server 2005, Oracle, & MySQL 2006.pdf'
    print(f"Parsing PDF to extract sample text...")
    res = parser.parse(path, "test_book")
    
    sample_text = res.getFullText()

    if not sample_text:
        print("Could not find a chapter with sufficient text.")
        return
        
    # 2. Initialize KeyBERT Model
    # By default, it uses 'all-MiniLM-L6-v2' which is fast and great for general semantic similarity.
    print("Initializing KeyBERT model (this may download weights on first run)...")
    try:
        kw_model = KeyBERT()
    except Exception as e:
        print(f"\n[Environment Error]: Failed to initialize KeyBERT model.")
        print(f"Error details: {e}")
        print("Note: KeyBERT relies on `sentence-transformers` and `transformers`. If you see errors about")
        print("'Modality audio is not supported' or 'cannot import name find_pruneable_heads_and_indices',")
        print("you likely have a version conflict between transformers and sentence-transformers in your environment.")
        print("Try running: pip install -U sentence-transformers transformers")
        return
    
    # 3. Extract Keywords
    # keyphrase_ngram_range: Set the length of the extracted keywords/keyphrases
    # stop_words: Language to use for stop word removal
    # top_n: Number of keywords to return
    start = time.perf_counter()
    print("Extracting keywords (Top 10 individual words)...")
    keywords = kw_model.extract_keywords(sample_text, keyphrase_ngram_range=(1, 1), stop_words='english', top_n=25)
    print(keywords)
    
    # 4. Extract Keyphrases (Bigrams/Trigrams)
    print(f"\nExtracting keyphrases (2-3 words)...")
    keyphrases = kw_model.extract_keywords(sample_text, keyphrase_ngram_range=(1, 5), stop_words='english', top_n=100)
    
    print(f"\n{'Keyphrase':<40} | {'Cosine Similarity (Higher is better)':<10}")
    print("-" * 80)
    for kw, score in keyphrases:
        print(f"{kw:<40} | {score:.4f}")
        
    # 5. Max Sum Similarity (Optional advanced feature)
    # To diversify the results, you can use Max Sum Similarity to ensure keywords are similar to the document,
    # but not too similar to each other.
    print("\nExtracting diversified keyphrases using Max Sum Similarity (nr_candidates=20)...")
    diversified = kw_model.extract_keywords(sample_text, keyphrase_ngram_range=(1, 5), stop_words='english', 
                                            use_maxsum=True, nr_candidates=20, top_n=100)
    for kw, score in diversified:
        print(f"{kw:<40} | {score:.4f}")

    end = time.perf_counter()
    print(f"Elapsed: {(end - start) * 1000:.3f} ms")

if __name__ == "__main__":
    main()
