from pydantic import BaseModel, Field
from typing import Optional


class ProcessedQueryLLM(BaseModel):
    """OpenAI Function Schema for preprocessing queries"""
    is_valid: bool = Field(..., description="Whether the query is suitable for legal research")
    legal_term: Optional[str] = Field(
        None,
        description="The key legal concept extracted from the query (e.g., negligence, breach of contract)."
    )


class ProcessedQuery(BaseModel):
    """Full query processing result"""
    original_query: str
    processed_result: ProcessedQueryLLM
    processing_time: float
