from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import main_router, search_router
import os

app = FastAPI()
app.include_router(main_router.router)
app.include_router(search_router.search_router)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="front"), name="static")