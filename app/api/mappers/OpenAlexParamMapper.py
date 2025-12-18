from typing import Dict, Any
from app.api.mappers.ParamMapper import ParamMapper

class OpenAlexParamMapper(ParamMapper):
    """Модуль для сопоставления входящих параметров с атрибутами OpenAlex и crossref API"""

    # Словарь маппинга: внешний_параметр -> openAlex_атрибут

    FILTER_FIELD_MAPPING = {
        # Основные поля поиска
        'article_title': 'title.search',
        'article_text': 'fulltext.search',
        'doi': 'doi',
        'abstract': 'abstract.search',

        # Авторы
        'author': 'authorships.author.display_name',
        'author_id': 'authorships.author.id',
        'authors_count': 'authors_count',

        # Организации
        'institution': 'authorships.institutions.display_name',
        'institution_id': 'authorships.institutions.id',
        'affiliation': 'authorships.institutions.display_name',
        'collaboration_countries': 'authorships.institutions.country_code',

        # Временные периоды
        'year': 'publication_year',
        'year_from': 'from_publication_date',
        'year_to': 'to_publication_date',
        'publication_year': 'publication_year',

        # Журналы/источники
        'journal_title': 'primary_location.source.host_organization',
        'journal_id': 'primary_location.source.id',
        'issn': 'primary_location.source.issn',
        'publisher': 'primary_location.source.host_organization.name',

        # Тематики
        'topic': 'topics.display_name.search',
        'concept': 'concepts.display_name.search',
        'field': 'concepts.display_name.search',
        'keyword': 'keywords.keyword.search',

        # Типы и статусы
        'type': 'type',
        'open_access': 'open_access.is_oa',
        'oa_status': 'open_access.oa_status',

        # Цитирования
        'citations': 'cited_by_count',
        'min_citations': 'cited_by_count:>',
        'max_citations': 'cited_by_count:<'
    }

    # Параметры, которые не требуют префикса filter=
    DIRECT_PARAMS = {
        'query': 'search',
        'sort': 'sort',
        'page': 'page',
        'page_size': 'per-page',
        'select': 'select',
        'cursor': 'cursor'
    }

    @classmethod
    def map_parameters(cls, user_params : Dict[str, Any]):
        """Основной метод преобразования параметров"""
        openalex_params = {}

        # Обрабатываем query
        if 'query' in user_params and user_params['query']:
            openalex_key = cls.map_param('query', cls.DIRECT_PARAMS)
            openalex_params[openalex_key] = user_params['query']

        # Фильтры
        if 'filters' in user_params and user_params['filters']:
            cls._map_filters(user_params['filters'], openalex_params)

        # Обрабатываем пагинацию
        if 'page' in user_params and 'page_size' in user_params:
            page = user_params.get('page', 1)
            per_page = min(user_params.get('page_size'), 200)
            openalex_params[cls.map_param('page', cls.DIRECT_PARAMS)] = page
            openalex_params[cls.map_param('page_size', cls.DIRECT_PARAMS)] = per_page

        return openalex_params

    @classmethod
    def _map_filters(cls, filters_dict: Dict[str, Any], openalex_params: Dict[str, Any]):
        filters = []
        for key, value in filters_dict.items():
            if value is None:
                continue

            if key in cls.FILTER_FIELD_MAPPING:
                map_key = cls.map_param(key, cls.FILTER_FIELD_MAPPING)
                filter_result = cls._map_filter(map_key, value)
                if filter_result:
                    filters.append(filter_result)

        if filters:
            openalex_params["filter"] = ','.join(filters)
