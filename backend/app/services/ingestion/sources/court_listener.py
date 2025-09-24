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

        # If no API key is provided, return empty results
        if not settings.COURTLISTENER_API_KEY:
            print("No CourtListener API key provided.")
            return []

        cases = []
        # Create SSL context that doesn't verify certificates
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        headers = {"Authorization": f"Token {settings.COURTLISTENER_API_KEY}"}
        
        async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
            params = {
                "search": query,
                "page_size": min(max_results, 100),  # CourtListener max is 100 per page
            }

            try:
                async with session.get(self.BASE_URL, params=params) as response:
                    if response.status != 200:
                        return []

                    data = await response.json()
                    results = data.get("results", [])

                    if not results:
                        return []

                    for item in results:
                        case = LegalCase(
                            case_name=item.get("caseName", "Unknown Case"),
                            summary=item.get("plain_text", "")[:2000],  # limit length
                            url=item.get("absolute_url", ""),
                            confidence=0.8,  # Default confidence for API results
                            jurisdiction=item.get("jurisdiction", "Unknown"),
                            court=item.get("court"),
                            year=item.get("dateFiled", {}).get("year") if item.get("dateFiled") else None,
                            judges=[],
                            legal_topics=[],
                            docket_number=item.get("docket_number")
                        )
                        cases.append(case)
            except Exception as e:
                return []

        return cases

