from pydantic import BaseModel
from typing import Optional


class ProcessedQueryLLM(BaseModel):
    """LLM-processed query result"""
    is_valid: bool
    legal_term: Optional[str] = None


class ProcessedQuery(BaseModel):
    """Complete processed query with metadata"""
    original_query: str
    processed_result: ProcessedQueryLLM
    processing_time: float
