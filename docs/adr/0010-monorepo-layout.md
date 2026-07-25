# ADR 0010: Monorepo apps/web + apps/api with colocated CrewAI

## Status

Accepted

## Context

Local-first stack needs a clear place for Vite UI, FastAPI, CrewAI flows/crews, SQLite, and Markdown memory.

## Decision

Monorepo layout:

```
apps/web
apps/api          # includes job_pilot/flows, job_pilot/crews (+ crew.jsonc as needed)
memory/
data/
packages/shared   # optional
```

Root keeps `.agents/skills/`, `docs/`, `AGENTS.md`, `CONTEXT.md`.

## Consequences

- Root scripts (or just docs) to run API + web together
- Python package lives under `apps/api`; Node app under `apps/web`
- `data/*.sqlite` gitignored; schema migrations owned by API
- Shared OpenAPI → TS client can land in `packages/shared` when needed
