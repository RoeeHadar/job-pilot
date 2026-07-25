# ADR 0014: PDF-first resume onboarding with fallback review

## Status

Accepted

## Context

Most Seekers have PDF resumes; some have Word; a minority bring other or awkward formats. Onboarding must not fail hard on parse quality.

## Decision

- Primary parse target: **PDF**
- Secondary: **DOCX**
- Other uploads: store original bytes; best-effort text extraction
- Weak extraction → guided in-app profile completion (edit structured Memory)
- Always retain original file blob; extracted profile is editable

## Consequences

- PDF/DOCX parsers on the API (e.g. pypdf / python-docx); optional OCR later for scans
- `data/` or `memory/rag/resume/originals/` for blobs
- Onboarding UX: upload → preview extraction → confirm/edit → ready for match/CV
- Export of tailored CV remains DOCX (ADR 0009); baseline input is PDF-heavy
