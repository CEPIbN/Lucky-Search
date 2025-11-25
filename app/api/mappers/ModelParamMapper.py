from app.DTO.Request.SearchRequest import SearchRequest

class ModelParamsMapper:
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
    def map_parameters(cls, user_params):
        openalex_params = dict()
        for key, value in user_params.items():
            if key == "filters":
                cls.map_filters(value, openalex_params)
            else:
                openalex_params[cls.DIRECT_PARAMS.get(key)] = value

        return openalex_params

    @classmethod
    def map_from_model(cls, model_instance: SearchRequest):
        params = model_instance.model_dump(exclude_none=True, mode='json')
        print(params.get("filters", {}))
        return cls.map_parameters(params)

    @classmethod
    def map_filter(cls, key: str, filter_value):
        if key not in cls.FILTER_FIELD_MAPPING:
            return None

        if key.startswith("year"):
            filters = [cls.map_date(key, int(filter_value))]

        # Обрабатываем список (например, collaboration_countries)
        elif isinstance(filter_value, list):
            # Фильтруем пустые значения
            filters = [item.strip() for item in filter_value if item and item.strip()]
            # Если список пустой, возвращаем пустую строку
            if not filters:
                return ""

        # Обрабатываем строку (стандартный случай)
        elif isinstance(filter_value, str):
            # Фильтруем пустые значения
            filters = [item.strip() for item in filter_value.split(',') if item and item.strip()]
            # Если список пустой, возвращаем пустую строку
            if not filters:
                return ""

        # Обрабатываем другие типы (числа и т.д.)
        else:
            # Проверяем, что значение не None
            if filter_value is None:
                return ""
            filters = [str(filter_value)]
            
        return f"{cls.FILTER_FIELD_MAPPING.get(key)}:{'|'.join(filters)}"

    @classmethod
    def map_date(cls , key: str, year: int):
        if key.endswith("from"):
            return f"{year}-01-01"
        return f"{year}-12-31"

    @classmethod
    def map_filters(cls, filters_dict: dict, openalex_params: dict):
        filters = []
        for key, value in filters_dict.items():
            filter_result = cls.map_filter(key, value)
            if filter_result:
                filters.append(filter_result)

        if filters:
            openalex_params["filter"] = ','.join(filters)
