from typing import Dict
import time

from app.DTO.Request.SearchRequest import SearchRequest
from app.DTO.Response.SearchResponse import SearchResponse, Article, Author, CountryInfo
from app.api.clients.crossref_client import CrossrefClient
from app.api.clients.openAlex_client import OpenAlexClient
from app.api.mappers.ModelParamMapper import ModelParamsMapper


async def main(request: SearchRequest) -> SearchResponse:
    start_time = time.time()
    openalex_results = await open_alex_search(request)
    #crossref_results = await crossref_search(request)
    
    # Преобразуем результаты в формат Article
    articles = [_normalize_article(item) for item in openalex_results]
    
    # Рассчитываем время выполнения
    search_time_ms = (time.time() - start_time) * 1000
    
    # Создаем объект ответа
    response = SearchResponse(
        articles=articles,
        total_results=len(articles),
        total_pages=1,  # Для простоты предполагаем 1 страницу
        current_page=request.page,
        page_size=request.page_size,
        search_time_ms=search_time_ms
    )
    
    return response

async def open_alex_search(request: SearchRequest):
    map_params = ModelParamsMapper.map_from_model(request)
    client = OpenAlexClient()
    results = await client.search_works(map_params)
    await client.close()
    return results

async def crossref_search(query:str, params:dict[str, str], rows: int):
    map_params = get_params(params.copy())
    map_params.update({"query": query})
    map_params.update({"rows": rows})
    client = CrossrefClient()
    results = await client.search_works(map_params)
    await client.close()
    return results

def get_filters(filters: Dict[str, str]):
    if filters:
        filter_parts = []
        for field, value in filters.items():
            print(f"{field}:{value}")
            filter_parts.append(f"{field}:{value}")
        return ",".join(filter_parts)

def get_params(params: dict[str, str]) -> dict[str, object]:
    return { f"query.{key}": value for key, value in params.items() }

def _normalize_article(item: Dict) -> Article:
    """Преобразует данные из OpenAlex в формат Article"""
    # Преобразуем авторов
    authors = []
    for author_data in item.get("authors", []):
        # Разделяем имя и фамилию (если возможно)
        name_parts = author_data.get("name", "").split()
        surname = name_parts[-1] if name_parts else ""
        name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else author_data.get("name", "")
        
        authors.append(Author(
            name=name,
            surname=surname,
            affiliation=author_data.get("affiliation"),
            country=author_data.get("country"),
            ror_id=author_data.get("ror_id")
        ))
    
    # Преобразуем страны
    countries = []
    country_codes = set()
    for author_data in item.get("authors", []):
        country_code = author_data.get("country")
        if country_code and country_code not in country_codes:
            country_codes.add(country_code)
            # Преобразуем код страны в полное название (упрощенная версия)
            country_names = {
                "RU": "Russia",
                "US": "United States",
                "CN": "China",
                "GB": "United Kingdom",
                "DE": "Germany",
                "FR": "France",
                "JP": "Japan"
            }
            countries.append(CountryInfo(
                code=country_code,
                name=country_names.get(country_code, country_code),
                organizations=[author_data.get("affiliation", "")] if author_data.get("affiliation") else []
            ))
    
    return Article(
        id=item.get("id", ""),
        title=item.get("title", "Без названия"),
        authors=authors,
        year=item.get("publication_year", 0),
        journal_full=item.get("journal", ""),
        journal_abbreviation=item.get("journal_abbreviation", ""),
        publisher=item.get("publisher", ""),
        citations=item.get("cited_by_count", 0),
        annual_citations=0.0,  # Упрощенная версия
        volume=item.get("volume"),
        issue=item.get("issue"),
        authors_count=item.get("authors_count", 0),
        countries=countries,
        doi=item.get("doi", ""),
        abstract=item.get("abstract", ""),
        url=item.get("url", "")
    )
