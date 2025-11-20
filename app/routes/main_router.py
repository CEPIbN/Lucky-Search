from pathlib import Path

from fastapi import APIRouter
from starlette.responses import HTMLResponse

router = APIRouter()

# Путь к папке с HTML файлами на уровень выше
ROUTE_DIR = Path(__file__).parent
APP_DIR = ROUTE_DIR.parent
PROJECT_ROOT = APP_DIR.parent
HTML_DIR = PROJECT_ROOT / "front"
@router.get("/", response_class=HTMLResponse)
async def root():
    #return {"message": "Hello, I'm Lucky-Search Service! See you later"}
    html_file = HTML_DIR / "index.html"
    return HTMLResponse(content=html_file.read_text(encoding="utf-8"))