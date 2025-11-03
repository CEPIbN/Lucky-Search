from fastapi import FastAPI
from app.routes import main_router, search_router

app = FastAPI()
app.include_router(main_router.router)
app.include_router(search_router.router)