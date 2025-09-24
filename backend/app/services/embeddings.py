import hashlib
import numpy as np

class EmbeddingService:
    def __init__(self):
        # Use hash-based embeddings for consistency and to avoid dependency issues
        self.model = None
        self.embedding_dim = 1024
        self.use_real_embeddings = False
    
    def get_embedding(self, text: str) -> list[float]:
        if self.use_real_embeddings and self.model:
            # Use real sentence transformer embeddings
            embedding = self.model.encode(text)
            return embedding.tolist()
        else:
            # Fallback to hash-based embeddings for consistency
            hash_obj = hashlib.md5(text.encode())
            seed = int(hash_obj.hexdigest()[:8], 16)
            np.random.seed(seed)
            embedding = np.random.normal(0, 1, self.embedding_dim)
            return embedding.tolist()