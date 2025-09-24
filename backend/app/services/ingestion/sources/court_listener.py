import aiohttp
from typing import List
from app.schemas.search import LegalCase
from app.config import settings

class CourtListenerConnector:
    BASE_URL = "https://www.courtlistener.com/api/rest/v4/opinions/"

    def __init__(self, rate_limit_seconds: float = 1.0):
        self.rate_limit_seconds = rate_limit_seconds  # simple rate limiting

    async def fetch_cases(self, query: str, max_results: int = 50) -> List[LegalCase]:
        """Fetch cases from CourtListener API based on query."""
        if not query:
            return []

        cases = []
        async with aiohttp.ClientSession() as session:
            params = {
                "search": query,
                "page_size": min(max_results, 100),  # CourtListener max is 100 per page
            }

            async with session.get(self.BASE_URL, params=params) as response:
                if response.status != 200:
                    print(f"Error from CourtListener API: {response.status}")
                    return []

                data = await response.json()
                results = data.get("results", [])

                for item in results:
                    case = LegalCase(
                        id=str(item.get("id")),
                        case_name=item.get("caseName"),
                        summary=item.get("plain_text", "")[:2000],  # limit length
                        url=item.get("absolute_url"),
                        metadata={
                            "court": item.get("court"),
                            "jurisdiction": item.get("jurisdiction"),
                            "docket_number": item.get("docket_number"),
                            "date_filed": item.get("dateFiled")
                        }
                    )
                    cases.append(case)

        return cases
