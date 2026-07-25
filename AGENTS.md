# Job Pilot — agent brief

Israel-first job-finding OS for developers: match roles, tailor CVs, draft recruiter/network outreach, and run a memory + dreaming loop. AI and scrapers are **bring-your-own-key** — no free site-provided models.

## Skills installed

| Skill | Role |
|-------|------|
| `ponytail` | YAGNI / anti-overengineering |
| CrewAI pack (`getting-started`, `design-agent`, `design-task`, `ask-docs`) | Multi-agent crew patterns |
| `grill-with-docs` + `grilling` + `domain-modeling` | Sharpen design + glossary/ADRs |
| `design-taste-frontend` (Taste) | Distinctive UI |
| `skill-creator` | Author new skills |
| `mcp-builder` | Build MCP servers |
| `task-decomposer` + `planning-and-task-breakdown` | Break work into tasks |
| `find-skills` | Discover more skills |
| `job-pilot-memory` | Persistent memory + RAG |
| `job-pilot-dreaming` | Opportunity synthesis cycles |

Skills live in `.agents/skills/`. Local `.cursor/skills/` mirrors are ignored to
avoid committing duplicate copies.

## Memory

Canonical store: `memory/` (see `job-pilot-memory`). Dream outputs: `memory/dreams/`.

## MCP

Job platforms: `.cursor/mcp.json` → Apify (`apify-jobs`) with Israeli boards + Google Jobs + LinkedIn jobs Actors.

Research notes: `docs/research/job-platform-mcps.md`.

Connect Apify in Cursor Settings → MCP (OAuth or Bearer token). Obsidian MCP is optional and currently errored if misconfigured — do not block on it; `memory/` is source of truth.

## Domain docs

- Glossary: `CONTEXT.md` (created during grill-with-docs)
- Decisions: `docs/adr/`

## Hard product constraints

1. Market: Israel + remote open to Israeli developers only
2. BYO AI keys only
3. No auto-send outreach without user confirmation
4. Prefer MCP Actors over custom scrapers

## App runtime

- API: `apps/api` — `uvicorn app.main:app --reload --port 8000`
- Web: `apps/web` — `npm run dev`
- Details: root `README.md`
