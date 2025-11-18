# crossref_client.py
import httpx
from typing import List, Dict

BASE_URL = "https://api.crossref.org/works"

class CrossrefClient:
    def __init__(self, timeout: int = 10):
        self.base_url = BASE_URL
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def search_works(self, query_params:dict) -> List[Dict]:
        try:
            response = await self.client.get(self.base_url, params=query_params)
            response.raise_for_status()
            data = response.json()
            items = data.get("message", {}).get("items", [])
            return [self._normalize_item(item) for item in items]
        except httpx.HTTPError as e:
            print(f"[CrossrefClient] HTTP error: {e}")
            return []
        except Exception as e:
            print(f"[CrossrefClient] Unexpected error: {e}")
            return []

    @staticmethod
    def _normalize_item(item: Dict) -> Dict:
        """
        Приводит данные Crossref к единому формату для нашего агрегатора.
        """
        doi = item.get("DOI")
        title = item.get("title", [""])[0] if item.get("title") else ""
        authors = []
        for a in item.get("author", []):
            name_parts = []
            if "given" in a:
                name_parts.append(a["given"])
            if "family" in a:
                name_parts.append(a["family"])
            authors.append(" ".join(name_parts))
        year = item.get("published-print", {}).get("date-parts", [[None]])[0][0] \
               or item.get("published-online", {}).get("date-parts", [[None]])[0][0]
        url = item.get("URL")

        return {
            "doi": doi,
            "title": title,
            "authors": authors,
            "year": year,
            "url": url,
            "source": "crossref"
        }

    async def close(self):
        await self.client.aclose()
