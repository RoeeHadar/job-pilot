# ADR 0009: In-app CV edit plus DOCX export

## Status

Accepted

## Context

CV tailor must produce something usable for Israeli applications and still support iteration.

## Decision

- Working format: structured/Markdown content editable in the UI
- Primary export: **DOCX**
- PDF export deferred

## Consequences

- Need a DOCX generation library on the Python side (or a small export service)
- Store CV variants in SQLite + optional Markdown snapshots under `memory/rag/resume/`
- ATS-friendly simple layout over fancy design in v1
