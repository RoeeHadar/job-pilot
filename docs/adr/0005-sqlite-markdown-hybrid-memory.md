# ADR 0005: SQLite + Markdown hybrid memory

## Status

Accepted

## Context

Local-first Memory needs queryable structure (jobs, matches, outreach) and human-readable artifacts (profile, dreams). Options: Markdown-only, SQLite-only, vector-DB-primary, or hybrid.

## Decision

**Hybrid:**
- **SQLite** — entities and events (jobs, matches, outreach status, fact records, IDs)
- **Markdown** under `memory/` — seeker profile, dream reports, ops log, contradictions
- **Embeddings index** — derived cache for RAG, rebuildable from SQLite + files

## Consequences

- Clear split: query/filter in SQL; narrative review in Markdown
- Backup = copy DB file + `memory/` folder
- Need a small sync convention so fact IDs in SQLite point at Markdown paths when both exist
- Vector store is optional acceleration, not canonical
