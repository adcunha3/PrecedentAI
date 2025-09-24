from typing import List, Dict
import asyncio
from datetime import datetime
from pinecone import Pinecone
from app.services.embeddings import EmbeddingService
from app.config import settings
from app.services.ingestion.sources.court_listener import CourtListenerConnector

class SearchPipeline:
    """Pipeline for searching legal cases from CourtListener"""

    def __init__(self):
        self.source = CourtListenerConnector()
        self.embedding_service = EmbeddingService()
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX)

    async def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search Pinecone for legal cases and fetch details from CourtListener"""
        print(f"SEARCH PIPELINE: Starting search for query: {query}")
        
        # 1. Generate query embedding
        query_embedding = self.embedding_service.get_embedding(query)
        print(f"SEARCH PIPELINE: Generated embedding with {len(query_embedding)} dimensions")
        
        # 2. Query Pinecone index for similar cases
        try:
            print(f"SEARCH PIPELINE: Querying Pinecone index: {settings.PINECONE_INDEX}")
            pinecone_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            print(f"SEARCH PIPELINE: Found {len(pinecone_results.matches)} matches from Pinecone")
            
            # 3. Convert Pinecone results to our format
            results = []
            for i, match in enumerate(pinecone_results.matches):
                result = {
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
                results.append(result)
                print(f"SEARCH PIPELINE: Match {i+1} - {result['title']} (score: {result['score']:.4f})")
            
            print(f"SEARCH PIPELINE: Returning {len(results)} results")
            return results
            
        except Exception as e:
            # Fallback to CourtListener search if Pinecone fails
            print(f"Pinecone search failed, falling back to CourtListener: {e}")
            court_results = await self.source.fetch_cases(query)
            
            # Generate query embedding once
            query_embedding = self.embedding_service.get_embedding(query)
            
            # Rank results based on similarity
            scored_results = await self._rank_results(query_embedding, court_results)
            
            # Keep only top_k
            top_results = sorted(scored_results, key=lambda x: x['score'], reverse=True)[:top_k]
            
            return top_results

    async def _rank_results(self, query_embedding: List[float], documents: List) -> List[Dict]:
        """Rank results by cosine similarity to query"""
        scored_docs = []

        async def get_score(doc):
            # Handle both LegalCase objects and dictionaries
            if hasattr(doc, 'case_name'):
                # LegalCase object
                doc_text = f"{doc.case_name} {doc.summary[:1000]}"
            else:
                # Dictionary
                doc_text = f"{doc['title']} {doc.get('summary', '')[:1000]}"
            
            doc_embedding = self.embedding_service.get_embedding(doc_text)
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            
            # Convert to dictionary format
            if hasattr(doc, 'case_name'):
                result = {
                    'title': doc.case_name,
                    'summary': doc.summary,
                    'url': doc.url,
                    'score': similarity,
                    'jurisdiction': doc.jurisdiction,
                    'court': doc.court,
                    'year': doc.year,
                    'judges': doc.judges,
                    'legal_topics': doc.legal_topics,
                    'docket_number': doc.docket_number
                }
            else:
                result = doc.copy()
                result['score'] = similarity
            
            return result

        tasks = [get_score(doc) for doc in documents]
        scored_docs = await asyncio.gather(*tasks, return_exceptions=False)
        return scored_docs

    def _cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        """
        return sum(a * b for a, b in zip(embedding1, embedding2)) / (sum(a**2 for a in embedding1) * sum(b**2 for b in embedding2))