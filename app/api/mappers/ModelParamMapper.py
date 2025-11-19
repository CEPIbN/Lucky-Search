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
        'author': 'authorships.author.display_name.search',
        'author_id': 'authorships.author.id',
        'authors_count': 'authorships.author.works_count.search',

        # Организации
        'institution': 'authorships.institutions.display_name',
        'institution_id': 'authorships.institutions.id',
        'affiliation': 'authorships.institutions.display_name.search',
        'collaboration_countries': 'authorships.institutions.country_code',

        # Временные периоды
        'year': 'publication_year',
        'from_year': 'from_publication_date',
        'to_year': 'to_publication_date',
        'publication_year': 'publication_year',

        # Журналы/источники
        'journal_title': 'primary_location.source.display_name',
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
    DIRECT_PARAMS = ['search', 'sort', 'page', 'per-page', 'select', 'cursor']

    @classmethod
    def map_parameters(cls, user_params):
        openalex_params = dict()
        filter_str = []
        for user_key, value in user_params.items():
            if user_key in cls.FILTER_FIELD_MAPPING:
                filter_str.append(cls.map_filter(user_key, value))
            elif user_key in cls.DIRECT_PARAMS:
                openalex_params[user_key] = value

        openalex_params["filter"] = ','.join(filter_str)
        return openalex_params

    @classmethod
    def map_from_model(cls, model_instance: SearchRequest):
        user_params = model_instance.model_dump(exclude_none=True)
        user_params["search"] = user_params.get("query")
        return cls.map_parameters(user_params)

    @classmethod
    def map_filter(cls, key: str, filter_str: str):
        if key.endswith("year"):
            filter_str = cls.map_date(key, int(filter_str))
        filters = [item.strip()
                   for item in filter_str.split(',')
                   if item.strip()]
        return f"{cls.FILTER_FIELD_MAPPING.get(key)}:{'|'.join(filters)}"

    @classmethod
    def map_date(cls , key: str, year: int):
        if key.startswith("from"):
            return f"{year}-01-01"
        return f"{year}-12-31"

