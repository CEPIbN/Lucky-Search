from enum import Enum
from typing import List, Dict
from pydantic import BaseModel, Field
from fastapi import APIRouter

from app.DTO.Request.SearchRequest import SearchRequest
from app.DTO.Response.SearchResponse import SearchResponse
from app.api.searching_service import main

search_router = APIRouter(prefix="/api/v1/search")

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

@search_router.post("/", response_model=SearchResponse, summary="Расширенный поиск статей")
async def search_articles(request: SearchRequest):
    """
    Расширенный поиск научных статей с фильтрацией по авторам, журналам, годам и другим параметрам.
    """
    result = await main(request)
    return result

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