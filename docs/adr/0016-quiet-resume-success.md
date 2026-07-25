# ADR 0016: Quiet resume success + conditional review

## Status

Accepted

## Context

Dumping extracted resume text after upload confused Seekers and offered no Continue path.

## Decision

- Default UX after upload: **success state** ("Resume loaded") + Continue
- **Review/edit** (name, title, key skills) only when extraction quality is low
- Never show a full raw extract as the primary success UI

## Consequences

- Onboarding API returns quality + structured fields, not a giant preview blob in the happy path
- Extracted text still stored in Memory for RAG; UI just doesn't dump it
