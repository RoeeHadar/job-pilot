"""Ground tailored CV content in the baseline resume — no invented experience."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


_ALLOW = {
    "tailored",
    "candidate",
    "experience",
    "skills",
    "baseline",
    "resume",
    "focus",
    "description",
    "optional",
    "required",
    "memory",
    "hebrew",
    "english",
    "israel",
    "remote",
    "hybrid",
}


@dataclass
class ReviewResult:
    ok: bool
    issues: list[str] = field(default_factory=list)
    content_md: str = ""


def _tokens(text: str) -> set[str]:
    return {
        t
        for t in re.split(r"\W+", text.lower())
        if len(t) >= 5 and t not in _ALLOW and not t.isdigit()
    }


def review_cv(baseline: str, content_md: str, job_description: str = "") -> ReviewResult:
    """Flag experience tokens in the tailored CV that appear in neither baseline nor JD.

    Soft gate: warn and, when inventiveness is high, rewrite to a grounded stub
    so we never ship fabricated bullets as the saved variant.
    """
    # Only audit the experience block when present; else whole doc minus JD focus.
    experience = content_md
    m = re.search(
        r"## Experience & skills.*?\n(.*)$",
        content_md,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m:
        experience = m.group(1)

    base_toks = _tokens(baseline)
    jd_toks = _tokens(job_description)
    allowed = base_toks | jd_toks | _ALLOW
    novel = sorted(t for t in _tokens(experience) if t not in allowed)

    issues: list[str] = []
    if novel:
        preview = ", ".join(novel[:8])
        issues.append(
            f"Possible invented terms not in baseline/JD: {preview}"
            + ("…" if len(novel) > 8 else "")
        )

    # High novelty → replace experience section with baseline only
    if len(novel) >= 6:
        issues.append(
            "Reviewer rewrote CV to baseline-only experience (blocked invented content)."
        )
        heading_match = re.search(r"^# .+$", content_md, re.MULTILINE)
        heading = heading_match.group(0) if heading_match else "# Tailored CV"
        candidate_match = re.search(r"\*\*Candidate:\*\*.+", content_md)
        candidate = candidate_match.group(0) if candidate_match else ""
        jd_block = ""
        jd_m = re.search(
            r"(## Role focus \(from JD\)\n.*?)(?=\n## |\Z)",
            content_md,
            flags=re.DOTALL,
        )
        if jd_m:
            jd_block = jd_m.group(1).strip() + "\n\n"
        safe = (
            f"{heading}\n\n"
            f"{candidate}\n\n"
            f"{jd_block}"
            f"## Experience & skills (from your baseline resume — edit, do not invent)\n"
            f"{baseline[:6000]}\n\n"
            f"> Reviewer note: removed unverified claims ({', '.join(novel[:6])}).\n"
        )
        return ReviewResult(ok=False, issues=issues, content_md=safe)

    return ReviewResult(
        ok=len(issues) == 0,
        issues=issues,
        content_md=content_md,
    )
