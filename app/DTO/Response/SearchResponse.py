from typing import List, Optional

from pydantic import BaseModel

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
    doi: Optional[str]
    abstract: Optional[str]
    url: Optional[str]

class SearchResponse(BaseModel):
    #request: SearchRequest
    articles: List[Article]
    total_results: int
    total_pages: int
    current_page: int
    page_size: int
    search_time_ms: float