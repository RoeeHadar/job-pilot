# ADR 0008: CrewAI Flow with crews inside steps

## Status

Accepted

## Context

Match and CV tailor need orchestration. Options: independent crews only, one Flow, plain LLM services first, or Flow + nested crews.

## Decision

- **Flow** owns pipeline state and step order for MVP (match → rank → optional tailor_cv)
- **Crews** are used inside steps when multi-agent roles add value
- FastAPI is the HTTP entrypoint that starts/resumes Flows and exposes results

## Consequences

- Backend package layout should include `flows/` and `crews/` (or CrewAI JSON-first layout)
- UI polls or subscribes to Flow/run status
- Dreaming later can be a second Flow without rewriting match/CV
- Slightly more framework surface than plain `LLM.call()` — accepted to leverage CrewAI foundation
