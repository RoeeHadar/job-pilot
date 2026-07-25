# ADR 0020: Post-research enhancement scope

After competitive research, Job Pilot deepens match/tailor quality before becoming a full application CRM. Kanban-style trackers and mass-apply tools are rejected; Memory compounding and human confirmation stay primary.

## Status

Accepted

## Decision

- **Application tracker (Kanban):** post-MVP. Use **minimal job status** only: saved → tailored → ready (enough to measure progress and feed Memory).
- **Application Pack** (cover letter, interview prep, ATS form answers): separate explicit action — not bundled into every Tailor run.
- **Outreach Pack** (short pitch / LinkedIn note / cold email): always available from a Jobs card; Dreaming proposes *when* to act, not the only draft path. Never auto-send.
- **Fit scoring:** hybrid — **Local Score** always; LLM **Fit Rubric** + citations when a BYO key is set.
- **Ingest:** Apify + manual paste/URL for now; direct Greenhouse/Ashby/Lever scans later.
- **No LLM key:** degrade gracefully — Jobs, Memory, and Local Score work; Tailor, Dreaming, Outreach Pack, Application Pack, and LLM rubric are blocked with a clear add-key prompt.
- **Success metric:** time from `onboarding_complete` to first **Qualified Application** (reviewed tailored CV marked ready).
- **P0 build order:** (1) rubric + keyword gaps → (2) Tailor reviewer gate → (3) snooze/like/dismiss → Memory → (4) minimal status + Jobs Outreach Pack.

## Fit Rubric dimensions

Scored with evidence citations to baseline resume/Memory and the JD:

1. Hard requirements  
2. Skills and experience evidence  
3. Role / career alignment  
4. Israel / location eligibility  
5. Risks and missing information  

Compensation and culture are **advisory** only (postings often lack reliable data).

## Consequences

- Next implementation slice is P0.1 (rubric schema + keyword gaps on Jobs), not a tracker UI.
- ADR 0007 (Apify + manual) remains the ingest boundary until a later ADR revisits ATS APIs.
- ADR 0018 (baseline + Memory truth) is reinforced by the Tailor reviewer gate in P0.2.
