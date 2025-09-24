from typing import List, Dict
import asyncio
from datetime import datetime
from pinecone import Pinecone
from app.services.embeddings import EmbeddingService
from app.config import settings
from app.services.ingestion.sources.courtlistener import CourtListenerConnector

class SearchPipeline:
    """Pipeline for searching legal cases from CourtListener"""

    def __init__(self):
        self.source = CourtListenerConnector()
        self.embedding_service = EmbeddingService()
        self.pinecone_client = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pinecone_client.Index(settings.PINECONE_INDEX)

    async def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Fetch, rank, and return top_k results for a query"""
        start_time = datetime.now()

        # Fetch results from CourtListener
        results = await self.source.fetch_cases(query)
        print(f"Fetched {len(results)} cases in {datetime.now() - start_time}")

        # Generate query embedding once
        query_embedding = self.embedding_service.get_embedding(query)

        # Rank results based on similarity
        scored_results = await self._rank_results(query_embedding, results)

        # Keep only top_k
        top_results = sorted(scored_results, key=lambda x: x['score'], reverse=True)[:top_k]
        print(f"Total search time: {datetime.now() - start_time}")

        return top_results

    async def _rank_results(self, query_embedding: List[float], documents: List[Dict]) -> List[Dict]:
        """Rank results by cosine similarity to query"""
        scored_docs = []

        async def get_score(doc):
            doc_text = f"{doc['title']} {doc.get('summary', '')[:1000]}"
            doc_embedding = self.embedding_service.get_embedding(doc_text)
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            doc['score'] = similarity
            return doc

        tasks = [get_score(doc) for doc in documents]
        scored_docs = await asyncio.gather(*tasks, return_exceptions=False)
        return scored_docs

    def _cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        """
        return sum(a * b for a, b in zip(embedding1, embedding2)) / (sum(a**2 for a in embedding1) * sum(b**2 for b in embedding2))