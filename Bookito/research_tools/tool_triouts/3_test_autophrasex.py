import sys
import os

# Ensure the root of the project is on the python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parsers.pdf_parser import PdfBookParser

# AutoPhraseX is a python port of AutoPhrase
from autophrasex import AutoPhrase

def main():
    print("=== AutoPhrasex Tutorial ===")
    print("AutoPhrase is a popular phrase mining tool that extracts quality phrases from a massive text corpus.")
    print("AutoPhrasex is a python implementation that builds on similar principles using POS tagging and frequency.\n")
    
    # 1. Get sample text from our book corpus
    parser = PdfBookParser()
    path = r'e:\Development\GitHub\MachineLarning\Bookito\tests\integrations\files\Professional ADO NET 2 Programming With SQL Server 2005, Oracle, & MySQL 2006.pdf'
    print(f"Parsing PDF to extract sample text...")
    res = parser.parse(path, "test_book")
    
    # AutoPhrase works best with more text, let's gather the first few chapters
    sample_text_blocks = []
    total_len = 0
    for ch in res.Chapters:
        text = ch.getFullText()
        if len(text) > 500:
            sample_text_blocks.append(text)
            total_len += len(text)
            if total_len > 500000: # get about 500k characters
                break
                
    print(f"Gathered {len(sample_text_blocks)} chapters ({total_len} characters) for phrase mining.")
    
    if not sample_text_blocks:
        print("Could not find sufficient text.")
        return
        
    # Write to a temporary text file because AutoPhraseX usually processes from a file or iterator
    temp_file = "temp_corpus.txt"
    with open(temp_file, "w", encoding="utf-8") as f:
        for block in sample_text_blocks:
            # simple sentence splitting by period for the sake of the corpus
            sentences = block.split('.')
            for s in sentences:
                s = s.strip().replace('\n', ' ')
                if len(s) > 10:
                    f.write(s + "\n")
    
    quality_file = "temp_quality.txt"
    with open(quality_file, "w", encoding="utf-8") as f:
        f.write("sql server\ndatabase\nmicrosoft\nado.net\ndata access\nwindows\n")

    # 2. Initialize AutoPhrase
    print("\nInitializing AutoPhrase...")
    from autophrasex import DefaultCorpusReader, DefaultPhraseSelector, JiebaTokenizer
    autophrase = AutoPhrase(
        reader=DefaultCorpusReader(tokenizer=JiebaTokenizer()),
        selector=DefaultPhraseSelector(),
        extractors=[
            __import__('autophrasex').NgramsExtractor(N=4),
            __import__('autophrasex').IDFExtractor(),
            __import__('autophrasex').EntropyExtractor()
        ]
    )
    
    # 3. Mine Phrases
    print("Mining phrases...")
    try:
        # autophrasex typically runs a mine() method
        predictions = autophrase.mine(
            corpus_files=[temp_file],
            quality_phrase_files=[quality_file],
            callbacks=[]
        )
        
        # 4. Display Results
        print("\nExtracted Quality Phrases:")
        print(f"{'Phrase':<35} | {'Score'}")
        print("-" * 50)
        # Sort by score descending
        # the predictions list has tuples or dicts, depending on version, let's just print
        for p in predictions[:20]:
            print(p)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        
    # Cleanup
    if os.path.exists(temp_file):
        os.remove(temp_file)
    if os.path.exists(quality_file):
        os.remove(quality_file)

if __name__ == "__main__":
    main()
