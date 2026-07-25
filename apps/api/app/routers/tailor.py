from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import CvVariant, Job, SeekerProfile, get_db
from app.services.docx_export import markdown_to_docx_bytes
from app.services.gate import require_onboarding
from app.settings import get_settings

router = APIRouter(tags=["tailor"])


class TailorRequest(BaseModel):
    job_description: str = Field(..., min_length=20)
    job_id: int | None = None
    title: str | None = None
    company: str | None = None
    run_crew: bool = False


class TailorResult(BaseModel):
    id: int
    content_md: str
    mode: str


@router.post("/tailor", response_model=TailorResult)
def tailor_cv(
    payload: TailorRequest,
    db: Session = Depends(get_db),
    profile: SeekerProfile = Depends(require_onboarding),
):
    settings = get_settings()
    resume_path = settings.memory_dir / "rag" / "resume" / "baseline.md"
    profile_path = settings.memory_dir / "profiles" / "seeker.md"
    if not resume_path.exists() or resume_path.stat().st_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Baseline resume missing — complete onboarding.",
        )

    job = None
    if payload.job_id:
        job = db.get(Job, payload.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

    description = payload.job_description.strip()
    title = (payload.title or (job.title if job else "") or "Role").strip()
    company = (payload.company or (job.company if job else "") or "").strip()

    resume = resume_path.read_text(encoding="utf-8")
    seeker_profile = (
        profile_path.read_text(encoding="utf-8") if profile_path.exists() else ""
    )

    if payload.run_crew:
        crew_src = Path(__file__).resolve().parents[2] / "job_pilot" / "src"
        if str(crew_src) not in sys.path:
            sys.path.insert(0, str(crew_src))
        from job_pilot.main import run_flow

        state = run_flow(
            {
                "mode": "tailor",
                "resume_text": resume,
                "seeker_profile": seeker_profile,
                "job_description": description,
                "job_title": title,
                "company": company,
            }
        )
        content = state.tailored_cv
        mode = "crew"
    else:
        # Stub still grounded in baseline resume (truth source)
        heading = f"{title}" + (f" @ {company}" if company else "")
        content = (
            f"# Tailored CV — {heading}\n\n"
            f"**Candidate:** {profile.name} · {profile.title}\n\n"
            f"## Role focus (from JD)\n{description[:1200]}\n\n"
            f"## Experience & skills (from your baseline resume — edit, do not invent)\n"
            f"{resume[:6000]}\n"
        )
        mode = "stub"

    variant = CvVariant(
        job_id=job.id if job else None,
        title=f"{title} — tailored",
        content_md=content,
    )
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return TailorResult(id=variant.id, content_md=variant.content_md, mode=mode)


@router.get("/tailor/{variant_id}/docx")
def export_docx(
    variant_id: int,
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    variant = db.get(CvVariant, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="CV variant not found")
    data = markdown_to_docx_bytes(variant.content_md, title=variant.title)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="job-pilot-cv-{variant_id}.docx"'
        },
    )


@router.get("/tailor/{variant_id}")
def get_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    variant = db.get(CvVariant, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="CV variant not found")
    return {
        "id": variant.id,
        "title": variant.title,
        "content_md": variant.content_md,
        "job_id": variant.job_id,
    }
