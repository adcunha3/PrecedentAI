from typing import List
from openai import AsyncOpenAI
from app.schemas.case_summary import CaseSummary
from app.schemas.search import LegalCase
from app.config import settings

class LLMService:
    """Generate summaries from legal/academic cases only."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def generate_summary(self, query: str, cases: List[LegalCase]) -> CaseSummary:
        """Generate a research summary from cases"""
        if not cases:
            return CaseSummary(
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
            # Try structured output first
            completion = await self.client.beta.chat.completions.parse(
                model="gpt-3.5-turbo",
                messages=messages,
                response_format=CaseSummary
            )
            return completion.choices[0].message.parsed
        
        except Exception as e:
            try:
                # Fallback to regular completion
                response = await self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0
                )
                
                # Parse the response manually
                content = response.choices[0].message.content
                return CaseSummary(
                    summary=content[:500] + "..." if len(content) > 500 else content,
                    findings=[
                        {
                            "title": f"Case: {case.case_name}",
                            "text": case.summary[:200] + "...",
                            "source_url": case.url,
                            "court": case.court or "Unknown Court",
                            "decision_date": str(case.year) if case.year else "Unknown"
                        }
                        for case in cases[:3]  # Limit to first 3 cases
                    ],
                    error=None
                )
            except Exception as e2:
                # Final fallback to simple summary
                return CaseSummary(
                    summary=f"Summary for query: {query}. Found {len(cases)} relevant cases.",
                    findings=[
                        {
                            "title": f"Case: {case.case_name}",
                            "text": case.summary[:200] + "...",
                            "source_url": case.url,
                            "court": case.court or "Unknown Court",
                            "decision_date": str(case.year) if case.year else "Unknown"
                        }
                        for case in cases[:3]  # Limit to first 3 cases
                    ],
                    error=None
                )
