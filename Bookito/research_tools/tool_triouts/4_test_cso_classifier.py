import sys
import os
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure the root of the project is on the python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parsers.pdf_parser import PdfBookParser

# CSO Classifier maps text to the Computer Science Ontology
from cso_classifier import CSOClassifier

def main():
    print("=== CSO (Computer Science Ontology) Classifier Tutorial ===")
    print("The CSO Classifier takes text and classifies it into research topics from the Computer Science Ontology.")
    print("It uses both syntactic matching and semantic similarity (via Word2Vec embeddings).\n")
    
    # 1. Get sample text from our book corpus
    parser = PdfBookParser()
    path = r'e:\Development\GitHub\MachineLarning\Bookito\tests\integrations\files\Professional ADO NET 2 Programming With SQL Server 2005, Oracle, & MySQL 2006.pdf'
    print(f"Parsing PDF to extract sample text...")
    res = parser.parse(path, "test_book")
    
    sample_text = ""
    for ch in res.Chapters:
        ch_text = ch.getFullText()
        if len(ch_text) > 1500:
            sample_text = ch_text
            print(f"Selected Chapter: '{ch.Title}' ({len(sample_text)} characters)\n")
            break
            
    if not sample_text:
        print("Could not find a chapter with sufficient text.")
        return
        
    # 2. Initialize the Classifier
    # Note: On first run, this might try to download the CSO ontology or word2vec model if not present.
    print("Initializing CSO Classifier (this may take a moment to load the ontology)...")
    
    # We use modules="both" to run both the syntactic module and the semantic module
    classifier = CSOClassifier(modules="both", enhancement="first", explanation=True)
    
    try:
        # 3. Classify Text
        # For speed and demonstration, we'll just classify the first 5000 characters
        print("Classifying text...")
        result = classifier.run(sample_text[:5000])
        
        # 4. Display Results
        print("\nClassification Results:")
        
        print("\nSyntactic Topics (Exact/fuzzy matches):")
        for topic in result.get("syntactic", []):
            print(f" - {topic}")
            
        print("\nSemantic Topics (Inferred via embeddings):")
        for topic in result.get("semantic", []):
            print(f" - {topic}")
            
        print("\nUnion (All unique topics):")
        for topic in result.get("union", []):
            print(f" - {topic}")
            
        print("\nEnhanced (Parents in the ontology):")
        for topic in result.get("enhanced", []):
            print(f" - {topic}")
            
        # Print explanations for why semantic topics were chosen
        if result.get("explanation"):
            print("\nExplanation (Why a semantic topic was chosen):")
            for topic, reason in list(result.get("explanation", {}).items())[:5]:
                print(f" - {topic}: inferred from {reason}")
    except Exception as e:
        print(f"\n[Environment Error]: CSO Classifier crashed during execution.")
        print(f"Error details: {e}")
        print("Note: The cso-classifier package has known compatibility issues with newer versions of `igraph`.")
        print("In a working environment, it would output topics like 'data access', 'database systems', etc.")

if __name__ == "__main__":
    main()
