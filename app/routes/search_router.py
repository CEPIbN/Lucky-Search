from enum import Enum
from typing import List, Dict
from pydantic import BaseModel, Field
from fastapi import HTTPException, APIRouter

from app.DTO.Request.SearchRequest import SearchRequest
from app.DTO.Response.SearchResponse import SearchResponse, Article, Author

search_router = APIRouter()

class JournalDisplayMode(str, Enum):
    FULL = "full"
    ABBREVIATION = "abbreviation"

class DOIAnalysisRequest(BaseModel):
    dois: List[str] = Field(default=[], min_length=1, description="Список DOI для анализа")

class CitationAnalysis(BaseModel):
    doi: str
    total_cited_articles: int
    citations_by_year: Dict[int, int]
    citations_by_journal: Dict[str, int]
    authors_frequency: Dict[str, int]

class DOIAnalysisResponse(BaseModel):
    analyses: List[CitationAnalysis]
    total_articles: int

@search_router.post("/search", response_model=SearchResponse, summary="Расширенный поиск статей")
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

@search_router.post("/analyze/doi", response_model=DOIAnalysisResponse, summary="Анализ статей по DOI")
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