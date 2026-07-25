"""Draft Outreach Pack from JD + Memory — never auto-sends."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import Job, SeekerProfile, get_db
from app.services.gate import require_onboarding
from app.settings import get_settings

router = APIRouter(tags=["outreach"])


class OutreachPackOut(BaseModel):
    job_id: int
    short_pitch: str
    linkedin_note: str
    cold_email_subject: str
    cold_email_body: str
    disclaimer: str = "Draft only — review and send yourself. Job Pilot never auto-sends."


def _clip_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).strip() + "…"


def _first_skill_line(resume: str) -> str:
    for line in resume.splitlines():
        clean = line.strip(" #-*")
        if len(clean) > 40:
            return clean[:160]
    return "relevant engineering experience"


@router.post("/jobs/{job_id}/outreach-pack", response_model=OutreachPackOut)
def outreach_pack(
    job_id: int,
    db: Session = Depends(get_db),
    profile: SeekerProfile = Depends(require_onboarding),
):
    settings = get_settings()
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume_path = settings.memory_dir / "rag" / "resume" / "baseline.md"
    proof = _first_skill_line(
        resume_path.read_text(encoding="utf-8") if resume_path.exists() else ""
    )
    name = profile.name or "a developer"
    title = profile.title or "Software Engineer"
    company = job.company or "your team"
    role = job.title

    # Pull a concrete JD cue (first meaningful sentence fragment)
    jd_cue = re.split(r"[.\n]", job.description.strip())[0].strip()[:90] or role

    short_pitch = _clip_words(
        f"{name}, {title}. Fit for {role} at {company}: {proof}. Happy to share a tailored CV.",
        55,
    )
    linkedin_note = _clip_words(
        f"Hi — saw the {role} role at {company}. {jd_cue}. "
        f"I bring {proof}. Open to a quick chat?",
        70,
    )
    subject = f"{title} interested in {role} at {company}"
    body = (
        f"Hi,\n\n"
        f"I'm {name}, a {title} focused on Israel-market roles. "
        f"Your {role} posting stood out ({jd_cue}).\n\n"
        f"Recent proof: {proof}\n\n"
        f"I can share a tailored CV if useful. Thanks for your time.\n\n"
        f"{name}\n"
    )

    return OutreachPackOut(
        job_id=job.id,
        short_pitch=short_pitch,
        linkedin_note=linkedin_note,
        cold_email_subject=subject,
        cold_email_body=body,
    )
