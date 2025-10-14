from app.services.query.processor import QueryProcessor
from app.services.ingestion.pipeline import SearchPipeline
from app.services.llm.llm_service import LLMService
from app.schemas.search import SearchResponse, LegalCase
from app.schemas.case_summary import CaseSummary
from typing import List

class SearchOrchestrator:
    """Orchestrator for legal/academic case search and summarization."""
    
    def __init__(self):
        self.query_processor = QueryProcessor()
        self.search_pipeline = SearchPipeline()
        self.llm_service = LLMService()
    
    async def search(self, query: str) -> SearchResponse:
        # Process the query for legal terms
        processed = await self.query_processor.process_query(query)
        
        if not processed.processed_result.is_valid or not processed.processed_result.legal_term:
            return SearchResponse(
                is_valid=False,
                cases=[],
                web_summary=None
            )
        
        legal_term = processed.processed_result.legal_term
        academic_results = await self.search_pipeline.search(legal_term=legal_term, original_query=query)

        cases = []
        for paper in academic_results:
            case = LegalCase(
                case_name=paper.get('title', 'Unknown Case'),
                summary=paper.get('summary', '')[:500] + "..." if len(paper.get('summary', '')) > 500 else paper.get('summary', ''),
                url=paper.get('url', ''),
                confidence=paper.get('score', 0.0),
                jurisdiction=paper.get('jurisdiction', 'Unknown'),
                court=paper.get('court'),
                year=paper.get('year'),
                judges=paper.get('judges', []),
                legal_topics=paper.get('legal_topics', []),
                docket_number=paper.get('docket_number')
            )
            cases.append(case)
        
        summary = await self.llm_service.generate_summary(query, cases)
        
        return SearchResponse(
            is_valid=True,
            cases=cases,
            web_summary=summary
        )
