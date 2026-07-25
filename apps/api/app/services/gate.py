from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SeekerProfile, get_db, get_or_create_profile


def require_onboarding(db: Session = Depends(get_db)) -> SeekerProfile:
    profile = get_or_create_profile(db)
    if not profile.onboarding_complete:
        raise HTTPException(
            status_code=403,
            detail="Complete onboarding first (name, title, resume).",
        )
    return profile
