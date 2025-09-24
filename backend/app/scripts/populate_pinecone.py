#!/usr/bin/env python3
"""
Script to populate Pinecone index with legal cases from CourtListener
"""
import asyncio
import sys
import os
from typing import List, Dict
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.services.ingestion.sources.court_listener import CourtListenerConnector
from pinecone import Pinecone
import hashlib
import numpy as np

class PineconePopulator:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX)
        self.court_listener = CourtListenerConnector()
        self.embedding_dim = 1024
        
    async def populate_index(self, max_cases: int = 10):
        """Populate Pinecone index with real legal cases from CourtListener API"""
        print(f"Starting to populate Pinecone index with {max_cases} real cases from CourtListener API...")
        
        # Use a single search term to get real cases
        search_term = "contract law"
        print(f"Fetching {max_cases} real cases for: {search_term}")
        
        try:
            all_cases = await self.court_listener.fetch_cases(search_term, max_results=max_cases)
            print(f"Successfully fetched {len(all_cases)} real cases from CourtListener API")
        except Exception as e:
            print(f"Error fetching cases from CourtListener API: {e}")
            return
        
        if not all_cases:
            print("No cases found. Check your CourtListener API key and connection.")
            return
        
        # Prepare vectors for Pinecone
        vectors_to_upsert = []
        
        for i, case in enumerate(all_cases):
            # Create text for embedding
            case_text = f"{case.case_name} {case.summary}"
            
            # Generate embedding using hash-based method (same as your embedding service)
            embedding = self._get_embedding(case_text)
            
            # Prepare metadata
            metadata = {
                "case_name": case.case_name,
                "summary": case.summary,
                "url": case.url,
                "jurisdiction": case.jurisdiction,
                "court": case.court or "",
                "year": case.year or 0,
                "judges": case.judges,
                "legal_topics": case.legal_topics,
                "docket_number": case.docket_number or ""
            }
            
            # Create vector for Pinecone
            vector = {
                "id": f"case_{i}_{hash(case.case_name) % 100000}",
                "values": embedding,
                "metadata": metadata
            }
            
            vectors_to_upsert.append(vector)
            
            if len(vectors_to_upsert) >= 100:  # Batch upsert every 100 vectors
                await self._upsert_batch(vectors_to_upsert)
                vectors_to_upsert = []
                print(f"Upserted batch, total processed: {i + 1}")
        
        # Upsert remaining vectors
        if vectors_to_upsert:
            await self._upsert_batch(vectors_to_upsert)
        
        print(f"Successfully populated Pinecone index with {len(all_cases)} legal cases!")
        
    def _get_embedding(self, text: str) -> list[float]:
        """Generate a consistent embedding based on text hash (same as your embedding service)"""
        hash_obj = hashlib.md5(text.encode())
        seed = int(hash_obj.hexdigest()[:8], 16)
        np.random.seed(seed)
        embedding = np.random.normal(0, 1, self.embedding_dim)
        return embedding.tolist()
    
    async def _upsert_batch(self, vectors: List[Dict]):
        """Upsert a batch of vectors to Pinecone"""
        try:
            self.index.upsert(vectors=vectors)
        except Exception as e:
            print(f"Error upserting batch: {e}")

async def main():
    populator = PineconePopulator()
    await populator.populate_index(max_cases=10)  # Upload 10 real cases

if __name__ == "__main__":
    asyncio.run(main())
