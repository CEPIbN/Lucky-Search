from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from fastapi import FastAPI, Query, HTTPException

app = FastAPI(
    title="Academic Search API",
    description="Расширенный поиск и анализ научных статей",
    version="1.0.0"
)


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


class JournalDisplayMode(str, Enum):
    FULL = "full"
    ABBREVIATION = "abbreviation"


class SearchRequest(BaseModel):
    # Основные параметры поиска
    query: str = Query(..., description="Поисковый запрос"),
    authors: Optional[str] = Field(None, description="Авторы (через запятую)")
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
    collaboration_countries: Optional[List[str]] = Field(None, max_items=4, description="Коллаборации стран (макс. 4)")

    # Параметры вывода
    show_authors: bool = Field(True, description="Показывать авторов")
    show_title: bool = Field(True, description="Показывать название статьи")
    show_year: bool = Field(True, description="Показывать год")
    show_journal: bool = Field(True, description="Показывать журнал")
    show_publisher: bool = Field(True, description="Показывать издателя")
    show_citations: bool = Field(True, description="Показывать цитирования")
    show_annual_citations: bool = Field(True, description="Показывать среднегодовые цитирования")
    show_volume: bool = Field(True, description="Показывать том")
    show_issue: bool = Field(True, description="Показывать выпуск")
    show_authors_count: bool = Field(True, description="Показывать число авторов")
    show_countries: bool = Field(True, description="Показывать страны")
    show_doi: bool = Field(True, description="Показывать DOI")

    journal_display: JournalDisplayMode = Field(JournalDisplayMode.FULL, description="Формат отображения журнала")

    # Сортировка
    sort_by: SortField = Field(SortField.YEAR, description="Поле для сортировки")
    sort_order: SortOrder = Field(SortOrder.DESC, description="Порядок сортировки")

    page: int = Field(1, ge=1, description="Номер страницы")
    page_size: int = Field(20, ge=1, le=100, description="Размер страницы")

    @field_validator('collaboration_countries')
    def validate_collaboration_countries(cls, v):
        if v and len(v) > 4:
            raise ValueError('Максимум 4 страны для коллаборации')
        return v

    @field_validator('year_to')
    def validate_year_range(cls, v, values):
        if 'year_from' in values and values['year_from'] and v:
            if v < values['year_from']:
                raise ValueError('Год "до" не может быть меньше года "от"')
        return v


class DOIAnalysisRequest(BaseModel):
    dois: List[str] = Field(..., min_items=1, description="Список DOI для анализа")


class Author(BaseModel):
    name: str
    surname: str
    affiliation: Optional[str]
    country: Optional[str]
    ror_id: Optional[str]


class CountryInfo(BaseModel):
    code: str
    name: str
    organizations: List[str]


class Article(BaseModel):
    id: str
    title: str
    authors: List[Author]
    year: int
    journal_full: str
    journal_abbreviation: str
    publisher: str
    citations: int
    annual_citations: float
    volume: Optional[str]
    issue: Optional[str]
    authors_count: int
    countries: List[CountryInfo]
    doi: str
    abstract: Optional[str]
    url: str

class CitationAnalysis(BaseModel):
    doi: str
    total_cited_articles: int
    citations_by_year: Dict[int, int]
    citations_by_journal: Dict[str, int]
    authors_frequency: Dict[str, int]


class DOIAnalysisResponse(BaseModel):
    analyses: List[CitationAnalysis]
    total_articles: int


class SearchResponse(BaseModel):
    request: SearchRequest
    articles: List[Article]
    total_results: int
    total_pages: int
    current_page: int
    page_size: int
    search_time_ms: float


@app.post("/search", response_model=SearchResponse, summary="Расширенный поиск статей")
async def search_articles(request: SearchRequest):
    """
    Расширенный поиск научных статей с фильтрацией по авторам, журналам, годам и другим параметрам.
    """
    # Валидация параметров
    if request.year_from and request.year_to and request.year_from > request.year_to:
        raise HTTPException(
            status_code=400,
            detail="Год 'от' не может быть больше года 'до'"
        )

    if (request.authors_number_min and request.authors_number_max and
            request.authors_number_min > request.authors_number_max):
        raise HTTPException(
            status_code=400,
            detail="Минимальное число авторов не может быть больше максимального"
        )

    mock_articles = [
        Article(
            id="10.1234/example.2023",
            title="Advanced Machine Learning Techniques in Healthcare",
            authors=[
                Author(
                    name="Ivan",
                    surname="Petrov",
                    affiliation="Moscow State University",
                    country="Russia",
                    ror_id="05gq02967"
                ),
                Author(
                    name="Wei",
                    surname="Zhang",
                    affiliation="Tsinghua University",
                    country="China",
                    ror_id="03n51xr89"
                )
            ],
            year=2023,
            journal_full="Journal of Artificial Intelligence Research",
            journal_abbreviation="JAIR",
            publisher="Springer",
            citations=45,
            annual_citations=15.0,
            volume="15",
            issue="2",
            authors_count=2,
            countries=[
                {"code": "RUS", "name": "Russia", "organizations": ["Moscow State University"]},
                {"code": "CHN", "name": "China", "organizations": ["Tsinghua University"]}
            ],
            doi="10.1234/example.2023",
            abstract="This paper presents novel machine learning approaches for healthcare applications...",
            url="https://dx.doi.org/10.1234/example.2023"
        )
    ]

    return SearchResponse(
        request=request,
        articles=mock_articles,
        total_results=1,
        total_pages=1,
        current_page=request.page,
        page_size=request.page_size,
        search_time_ms=52.1
    )


@app.post("/analyze/doi", response_model=DOIAnalysisResponse, summary="Анализ статей по DOI")
async def analyze_doi(request: DOIAnalysisRequest):
    """
    Анализ одной или нескольких статей по DOI с детальной статистикой цитирований.
    """
    analyses = []

    for doi in request.dois:
        analysis = CitationAnalysis(
            doi=doi,
            total_cited_articles=125,
            citations_by_year={
                2020: 15,
                2021: 28,
                2022: 42,
                2023: 40
            },
            citations_by_journal={
                "Nature": 12,
                "Science": 8,
                "IEEE Transactions": 25,
                "Journal of ML Research": 18
            },
            authors_frequency={
                "Smith": 8,
                "Johnson": 6,
                "Wang": 5,
                "Zhang": 4,
                "Ivanov": 3
            }
        )
        analyses.append(analysis)

    return DOIAnalysisResponse(
        analyses=analyses,
        total_articles=len(analyses)
    )