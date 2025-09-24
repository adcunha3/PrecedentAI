from app.services.query.processor import QueryProcessor
from app.services.ingestion.pipeline import SearchPipeline
from app.services.llm.llm_service import LLMService
from app.schemas.search import SearchResponse, ResearchPaper
from app.schemas.research_summary import ResearchSummary
from typing import List

class SearchOrchestrator:
    """Orchestrator for legal/academic case search and summarization."""
    
    def __init__(self):
        self.query_processor = QueryProcessor()
        self.search_pipeline = SearchPipeline()
        self.llm_service = LLMService()
    
    async def search(self, query: str) -> SearchResponse:
        # 1. Process query
        processed = await self.query_processor.process_query(query)
        if not processed.processed_result.is_valid:
            return SearchResponse(
                is_valid=False,
                papers=[],
                web_summary=None
            )
        
        # 2. Fetch academic/legal cases
        academic_results = await self.search_pipeline.search(processed.processed_result.academic_term)
        
        # 3. Convert to ResearchPaper objects
        papers: List[ResearchPaper] = [
            ResearchPaper(
                title=paper['title'],
                summary=f"{paper.get('abstract', paper.get('summary',''))[:500]}...",
                url=paper['url'],
                confidence=paper['score'],
                source=paper.get('source', 'CourtListener'),
                categories=paper.get('categories', []),
                authors=paper.get('authors', []),
                year=paper.get('year')
            )
            for paper in academic_results
        ]
        
        # 4. Generate LLM summary of the cases
        summary: ResearchSummary = await self.llm_service.generate_summary(
            query=query,
            cases=academic_results
        )
        
        return SearchResponse(
            is_valid=True,
            papers=papers,
            web_summary=summary
        )
