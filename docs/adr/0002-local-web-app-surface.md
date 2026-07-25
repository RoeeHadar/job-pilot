# ADR 0002: Local web app as v1 surface

## Status

Accepted

## Context

With local-first chosen, we needed the Seeker's primary interface: local web, desktop shell, CLI/agent-first, or local web then later desktop wrap.

## Decision

v1 is a **local web app** on localhost. Desktop packaging (Tauri/Electron) and CLI-first flows are deferred.

## Consequences

- Fast UI iteration with standard web stack
- Seeker runs a local server process to use the app
- Taste/frontend skill applies to the localhost UI
- Installer/auto-update and OS integration wait until a later packaging decision
