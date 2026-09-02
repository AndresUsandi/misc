import sys
import os
import time

# Ensure the root of the project is on the python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parsers.pdf_parser import PdfBookParser
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def main():
    print("=== TF-IDF N-Gram Extractor ===")
    parser = PdfBookParser()
    path = r'e:\Development\GitHub\MachineLarning\Bookito\tests\integrations\files\Professional ADO NET 2 Programming With SQL Server 2005, Oracle, & MySQL 2006.pdf'
    res = parser.parse(path, "test_book")
    
    # Treat each chapter as a document in our corpus
    documents = [ch.getFullText() for ch in res.Chapters if len(ch.getFullText()) > 100]
    
    print(f"Extracting 1 to 5-word phrases across {len(documents)} chapters...")
    start = time.perf_counter()
    
    # Extract 1 to 5-grams, ignoring standard english stop words
    # min_df=2 means the phrase must appear in at least 2 chapters to be considered "globally important"
    vectorizer = TfidfVectorizer(ngram_range=(1, 5), stop_words='english', min_df=2)
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Sum the TF-IDF scores for each phrase across all chapters
    sum_tfidf = np.asarray(tfidf_matrix.sum(axis=0)).ravel()
    
    # Get the feature names (the phrases)
    feature_names = vectorizer.get_feature_names_out()
    
    # Sort phrases by their sum TF-IDF score
    sorted_indices = sum_tfidf.argsort()[::-1]
    
    end = time.perf_counter()
    
    print(f"\nTop 20 Phrases Across the Entire Book:")
    print(f"{'Phrase':<40} | {'TF-IDF Score':<10} | Elapsed: {(end - start) * 1000:.3f} ms")
    print("-" * 70)
    
    for idx in sorted_indices[:20]:
        print(f"{feature_names[idx]:<40} | {sum_tfidf[idx]:.4f}")
        
    print("\nTop 20 4-to-5 Word Phrases:")
    print("-" * 70)
    count = 0
    for idx in sorted_indices:
        word_count = len(feature_names[idx].split())
        if word_count >= 4:
            print(f"{feature_names[idx]:<40} | {sum_tfidf[idx]:.4f}")
            count += 1
            if count == 20: break

if __name__ == "__main__":
    main()
