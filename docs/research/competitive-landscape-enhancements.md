# Competitive landscape & enhancement ideas

Research date: 2026-07-25  
Scope: open-source job-search / CV-tailoring systems and commercial analogues, mapped to Job Pilot’s locked constraints (Israel market, local-first, BYO keys, no auto-send).

This doc answers: what exists, what we should take (copy / inspire / ignore), and how to integrate without abandoning ADRs.

---

## 1. How Job Pilot sits today

| Capability | Job Pilot MVP |
|---|---|
| Surface | Local Vite+React web app + FastAPI |
| Onboarding | Profile gate (name, title, resume → Memory) |
| Jobs | Apify ingest + match vs Memory; newest-first fallback |
| Tailor | JD-only; baseline CV + Memory as truth; DOCX export |
| Alerts | In-app inbox |
| Outreach / Dreaming | Skills + Memory; no auto-send |
| Market | Israel + remote open to IL |
| Differentiator | Memory + Dreaming loop; Israel-first; CrewAI Flows; bilingual EN/HE |

Peers cluster into three shapes:

1. **CLI / agent-skill kits** (Claude Code, Codex) — markdown skills + local files  
2. **Local web apps** (FastAPI/Svelte/Next + SQLite) — closest stack cousins  
3. **Cloud SaaS** (Teal, Huntr, Simplify, LazyApply) — trackers + autofill / mass apply  

Job Pilot is intentionally in cluster 2, with Memory/Dreaming closer to agent OS ideas than to Teal.

---

## 2. Open-source projects surveyed

### 2.1 career-ops (santifer / career-ops.org)

- **Shape:** CLI-agnostic agent skills; local Markdown/YAML; Go TUI pipeline  
- **License:** MIT (copy-friendly for ideas and patterns; do not vendor their brand)  
- **Standouts:**
  - Published **5-dimension fit rubric** (match, north-star, comp, culture, red flags) → 1.0–5.0 with CV-line citations  
  - **Human-in-the-loop apply:** drafts Greenhouse/Ashby/Lever answers; never clicks Submit  
  - **Zero-token portal scan** of 150+ Greenhouse/Ashby/Lever career pages  
  - Explicit anti–mass-apply stance (aligned with Job Pilot)  
- **Take:** **Inspire hard** on rubric transparency and ATS form Q&A drafts. Portal scan is valuable but US/EU-company skewed — adapt for IL employers on those ATS hosts.  
- **Ignore:** Replacing our web UI with CLI-only; abandoning CrewAI for skill files as the only UX.

### 2.2 MadsLorentzen/ai-job-search (~24k★)

- **Shape:** Claude Code fork-your-profile framework; LaTeX CV/cover letter  
- **License:** MIT  
- **Standouts:**
  - Country-agnostic core + **swappable local job-board skills** (built for Denmark — same pattern Job Pilot needs for IL)  
  - **Drafter → reviewer** pipeline for CV/cover letter quality  
  - Interview prep + salary benchmarking optional paths  
  - Proven funnel narrative (applications → interviews → offer)  
- **Take:** **Inspire** — reviewer pass on tailored CVs; market-specific scrape skills as a pattern for AllJobs / Drushim / LinkedIn IL via Apify.  
- **Ignore:** LaTeX-as-primary export (we ship DOCX); requiring Claude Code as runtime.

### 2.3 srbhr/Resume-Matcher (~28k★)

- **Shape:** Local harness for master resume → per-JD tailor, cover letter, interview prep, PDF templates; 100+ LLMs including Ollama  
- **License:** Apache-2.0  
- **Standouts:** Master-resume model; multi-provider LLM; layout/templates; interview prep grounded in tailored resume  
- **Take:** **Inspire** — explicit “master resume” UX language (maps to our baseline + Memory); optional Ollama; cover-letter + interview-prep as post-tailor packs.  
- **Ignore:** Competing as a general resume designer; pulling in their full template marketplace.

### 2.4 ApplyKit (wihlarkop/applykit)

- **Shape:** Local SvelteKit + FastAPI + SQLite + LiteLLM; BYOK / Ollama  
- **License:** check repo before copying code (treat as inspire until verified)  
- **Standouts:** Fit score + keyword gaps → tailored CV → cover letter → **Kanban tracker**; JD URL ingest; multi-profile  
- **Take:** **Inspire** — application Kanban stages; URL→JD fetch; keyword-gap panel next to fit score. Stack is almost identical to ours.  
- **Ignore:** Multi-user SaaS mode; “Smart Apply” that blurs into auto-submit.

### 2.5 Career-Seek (iamadarsha/Career-Seek)

- **Shape:** Local Next.js command center; SQLite; JobSpy + Playwright; optional AI keys  
- **License:** MIT  
- **Standouts:**
  - Works **without** LLM for TF-IDF / deterministic scoring  
  - **3-format outreach pack** (short pitch / LinkedIn note / cold email) in one click  
  - Feedback signals (👍/👎), snooze, deduped multi-board scan  
  - One-command installer (heavy: Redis, Meilisearch, Chromium)  
- **Take:** **Copy pattern (MIT)** — outreach pack shapes; snooze/dismiss on job cards; offline-capable scoring fallback when no LLM key.  
- **Ignore:** Their full installer stack and India-centric boards as defaults.

### 2.6 job-hunt-os (alexmonegrop)

- **Shape:** Rules + skills + Python tools + NocoDB; Claude Code OS  
- **Standouts:** Cold outreach / warm follow-up / meeting prep skills; shared DB hygiene; regional config  
- **Take:** **Inspire** — skill naming and session checkpoints map to our `job-pilot-dreaming` / memory skills.  
- **Ignore:** NocoDB dependency; Chrome LinkedIn automation as core path.

### 2.7 PunithVT/career-ops (web fork lineage)

- **Shape:** Self-hosted multi-user Node web app; Claude evaluation; portal scan; LinkedIn outreach drafts; rejection pattern analysis  
- **Take:** **Inspire** — rejection/outcome analytics feeding Memory; follow-up cadence.  
- **Ignore:** Multi-tenant hosted positioning; AWS-first packaging for MVP.

### 2.8 HireForge (profitelai/hireforge)

- **Shape:** FastAPI + Svelte; ATS CV; Kanban; Greenhouse/Lever/Ashby URL scrape; Ollama  
- **Take:** **Inspire** — URL scrape for ATS hosts; LinkedIn About/headline optimizer as optional Memory export.  
- **Ignore:** Multi-user SaaS architecture for v1.

### 2.9 CrewAI resume crews (tonykipkemboi, tezansahu/ai-garage, unikill066, Prernapaliwal21, drukpa1455)

- **Shape:** Small CrewAI demos — JD analyst → matcher → rewrite → interview/cover letter  
- **Take:** **Already aligned** — validate our Flow step boundaries against common agent splits (Analyst / Matcher / Strategist / Interview). Prefer structured JSON outputs + reviewer gate over more agents.  
- **Ignore:** Streamlit UIs; GitHub profile scraping as required input.

### 2.10 Claude LinkedIn assistants / ATS shell skills

- Examples: FarzamHejaziK/claude-linkedin-assistant, nishilbhave/ats-resume-tailor  
- **Take:** **Inspire** — batch outreach with single confirmation; `/resume compare` multi-JD fit matrix.  
- **Ignore:** Browser automation that sends LinkedIn invites (ToS + our no-auto-send rule). Prefer draft + user confirm only.

---

## 3. Commercial products (inspire only — no code)

| Product | Core bet | Job Pilot stance |
|---|---|---|
| **Teal** | Resume CRM + keyword match score | Inspire keyword scorecard UI; we keep local data |
| **Huntr** | Kanban application CRM | Inspire pipeline stages linked to Memory events |
| **Simplify** | Autofill ATS forms + tracker | Inspire paste-ready field packs; **never** autofill-submit bots |
| **LazyApply / LoopCV / AutoApply** | Volume / Easy Apply automation | **Ignore** — conflicts with quality + no-auto-send |
| **Jobscan / Kickresume** | ATS keyword report + rewrite | Inspire ATS parseability check on export |
| **Final Round AI** | Interview practice | Later phase; optional after tailor |

Commercial tools are US-centric, cloud-hosted, and often monetize volume apply. Job Pilot wins on **privacy, Israel market, Memory continuity, and Dreaming**—not on Easy Apply count.

---

## 4. Decision matrix — copy / inspire / ignore

### Copy (allowed + high leverage)

| Idea | Source | Notes |
|---|---|---|
| Transparent multi-dimension fit rubric with citations | career-ops | Publish our rubric in docs; show per-dimension scores in UI |
| 3-format outreach pack (pitch / LI note / email) | Career-Seek | Ground in Memory; user confirms send |
| Application pipeline stages (Kanban or list) | ApplyKit / Huntr / HireForge | Store as SQLite events; link tailored CV artifacts |
| Offline / no-key scoring fallback | Career-Seek | TF-IDF or embedding-local when LLM missing |
| Drafter → reviewer for tailor | ai-job-search | Extra CrewAI step; blocks invented experience |
| Multi-JD compare / prioritize | ats-resume-tailor | Fit matrix before apply |

### Inspire (rebuild in our architecture)

| Idea | Source | Integration sketch |
|---|---|---|
| Greenhouse/Ashby/Lever zero-token scan | career-ops | Prefer Apify or small ATS API clients; filter IL/remote-IL |
| ATS form answer drafts | career-ops | New Flow step: JD + Memory → Q&A pack |
| Cover letter + interview prep pack | Resume-Matcher / CrewAI demos | Post-tailor “application pack” endpoint |
| JD from URL | ApplyKit / HireForge | Fetch + extract; Seeker edits before tailor |
| Keyword gap panel | Teal / ApplyKit | Beside match score on Jobs + Tailor |
| Snooze / thumbs feedback | Career-Seek | Feeds Memory + re-rank |
| Rejection / outcome analytics | career-ops web forks | Dreaming inputs |
| LaTeX / fancy PDF templates | ai-job-search / Resume-Matcher | Optional later; DOCX remains MVP |
| Ollama / LiteLLM multi-provider | Resume-Matcher / ApplyKit | Extend BYO beyond OpenAI/Anthropic |
| LinkedIn profile text optimizer | HireForge | Export-only; no LinkedIn API write |

### Ignore (conflict or YAGNI)

| Idea | Why |
|---|---|
| Mass Easy Apply / LazyApply-style bots | Product constraint + recruiter trust |
| Hosted multi-tenant SaaS | ADR local-first |
| Claude-Code-only runtime | We ship a web app; skills stay complementary |
| India/US board defaults as primary | Wrong market |
| Chrome LinkedIn invite automation | ToS risk; auto-send adjacent |
| Heavy Redis/Meilisearch installers | Ponytail: SQLite + Markdown enough |
| Fabricating experience for ATS | Violates baseline+Memory truth ADR |

---

## 5. Recommended enhancement backlog (ordered)

Priority = impact × fit with ADRs × implementation cost.

### P0 — sharpen what we already claim

1. **Published fit rubric + UI score breakdown** (career-ops inspired)  
2. **Keyword gap + strengths panel** on Jobs cards and Tailor  
3. **Drafter → reviewer** gate on CV tailor (no invented bullets)  
4. **Snooze / like / dismiss** on suggestions → Memory feedback  

### P1 — close the “application OS” gap

5. **Application tracker** (stages: saved → tailored → applied → interview → offer/rejected) linked to job + CV artifact  
6. **Outreach pack** (3 formats) from Dreaming or Jobs detail — still confirm-to-send  
7. **JD-from-URL** extractor (ATS HTML / plain page)  
8. **Post-tailor Application Pack:** cover letter draft + interview Qs + ATS form answers  

### P2 — market & ingest depth

9. **IL-specific board coverage checklist** via Apify (AllJobs, Drushim, LinkedIn Jobs IL, Google Jobs IL) — document gaps  
10. **Greenhouse/Ashby/Lever company list** filtered to IL employers / remote-IL  
11. **Multi-JD compare** for prioritization  
12. **No-LLM ranking fallback** when keys missing  

### P3 — later / optional

13. Ollama / more providers via LiteLLM-style router  
14. PDF template polish (beyond DOCX)  
15. Rejection-pattern Dreaming reports  
16. LinkedIn About/headline draft export  
17. Browser extension that **only** captures JD → Job Pilot (no submit)

---

## 6. How to integrate (architecture)

Stay inside existing ADRs:

```text
Seeker UI (apps/web)
    → FastAPI (apps/api)
        → CrewAI Flows/crews (match, tailor, dream, draft)
            → Memory (SQLite structured + memory/*.md)
            → Apify Actors (ingest)
```

| Enhancement | Likely touchpoints |
|---|---|
| Rubric + keyword gaps | Match crew JSON schema; Jobs UI cards |
| Reviewer gate | Tailor Flow extra step; reject fabricated claims |
| Tracker | New SQLite tables + `/applications` API + simple board UI |
| Outreach pack | Dreaming / draft crew; reuse Memory facts |
| JD URL | Ingest helper; no new scraper farm if Apify/ATS APIs suffice |
| Offline score | Deterministic scorer beside LLM ranker |

**Do not** fork career-ops or Resume-Matcher into the monorepo. Reimplement patterns; cite sources in ADRs when decisions land.

Licensing hygiene:

- MIT / Apache-2.0: safe to read and reimplement ideas; attribute if copying substantial text/rubric wording.  
- Commercial UIs: visual/UX inspiration only.  
- Before vendoring any file, confirm LICENSE in that repo revision.

---

## 7. What Job Pilot should not try to be

- The highest-volume auto-applier  
- A generic global resume Canva  
- A Claude Code skill pack with no product UI  
- A US job board aggregator  

**Be:** Israel-first local OS where Memory compounds, Dreaming proposes, Seeker approves.

---

## 8. Locked decisions (grill 2026-07-25)

Recorded in `docs/adr/0020-post-research-enhancement-scope.md` and `CONTEXT.md`.

| Question | Locked choice |
|---|---|
| Application tracker | Post-MVP; minimal job status only |
| Cover letter / interview / ATS answers | Separate Application Pack action |
| Fit scoring | Hybrid: Local Score always; Fit Rubric when key set |
| IL ingest | Apify + manual; direct ATS later |
| Outreach | Always-on Outreach Pack on Jobs; Dreaming for timing |
| No LLM key | Degrade: Jobs/Memory/Local Score work; LLM actions blocked |
| Success metric | Time to first Qualified Application |
| Fit Rubric dimensions | Hard reqs, skills/evidence, role alignment, IL/location, risks; comp/culture advisory |
| P0 build order | Rubric+gaps → Tailor reviewer → snooze/like/dismiss → status + Outreach Pack |

---

## 9. Source links

| Project | URL |
|---|---|
| career-ops | https://career-ops.org/ · https://github.com/santifer/career-ops (verify exact org) |
| ai-job-search | https://github.com/MadsLorentzen/ai-job-search |
| Resume-Matcher | https://github.com/srbhr/Resume-Matcher |
| ApplyKit | https://github.com/wihlarkop/applykit |
| Career-Seek | https://github.com/iamadarsha/Career-Seek |
| job-hunt-os | https://github.com/alexmonegrop/job-hunt-os |
| HireForge | https://github.com/profitelai/hireforge |
| resume-optimization-crew | https://github.com/tonykipkemboi/resume-optimization-crew |
| Teal / Huntr / Simplify | commercial — compare pages via career-ops.org/compare |

Internal: `CONTEXT.md`, `docs/adr/0001`–`0020`, `docs/research/job-platform-mcps.md`.
