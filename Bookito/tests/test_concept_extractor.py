import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processors.concept_extractor import ConceptExtractor, is_valid_pos_sequence
from processors.concept_processor import ConceptProcessor
from book import Book, Chapter, Chunk

# Top-of-file Constants for Unit Tests
SAMPLE_PROSE_TEXT = (
    "Object-oriented programming is a programming paradigm based on the concept of objects. "
    "Objects can contain data in the form of fields and code in the form of procedures. "
    "Object-oriented programming uses classes and objects to structure software design."
)

SAMPLE_SHORT_TEXT = "hello world"
TEST_CHAPTER_TITLE = "Introduction to Object-Oriented Programming"
TEST_CHAPTER_NUMBER = 1
MIN_EXPECTED_CONCEPTS = 1

class TestConceptExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = ConceptExtractor(final_top_n=10)

    def test_pos_sequence_validation(self):
        self.assertTrue(is_valid_pos_sequence(["NOUN", "NOUN"]))
        self.assertTrue(is_valid_pos_sequence(["ADJ", "NOUN"]))
        self.assertTrue(is_valid_pos_sequence(["PROPN", "NOUN"]))
        self.assertFalse(is_valid_pos_sequence(["VERB", "NOUN"]))
        self.assertFalse(is_valid_pos_sequence(["ADP", "NOUN"]))
        self.assertFalse(is_valid_pos_sequence(["ADJ", "VERB"]))

    def test_extract_from_text_empty(self):
        results = self.extractor.extract_from_text(SAMPLE_SHORT_TEXT)
        self.assertEqual(results, [])

    def test_extract_from_text_valid_prose(self):
        results = self.extractor.extract_from_text(SAMPLE_PROSE_TEXT)
        self.assertGreaterEqual(len(results), MIN_EXPECTED_CONCEPTS)
        
        for item in results:
            self.assertEqual(len(item), 3)
            phrase, score, occurrences = item
            self.assertIsInstance(phrase, str)
            self.assertIsInstance(score, float)
            self.assertIsInstance(occurrences, int)
            self.assertGreater(occurrences, 0)

    def test_extractFromText_alias(self):
        results_snake = self.extractor.extract_from_text(SAMPLE_PROSE_TEXT)
        results_camel = self.extractor.extractFromText(SAMPLE_PROSE_TEXT)
        self.assertEqual(results_snake, results_camel)

    def test_concept_processor_integration(self):
        processor = ConceptProcessor(final_top_n=10)
        book = Book()
        book.Title = "Sample Technical Book"

        chapter = Chapter()
        chapter.Title = TEST_CHAPTER_TITLE
        chapter.Number = TEST_CHAPTER_NUMBER

        long_prose = (
            "Software architecture refers to the fundamental structures of a software system. "
            "Each structure comprises software elements, relations among them, and properties of both. "
            "Good software architecture enables high performance, scalability, and maintainability. "
            "Microservices architecture decomposes applications into small independent services. "
            "Design patterns provide reusable solutions to common software development problems."
        )
        
        # Multiply prose to satisfy chapter minimum word count (200 words)
        full_text = " ".join([long_prose] * 5)
        for sentence in full_text.split(". "):
            if sentence.strip():
                chunk = Chunk()
                chunk.Text = sentence.strip() + "."
                chapter.Chunks.append(chunk)
                
        book.Chapters.append(chapter)

        results = processor.processBook(book)
        self.assertGreaterEqual(len(results), MIN_EXPECTED_CONCEPTS)
        for item in results:
            self.assertEqual(len(item), 4)
            phrase, score, chapters_count, total_occurrences = item
            self.assertIsInstance(phrase, str)
            self.assertIsInstance(score, float)
            self.assertIsInstance(chapters_count, int)
            self.assertIsInstance(total_occurrences, int)

if __name__ == "__main__":
    unittest.main()
