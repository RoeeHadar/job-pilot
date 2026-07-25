# ADR 0001: Local-first runtime

## Status

Accepted

## Context

Job Pilot handles resumes, outreach drafts, BYO API keys, and a personal Memory/Dreaming store. We needed to choose whether v1 is local-first, a hosted multi-user web app, or a hybrid.

## Decision

Ship Job Pilot as a **local-first** application on the Seeker's machine. Canonical data (keys, `memory/`, CV variants, dream proposals) lives on disk. No required cloud account for core loops.

## Consequences

- Simpler v1: no multi-tenant auth/isolation before the match→CV→message loop is proven
- Aligns with BYO-key and Markdown memory scaffold
- Distribution and updates must be designed for desktop/local install (or local web server)
- Cross-device sync and team features deferred
