import sys
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, CountVectorizer

def main():
    print("=== Scikit-Learn Stop Words Tutorial ===\n")
    
    # 1. Inspecting the built-in stop words list
    print("1. THE BUILT-IN STOP WORDS LIST")
    print("-" * 50)
    stop_words_list = sorted(list(ENGLISH_STOP_WORDS))
    print(f"Scikit-learn comes with a built-in set of {len(stop_words_list)} common English stop words.")
    
    # Let's print a sample of them (every 20th word)
    sample_words = stop_words_list[::20]
    print("Here is a sample of what's inside (every 20th word):")
    print(", ".join(sample_words))
    print("\n")
    
    # 2. Demonstrating the effect of stop words on text
    print("2. HOW IT AFFECTS TEXT PROCESSING")
    print("-" * 50)
    
    sample_text = [
        "This is an example sentence that demonstrates how the stop words filter works in python.",
        "The quick brown fox jumps over the lazy dog, but the dog is just too tired to care."
    ]
    
    print("Original Text:")
    for text in sample_text:
        print(f" - '{text}'")
    print()
    
    # Create a vectorizer WITHOUT filtering stop words
    vectorizer_no_filter = CountVectorizer(ngram_range=(1, 3))
    vectorizer_no_filter.fit(sample_text)
    unfiltered_phrases = vectorizer_no_filter.get_feature_names_out()
    
    # Create a vectorizer WITH filtering stop words
    vectorizer_with_filter = CountVectorizer(ngram_range=(1, 3), stop_words='english')
    vectorizer_with_filter.fit(sample_text)
    filtered_phrases = vectorizer_with_filter.get_feature_names_out()
    
    print(f"Total phrases found WITHOUT filtering: {len(unfiltered_phrases)}")
    print(f"Total phrases found WITH 'english' filtering: {len(filtered_phrases)}")
    print()
    
    print("Example 3-word phrases (Trigrams) WITHOUT filtering:")
    print([p for p in unfiltered_phrases if len(p.split()) == 3][:5])
    
    print("\nExample 3-word phrases (Trigrams) WITH filtering:")
    print([p for p in filtered_phrases if len(p.split()) == 3][:5])
    print("\nNotice how the filtered trigrams are completely stripped of words like 'this', 'is', 'the', etc.")
    print("This means 'quick brown fox' is perfectly preserved, but 'this is an' is completely removed!\n")
    
    # 3. Customizing the stop words list
    print("3. ADDING CUSTOM STOP WORDS")
    print("-" * 50)
    print("Sometimes 'english' isn't enough. In programming books, words like 'dim', 'string', or 'new' might be noise.")
    
    custom_stop_words = list(ENGLISH_STOP_WORDS.union({"dim", "string", "new", "public", "private", "class"}))
    print(f"By using python sets, we can combine the {len(ENGLISH_STOP_WORDS)} built-in words with our own custom programming words.")
    print(f"New custom list length: {len(custom_stop_words)} words.")
    
    custom_vectorizer = CountVectorizer(stop_words=custom_stop_words)
    print("You can then pass this custom list directly into any vectorizer: CountVectorizer(stop_words=custom_stop_words)")

if __name__ == "__main__":
    main()
