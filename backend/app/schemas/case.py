from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CaseMetadata(BaseModel):
    """
    Flexible metadata for a legal case.
    All fields optional for different sources.
    """
    judges: List[str] = []
    jurisdiction: Optional[str] = None   # e.g., "Ontario", "US Supreme Court"
    court: Optional[str] = None
    year: Optional[int] = None
    decision_date: Optional[datetime] = None
    citations: List[str] = []            # list of cited cases
    legal_topics: List[str] = []         # e.g., ["contract law", "tort negligence"]
    docket_number: Optional[str] = None
    summary: Optional[str] = None


class Case(BaseModel):
    """
    Full canonical case information including metadata.
    This is stored in DB / vector DB.
    """
    title: str
    url: str
    metadata: CaseMetadata
