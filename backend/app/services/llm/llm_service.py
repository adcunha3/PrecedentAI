from typing import List
from openai import AsyncOpenAI
from app.schemas.research_summary import ResearchSummary
from app.schemas.search import LegalCase
from app.config import settings

class LLMService:
    """Generate summaries from legal/academic cases only."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def generate_summary(self, query: str, cases: List[LegalCase]) -> ResearchSummary:
        """Generate a research summary from cases"""
        
        if not cases:
            return ResearchSummary(
                summary="No cases available.",
                findings=[],
                error="No cases to analyze"
            )
        
        # Prepare context from cases
        context = "\n".join([
            f"Title: {case.case_name}\nSummary: {case.summary}\nURL: {case.url}" 
            for case in cases
        ])
        
        messages = [
            {"role": "system", "content": """
            You are a factual research assistant focused on legal cases.
            Analyze the provided cases and generate a structured summary with:
            1. Key findings
            2. Specific claims, titles, and sources
            """},
            {"role": "user", "content": f"""
            Research Query: {query}

            Cases:
            {context}

            Generate a research summary highlighting key insights and sources.
            """}
        ]
        
        try:
            completion = await self.client.beta.chat.completions.parse(
                model="gpt-3.5-turbo",
                messages=messages,
                response_format=ResearchSummary
            )
            return completion.choices[0].message.parsed
        
        except Exception as e:
            return ResearchSummary(
                summary="Error generating summary",
                findings=[],
                error=str(e)
            )
