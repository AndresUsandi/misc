import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from embeddings.embedding_generator import EmbeddingGenerator

class TestEmbeddingGenerator(unittest.TestCase):
    @patch('embeddings.embedding_generator.SentenceTransformer')
    def test_embed_texts(self, mock_transformer):
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model
        
        import numpy as np
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        
        generator = EmbeddingGenerator()
        res = generator.embed_texts(["test text"])
        
        self.assertEqual(res, [[0.1, 0.2, 0.3]])
        mock_model.encode.assert_called_once_with(["test text"], batch_size=128, show_progress_bar=False, convert_to_numpy=True)

    @patch('embeddings.embedding_generator.SentenceTransformer')
    def test_embed_texts_empty(self, mock_transformer):
        generator = EmbeddingGenerator()
        res = generator.embed_texts([])
        self.assertEqual(res, [])

if __name__ == '__main__':
    unittest.main()
