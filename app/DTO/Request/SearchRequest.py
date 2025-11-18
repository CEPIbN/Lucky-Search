from datetime import datetime
from enum import Enum
from typing import Optional, List

from fastapi import Query
from pydantic import BaseModel, Field, field_validator

class SearchField(str, Enum):
    TITLE = "title"
    JOURNAL = "journal"
    AUTHORS = "authors"
    ENTIRE_TEXT = "entire_text"
    ABSTRACT = "abstract"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class SortField(str, Enum):
    AUTHORS = "authors"
    TITLE = "title"
    YEAR = "year"
    CITATIONS = "citations"
    ANNUAL_CITATIONS = "annual_citations"
    VOLUME = "volume"
    ISSUE = "issue"
    AUTHORS_COUNT = "authors_count"

class SearchRequest(BaseModel):
    # Основные параметры поиска
    query: str = Query(..., description="Поисковый запрос"),
    authors: Optional[str] = Query(None, description="Авторы (через запятую)")
    journal_title: Optional[str] = Field(None, description="Название журнала")
    issn: Optional[str] = Field(None, description="ISSN журнала")
    article_title: Optional[str] = Field(None, description="Название статьи")
    article_text: Optional[str] = Field(None, description="Поиск по всему тексту")

    # Диапазон годов
    year_from: Optional[int] = Field(None, ge=1900, le=datetime.now().year, description="Год от")
    year_to: Optional[int] = Field(None, ge=1900, le=datetime.now().year, description="Год до")

    # Дополнительные фильтры
    abstract: Optional[str] = Field(None, description="Аннотация")
    authors_number_min: Optional[int] = Field(None, ge=1, description="Минимальное число авторов")
    authors_number_max: Optional[int] = Field(None, ge=1, description="Максимальное число авторов")
    affiliation: Optional[str] = Field(None, description="Аффилиация")
    collaboration_countries: Optional[List[str]] = Field(default=[], max_length=4, description="Коллаборации стран (макс. 4)")

    # Флаг отображения параметров вывода
    show_params: bool = Field(False, description="Показывать авторов")

    # Сортировка
    sort_by: SortField = Field(SortField.YEAR, description="Поле для сортировки")
    sort_order: SortOrder = Field(SortOrder.DESC, description="Порядок сортировки")

    page: int = Field(1, ge=1, description="Номер страницы")
    page_size: int = Field(20, ge=1, le=100, description="Размер страницы")

    @field_validator('collaboration_countries')
    def validate_collaboration_countries(self, v):
        if v and len(v) > 4:
            raise ValueError('Максимум 4 страны для коллаборации')
        return v

    @field_validator('year_to')
    def validate_year_range(self, v, values):
        if 'year_from' in values and values['year_from'] and v:
            if v < values['year_from']:
                raise ValueError('Год "до" не может быть меньше года "от"')
        return v
