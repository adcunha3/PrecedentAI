from typing import List
from openai import AsyncOpenAI
from app.schemas.case_summary import CaseSummary, CaseFinding
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
        
        # Create findings for each case
        findings = self._create_findings_from_cases(cases)
        
        # Generate overall summary from the findings
        overall_summary = await self._generate_overall_summary(query, findings)
        
        return CaseSummary(
            summary=overall_summary,
            findings=findings,
            error=None
        )
    
    def _create_findings_from_cases(self, cases: List[LegalCase]) -> List[CaseFinding]:
        """Create CaseFinding objects from each case"""
        findings = []
        for case in cases[:3]:  # Limit to first 3 cases
            finding = CaseFinding(
                title=f"Case: {case.case_name}",
                text=case.summary[:200] + "..." if len(case.summary) > 200 else case.summary,
                source_url=case.url,
                court=case.court or "Unknown Court",
                decision_date=str(case.year) if case.year else "Unknown"
            )
            findings.append(finding)
        return findings
    
    async def _generate_overall_summary(self, query: str, findings: List[CaseFinding]) -> str:
        """Generate overall summary from findings using LLM"""
        messages = [
            {"role": "system", "content": "You are a legal research assistant. Provide a concise summary of the key findings."},
            {"role": "user", "content": f"Query: {query}\n\nProvide a summary of the key legal findings from the {len(findings)} cases found."}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0
            )
            return response.choices[0].message.content
        except Exception:
            # Fallback to simple summary
            return f"Found {len(findings)} relevant cases for: {query}"