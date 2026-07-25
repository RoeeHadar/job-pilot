# ADR 0017: Jobs home is auto shortlist (newest fallback)

## Status

Accepted

## Context

Seekers do not want to type title/company to see jobs. They want best fits on entry.

## Decision

- Jobs page loads an **auto shortlist** (ingest + match vs Memory) with no required form fields.
- If personalization isn't possible (insufficient Memory / no usable profile signals), show **general Israel-market jobs sorted newest-first**.
- Manual paste/import remains available but secondary.

## Consequences

- Needs background or on-open ingest + rank pipeline
- Empty Apify token still needs a source of "general jobs" (cached feed, last ingest, or seed) — implementation detail later
- Search filters are optional enhancements, not the default path
