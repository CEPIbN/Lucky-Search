from fastapi import APIRouter

from fastapi.params import Query
from starlette.responses import JSONResponse

from app.api.searching_service import main, crossref_search

router = APIRouter(prefix="/api/v1/search")

@router.post("/")
async def search(query : str = Query(), title : str = Query(), rows : int = Query(default=5)):
    params = {
        'title': title
    }
    results = await main(query, params, rows)
    return JSONResponse(status_code=200, content=results)