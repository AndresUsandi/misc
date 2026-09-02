from sentence_transformers import SentenceTransformer

# Top-of-file Constants
DEFAULT_MODEL_NAME = 'all-MiniLM-L6-v2'
DEFAULT_BATCH_SIZE = 128

LOG_LOADING_MODEL_FORMAT = "Loading local sentence-transformers model ({model_name})..."
LOG_MODEL_LOADED = "Embedding model loaded."

class EmbeddingGenerator:
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        print(LOG_LOADING_MODEL_FORMAT.format(model_name=model_name))
        self.model = SentenceTransformer(model_name)
        print(LOG_MODEL_LOADED)
        
    def embed_texts(self, texts: list, batch_size: int = DEFAULT_BATCH_SIZE) -> list:
        if not texts:
            return []
        embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=False, convert_to_numpy=True)
        return [emb.tolist() for emb in embeddings]
