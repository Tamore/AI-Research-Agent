import httpx
import logging
from typing import List, Dict, Any

logger = logging.getLogger("s2_client")

class SemanticScholarClient:
    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    async def search_papers(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Query Semantic Scholar Graph API for academic paper metadata."""
        url = f"{self.BASE_URL}/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,authors,year,abstract,citationCount,influentialCitationCount,openAccessPdf,externalIds"
        }
        
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("data", [])
                else:
                    logger.warning(f"Semantic Scholar API returned status {res.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Error querying Semantic Scholar API: {e}")
            return []
