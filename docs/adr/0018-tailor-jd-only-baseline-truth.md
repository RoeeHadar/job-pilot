# ADR 0018: Tailor CV requires JD only; baseline CV is truth

## Status

Accepted

## Context

Tailor must reflect what is true about the developer. Title/company fields felt mandatory but aren't essential.

## Decision

- Tailor always reads **baseline resume + Memory**
- **Only Job Description is required** from the Seeker
- Title/company optional
- Gated by `onboarding_complete`

## Consequences

- API/UI drop required title/company
- Selecting a shortlist job may prefill JD (and optional title/company) as a convenience
- Crew prompts must forbid inventing experience not in baseline/Memory
