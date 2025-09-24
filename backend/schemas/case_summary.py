from pydantic import BaseModel
from typing import List, Optional


class CaseFinding(BaseModel):
    """A key legal finding extracted from a case"""
    title: str                       # e.g., "Duty of Care Established"
    text: str                        # principle explained
    source_url: str                  # case source link
    court: Optional[str] = None
    decision_date: Optional[str] = None


class CaseSummary(BaseModel):
    """Condensed summary of key precedents"""
    summary: str
    findings: List[CaseFinding]
    error: Optional[str] = None
