# crossref_client.py
import httpx
from typing import List, Dict

BASE_URL = "https://api.crossref.org/works"

class CrossrefClient:
    def __init__(self, timeout: int = 10):
        self.base_url = BASE_URL
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def _search_per_page(self,
                      all_items: list,
                      offset: int,
                      rows_per_page: int,
                      current_params: dict,
                      max_results: int):
        while len(all_items) < max_results:
            # Обновляем параметры пагинации
            current_params.update({
                'rows': rows_per_page,
                'offset': offset
            })

            response = await self.client.get(self.base_url, params=current_params)
            print(f"Crossref URL: {response.url}")
            response.raise_for_status()
            data = response.json()

            items = data.get("message", {}).get("items", [])
            current_total = len(items)

            print(f"Page: offset={offset}, requested={rows_per_page}, received={current_total}")

            all_items.extend(items)
            offset += current_total  # Увеличиваем на ФАКТИЧЕСКОЕ количество

            if current_total < rows_per_page:
                # Получили меньше, чем запросили - значит, это последняя страница
                print(f"Last page reached. Got {current_total} instead of {rows_per_page}")
                break

            total_available = data.get("message", {}).get("total-results", 0)
            print(f"Total collected: {len(all_items)} of {total_available} available")

    async def search_works(self, query_params: dict, max_results: int) -> List[Dict]:
        try:
            """Получить все результаты с пагинацией"""
            all_items = []
            params = query_params.copy()
            await self._search_per_page(all_items,
                            offset=0,
                            rows_per_page=min(1000, params.get('rows', 10)),
                            current_params=params,
                            max_results=max_results)

            return [self._normalize_item(item) for item in all_items]

        except httpx.HTTPError as e:
            print(f"[CrossrefClient] HTTP error: {e}")
            return []
        except Exception as e:
            print(f"[CrossrefClient] Unexpected error: {e}")
            return []

    @classmethod
    def normalize_items(cls, data: Dict) -> List[Dict]:
        """
        Основной метод для нормализации ответа от Crossref API.

        Args:
            data: Словарь с данными из Crossref API

        Returns:
            Список нормализованных словарей
        """
        items = data.get("message", {}).get("items", [])
        return [cls._normalize_item(item) for item in items if item]

    @classmethod
    def _normalize_item(cls, item: Dict) -> Dict:
        """
        Приводит данные Crossref к единому формату для нашего агрегатора.

        Args:
            item: Элемент из Crossref API

        Returns:
            Нормализованный словарь в том же формате, что и для OpenAlex
        """
        # Извлекаем DOI
        doi = item.get("DOI", "")

        # Извлекаем информацию о журнале
        container_title = item.get("container-title", [])
        publisher_info = item.get("publisher", "")

        # Извлекаем информацию о цитировании
        is_referenced_by_count = item.get("is-referenced-by-count", 0)

        # Извлекаем авторов
        authors = cls._extract_authors(item.get("author", []))

        # Извлекаем дату публикации
        publication_year = cls._extract_publication_year(item.get("published", {}))

        return {
            # Основная информация
            'id': f"https://doi.org/{doi}" if doi else "",
            'doi': doi,
            'title': " ".join(item.get("title", [])) if item.get("title") else "",
            'publication_year': publication_year,

            # Журнал
            'journal': container_title[0] if container_title else "",
            'journal_abbreviation': "",  # Crossref обычно не предоставляет сокращенное название
            'publisher': publisher_info,

            # Цитирование
            'cited_by_count': is_referenced_by_count,

            # Авторы
            'authors': authors,

            # Дополнительная информация
            'volume': item.get("volume", ""),
            'issue': item.get("issue", ""),
            'authors_count': len(item.get("author", [])),
            'url': item.get("URL", f"https://doi.org/{doi}" if doi else ""),
            'abstract': cls._extract_abstract(item)
        }

    @classmethod
    def _extract_authors(cls, authors_data: List[Dict]) -> List[Dict]:
        """
        Извлекает нормализованную информацию об авторах из Crossref.

        Crossref предоставляет авторов в формате:
        [
            {
                "given": "Имя",
                "family": "Фамилия",
                "affiliation": [...]
            },
            ...
        ]

        Args:
            authors_data: Список авторов из Crossref

        Returns:
            Список авторов в нормализованном формате
        """
        authors = []

        for author_data in authors_data:
            # Извлекаем информацию об аффилиации
            affiliation = ""
            country = ""
            ror_id = ""

            affiliations = author_data.get("affiliation", [])
            if affiliations:
                # Берем первую аффилиацию
                first_affiliation = affiliations[0]
                affiliation = first_affiliation.get("name", "")

                # Пытаемся извлечь страну (если доступно)
                if "country" in first_affiliation:
                    country = first_affiliation.get("country", "")

            # Создаем нормализованную запись автора
            author_info = {
                'id': "",  # Crossref не предоставляет ID авторов
                'name': f"{author_data.get('given', '')} {author_data.get('family', '')}".strip(),
                'surname': author_data.get("family", ""),
                'affiliation': affiliation,
                'country': country,
                'ror_id': ror_id  # Crossref не предоставляет ROR ID
            }
            authors.append(author_info)

        return authors

    @classmethod
    def _extract_publication_year(cls, published_data: Dict) -> int:
        """
        Извлекает год публикации из данных Crossref.

        Crossref предоставляет дату в формате:
        {
            "date-parts": [[2023, 10, 15]]
        }

        Args:
            published_data: Данные о дате публикации

        Returns:
            Год публикации или 0, если не удалось определить
        """
        date_parts = published_data.get("date-parts", [])
        if date_parts and len(date_parts) > 0 and len(date_parts[0]) > 0:
            return date_parts[0][0]
        return 0

    @classmethod
    def _extract_abstract(cls, item: Dict) -> str:
        """
        Извлекает аннотацию из данных Crossref.

        Crossref может предоставлять аннотацию в разных полях.

        Args:
            item: Элемент из Crossref

        Returns:
            Аннотация или пустая строка
        """
        # Пробуем разные возможные поля для аннотации
        abstract = item.get("abstract", "")

        # Если аннотация представлена как JATS XML
        if isinstance(abstract, dict) and "jats" in abstract:
            return abstract.get("jats", "")

        # Если это просто строка
        if isinstance(abstract, str):
            return abstract

        return ""

    async def close(self):
        await self.client.aclose()
