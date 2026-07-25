# ADR 0015: Local profile gate (no cloud auth)

## Status

Accepted

## Context

Seekers need a clear first-use flow (name, title, resume, Memory) before match/tailor. "Sign-in" was requested but the product is local-first.

## Decision

MVP uses a **local onboarding wizard** that sets `onboarding_complete`. No cloud account, no password. Jobs, Tailor, and Alerts are gated until complete.

## Consequences

- App shell redirects incomplete Seekers to onboarding
- Profile fields persist in SQLite + `memory/profiles/seeker.md`
- Real auth (email/OAuth) deferred if multi-device sync ever appears
