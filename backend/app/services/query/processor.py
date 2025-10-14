import json
from typing import Optional
from app.schemas.query_processing import ProcessedQuery, ProcessedQueryLLM
from openai import AsyncOpenAI
from app.config import settings

class QueryProcessor:
    """Simplified processor for PrecedentAI queries."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def process_query(self, user_query: str) -> ProcessedQuery:
        """Send query to LLM and return a structured ProcessedQuery."""

        prompt = f"""
        You are a legal research assistant.
        Determine if this user query is valid for legal research.
        If valid, extract the main legal term or topic.

        Query: "{user_query}"

        Respond in JSON with:
        {{
            "is_valid": true/false,
            "legal_term": "main legal topic if valid, else null"
        }}
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a legal research assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            raw_output = response.choices[0].message.content.strip()

            try:
                data = json.loads(raw_output)
                processed_result = ProcessedQueryLLM(
                    is_valid=data.get("is_valid", False),
                    legal_term=data.get("legal_term")
                )
            except json.JSONDecodeError:
                processed_result = ProcessedQueryLLM(is_valid=False)

        except Exception as e:
            processed_result = ProcessedQueryLLM(
                is_valid=False,
                legal_term=None
            )
        return ProcessedQuery(
            original_query=user_query,
            processed_result=processed_result,
            processing_time=0
        )

# TODO: Preprocess the query to remove stop words and other noise
