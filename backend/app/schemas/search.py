from pydantic import BaseModel
from typing import List, Optional
from app.schemas.case_summary import CaseSummary


class SearchQuery(BaseModel):
    """User query wrapper"""
    query: str


class LegalCase(BaseModel):
    """Lightweight case representation for search results"""
    case_name: str
    summary: str
    url: str
    confidence: float               # similarity score from RAG retrieval
    jurisdiction: str               # e.g., "Ontario", "US Supreme Court"
    court: Optional[str] = None
    year: Optional[int] = None
    judges: List[str] = []
    legal_topics: List[str] = []
    docket_number: Optional[str] = None


class SearchResponse(BaseModel):
    """Final packaged response to user"""
    is_valid: bool
    cases: List[LegalCase]
    web_summary: Optional[CaseSummary] = None
