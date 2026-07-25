# ADR 0007: Apify ingest plus always-on manual import

## Status

Accepted

## Context

MVP needs Israel-scoped jobs for matching. Cursor MCP helps development but is not the app runtime. Options: Apify-only, go-job-only, manual-only, or Apify + manual.

## Decision

- **Primary automated ingest:** Apify Actors (Israeli boards, Google Jobs, LinkedIn jobs) using the Seeker's Apify token
- **Always available:** paste JD, URL fetch where feasible, and file/CSV import
- `go-job` deferred unless Apify gaps appear

## Consequences

- Settings UI needs Apify token (local secret store)
- Matching/CV paths must accept manually imported jobs as first-class
- Actor choice stays aligned with `docs/research/job-platform-mcps.md`
- No hard dependency on Apify for first-run demo with a pasted JD
