# Job Pilot domain glossary

> Terms crystallise during grill-with-docs. Implementation details do not belong here.

## Seeker

The developer using Job Pilot to find work in the Israel market.

## Israel market

Jobs located in Israel, or remote roles explicitly open to Israeli developers (including IL employers posting remote).

## Memory

Persistent, local-first facts and RAG about the Seeker and market signals. **SQLite** holds structured entities/events (jobs, matches, outreach, fact IDs). **Markdown** under `memory/` holds human-readable profile, dream reports, and narrative logs. Embeddings index is derived, not the source of truth.

## Dreaming

A consolidation + opportunity-synthesis cycle that proposes timed outreach; never auto-sends.

## Alerts

Notifications about relevant new jobs and hiring signals. **MVP:** in-app alert inbox (and optional OS/browser notification) fed by scheduled job-board ingest + match against Memory while the local app is running. **Phase 2:** LinkedIn HR / “we're hiring” social-signal alerts.

## Opportunity

A ranked proposal linking a market signal, fit rationale, CV delta, draft message, and channel.

## MVP loop

v1 must support:
1. **Onboarding gate** — name, title, resume → Memory → `onboarding_complete`.
2. **Jobs home** — on open, show **best-fit suggestions** from ingest + match vs Memory (no required search form). If personalization isn't possible yet, show **general Israel-market jobs newest-first**. Manual paste JD is secondary.
3. **JD → Tailor CV** — grounded in baseline CV + Memory; JD required; title/company optional.
4. **Alerts** — MVP in-app inbox for matched job-board postings; LinkedIn hiring-signal alerts in phase 2.

Dreaming-style opportunity synthesis may power alerts; auto-send outreach remains out of scope.

## Job ingest

The local app ingests jobs via **Apify Actors** when the Seeker configures a token, and always supports **manual paste / URL / file import** so the match→CV loop works without scrapers.

## Baseline resume

The Seeker's first-use resume file, ingested into Memory. **PDF-first** parsing, **DOCX** second. Other formats are accepted: store the original blob, extract text when possible, and if extraction is weak, complete onboarding via a guided profile review. Extracted Memory is always editable.

## Tailored CV

A job-specific resume variant grounded in the **baseline resume + Memory** (source of truth — no invented experience). **Required input: Job Description only.** Title and company are optional hints. Seeker can **edit in-app** and **export as DOCX**. Blocked until onboarding is complete. Opening Tailor from a Jobs card **prefills the JD** (and title/company when known); Generate is explicit (not auto-started).

## BYO key

API credentials supplied by the Seeker (LLM, embeddings, Apify, etc.). Job Pilot does not ship free shared AI keys. **MVP storage:** local `.env` / `.env.local` (gitignored). OS keychain is a later hardening step.

## Local-first

Job Pilot runs primarily on the Seeker's machine. Keys, Memory, Dreaming outputs, and resume artifacts stay local by default. Optional sync is out of scope until explicitly decided.

## Local web app

v1 delivery surface: a web UI served on the Seeker's machine (localhost). Not a hosted multi-tenant SaaS; not a packaged desktop shell in v1.

## Stack split

- **Backend:** Python (FastAPI) with CrewAI for multi-agent orchestration (match, CV tailor, dream, draft).
- **Frontend:** TypeScript — Vite + React SPA talking to the local FastAPI.

## Crew orchestration

MVP uses CrewAI **Flows** with **Crews** inside steps. Entry points include: onboarding (resume → Memory), JD→tailor CV, and ingest→match→rank (feeding alerts). FastAPI kicks off Flows; it does not reimplement pipelines in ad-hoc scripts.

## Repo layout

Monorepo: `apps/web` (Vite + React), `apps/api` (FastAPI + CrewAI flows/crews), `memory/` (Markdown), `data/` (SQLite), optional `packages/shared`. Agent skills and docs stay at repo root.

## Product language

**Bilingual UI** with a language toggle; **default English**. Job descriptions, Memory content, and tailored CVs follow the source language (Hebrew and/or English). RTL Hebrew UI is supported as a secondary locale.

## Onboarding gate

First-run is a **local profile wizard** (not cloud auth): name, current title, baseline resume upload, Memory preparation. Until `onboarding_complete`, Jobs / Tailor CV / Alerts are blocked. No password in MVP.

Resume upload shows a **success confirmation**, not a raw text dump. A **review step** (edit name/title/skills) appears only when extraction quality is low; high-quality parse skips review and offers Continue.
