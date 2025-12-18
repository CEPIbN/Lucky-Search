from typing import Dict, Any, List
from app.api.mappers.ParamMapper import ParamMapper


class CrossrefParamMapper(ParamMapper):
    """Модуль для сопоставления входящих параметров с параметрами Crossref API"""

    # Словарь маппинга: параметр_filters -> crossref_параметр
    FILTER_FIELD_MAPPING = {
        # Основные поля
        'authors': 'query.author',
        'journal_title': 'query.container-title',
        'article_title': 'query.title',
        'affiliation': 'query.affiliation',
        'collaboration_countries': 'query.publisher-location',
        #'authors_count': '_handle_authors_count',

        # Годы публикации
        'year_from': 'from-pub-date',
        'year_to': 'until-pub-date',

        # ISSN (раскомментируйте если нужно)
        # 'issn': 'issn',
    }

    # Параметры, передаваемые напрямую
    DIRECT_PARAMS = {
        'query': 'query',
        'page': 'offset',
        'page_size': 'rows'
    }

    # Специальные обработчики для сложных преобразований
    SPECIAL_HANDLERS = {
        #'collaboration_countries': 'query.publisher-location',
        #'year_from': '_handle_year_from',
        #'year_to': '_handle_year_to'
    }

    @classmethod
    def map_parameters(cls, user_params: Dict[str, Any]) -> Dict[str, Any]:
        user_params_copy = user_params.copy()
        """Основной метод преобразования параметров"""
        crossref_params = {'query': cls._build_query(user_params_copy)}
        # Обрабатываем query

        # Обрабатываем фильтры
        if 'filters' in user_params_copy and user_params_copy['filters']:
            cls._map_filters(user_params_copy['filters'], crossref_params)

        # Обрабатываем пагинацию
        if 'page' in user_params_copy and 'page_size' in user_params_copy:
            page = user_params_copy.get('page', 1)
            page_size = user_params_copy.get('page_size', 5)
            crossref_params['offset'] = (page - 1) * page_size
            crossref_params['rows'] = page_size

        # Устанавливаем сортировку по умолчанию (score для релевантности)
        crossref_params['sort'] = 'score'
        crossref_params['order'] = 'desc'

        return crossref_params

    @classmethod
    def _build_query(cls, user_params: Dict[str, Any]):
        # Собираем условия для разных типов полей
        conditions = []

        # 1. Основной запрос (ищем во всех полях)
        if query := user_params.get('query'):
            conditions.append(f'{query}')

        # 2. Поиск по полному тексту
        if fulltext := user_params.get('filters', {}).get('article_text'):
            # Для полного текста можно использовать разные стратегии
            conditions.append(f'({fulltext})')

        # 3. Поиск по аннотации
        if abstract := user_params.get('filters', {}).get('abstract'):
            # Добавляем как есть или с указанием поля
            conditions.append(f'({abstract})')

        # Объединяем все условия
        if conditions:
            # Используем логическое И между всеми полями
            return ' AND '.join(conditions)

    @classmethod
    def _map_filters(cls, filters_dict: Dict[str, Any], crossref_params: Dict[str, Any]) -> None:
        filters = []
        """Обработка фильтров"""
        for key, value in filters_dict.items():
            if value is None:
                continue

            # Проверяем наличие специального обработчика
            if key in cls.SPECIAL_HANDLERS:
                handler = getattr(cls, cls.SPECIAL_HANDLERS[key])
                handler(value, crossref_params)
            elif key in cls.FILTER_FIELD_MAPPING:
                crossref_key = cls.FILTER_FIELD_MAPPING[key]
                cls._add_filter(crossref_key, value, crossref_params, filters)

        if len(filters) > 0:
            crossref_params["filter"] = ','.join(filters)

    @classmethod
    def _add_filter(cls,
                    crossref_key: str,
                    value: Any,
                    params: Dict[str, Any],
                    filters: list):
        if 'date' in crossref_key:
            filter_result = cls._map_filter(crossref_key, value)
            if filter_result:
                filters.append(filter_result)

            return

        """Добавление фильтра в параметры"""
        if isinstance(value, list):
            # Для списков - добавляем каждый элемент отдельно
            for item in cls._map_list(value):
                if item:
                    params[crossref_key] = item

        elif isinstance(value, str):
            # Для строк с запятыми - разбиваем
            if ',' in value:
                items = cls._map_str(value)
                for item in items:
                    params[crossref_key] = item
            else:
                params[crossref_key] = value
        else:
            # Для других типов (int, float, etc.)
            params[crossref_key] = str(value)

    @classmethod
    def _handle_collaboration_countries(cls, countries: List[str], params: Dict[str, Any]) -> None:
        """Обработка стран коллаборации"""
        if not countries:
            return

        # Для Crossref можно фильтровать по стране аффилиации
        # Ограничиваем 4 странами как в требованиях
        for country in countries[:4]:
            if country and country.strip():
                params[cls.map_param('affiliation', cls.FILTER_FIELD_MAPPING)] = country.strip()

    @classmethod
    def _handle_authors_count(cls, authors_count: int, params: Dict[str, Any]) -> None:
        """Обработка количества авторов"""
        # Crossref не поддерживает прямой фильтр по количеству авторов
        # Можно добавить логику для post-filtering или использовать другую стратегию
        pass  # Пропускаем, так как в Crossref нет такого фильтра

# Дополнительный класс для сложных запросов с булевой логикой
class CrossrefAdvancedMapper(CrossrefParamMapper):
    """Расширенный маппер для поддержки сложных запросов Crossref"""

    @classmethod
    def map_parameters(cls, user_params: Dict[str, Any]) -> Dict[str, Any]:
        """Переопределенный метод для построения сложных query строк"""
        crossref_params = {}

        # Собираем все условия поиска
        query_parts = []

        # Основной запрос
        if 'query' in user_params and user_params['query']:
            query_parts.append(user_params['query'])

        # Фильтры для включения в query
        if 'filters' in user_params and user_params['filters']:
            query_parts.extend(cls._build_filter_queries(user_params['filters']))

        # Объединяем все части запроса
        if query_parts:
            crossref_params['query'] = ' '.join(query_parts)

        # Добавляем фильтры по датам отдельно
        if 'filters' in user_params and user_params['filters']:
            cls._add_date_filters(user_params['filters'], crossref_params)

        # Пагинация
        if 'page' in user_params and 'page_size' in user_params:
            page = user_params.get('page', 1)
            page_size = user_params.get('page_size', 5)
            crossref_params['offset'] = (page - 1) * page_size
            crossref_params['rows'] = page_size

        # Сортировка
        crossref_params['sort'] = 'score'
        crossref_params['order'] = 'desc'

        return crossref_params

    @classmethod
    def _build_filter_queries(cls, filters_dict: Dict[str, Any]) -> List[str]:
        """Построение частей query из фильтров"""
        queries = []

        for key, value in filters_dict.items():
            if value is None:
                continue

            if key == 'authors' and value:
                authors = [author.strip() for author in value.split(',') if author.strip()]
                for author in authors:
                    queries.append(f'author:"{author}"')

            elif key == 'journal_title' and value:
                queries.append(f'container-title:"{value}"')

            elif key == 'article_title' and value:
                queries.append(f'title:"{value}"')

            elif key == 'abstract' and value:
                queries.append(f'abstract:"{value}"')

            elif key == 'affiliation' and value:
                queries.append(f'affiliation:"{value}"')

        return queries

    @classmethod
    def _add_date_filters(cls, filters_dict: Dict[str, Any], params: Dict[str, Any]) -> None:
        """Добавление фильтров по дате"""
        if 'year_from' in filters_dict and filters_dict['year_from']:
            params['from-pub-date'] = f"{filters_dict['year_from']}-01-01"

        if 'year_to' in filters_dict and filters_dict['year_to']:
            params['until-pub-date'] = f"{filters_dict['year_to']}-12-31"


#filters = []
#CrossrefParamMapper.add_filter("until-pub-date", "1980", {}, filters)
#print(filters)