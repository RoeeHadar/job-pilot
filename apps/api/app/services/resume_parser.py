from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader
from docx import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".rtf", ".odt"}


def extract_text_from_file(path: Path) -> tuple[str, str]:
    """
    Returns (extracted_text, quality) where quality is high|medium|low.
    """
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        parts = [(page.extract_text() or "") for page in reader.pages]
        text = "\n".join(parts).strip()
        quality = "high" if len(text) > 200 else "low"
        return text, quality

    if suffix == ".docx":
        doc = Document(str(path))
        text = "\n".join(p.text for p in doc.paragraphs).strip()
        quality = "high" if len(text) > 200 else "medium"
        return text, quality

    if suffix in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        quality = "high" if text else "low"
        return text, quality

    # Other formats: best-effort binary decode
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="ignore").strip()
    quality = "low"
    return text, quality


def write_seeker_profile(memory_dir: Path, resume_text: str) -> Path:
    profile = memory_dir / "profiles" / "seeker.md"
    profile.parent.mkdir(parents=True, exist_ok=True)
    body = f"""# Seeker profile

## Goals

_TBD_

## Constraints

- Market: Israel + remote-for-IL only

## Stack & strengths

_Extracted from baseline resume — review and edit._

## Baseline resume (extracted)

{resume_text[:12000]}
"""
    profile.write_text(body, encoding="utf-8")
    return profile
