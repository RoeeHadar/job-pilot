# ADR 0006: MVP loop is ingest-match-rank then CV tailor

## Status

Accepted

## Context

Product vision includes dreaming and outreach, but v1 needs a narrow vertical slice.

## Decision

MVP delivers:
1. **Ingest → Match → Rank** — Israel-scoped jobs into SQLite, scored against Memory, shortlist in UI
2. **Tailor CV** — for a selected job, produce an optimized resume variant from Memory/RAG

Dreaming and message drafting are explicitly **post-MVP**.

## Consequences

- First CrewAI crews focus on matching and CV adaptation, not outreach
- Job ingest adapters (Apify/etc.) are on the critical path
- Dreaming skill remains available for agent workflows, but the app UI can hide it until ready
