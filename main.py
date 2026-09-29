from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path

from database import create_tables
from routes import router

app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="Generate general fitness plans using Gemini AI",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent

app.include_router(router)


@app.on_event("startup")
def startup():
    create_tables()


@app.get("/static/style.css")
def get_stylesheet():
    return FileResponse(BASE_DIR / "style.css", media_type="text/css")


@app.get("/health")
def health():
    return {"status": "ok"}