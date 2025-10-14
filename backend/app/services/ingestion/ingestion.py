from typing import List
from pinecone import Pinecone
from app.config import settings
from app.schemas.search import LegalCase
from app.services.embeddings import EmbeddingService

class CaseIngestionService:
    """
    Handles ingestion of legal cases into Pinecone.
    Embeds case_name, summary, and legal_topics for semantic search.
    """

    def __init__(self, batch_size: int = 50):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX)
        self.embedding_service = EmbeddingService()
        self.batch_size = batch_size

    async def ingest_cases(self, cases: List[LegalCase]) -> None:
        # Ingest cases into Pinecone
        if not cases:
            return

        vectors = []
        for case in cases:
            text_to_embed = f"{case.case_name} {case.summary} {' '.join(case.legal_topics)}"
            vector = self.embedding_service.get_embedding(text_to_embed)
            vectors.append({
                "id": case.case_name.replace(" ", "_"),
                "values": vector,
                "metadata": {
                    "case_name": case.case_name,
                    "summary": case.summary[:1400],
                    "jurisdiction": case.jurisdiction,
                    "court": case.court,
                    "year": case.year,
                    "docket_number": case.docket_number,
                    "legal_topics": case.legal_topics
                }
            })

        self.index.upsert(vectors=vectors)

# TODO: Implement batch ingestion for larger datasets with retry logic
