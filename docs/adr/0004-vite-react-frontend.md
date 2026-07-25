# ADR 0004: Vite + React frontend

## Status

Accepted

## Context

With FastAPI owning the API, the frontend should be a client. Candidates: Vite+React, Next.js, or Vite+Vue/Svelte.

## Decision

Use **Vite + React (TypeScript)** as the v1 UI.

## Consequences

- Single backend authority (FastAPI); no Next BFF layer
- Aligns with Taste / React-oriented design skill
- CORS and API base URL must be configured for localhost dev
- SEO/SSR irrelevant for local-first app
