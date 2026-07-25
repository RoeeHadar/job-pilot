# Job Pilot — project description

**Job Pilot** is a local-first job-finding OS for developers targeting the **Israel market** (including remote roles open to Israeli candidates). It matches roles to your profile, helps tailor CVs without inventing experience, drafts outreach you still send yourself, and keeps a durable Memory of what you like and what the market looks like.

Repository: https://github.com/RoeeHadar/job-pilot

---

## Why it exists

Cloud job tools often push volume apply, store your resume on someone else’s servers, and ignore Israel-specific boards and bilingual (EN/HE) realities. Job Pilot runs on your machine, uses **bring-your-own** AI and Apify keys, and never auto-sends messages.

## What it does today

| Area | Behavior |
|------|----------|
| **Onboarding** | Local profile gate: name, title, baseline resume → Memory. Jobs/Tailor/Alerts blocked until complete. |
| **Jobs** | Suggested feed ranked against your resume (Local Score). Newest-first if personalization isn’t ready. Manual JD paste supported. |
| **Fit Rubric** | Five dimensions with citations: hard requirements, skills/evidence, role alignment, Israel/location, risks/gaps. Keyword gaps listed per role. |
| **Feedback** | Like, dislike, snooze (5 days), dismiss — written into Memory under `memory/rag/fits/` and `memory/log.md`. |
| **Tailor CV** | JD-only input; grounded in baseline resume + Memory. Reviewer gate blocks invented experience. Editable markdown + DOCX export. |
| **Job status** | Minimal progress: `saved` → `tailored` → `ready` (Qualified Application). No Kanban CRM yet. |
| **Outreach Pack** | Short pitch, LinkedIn note, cold email drafts from a Jobs card. Draft only — you send. |
| **Alerts** | In-app inbox (demo + matched signals path). |
| **Privacy** | Resume, profile, SQLite, `.env` keys, and dream outputs stay local and gitignored. |

## Hard product constraints

1. Market: Israel + remote open to Israeli developers only  
2. BYO AI / Apify keys only — no free shared models  
3. No auto-send outreach  
4. Prefer MCP/Apify Actors over custom scrapers  

## Architecture

```text
apps/web     Vite + React UI (default http://127.0.0.1:5190)
apps/api     FastAPI + SQLite + CrewAI scaffolding
memory/      Markdown Memory (profiles, resume baseline, fits, dreams)
data/        Local SQLite (gitignored)
docs/adr/    Architecture Decision Records
.agents/     Agent skills (memory, dreaming, CrewAI, etc.)
```

- **API:** `uvicorn app.main:app --reload --port 8000` from `apps/api`  
- **Web:** `npm run dev` from `apps/web` (port **5190**)  
- Domain language: `CONTEXT.md`  
- Decisions: `docs/adr/` (through **0020** for post-research P0 scope)

## Recent enhancement slice (P0)

Locked in ADR 0020 after competitive research (`docs/research/competitive-landscape-enhancements.md`):

1. Fit Rubric + keyword gaps on Jobs  
2. Tailor reviewer gate (no invented bullets)  
3. Snooze / like / dismiss → Memory  
4. Minimal job status + Outreach Pack on Jobs  

**Out of scope for this slice:** Kanban application tracker, bundled Application Pack on every Tailor, direct Greenhouse/Ashby/Lever scans, mass Easy Apply.

**Success metric:** time from onboarding complete to first **Qualified Application** (reviewed tailored CV marked ready).

## How to run

See root `README.md` for setup, env vars, and tests.

```powershell
# API
cd apps/api
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\pip install -e .\job_pilot
Copy-Item .env.example .env   # add your keys
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Web
cd apps/web
npm install
npm run dev -- --host 127.0.0.1 --port 5190
```

## How to test

```powershell
cd apps/api
.\.venv\Scripts\python -m unittest discover -s tests -v

cd ../web
npm run build
npm run lint
npm run test:e2e
```

## What is next (post-P0)

- Application Pack as a separate explicit action (cover letter / interview / ATS answers)  
- Full application tracker (Kanban) when quality signal is strong enough  
- Deeper IL board coverage via Apify; optional ATS portal scans later  
- Dreaming cycles proposing *when* to use Outreach Packs  
- Optional LLM overlay on Fit Rubric when keys are set (feed stays fast/heuristic today)

## License & contributions

Public repo on GitHub. Do not commit personal resumes, `.env` secrets, or live SQLite databases. Prefer ADRs for product decisions that are hard to reverse.
