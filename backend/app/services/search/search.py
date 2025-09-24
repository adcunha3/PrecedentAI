from typing import List
from pinecone import Pinecone
from app.config import settings
from app.schemas.search import LegalCase
from app.services.embeddings import EmbeddingService

class CaseSearchService:
    """Semantic search service for legal cases using Pinecone embeddings."""

    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX)
        self.embedding_service = EmbeddingService()
    
    async def search(self, query: str, top_k: int = 5) -> List[LegalCase]:
        """Search Pinecone for legal cases relevant to the query."""
        
        # 1. Convert query into embedding
        query_vector = self.embedding_service.get_embedding(query)
        
        # 2. Query Pinecone index
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        
        # 3. Convert results into LegalCase objects
        cases: List[LegalCase] = []
        for match in results.matches:
            meta = match.metadata

            legal_case = LegalCase(
                case_name=meta.get("case_name", "Unknown Case"),
                summary=meta.get("summary", ""),
                url=meta.get("url", ""),
                confidence=match.score
            )
            cases.append(legal_case)

        return cases
