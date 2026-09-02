import sys
import os

# Ensure the root of the project is on the python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parsers.pdf_parser import PdfBookParser

# For our custom ACM CCS classifier, we'll use scikit-learn for TF-IDF and Cosine Similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- A small subset of the 2012 ACM Computing Classification System (CCS) ---
# In a real implementation, you would parse the full XML/SKOS taxonomy file.
ACM_CCS_TAXONOMY = {
    "Hardware": [
        "Printed circuit boards", "Communication hardware, interfaces and storage", 
        "Integrated circuits", "Very large scale integration design",
        "Power and energy", "Electronic design automation", "Hardware validation"
    ],
    "Computer systems organization": [
        "Architectures", "Embedded and cyber-physical systems", 
        "Real-time systems", "Dependable and fault-tolerant systems and networks"
    ],
    "Networks": [
        "Network architectures", "Network protocols", "Network components", 
        "Network performance evaluation", "Network properties", "Network services", 
        "Network algorithms", "Network security"
    ],
    "Software and its engineering": [
        "Software organization and properties", "Software notations and tools", 
        "Software creation and management"
    ],
    "Theory of computation": [
        "Models of computation", "Formal languages and automata theory", 
        "Computational complexity and cryptography", "Logic", 
        "Design and analysis of algorithms"
    ],
    "Information systems": [
        "Data management systems", "Information storage systems", 
        "Information systems applications", "World Wide Web", "Information retrieval"
    ],
    "Security and privacy": [
        "Cryptography", "Formal methods and theory of security", 
        "Security services", "Intrusion/anomaly detection and malware mitigation",
        "Security in hardware", "Systems security", "Network security", 
        "Database and storage security", "Software and application security", 
        "Human and societal aspects of security and privacy"
    ]
}

def flatten_taxonomy():
    """Flattens the taxonomy into a list of concepts and their parent categories."""
    concepts = []
    for category, subtopics in ACM_CCS_TAXONOMY.items():
        # Add the parent category itself
        concepts.append({"category": category, "concept": category, "text": category})
        # Add the subtopics
        for sub in subtopics:
            concepts.append({"category": category, "concept": sub, "text": f"{category} {sub}"})
    return concepts

def main():
    print("=== ACM Computing Classification System (CCS) Tutorial ===")
    print("Because there is no official 'plug-and-play' python package for ACM CCS,")
    print("this script demonstrates how to build a custom heuristic classifier.")
    print("We use a small subset of the taxonomy and TF-IDF cosine similarity to map text to concepts.\n")
    
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
        
    # 2. Prepare the taxonomy data
    concepts = flatten_taxonomy()
    concept_texts = [c["text"] for c in concepts]
    
    # 3. Vectorize the taxonomy and the sample text
    print("Vectorizing taxonomy and document text using TF-IDF...")
    # We use english stop words to ignore common words like 'and', 'the', etc.
    vectorizer = TfidfVectorizer(stop_words='english')
    
    # Fit the vectorizer on both the taxonomy and the sample text to share the vocabulary
    tfidf_matrix = vectorizer.fit_transform(concept_texts + [sample_text])
    
    # The taxonomy vectors are everything except the last row
    taxonomy_vectors = tfidf_matrix[:-1]
    # The document vector is the last row
    document_vector = tfidf_matrix[-1]
    
    # 4. Calculate similarity
    print("Calculating cosine similarity between the document and ACM concepts...")
    similarities = cosine_similarity(document_vector, taxonomy_vectors)[0]
    
    # 5. Display Results
    # Pair concepts with their scores and sort descending
    scored_concepts = list(zip(concepts, similarities))
    scored_concepts.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTop ACM CCS Matches:")
    print(f"{'Category':<35} | {'Concept':<45} | {'Score'}")
    print("-" * 90)
    
    for concept, score in scored_concepts[:5]:
        # Only show matches with a non-zero score
        if score > 0:
            print(f"{concept['category']:<35} | {concept['concept']:<45} | {score:.4f}")
            
    print("\nNote: For better results, you would download the full ACM CCS taxonomy")
    print("and potentially use SentenceTransformers (SBERT) instead of TF-IDF for semantic matching.")

if __name__ == "__main__":
    main()
