# ADR 0012: Env-file secrets for MVP

## Status

Accepted

## Context

BYO keys must stay on the Seeker's machine. Options: plain env files, OS keychain, encrypted vault, or env now with keychain later.

## Decision

MVP uses **gitignored `.env` / `.env.local`**. OS keychain (or equivalent) is planned hardening, not a v1 blocker.

## Consequences

- Document setup in README / `.env.example`
- Never log secret values
- Settings UI may write to env file or instruct manual edit
- Upgrade path to keychain should not change API shapes for providers
