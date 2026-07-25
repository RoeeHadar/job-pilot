from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import SeekerProfile, get_db, get_or_create_profile
from app.services.resume_parser import extract_text_from_file
from app.settings import get_settings

router = APIRouter(tags=["onboarding"])


class ProfileOut(BaseModel):
    name: str
    title: str
    skills_notes: str
    resume_filename: str | None
    extraction_quality: str | None
    onboarding_complete: bool
    has_baseline_resume: bool


class ProfileUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    skills_notes: str = ""


class ResumeUploadOut(BaseModel):
    ok: bool
    filename: str
    extraction_quality: str
    needs_review: bool
    message: str


class CompleteOut(BaseModel):
    onboarding_complete: bool
    profile: ProfileOut


def _profile_out(profile: SeekerProfile, settings) -> ProfileOut:
    baseline = settings.memory_dir / "rag" / "resume" / "baseline.md"
    return ProfileOut(
        name=profile.name,
        title=profile.title,
        skills_notes=profile.skills_notes or "",
        resume_filename=profile.resume_filename,
        extraction_quality=profile.extraction_quality,
        onboarding_complete=profile.onboarding_complete,
        has_baseline_resume=baseline.exists() and baseline.stat().st_size > 0,
    )


def _sync_markdown_profile(profile: SeekerProfile, resume_excerpt: str = "") -> None:
    settings = get_settings()
    path = settings.memory_dir / "profiles" / "seeker.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    body = f"""# Seeker profile

## Name

{profile.name or "_TBD_"}

## Current title

{profile.title or "_TBD_"}

## Constraints

- Market: Israel + remote-for-IL only

## Skills notes

{profile.skills_notes or "_TBD_"}

## Baseline resume (extracted)

{resume_excerpt[:12000] if resume_excerpt else "_See memory/rag/resume/baseline.md_"}
"""
    path.write_text(body, encoding="utf-8")


@router.get("/onboarding/status", response_model=ProfileOut)
def onboarding_status(db: Session = Depends(get_db)):
    settings = get_settings()
    profile = get_or_create_profile(db)
    return _profile_out(profile, settings)


@router.put("/onboarding/profile", response_model=ProfileOut)
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db)):
    settings = get_settings()
    profile = get_or_create_profile(db)
    profile.name = payload.name.strip()
    profile.title = payload.title.strip()
    profile.skills_notes = payload.skills_notes.strip()
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    baseline = settings.memory_dir / "rag" / "resume" / "baseline.md"
    excerpt = baseline.read_text(encoding="utf-8") if baseline.exists() else ""
    _sync_markdown_profile(profile, excerpt)
    return _profile_out(profile, settings)


@router.post("/onboarding/resume", response_model=ResumeUploadOut)
async def upload_baseline_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    profile = get_or_create_profile(db)
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    suffix = Path(file.filename).suffix.lower() or ".bin"
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    dest = settings.resume_originals_dir / stored_name
    dest.write_bytes(await file.read())

    text, quality = extract_text_from_file(dest)
    needs_review = quality != "high" or len(text) < 200

    extracted_path = settings.memory_dir / "rag" / "resume" / "baseline.md"
    extracted_path.parent.mkdir(parents=True, exist_ok=True)
    extracted_path.write_text(text or "", encoding="utf-8")

    profile.resume_stored_as = stored_name
    profile.resume_filename = file.filename
    profile.extraction_quality = quality
    profile.updated_at = datetime.utcnow()
    db.commit()

    _sync_markdown_profile(profile, text or "")

    return ResumeUploadOut(
        ok=True,
        filename=file.filename,
        extraction_quality=quality,
        needs_review=needs_review,
        message="Resume loaded successfully."
        if not needs_review
        else "Resume loaded — please review a few details.",
    )


@router.post("/onboarding/complete", response_model=CompleteOut)
def complete_onboarding(db: Session = Depends(get_db)):
    settings = get_settings()
    profile = get_or_create_profile(db)
    if not profile.name.strip() or not profile.title.strip():
        raise HTTPException(status_code=400, detail="Name and title are required")
    baseline = settings.memory_dir / "rag" / "resume" / "baseline.md"
    if not baseline.exists() or baseline.stat().st_size == 0:
        raise HTTPException(status_code=400, detail="Upload a resume first")

    profile.onboarding_complete = True
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    excerpt = baseline.read_text(encoding="utf-8")
    _sync_markdown_profile(profile, excerpt)
    return CompleteOut(
        onboarding_complete=True,
        profile=_profile_out(profile, settings),
    )
