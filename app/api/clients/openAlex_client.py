import httpx
from typing import List, Dict

BASE_URL = "https://api.openalex.org/works"

class OpenAlexClient:
    def __init__(self, timeout: int = 10):
        self.base_url = BASE_URL
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def search_works(self, query_params:dict) -> List[Dict]:
        try:
            response = await self.client.get(self.base_url, params=query_params)
            response.raise_for_status()
            data = response.json()
            items = data.get("results", [])
            return [self._normalize_item(item) for item in items]
        except httpx.HTTPError as e:
            print(f"[CrossrefClient] HTTP error: {e}")
            return []
        except Exception as e:
            print(f"[CrossrefClient] Unexpected error: {e}")
            return []

    @classmethod
    def _normalize_item(cls, item: Dict) -> Dict:
        """
        Приводит данные Crossref к единому формату для нашего агрегатора.
        """
        return {
            # Основная информация
            'id': item.get('id'),
            'doi': item.get('doi'),
            'title': item.get('title'),

            # Авторы
            'authors': cls._extract_authors(item.get('authorships', [])),
        }

    @classmethod
    def _extract_authors(cls, author_ships: List[Dict]) -> List[Dict]:
        """Извлекает нормализованную информацию об авторах"""
        authors = []

        for authorship in author_ships:
            author_info = authorship.get('author', {})

            author_data = {
                'id': author_info.get('id'),
                'name': author_info.get('display_name')
            }
            authors.append(author_data)

        return authors

    async def close(self):
        await self.client.aclose()