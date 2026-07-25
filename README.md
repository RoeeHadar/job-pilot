# Job Pilot

Local-first job discovery and CV tailoring for developers seeking work in
Israel, including remote roles open to Israeli candidates.

## Current MVP

- Local onboarding: name, current title, and baseline resume
- PDF-first resume extraction with DOCX/text fallback
- Resume-backed Memory stored on the user's machine
- Suggested jobs ranked against the baseline resume (Local Score)
- Fit Rubric (five dimensions + citations) and keyword gaps on Jobs
- Like / dislike / snooze / dismiss feedback written into Memory
- Newest-first fallback when personalization is unavailable
- JD-only CV tailoring with a reviewer gate against invented experience
- Editable tailored CV with DOCX export
- Minimal job status: saved → tailored → ready
- Outreach Pack drafts (pitch / LinkedIn note / email) — never auto-sent
- In-app alerts
- English/Hebrew-ready product structure

The app never auto-sends outreach. AI and job-data providers use keys supplied
by the user.

Full project narrative: [`docs/PROJECT.md`](docs/PROJECT.md).
Competitive research and P0 decisions: [`docs/research/competitive-landscape-enhancements.md`](docs/research/competitive-landscape-enhancements.md), ADR [`0020`](docs/adr/0020-post-research-enhancement-scope.md).

## Repository

```text
apps/web          Vite + React UI
apps/api          FastAPI API and local SQLite storage
apps/api/job_pilot
                  CrewAI Flow and crews
memory/           Local Markdown Memory structure
data/             Local SQLite database (ignored by Git)
docs/adr/         Product and architecture decisions
.agents/skills/   Project agent skills
```

`CONTEXT.md` defines the product language. `docs/adr/` records the decisions
behind the current architecture.

## Privacy

Resume files, extracted resume text, seeker profiles, dream outputs, API keys,
and SQLite databases are ignored by Git. Only empty Memory directory
placeholders and non-personal configuration are committed.

Before pushing, keep real values only in `.env`; start from `.env.example`.

## Requirements

- Python 3.11+
- Node.js 20+
- Microsoft Edge for local Playwright tests (CI uses Chromium)
- Optional: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `APIFY_TOKEN`

## Setup

### API

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\pip install -e .\job_pilot
Copy-Item .env.example .env
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

If the local Python installation has a certificate-chain problem, add
`--trusted-host pypi.org --trusted-host files.pythonhosted.org` to the pip
commands.

API docs: http://127.0.0.1:8000/docs

### Web

```powershell
cd apps/web
npm install
npm run dev -- --host 127.0.0.1 --port 5190
```

App: http://127.0.0.1:5190

## Tests

```powershell
# API integration flow (isolated temp DB and Memory)
cd apps/api
.\.venv\Scripts\python -m unittest discover -s tests -v

# Frontend checks and full browser journey
cd ../web
npm run build
npm run lint
npm audit --omit=dev
npm run test:e2e
```

The E2E test covers onboarding, route gating, synthetic resume upload, suggested
jobs, fit rubric, outreach pack, dismiss feedback, manual JD import, Tailor
prefill/generation, mark ready, DOCX download, alerts, console errors, API
errors, and a mobile viewport. It uses temporary data and does not touch the
user's local resume or profile.

## Provider configuration

Copy `.env.example` to `.env` and add only the providers you want. Without LLM
keys, the current MVP uses deterministic/lexical behavior so the core product
flow remains testable.

Apify MCP setup and researched job sources are documented in
`docs/research/job-platform-mcps.md`.

## Current limitations

- Automated Apify ingestion and scheduled alerts are scaffolded but not yet
  connected to the UI.
- LinkedIn HR-post monitoring is phase 2.
- Tailoring defaults to deterministic mode until the UI enables the configured
  CrewAI provider.
