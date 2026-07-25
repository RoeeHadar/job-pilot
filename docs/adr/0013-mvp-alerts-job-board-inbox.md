# ADR 0013: MVP alerts are job-board inbox; LinkedIn signals later

## Status

Accepted

## Context

Seekers want alerts for interesting new jobs and LinkedIn HR hiring posts. Local-first constrains push delivery; LinkedIn social monitoring is ToS- and auth-heavy.

## Decision

- **MVP alerts:** in-app inbox (+ optional browser/OS notification) from scheduled Israel job-board ingest scored against Memory, while the local server runs
- **Phase 2:** LinkedIn HR / hiring-post signal alerts
- No email-required path in MVP

## Consequences

- Need a scheduler/worker in `apps/api` (or APScheduler/cron-like loop)
- Alert entities in SQLite; unread state in UI
- Document that alerts pause when the app is not running (unless a later background service is added)
- LinkedIn Actors for jobs search may still be used for ingest; social/HR feed is separate and deferred
