import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.registry import BookParserRegistry

class DummyParser:
    pass

class TestBookParserRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = BookParserRegistry()

    def test_register_and_get_parser(self):
        self.registry.register_parser(".txt", DummyParser)
        parser = self.registry.get_parser(".txt")
        self.assertIsInstance(parser, DummyParser)

    def test_case_insensitivity(self):
        self.registry.register_parser(".TXT", DummyParser)
        parser = self.registry.get_parser(".txt")
        self.assertIsInstance(parser, DummyParser)

    def test_unregistered_extension(self):
        parser = self.registry.get_parser(".doc")
        self.assertIsNone(parser)

if __name__ == '__main__':
    unittest.main()
