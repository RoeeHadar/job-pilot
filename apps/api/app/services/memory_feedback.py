"""Append seeker job feedback into local Memory markdown."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def record_job_feedback(
    memory_dir: Path,
    *,
    job_id: int,
    title: str,
    company: str | None,
    action: str,
    detail: str = "",
) -> None:
    fits = memory_dir / "rag" / "fits"
    fits.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    slug = action.replace(" ", "-")
    path = fits / f"{stamp}-{slug}-job-{job_id}.md"
    body = (
        f"# Job feedback: {action}\n\n"
        f"- job_id: {job_id}\n"
        f"- title: {title}\n"
        f"- company: {company or 'n/a'}\n"
        f"- action: {action}\n"
        f"- at: {stamp}\n"
    )
    if detail:
        body += f"- detail: {detail}\n"
    path.write_text(body, encoding="utf-8")

    log = memory_dir / "log.md"
    line = f"- {stamp} · feedback `{action}` · job {job_id} · {title}\n"
    if log.exists():
        log.write_text(log.read_text(encoding="utf-8") + line, encoding="utf-8")
    else:
        log.write_text("# Memory log\n\n" + line, encoding="utf-8")
