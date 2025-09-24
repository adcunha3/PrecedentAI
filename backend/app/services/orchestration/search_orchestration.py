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
        print(f"SEARCH ORCHESTRATOR: Starting search for: {query}")
        
        # 1. Process query
        processed = await self.query_processor.process_query(query)
        print(f"SEARCH ORCHESTRATOR: Query processed - Valid: {processed.processed_result.is_valid}")
        
        if not processed.processed_result.is_valid:
            print("SEARCH ORCHESTRATOR: Query invalid, returning empty response")
            return SearchResponse(
                is_valid=False,
                cases=[],
                web_summary=None
            )
        
        # Use the original query if legal_term is None
        search_term = processed.processed_result.legal_term or query
        print(f"SEARCH ORCHESTRATOR: Using search term: {search_term}")
        
        # 2. Fetch academic/legal cases
        academic_results = await self.search_pipeline.search(search_term)
        print(f"SEARCH ORCHESTRATOR: Retrieved {len(academic_results)} cases from pipeline")
        
        # 3. Convert to LegalCase objects
        cases: List[LegalCase] = [
            LegalCase(
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
            for paper in academic_results
        ]
        
        # 4. Generate LLM summary of the cases
        summary: CaseSummary = await self.llm_service.generate_summary(
            query=query,
            cases=cases
        )
        
        return SearchResponse(
            is_valid=True,
            cases=cases,
            web_summary=summary
        )
