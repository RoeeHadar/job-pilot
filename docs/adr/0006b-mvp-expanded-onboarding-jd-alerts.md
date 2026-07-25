# ADR 0006b: MVP expanded — onboarding, JD tailor, alerts

## Status

Accepted (amends 0006)

## Context

Original MVP was ingest → match → rank, then CV tailor. Seeker pushback required first-use resume upload, paste/upload JD → tailor CV as a primary path, and alerts for new relevant jobs / hiring signals.

## Decision

MVP scope includes:
1. Baseline resume upload (onboarding into Memory)
2. JD upload/paste → tailored CV (not only from shortlist)
3. Ingest → match → rank shortlist
4. Alerts for relevant new jobs and hiring signals (mechanism TBD)

Auto-send outreach still deferred.

## Consequences

- ADR 0006's "CV only after shortlist" is superseded: shortlist and paste-JD are both first-class entry points to tailor
- Alerting needs a local notification strategy (grilling)
- Onboarding is on the critical path before quality matching
