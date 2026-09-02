import sys
import os
import time

# Ensure the root of the project is on the python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parsers.pdf_parser import PdfBookParser
import yake

def main():
    print("=== YAKE (Yet Another Keyword Extractor) Tutorial ===")
    print("YAKE is a light-weight unsupervised approach for automatic keyword extraction which rests on text statistical features.")
    print("It does not need to be trained on a particular corpus, nor does it rely on dictionaries, external corpora, or POS tagging.\n")
    
    # 1. Get sample text from our book corpus
    parser = PdfBookParser()
    path = r'e:\Development\GitHub\MachineLarning\Bookito\tests\integrations\files\Professional ADO NET 2 Programming With SQL Server 2005, Oracle, & MySQL 2006.pdf'
    print(f"Parsing PDF to extract sample text...")
    res = parser.parse(path, "test_book")

    # Find a chapter with enough text to extract meaningful keywords
    sample_text = res.getFullText()

    # 2. Configure YAKE
    # lan: Language of the text (default: 'en')
    # n: Maximum size of the n-gram / keyword (e.g. 3 means up to 3 words per phrase)
    # dedupLim: Deduplication threshold. Lower value means less duplication of similar keywords
    # top: Number of keywords to extract
    kw_extractor_1 = yake.KeywordExtractor(
        lan="en", 
        n=1, 
        dedupLim=0.9, 
        top=20, 
        features=None
    )
    kw_extractor_2 = yake.KeywordExtractor(
        lan="en", 
        n=2, 
        dedupLim=0.9, 
        top=20, 
        features=None
    )
    kw_extractor_3 = yake.KeywordExtractor(
        lan="en", 
        n=3, 
        dedupLim=0.9, 
        top=20, 
        features=None
    )
    
    # 3. Extract Keywords
    start = time.perf_counter()
    print("\nExtracting keywords using YAKE...")
    keywords = []
    keywords.extend(kw_extractor_1.extract_keywords(sample_text))
    keywords.extend(kw_extractor_2.extract_keywords(sample_text))
    keywords.extend(kw_extractor_3.extract_keywords(sample_text))
    end = time.perf_counter()
    
    # 4. Display Results
    # Important: YAKE returns (keyword, score). A LOWER score indicates HIGHER relevance.
    print(f"{'Keyword/Phrase':<35} | {'Score (Lower is better)':<10} | Elapsed: {(end - start) * 1000:.3f} ms")
    print("-" * 60)
    for kw, score in keywords:
        print(f"{kw:<35} | {score:.4f}")

if __name__ == "__main__":
    main()
