from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.settings import get_settings


class Base(DeclarativeBase):
    pass


class SeekerProfile(Base):
    """Singleton local profile (id=1)."""

    __tablename__ = "seeker_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    name: Mapped[str] = mapped_column(String(255), default="")
    title: Mapped[str] = mapped_column(String(255), default="")
    skills_notes: Mapped[str] = mapped_column(Text, default="")
    resume_stored_as: Mapped[str | None] = mapped_column(String(512), nullable=True)
    resume_filename: Mapped[str | None] = mapped_column(String(512), nullable=True)
    extraction_quality: Mapped[str | None] = mapped_column(String(32), nullable=True)
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="manual")
    title: Mapped[str] = mapped_column(String(512))
    company: Mapped[str | None] = mapped_column(String(512), nullable=True)
    location: Mapped[str | None] = mapped_column(String(512), nullable=True)
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    # Seeker feedback (P0.3)
    feedback: Mapped[str | None] = mapped_column(String(32), nullable=True)  # like|dislike|dismiss
    snoozed_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # Minimal apply progress (P0.4): saved|tailored|ready
    status: Mapped[str] = mapped_column(String(32), default="saved")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(64), default="job_match")
    title: Mapped[str] = mapped_column(String(512))
    body: Mapped[str] = mapped_column(Text, default="")
    job_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CvVariant(Base):
    __tablename__ = "cv_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(512), default="Tailored CV")
    content_md: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


_settings = get_settings()
engine = create_engine(
    _settings.resolved_database_url,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _seed_sample_jobs(db) -> None:
    if db.query(Job).count() > 0:
        return
    samples = [
        {
            "title": "Backend Engineer",
            "company": "Example Fintech IL",
            "location": "Tel Aviv",
            "description": (
                "Python or Node backend role. Build APIs, work with PostgreSQL, "
                "AWS. Hybrid Tel Aviv. Hebrew + English."
            ),
        },
        {
            "title": "Full Stack Developer",
            "company": "Example Startup",
            "location": "Remote (Israel)",
            "description": (
                "React + TypeScript frontend, Node/Python backend. Remote for "
                "Israeli developers. Product-minded team."
            ),
        },
        {
            "title": "Software Engineer",
            "company": "Example Enterprise",
            "location": "Herzliya",
            "description": (
                "Java or C# services, microservices, CI/CD. On-site Herzliya. "
                "3+ years experience."
            ),
        },
    ]
    now = datetime.utcnow()
    for i, s in enumerate(samples):
        db.add(
            Job(
                source="seed",
                title=s["title"],
                company=s["company"],
                location=s["location"],
                description=s["description"],
                posted_at=now,
                created_at=now,
            )
        )
    db.commit()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    # Lightweight SQLite column add for local-first MVP (no Alembic yet)
    with engine.begin() as conn:
        cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(jobs)").fetchall()}
        if "posted_at" not in cols:
            conn.exec_driver_sql("ALTER TABLE jobs ADD COLUMN posted_at DATETIME")
        if "feedback" not in cols:
            conn.exec_driver_sql("ALTER TABLE jobs ADD COLUMN feedback VARCHAR(32)")
        if "snoozed_until" not in cols:
            conn.exec_driver_sql("ALTER TABLE jobs ADD COLUMN snoozed_until DATETIME")
        if "status" not in cols:
            conn.exec_driver_sql(
                "ALTER TABLE jobs ADD COLUMN status VARCHAR(32) DEFAULT 'saved'"
            )
        tables = {
            row[0]
            for row in conn.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        if "seeker_profile" not in tables:
            Base.metadata.tables["seeker_profile"].create(bind=conn)

    db = SessionLocal()
    try:
        profile = db.get(SeekerProfile, 1)
        if not profile:
            db.add(SeekerProfile(id=1))
            db.commit()
        _seed_sample_jobs(db)
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_profile(db) -> SeekerProfile:
    profile = db.get(SeekerProfile, 1)
    if not profile:
        profile = SeekerProfile(id=1)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile
