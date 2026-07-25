from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.db.session import Job, SeekerProfile, get_db
from app.services.fit_score import compute_fit, llm_available
from app.services.gate import require_onboarding
from app.services.memory_feedback import record_job_feedback
from app.settings import get_settings

router = APIRouter(tags=["jobs"])


class ManualJobIn(BaseModel):
    """Secondary path: paste a JD. Title/company optional."""

    description: str = Field(..., min_length=20)
    title: str | None = None
    company: str | None = None
    location: str | None = "Israel"
    url: str | None = None


class RubricDimOut(BaseModel):
    id: str
    label: str
    score: float
    citation: str


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
    keyword_gaps: list[str] = Field(default_factory=list)
    rubric: list[RubricDimOut] | None = None
    rubric_mode: str | None = None
    advisory: dict[str, str] | None = None
    feedback: str | None = None
    snoozed_until: datetime | None = None
    status: str = "saved"


class FeedOut(BaseModel):
    mode: str  # ranked | newest
    llm_available: bool = False
    jobs: list[JobOut]


class FeedbackIn(BaseModel):
    action: str  # like | dislike | dismiss | snooze | clear
    snooze_days: int | None = 5


class StatusIn(BaseModel):
    status: str  # saved | tailored | ready


def _can_personalize(settings) -> bool:
    baseline = settings.memory_dir / "rag" / "resume" / "baseline.md"
    if not baseline.exists():
        return False
    text = baseline.read_text(encoding="utf-8").strip()
    return len(text) >= 200


def _guess_title(description: str) -> str:
    first = description.strip().splitlines()[0].strip()
    return (first[:120] if first else "Untitled role") or "Untitled role"


def _visible(job: Job, now: datetime) -> bool:
    if job.feedback == "dismiss":
        return False
    if job.snoozed_until and job.snoozed_until > now:
        return False
    return True


def _job_out(job: Job, *, resume: str | None, has_llm: bool) -> JobOut:
    base = JobOut.model_validate(job)
    if not resume:
        return base
    signals = compute_fit(
        resume,
        job.title,
        job.company,
        job.location,
        job.description,
        has_llm_key=has_llm,
    )
    return base.model_copy(
        update={
            "match_score": signals.local_score,
            "keyword_gaps": signals.keyword_gaps,
            "rubric": [
                RubricDimOut(
                    id=d.id, label=d.label, score=d.score, citation=d.citation
                )
                for d in signals.rubric
            ],
            "rubric_mode": signals.rubric_mode,
            "advisory": signals.advisory,
        }
    )


@router.get("/jobs/feed", response_model=FeedOut)
def jobs_feed(
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    """Best fits when possible; otherwise newest-first general jobs."""
    settings = get_settings()
    has_llm = llm_available(settings.openai_api_key, settings.anthropic_api_key)
    now = datetime.utcnow()
    jobs = [j for j in db.query(Job).all() if _visible(j, now)]
    if not jobs:
        return FeedOut(mode="newest", llm_available=has_llm, jobs=[])

    if _can_personalize(settings):
        resume = (
            settings.memory_dir / "rag" / "resume" / "baseline.md"
        ).read_text(encoding="utf-8")
        outs: list[JobOut] = []
        for j in jobs:
            out = _job_out(j, resume=resume, has_llm=has_llm)
            j.match_score = out.match_score
            outs.append(out)
        db.commit()
        ranked = sorted(
            outs,
            key=lambda j: (j.match_score or 0, j.posted_at or j.created_at),
            reverse=True,
        )
        return FeedOut(mode="ranked", llm_available=has_llm, jobs=ranked)

    newest = sorted(
        jobs,
        key=lambda j: j.posted_at or j.created_at,
        reverse=True,
    )
    return FeedOut(
        mode="newest",
        llm_available=has_llm,
        jobs=[_job_out(j, resume=None, has_llm=has_llm) for j in newest],
    )


@router.post("/jobs", response_model=JobOut)
def create_manual_job(
    payload: ManualJobIn,
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    settings = get_settings()
    has_llm = llm_available(settings.openai_api_key, settings.anthropic_api_key)
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
        status="saved",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    resume = None
    if _can_personalize(settings):
        resume = (
            settings.memory_dir / "rag" / "resume" / "baseline.md"
        ).read_text(encoding="utf-8")
    return _job_out(job, resume=resume, has_llm=has_llm)


@router.post("/jobs/{job_id}/feedback", response_model=JobOut)
def job_feedback(
    job_id: int,
    payload: FeedbackIn,
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    settings = get_settings()
    has_llm = llm_available(settings.openai_api_key, settings.anthropic_api_key)
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    action = payload.action.strip().lower()
    if action not in {"like", "dislike", "dismiss", "snooze", "clear"}:
        raise HTTPException(status_code=400, detail="Invalid feedback action")

    detail = ""
    if action == "clear":
        job.feedback = None
        job.snoozed_until = None
    elif action == "snooze":
        days = payload.snooze_days if payload.snooze_days in (2, 5, 10) else 5
        job.snoozed_until = datetime.utcnow() + timedelta(days=days)
        detail = f"{days} days"
    else:
        job.feedback = action
        if action == "dismiss":
            job.snoozed_until = None

    db.commit()
    db.refresh(job)
    record_job_feedback(
        settings.memory_dir,
        job_id=job.id,
        title=job.title,
        company=job.company,
        action=action,
        detail=detail,
    )
    resume = None
    if _can_personalize(settings):
        resume = (
            settings.memory_dir / "rag" / "resume" / "baseline.md"
        ).read_text(encoding="utf-8")
    return _job_out(job, resume=resume, has_llm=has_llm)


@router.post("/jobs/{job_id}/status", response_model=JobOut)
def set_job_status(
    job_id: int,
    payload: StatusIn,
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    settings = get_settings()
    has_llm = llm_available(settings.openai_api_key, settings.anthropic_api_key)
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    status = payload.status.strip().lower()
    if status not in {"saved", "tailored", "ready"}:
        raise HTTPException(status_code=400, detail="Invalid status")
    job.status = status
    db.commit()
    db.refresh(job)
    resume = None
    if _can_personalize(settings):
        resume = (
            settings.memory_dir / "rag" / "resume" / "baseline.md"
        ).read_text(encoding="utf-8")
    return _job_out(job, resume=resume, has_llm=has_llm)


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    settings = get_settings()
    has_llm = llm_available(settings.openai_api_key, settings.anthropic_api_key)
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    resume = None
    if _can_personalize(settings):
        resume = (
            settings.memory_dir / "rag" / "resume" / "baseline.md"
        ).read_text(encoding="utf-8")
    return _job_out(job, resume=resume, has_llm=has_llm)


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    settings = get_settings()
    has_llm = llm_available(settings.openai_api_key, settings.anthropic_api_key)
    resume = None
    if _can_personalize(settings):
        resume = (
            settings.memory_dir / "rag" / "resume" / "baseline.md"
        ).read_text(encoding="utf-8")
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return [_job_out(j, resume=resume, has_llm=has_llm) for j in jobs]
