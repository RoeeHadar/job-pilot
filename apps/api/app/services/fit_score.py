"""Local fit signals: lexical score, keyword gaps, heuristic Fit Rubric."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Common JD requirement tokens worth surfacing as gaps (len filter still applies).
_STOP = {
    "about",
    "above",
    "after",
    "again",
    "their",
    "there",
    "these",
    "those",
    "which",
    "would",
    "could",
    "should",
    "using",
    "years",
    "experience",
    "required",
    "requirements",
    "looking",
    "strong",
    "ability",
    "working",
    "team",
    "role",
    "position",
    "company",
    "israel",
    "remote",
}


@dataclass
class RubricDim:
    id: str
    label: str
    score: float  # 0–100
    citation: str


@dataclass
class FitSignals:
    local_score: float
    keyword_gaps: list[str]
    rubric: list[RubricDim]
    rubric_mode: str  # heuristic | llm
    advisory: dict[str, str]


def _tokens(text: str, min_len: int = 4) -> set[str]:
    return {
        t
        for t in re.split(r"\W+", text.lower())
        if len(t) >= min_len and t not in _STOP and not t.isdigit()
    }


def local_score(resume: str, title: str, company: str | None, description: str) -> float:
    hay = f"{title} {company or ''} {description}".lower()
    tokens = {t for t in re.split(r"\W+", resume.lower()) if len(t) > 4}
    overlap = sum(1 for t in tokens if t in hay)
    return min(100.0, float(overlap) * 2.0)


def keyword_gaps(resume: str, description: str, limit: int = 8) -> list[str]:
    """JD tokens absent from resume — lexical, no LLM."""
    resume_toks = _tokens(resume, min_len=4)
    jd_toks = _tokens(description, min_len=5)
    # Prefer longer / more distinctive tokens
    missing = sorted(jd_toks - resume_toks, key=lambda t: (-len(t), t))
    return missing[:limit]


def _has_any(hay: str, needles: list[str]) -> bool:
    return any(n in hay for n in needles)


def heuristic_rubric(
    resume: str,
    title: str,
    company: str | None,
    location: str | None,
    description: str,
) -> tuple[list[RubricDim], dict[str, str]]:
    """Five Fit Rubric dimensions from lexical cues (Local Score family)."""
    resume_l = resume.lower()
    jd_l = description.lower()
    loc_l = (location or "").lower()
    gaps = keyword_gaps(resume, description)
    score = local_score(resume, title, company, description)

    # 1. Hard requirements — overlap density vs gap pressure
    hard = max(0.0, min(100.0, score - len(gaps) * 4))
    hard_cite = (
        f"Lexical overlap {score:.0f}/100; {len(gaps)} JD terms weak/missing in resume."
        if gaps
        else f"Lexical overlap {score:.0f}/100; no strong JD term gaps detected."
    )

    # 2. Skills / experience evidence
    skill_hits = sum(
        1
        for s in (
            "python",
            "fastapi",
            "typescript",
            "react",
            "sql",
            "node",
            "java",
            "aws",
            "docker",
            "kubernetes",
            "postgres",
        )
        if s in jd_l and s in resume_l
    )
    skill_asks = sum(
        1
        for s in (
            "python",
            "fastapi",
            "typescript",
            "react",
            "sql",
            "node",
            "java",
            "aws",
            "docker",
            "kubernetes",
            "postgres",
        )
        if s in jd_l
    )
    skills = (
        min(100.0, (skill_hits / skill_asks) * 100.0)
        if skill_asks
        else min(100.0, score)
    )
    skills_cite = (
        f"{skill_hits}/{skill_asks} named stack terms from JD also appear in resume."
        if skill_asks
        else "JD has few named stack terms; used overall overlap."
    )

    # 3. Role / career alignment — title tokens in resume
    title_toks = _tokens(title, min_len=4)
    title_hits = sum(1 for t in title_toks if t in resume_l)
    role = (
        min(100.0, (title_hits / max(1, len(title_toks))) * 100.0)
        if title_toks
        else score
    )
    role_cite = (
        f"Title tokens in resume: {title_hits}/{len(title_toks) or 1} ({title or 'n/a'})."
    )

    # 4. Israel / location eligibility
    il_ok = _has_any(
        f"{loc_l} {jd_l}",
        [
            "israel",
            "tel aviv",
            "tel-aviv",
            "herzliya",
            "haifa",
            "jerusalem",
            "ramat",
            "remote",
            "hybrid",
        ],
    )
    remote_il = "remote" in f"{loc_l} {jd_l}" and (
        "israel" in f"{loc_l} {jd_l}" or "israeli" in jd_l
    )
    location_score = 90.0 if il_ok or remote_il else (40.0 if location else 55.0)
    loc_cite = (
        f"Location signal: {location or 'unspecified'}; "
        f"{'IL/remote-IL cues found' if il_ok or remote_il else 'weak IL eligibility cues'}."
    )

    # 5. Risks / missing information
    risk_penalties = 0
    risk_notes: list[str] = []
    if gaps:
        risk_penalties += min(40, len(gaps) * 5)
        risk_notes.append(f"gaps: {', '.join(gaps[:4])}")
    if len(description.strip()) < 80:
        risk_penalties += 25
        risk_notes.append("short JD")
    if not _has_any(jd_l, ["year", "senior", "junior", "mid"]):
        risk_penalties += 5
        risk_notes.append("level unclear")
    risks = max(0.0, 100.0 - risk_penalties)
    risks_cite = "; ".join(risk_notes) if risk_notes else "No major lexical risk flags."

    dims = [
        RubricDim("hard_requirements", "Hard requirements", hard, hard_cite),
        RubricDim("skills_evidence", "Skills & experience evidence", skills, skills_cite),
        RubricDim("role_alignment", "Role / career alignment", role, role_cite),
        RubricDim("israel_location", "Israel / location eligibility", location_score, loc_cite),
        RubricDim("risks_gaps", "Risks & missing information", risks, risks_cite),
    ]

    advisory: dict[str, str] = {}
    if _has_any(jd_l, ["salary", "₪", "nis", "compensation", "$"]):
        advisory["compensation"] = "Compensation mentioned in JD — verify before applying."
    else:
        advisory["compensation"] = "No reliable compensation data in JD (advisory only)."
    if _has_any(jd_l, ["culture", "values", "mission"]):
        advisory["culture"] = "Culture language present — skim for fit; not scored."
    else:
        advisory["culture"] = "Little culture signal in JD (advisory only)."

    return dims, advisory


def llm_available(openai_key: str | None, anthropic_key: str | None) -> bool:
    return bool((openai_key or "").strip() or (anthropic_key or "").strip())


def compute_fit(
    resume: str,
    title: str,
    company: str | None,
    location: str | None,
    description: str,
    *,
    has_llm_key: bool,
) -> FitSignals:
    """Hybrid: always local score + gaps + heuristic rubric.

    When an LLM key is present, rubric_mode is still 'heuristic' on the feed
    (fast path). Deep LLM rubric can be added later via a dedicated endpoint;
    llm_available is exposed on the feed for the UI.
    """
    score = local_score(resume, title, company, description)
    gaps = keyword_gaps(resume, description)
    dims, advisory = heuristic_rubric(resume, title, company, location, description)
    # Feed stays heuristic for cost/latency; key presence is signaled separately.
    _ = has_llm_key
    return FitSignals(
        local_score=score,
        keyword_gaps=gaps,
        rubric=dims,
        rubric_mode="heuristic",
        advisory=advisory,
    )
