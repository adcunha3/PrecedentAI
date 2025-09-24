import aiohttp
from typing import List
from app.schemas.search import LegalCase
from app.config import settings

class CourtListenerConnector:
    BASE_URL = "https://www.courtlistener.com/api/rest/v4/search/"

    def __init__(self, rate_limit_seconds: float = 1.0):
        self.rate_limit_seconds = rate_limit_seconds

    async def fetch_cases(self, query: str, max_results: int = 50) -> List[LegalCase]:
        if not query:
            return []

        if not settings.COURTLISTENER_API_KEY:
            print("No CourtListener API key provided.")
            return []

        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(ssl=ssl_context)
        headers = {"Authorization": f"Token {settings.COURTLISTENER_API_KEY}"}

        cases = []

        async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
            params = {
                "q": query,  # NOTE: for /search/, it’s `q`, not `search`
                "page_size": min(max_results, 100),
            }

            try:
                async with session.get(self.BASE_URL, params=params) as response:
                    if response.status != 200:
                        print(f"Error {response.status}: {await response.text()}")
                        return []

                    data = await response.json()
                    results = data.get("results", [])

                    for item in results:
                        case = LegalCase(
                            case_name=item.get("caseName") or "Unknown Case",
                            summary=item["opinions"][0].get("snippet", "") if item.get("opinions") else "",
                            url=f"https://www.courtlistener.com{item.get('absolute_url', '')}",
                            confidence=item.get("meta", {}).get("score", {}).get("bm25", 0.5),
                            jurisdiction=item.get("court"),
                            court=item.get("court_citation_string"),
                            year=item.get("dateFiled")[:4] if item.get("dateFiled") else None,
                            judges=[item.get("judge")] if item.get("judge") else [],
                            legal_topics=[],
                            docket_number=item.get("docketNumber")
                        )
                        cases.append(case)

            except Exception as e:
                print(f"Exception fetching cases: {e}")
                return []

        return cases
