"""Job Pilot local FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import init_db
from app.routers import alerts, health, jobs, onboarding, outreach, tailor
from app.settings import get_settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.resume_originals_dir.mkdir(parents=True, exist_ok=True)
    init_db()
    yield


app = FastAPI(
    title="Job Pilot API",
    version="0.1.0",
    description="Local-first Israel job matching + CV tailor API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5190",
        "http://127.0.0.1:5190",
        "http://localhost:5191",
        "http://127.0.0.1:5191",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(onboarding.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(outreach.router, prefix="/api")
app.include_router(tailor.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
