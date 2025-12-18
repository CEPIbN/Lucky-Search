import httpx
import logging
from typing import List, Dict
import asyncio

BASE_URL = "https://api.openalex.org/works"

class OpenAlexClient:
    def __init__(self, timeout: int = 10):
        self.base_url = BASE_URL
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def _search_per_page(self,
                      all_items: list,
                      page: int,
                      rows_per_page: int,
                      current_params: dict,
                      max_results: int):
        while len(all_items) < max_results:
            # Обновляем параметры пагинации
            current_params.update({
                'per-page': rows_per_page,
                'page': page
            })

            response = await self.client.get(self.base_url, params=current_params)
            print(f"OpenAlex URL: {response.url}")
            response.raise_for_status()
            data = response.json()

            items = data.get("results", [])
            current_total = len(items)

            print(f"Page={page}, requested={rows_per_page}, received={current_total}")

            all_items.extend(items)
            page += 1  # Увеличиваем на ФАКТИЧЕСКОЕ количество

            if current_total < rows_per_page:
                # Получили меньше, чем запросили - значит, это последняя страница
                print(f"Last page reached. Got {current_total} instead of {rows_per_page}")
                break

            total_available = data.get("meta", {}).get("count", 0)
            print(f"Total collected: {len(all_items)} of {total_available} available")

    async def search_works(self, query_params:dict, max_results) -> List[Dict]:
        try:
            """Получить все результаты с пагинацией"""
            all_items = []
            params = query_params.copy()
            params.update({'mailto': 'bogachev762@gmail.com'})
            await self._search_per_page(all_items,
                                        page=1,
                                        rows_per_page=min(1000, params.get('per-page', 10)),
                                        current_params=params,
                                        max_results=max_results)

            return [self._normalize_item(item) for item in all_items]

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


# Включите отладку httpx
'''logging.basicConfig(level=logging.DEBUG)

async def debug_request():
    async with httpx.AsyncClient(
            timeout=30.0,
            # Отключаем сжатие для упрощения отладки
            headers={'Accept-Encoding': 'identity'}
    ) as client:

        # Простой тестовый запрос
        test_url = "https://api.openalex.org/works?search=vodka&per-page=15"
        print(f"Тестируем URL: {test_url}")

        try:
            response = await client.get(test_url)
            print(f"Статус: {response.status_code}")
            print(f"Заголовки: {dict(response.headers)}")

            # Пробуем прочитать ответ небольшими порциями
            content = b""
            async for chunk in response.aiter_bytes(chunk_size=1024):
                content += chunk
                print(f"Получено {len(content)} байт...")

            print(f"Всего получено: {len(content)} байт")

        except httpx.ReadTimeout as e:
            print(f"Таймаут чтения: {e}")
        except httpx.ReadError as e:
            print(f"Ошибка чтения: {e}")
        except Exception as e:
            print(f"Другая ошибка: {type(e).__name__}: {e}")

async def main():
    test_task = asyncio.create_task(debug_request())
    await asyncio.gather(test_task)

if __name__ == "__main__":
    asyncio.run(main())  # <-- Ключевая строка'''

