from fastapi import APIRouter
import asyncio

from starlette.responses import JSONResponse

from app.api.searching_service import main

router = APIRouter(prefix="/api/v1/search")

@router.post("/{query}")
async def search(query : str):
    asyncio.run(main(query))
    return JSONResponse(status_code=200, content="I'm fine")