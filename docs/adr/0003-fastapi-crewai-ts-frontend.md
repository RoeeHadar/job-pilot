# ADR 0003: FastAPI + CrewAI backend, TypeScript frontend

## Status

Accepted

## Context

Local web app needs a stack for Memory/Dreaming/matching/MCP ingest and a UI suitable for Taste-driven design. Options ranged from all-TypeScript to Python-only to a split.

## Decision

- **Backend:** Python — FastAPI + CrewAI
- **Frontend:** TypeScript (React-family) SPA/app calling the local API

## Consequences

- Two runtimes to start locally (API + UI) unless a monorepo script orchestrates both
- CrewAI skills and Python RAG ecosystem apply directly
- Clear API boundary between UI and agents (good for testing and MCP tool adapters)
- Shared types need an explicit contract (OpenAPI → TS client, or hand-written DTOs)
