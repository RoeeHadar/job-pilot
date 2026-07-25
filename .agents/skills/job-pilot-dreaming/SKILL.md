---
name: job-pilot-dreaming
description: >-
  Runs Job Pilot dream cycles that consolidate memory, cross market signals with
  the seeker profile, and propose timed outreach opportunities with tailored CV
  hints and message drafts. Use when the user says dream, dreaming, sleep cycle,
  consolidate opportunities, suggest who to message, market timing, or proactive
  job outreach ideas.
---

# Job Pilot Dreaming

Dreaming is an **idle consolidation + opportunity synthesis** loop. It does not
auto-send messages. It produces proposals the user approves.

Depends on `job-pilot-memory` for facts and RAG.

## When to dream

- User invokes dreaming explicitly
- After a batch of market/job ingest
- Periodically when `memory/manifest.json` shows `last_dream` older than config

## Dream cycle steps

### 1. Load context

1. Recall high-confidence seeker facts (constraints, stack, target roles).
2. Load recent `memory/rag/market/` and `fits/` chunks.
3. Load unresolved `contradictions.md` (flag, do not invent resolutions).

### 2. Consolidate (sleep hygiene)

1. Run memory consolidate (merge duplicates, decay stale).
2. Archive low-confidence noise.
3. Snapshot summary into `memory/dreams/YYYY-MM-DD-HHMM.md` header.

### 3. Opportunity synthesis

Cross:

| Signal | Memory | Output |
|--------|--------|--------|
| Company X hiring / new role | Skills + fits overlap | Ranked opportunity |
| Company Y funding / revenue news | Interests + past touches | Timing rationale |
| Recruiter / employee match | Experience evidence | Suggested contact angle |
| JD requirements | Resume RAG | Tailored CV delta + draft message |

Every proposal must include:

1. **Why now** — market signal + timing
2. **Fit score rationale** — which facts/chunks fired (cite paths)
3. **CV action** — what to emphasize / cut for this JD
4. **Message draft** — Hebrew or English per channel norms; user edits before send
5. **Channel** — LinkedIn / AllJobs / email / other (never auto-post)
6. **Risks** — ToS, spam, missing data

### 4. Persist

Write `memory/dreams/YYYY-MM-DD-HHMM.md`:

```markdown
---
dream_id: dream-2026-07-23-001
created: 2026-07-23T15:00:00+03:00
facts_touched: 14
opportunities: 3
---

# Dream summary
...

## Opportunities

### 1. [Role] @ [Company]
- Why now: ...
- Fit: ...
- CV delta: ...
- Draft message: |
    ...
- Channel: LinkedIn
- Status: proposed
```

Update `memory/manifest.json` → `last_dream`.

### 5. Present to user

Show ranked opportunities. Ask which to pursue. Do **not** send outreach until confirmed.

## Market scope hard rule

Only synthesize opportunities for:

- Jobs located in Israel, or
- Remote roles clearly open to Israeli developers / IL time zones / IL entities posting

Drop or quarantine anything else into a `out_of_scope` section (do not recommend).

## AI keys

All scoring, drafting, and re-ranking use the user's configured providers. If unset, produce a structured dream skeleton from lexical memory only and mark `llm: skipped`.

## Examples

**User:** "Run a dream cycle on this week's market notes."
→ Consolidate → synthesize → write dream file → present top 3 for approval.

**User:** "Company Y raised; who should I ping?"
→ Mini-dream scoped to that company; one opportunity with draft + CV delta.
