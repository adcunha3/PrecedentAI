from typing import List, Dict
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm

from pinecone import Pinecone
from app.config import settings
from app.schemas.search import LegalCase
from app.services.embeddings import EmbeddingService

logger = logging.getLogger(__name__)

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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def ingest_case(self, case: LegalCase) -> bool:
        """
        Ingest a single case into Pinecone with retry logic.
        """
        try:
            # Create embedding from case_name + summary + legal topics
            text_to_embed = f"{case.case_name} {case.summary} {' '.join(case.legal_topics)}"
            vector = self.embedding_service.get_embedding(text_to_embed)

            # Metadata to store
            metadata = {
                "case_name": case.case_name,
                "summary": case.summary[:1400],  # limit summary length
                "jurisdiction": case.jurisdiction,
                "court": case.court,
                "year": case.year,
                "docket_number": case.docket_number,
                "legal_topics": case.legal_topics
            }

            self.index.upsert(
                vectors=[{
                    "id": case.case_name.replace(" ", "_"),  # unique id
                    "values": vector,
                    "metadata": metadata
                }]
            )
            return True
        except Exception as e:
            logger.error(f"Error ingesting case {case.case_name}: {str(e)}")
            raise

    async def batch_ingest_cases(self, cases: List[LegalCase]) -> None:
        """
        Batch ingest cases with progress tracking and error handling.
        """
        if not cases:
            return

        total_batches = (len(cases) + self.batch_size - 1) // self.batch_size
        failed_cases = []

        with tqdm(total=total_batches, desc="Case Batches") as pbar:
            for i in range(0, len(cases), self.batch_size):
                batch = cases[i:i+self.batch_size]
                vectors = []

                # Prepare batch embeddings
                for case in batch:
                    try:
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
                    except Exception as e:
                        logger.error(f"Error preparing case {case.case_name}: {str(e)}")
                        failed_cases.append(case.case_name)
                        continue

                # Attempt batch upsert with retry
                try:
                    if vectors:
                        await self._batch_upsert_with_retry(vectors)
                except Exception as e:
                    logger.error(f"Batch upsert failed for batch {i//self.batch_size + 1}: {str(e)}")
                    failed_cases.extend([v["id"] for v in vectors])
                finally:
                    pbar.update(1)

        if failed_cases:
            logger.warning(f"Failed to ingest {len(failed_cases)} cases: {failed_cases}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _batch_upsert_with_retry(self, vectors: List[Dict]) -> None:
        """
        Attempt batch upsert with retry logic.
        """
        try:
            self.index.upsert(vectors=vectors)
        except Exception as e:
            logger.error(f"Batch upsert error: {str(e)}")
            raise
