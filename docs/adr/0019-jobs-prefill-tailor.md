# ADR 0019: Jobs card prefills Tailor; Generate is explicit

## Status

Accepted

## Context

Seekers moving from a suggested job to CV tailor need a fast path without accidental LLM runs.

## Decision

Selecting a job opens Tailor with JD (and optional title/company) prefilled. Tailoring starts only when the Seeker clicks Generate.

## Consequences

- Frontend route state or query params carry job id / JD
- No auto-kickoff of CrewAI on navigation
