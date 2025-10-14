from typing import List, Dict
import asyncio
from datetime import datetime
from pinecone import Pinecone
from app.services.embeddings import EmbeddingService
from app.config import settings
from app.services.ingestion.sources.court_listener import CourtListenerConnector
from app.services.ingestion.ingestion import CaseIngestionService

class SearchPipeline:
    """Pipeline for searching legal cases from CourtListener"""

    def __init__(self):
        self.source = CourtListenerConnector()
        self.embedding_service = EmbeddingService()
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX)
        self.ingestion_service = CaseIngestionService()

    async def search(self, legal_term: str, original_query: str = None, top_k: int = 3) -> List[Dict]:
        # Try to find cases in our vector database first
        pinecone_results = await self._search_pinecone(legal_term, top_k)
        
        if pinecone_results:
            return pinecone_results
        
        # No cases found in DB - fetch from Court API and store them
        court_results = await self.source.fetch_cases(original_query)
        await self.ingestion_service.ingest_cases(court_results)
        
        # Return Court API results directly (they're already ranked by Court API)
        return [
            {
                'title': case.case_name,
                'summary': case.summary,
                'url': case.url,
                'score': case.confidence,
                'jurisdiction': case.jurisdiction,
                'court': case.court,
                'year': case.year,
                'judges': case.judges,
                'legal_topics': case.legal_topics,
                'docket_number': case.docket_number
            }
            for case in court_results[:top_k]
        ]

    async def _search_pinecone(self, legal_term: str, top_k: int) -> List[Dict]:
        # Search Pinecone vector database for similar cases
        try:
            query_embedding = self.embedding_service.get_embedding(legal_term)
            # Cosine Similarity
            pinecone_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            if not pinecone_results.matches:
                return []
            
            return [
                {
                    'title': match.metadata.get('case_name', 'Unknown Case'),
                    'summary': match.metadata.get('summary', ''),
                    'url': match.metadata.get('url', ''),
                    'score': match.score,
                    'jurisdiction': match.metadata.get('jurisdiction', 'Unknown'),
                    'court': match.metadata.get('court'),
                    'year': match.metadata.get('year'),
                    'judges': match.metadata.get('judges', []),
                    'legal_topics': match.metadata.get('legal_topics', []),
                    'docket_number': match.metadata.get('docket_number')
                }
                for match in pinecone_results.matches
            ]
        except Exception:
            return []
