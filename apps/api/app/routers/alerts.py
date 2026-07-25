from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.db.session import Alert, SeekerProfile, get_db
from app.services.gate import require_onboarding

router = APIRouter(tags=["alerts"])


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    title: str
    body: str
    job_id: int | None
    read: bool

@router.get("/alerts", response_model=list[AlertOut])
def list_alerts(
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    return db.query(Alert).order_by(Alert.id.desc()).limit(100).all()


@router.post("/alerts/{alert_id}/read", response_model=AlertOut)
def mark_read(
    alert_id: int,
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.read = True
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/alerts/demo", response_model=AlertOut)
def create_demo_alert(
    db: Session = Depends(get_db),
    _profile: SeekerProfile = Depends(require_onboarding),
):
    """Placeholder until Apify scheduler lands."""
    alert = Alert(
        kind="job_match",
        title="Demo: new matching role",
        body="Scheduler not running yet — this is a sample inbox item.",
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
