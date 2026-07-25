from __future__ import annotations

import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.db.session import Job, SeekerProfile, get_db
from app.services.gate import require_onboarding
from app.settings import get_settings

router = APIRouter(tags=["jobs"])


class ManualJobIn(BaseModel):
    """Secondary path: paste a JD. Title/company optional."""

    description: str = Field(..., min_length=20)
    title: str | None = None
    company: str | None = None
    location: str | None = "Israel"
    url: str | None = None


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    title: str
    company: str | None
    location: str | None
    url: str | None
    description: str
    match_score: float | None
    posted_at: datetime | None
    created_at: datetime

class FeedOut(BaseModel):
    mode: str  # ranked | newest
    jobs: list[JobOut]


def _can_personalize(settings) -> bool:
    baseline = settings.memory_dir / "rag" / "resume" / "baseline.md"
    if not baseline.exists():
        return False
    text = baseline.read_text(encoding="utf-8").strip()
    return len(text) >= 200


def _lexical_score(resume: str, job: Job) -> float:
    hay = f"{job.title} {job.company or ''} {job.description}".lower()
    tokens = {t for t in re.split(r"\W+", resume.lower()) if len(t) > 4}
    overlap = sum(1 for t in tokens if t in hay)
    return min(100.0, float(overlap) * 2.0)


def _guess_title(description: str) -> str:
    first = description.strip().splitlines()[0].strip()
    return (first[:120] if first else "Untitled role") or "Untitled role"


@router.get("/jobs/feed", response_model=FeedOut)
def jobs_feed(
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    """Best fits when possible; otherwise newest-first general jobs."""
    settings = get_settings()
    jobs = db.query(Job).all()
    if not jobs:
        return FeedOut(mode="newest", jobs=[])

    if _can_personalize(settings):
        resume = (
            settings.memory_dir / "rag" / "resume" / "baseline.md"
        ).read_text(encoding="utf-8")
        for j in jobs:
            j.match_score = _lexical_score(resume, j)
        db.commit()
        ranked = sorted(
            jobs,
            key=lambda j: (j.match_score or 0, j.posted_at or j.created_at),
            reverse=True,
        )
        return FeedOut(mode="ranked", jobs=ranked)

    newest = sorted(
        jobs,
        key=lambda j: j.posted_at or j.created_at,
        reverse=True,
    )
    return FeedOut(mode="newest", jobs=newest)


@router.post("/jobs", response_model=JobOut)
def create_manual_job(
    payload: ManualJobIn,
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    now = datetime.utcnow()
    job = Job(
        source="manual",
        title=(payload.title or _guess_title(payload.description)).strip(),
        company=payload.company,
        location=payload.location,
        url=payload.url,
        description=payload.description,
        posted_at=now,
        created_at=now,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    return db.query(Job).order_by(Job.created_at.desc()).all()
