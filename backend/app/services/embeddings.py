from langchain_openai import OpenAIEmbeddings
from app.config import settings

class EmbeddingService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
    
    def get_embedding(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)