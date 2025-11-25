import httpx
from typing import List, Dict

BASE_URL = "https://api.openalex.org/works"

class OpenAlexClient:
    def __init__(self, timeout: int = 30):
        self.base_url = BASE_URL
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def search_works(self, query_params:dict) -> List[Dict]:
        try:
            response = await self.client.get(self.base_url, params=query_params)
            print(response.url)
            response.raise_for_status()
            data = response.json()
            items = data.get("results", [])
            return [self._normalize_item(item) for item in items]

        except httpx.HTTPStatusError as e:
            # Ошибки статуса (4xx, 5xx)
            print(f"Ошибка статуса HTTP: {e.response.status_code}")
            print(f"URL: {e.request.url}")
            print(f"Тело ответа: {e.response.text}")
            return []

        except httpx.ConnectTimeout:
            # Таймаут подключения
            print("Не удалось подключиться к серверу: таймаут")
            return []

        except httpx.ReadTimeout as e:
            # Таймаут чтения данных
            print("Сервер не ответил вовремя: таймаут чтения")
            print(f"URL: {e.request.url}")
            return []

        except httpx.ConnectError as e:
            # Ошибки подключения (DNS, сеть и т.д.)
            print(f"Ошибка подключения: {e}")
            return []

        except httpx.RequestError as e:
            # Общие ошибки запроса
            print(f"Ошибка при выполнении запроса: {e}")
            return []

        except httpx.HTTPError as e:
            print(f"[OpenAlexClient] HTTP error: {e}")
            return []

        except Exception as e:
            print(f"[OpenAlexClient] Unexpected error: {e}")
            return []

    @classmethod
    def _normalize_item(cls, item: Dict) -> Dict:
        """
        Приводит данные OpenAlex к единому формату для нашего агрегатора.
        """
        # Извлекаем информацию о журнале
        primary_location = item.get('primary_location', {}) or {}
        source = primary_location.get('source', {}) or {}
        
        # Извлекаем информацию о цитировании
        cited_by_count = item.get('cited_by_count', 0)
        
        return {
            # Основная информация
            'id': item.get('id', ''),
            'doi': item.get('doi', ''),
            'title': item.get('title', ''),
            'publication_year': item.get('publication_year', 0),
            
            # Журнал
            'journal': source.get('display_name', ''),
            'journal_abbreviation': source.get('abbreviated_title', ''),
            'publisher': source.get('host_organization.name', ''),
            
            # Цитирование
            'cited_by_count': cited_by_count,
            
            # Авторы
            'authors': cls._extract_authors(item.get('authorships', [])),
            
            # Дополнительная информация
            'volume': item.get('biblio', {}).get('volume', ''),
            'issue': item.get('biblio', {}).get('issue', ''),
            'authors_count': len(item.get('authorships', [])),
            'url': item.get('id', ''),
            'abstract': item.get('abstract', '')
        }

    @classmethod
    def _extract_authors(cls, author_ships: List[Dict]) -> List[Dict]:
        """Извлекает нормализованную информацию об авторах"""
        authors = []
        
        for authorship in author_ships:
            author_info = authorship.get('author', {}) or {}
            institutions = authorship.get('institutions', []) or []
            
            # Извлекаем информацию об институте
            institution = institutions[0] if institutions else {}
            
            author_data = {
                'id': author_info.get('id', ''),
                'name': author_info.get('display_name', ''),
                'surname': '',  # OpenAlex не предоставляет отдельно фамилию
                'affiliation': institution.get('display_name', ''),
                'country': institution.get('country_code', ''),
                'ror_id': institution.get('ror', '')
            }
            authors.append(author_data)
        
        return authors

    async def close(self):
        await self.client.aclose()