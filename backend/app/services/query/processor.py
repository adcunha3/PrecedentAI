import json
from typing import Optional
from app.schemas.query_processing import ProcessedQuery, ProcessedQueryLLM
from openai import AsyncOpenAI

class QueryProcessor:
    """Simplified processor for PrecedentAI queries."""

    def __init__(self):
        self.client = AsyncOpenAI()

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

        # Call the LLM
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a legal research assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        raw_output = response.choices[0].message.content.strip()

        # Parse JSON
        try:
            data = json.loads(raw_output)
            processed_result = ProcessedQueryLLM(
                is_valid=data.get("is_valid", False),
                legal_term=data.get("legal_term")
            )
        except json.JSONDecodeError:
            processed_result = ProcessedQueryLLM(is_valid=False)

        # Return wrapped ProcessedQuery
        return ProcessedQuery(
            original_query=user_query,
            processed_result=processed_result,
            processing_time=0
        )
