
class ModelParamsMapper:
    """Модуль для сопоставления входящих параметров с атрибутами OpenAlex и crossref API"""

    # Словарь маппинга: внешний_параметр -> openAlex_атрибут

    FIELD_MAPPING = {
        # Основные поля поиска
        'title': 'title_and_abstract.search',
        'full_text': 'fulltext.search',
        'doi': 'doi',
        'orcid': 'authorships.author.orcid',

        # Авторы
        'author': 'authorships.author.display_name.search',
        'author_id': 'authorships.author.id',
        'author_name': 'authorships.author.display_name.search',

        # Организации
        'institution': 'authorships.institutions.display_name.search',
        'institution_id': 'authorships.institutions.id',
        'affiliation': 'authorships.institutions.display_name.search',
        'country': 'authorships.institutions.country_code',

        # Временные периоды
        'year': 'publication_year',
        'from_year': 'from_publication_date',
        'to_year': 'to_publication_date',
        'publication_year': 'publication_year',

        # Журналы/источники
        'journal': 'primary_location.source.display_name.search',
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
            if user_key in cls.FIELD_MAPPING:
                filter_str.append(f"{cls.FIELD_MAPPING.get(user_key)}:{value}")
            elif user_key in cls.DIRECT_PARAMS:
                openalex_params[user_key] = value

        return openalex_params

    @classmethod
    def map_from_model(cls, model_instance):
        # Получаем словарь, исключая None значения
        if hasattr(model_instance, 'model_dump'):
            user_params = model_instance.model_dump(exclude_none=True)
        else:
            user_params = model_instance.dict(exclude_none=True)

        user_params["search"] = user_params.get("query")
        return cls.map_parameters(user_params)