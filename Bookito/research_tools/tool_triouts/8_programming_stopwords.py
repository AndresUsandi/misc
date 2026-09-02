import keyword
from sklearn.feature_extraction.text import CountVectorizer

def main():
    print("=== Programming Language Stop Words Tutorial ===\n")
    print("Unlike natural languages, programming languages don't have built-in stop word lists in Scikit-Learn.")
    print("However, because programming languages have a strict, finite set of 'Reserved Keywords', it's extremely easy to create your own!\n")
    
    # ---------------------------------------------------------
    # 1. Python Stop Words (using built-in library)
    # ---------------------------------------------------------
    print("1. PYTHON STOP WORDS")
    print("-" * 50)
    
    # Python actually has a built-in library for this!
    python_stopwords = set(keyword.kwlist)
    print(f"Python has {len(python_stopwords)} reserved keywords.")
    print(f"Sample: {list(python_stopwords)[:10]}\n")
    
    python_code = [
        "def calculate_total(items):",
        "    total = 0",
        "    for item in items:",
        "        if item.is_valid():",
        "            total += item.price",
        "    return total"
    ]
    
    # Vectorizer without stopwords
    vec_unfiltered = CountVectorizer()
    vec_unfiltered.fit(python_code)
    
    # Vectorizer WITH python stopwords
    vec_python = CountVectorizer(stop_words=list(python_stopwords))
    vec_python.fit(python_code)
    
    print("Phrases WITHOUT filtering (contains 'def', 'for', 'if', 'return'):")
    print(vec_unfiltered.get_feature_names_out())
    print("\nPhrases WITH Python filtering (only the actual logic survives!):")
    print(vec_python.get_feature_names_out())
    print("\n")
    
    
    # ---------------------------------------------------------
    # 2. Java / C# Stop Words (Custom sets)
    # ---------------------------------------------------------
    print("2. JAVA / C# STOP WORDS")
    print("-" * 50)
    
    # For languages like Java or C#, you can simply copy-paste their 50 reserved keywords into a set
    java_stopwords = {
        "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class", 
        "const", "continue", "default", "do", "double", "else", "enum", "extends", "final", 
        "finally", "float", "for", "goto", "if", "implements", "import", "instanceof", "int", 
        "interface", "long", "native", "new", "package", "private", "protected", "public", 
        "return", "short", "static", "strictfp", "super", "switch", "synchronized", "this", 
        "throw", "throws", "transient", "try", "void", "volatile", "while", "true", "false", "null"
    }
    print(f"We defined a custom Java stop-words list with {len(java_stopwords)} keywords.\n")
    
    java_code = [
        "public class OrderProcessor {",
        "    private int orderId;",
        "    public boolean validateOrder() {",
        "        if (this.orderId > 0) { return true; }",
        "        else { return false; }",
        "    }",
        "}"
    ]
    
    vec_java = CountVectorizer(stop_words=list(java_stopwords))
    vec_java.fit(java_code)
    
    print("Extracted keywords from the Java code snippet:")
    print(vec_java.get_feature_names_out())
    print("\nNotice how 'public', 'class', 'private', 'int', 'boolean', 'if', 'this', 'return', 'true', 'else', and 'false' were perfectly ignored!")

if __name__ == "__main__":
    main()
