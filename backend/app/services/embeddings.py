from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
    
    def get_embedding(self, text: str) -> List[float]:
        embeddings = self.model.encode(text)
        return embeddings.tolist()
        
# TODO: Update the embedding service to use a better model that produces 1024-dimensional vectors
