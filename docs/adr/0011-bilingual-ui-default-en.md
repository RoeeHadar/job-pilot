# ADR 0011: Bilingual UI defaulting to English

## Status

Accepted

## Context

Israel-first product must handle Hebrew and English content; UI locale is a separate choice from JD/CV language.

## Decision

- UI: bilingual with toggle; **default English**
- Content: Hebrew and English as provided by jobs/resume
- Hebrew UI includes RTL when that locale is selected

## Consequences

- i18n framework in `apps/web` from early on (even if Hebrew strings lag)
- CV/JD rendering must not assume one language
- RTL QA when Hebrew locale is enabled
