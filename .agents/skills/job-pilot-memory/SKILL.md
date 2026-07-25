---
name: job-pilot-memory
description: >-
  Maintains Job Pilot persistent memory and RAG corpus from resume, experience,
  best fits, interests, outreach outcomes, and market signals. Use when the user
  mentions memory, recall, RAG, remember this, extract facts, update profile,
  resume index, or wants context loaded before matching or messaging.
---

# Job Pilot Memory

Local-first memory for one job seeker. Facts are plain Markdown under `memory/`.
No cloud memory service. Embeddings and LLM calls use the **user's own API keys** only.

## Store layout

```
memory/
├── config.yml              # thresholds, decay, embedding provider hints
├── manifest.json           # counts, last extract/dream timestamps
├── log.md                  # append-only ops log
├── profiles/
│   └── seeker.md           # long-term profile (soul): goals, constraints, style
├── facts/
│   ├── active/YYYY/MM/     # atomic facts
│   └── archive/            # consolidated / forgotten
├── rag/
│   ├── resume/             # chunked resume + variants
│   ├── experience/         # roles, projects, skills evidence
│   ├── fits/               # past strong matches and why
│   ├── interests/          # domains, stacks, companies of interest
│   └── market/             # hiring signals, funding, openings snapshots
├── contradictions.md       # unresolved conflicting facts
└── dreams/                 # dream-cycle outputs (see job-pilot-dreaming)
```

Create folders lazily. Never invent facts; extract only from user-provided or tool-fetched sources.

## Fact format

Each fact file:

```markdown
---
id: fact-2026-07-23-001
subject: seeker
tags: [stack, typescript, israel]
claim: Prefers TypeScript backend roles in Tel Aviv / remote-for-IL
confidence: 0.85
sources: [resume.md, chat]
created: 2026-07-23
last_recalled: 2026-07-23
---

Prefers TypeScript backend roles in Tel Aviv or remote roles open to Israeli developers.
```

## Workflows

### Setup (`/mem-setup` equivalent)

1. Ensure `memory/` tree exists.
2. Write `memory/config.yml` if missing (see `references/config-defaults.md`).
3. Seed `memory/profiles/seeker.md` from resume + explicit preferences.
4. Append to `memory/log.md`.

### Extract

1. Read the source (resume, JD, chat excerpt, market note).
2. Emit atomic claims (one claim per fact). Skip fluff.
3. Tag with: `resume`, `experience`, `fit`, `interest`, `market`, `outreach`, `constraint`.
4. Compare to active facts; on conflict append to `contradictions.md` instead of overwriting.
5. For resume/experience sources, also chunk into `memory/rag/<bucket>/` for retrieval.

### Recall

1. Lexical pass over `subject` / `tags` / `claim` under `facts/active/`.
2. Optionally re-rank with the user's configured model (BYO key).
3. Return top-k facts + relevant RAG chunks.
4. Update `last_recalled` on used facts.

### Consolidate

1. Merge near-duplicate claims; accumulate `sources`.
2. Decay confidence for facts not recalled within `recency_decay_days`.
3. Move superseded facts to `facts/archive/consolidated/`.

### Forget

1. Default: move to `facts/archive/forgotten/` (soft).
2. Hard delete only if user says `--hard` / "delete permanently".

## RAG rules for Job Pilot

| Bucket | Contents | Used for |
|--------|----------|----------|
| resume | Canonical + tailored CV variants | Match score, tailored CV |
| experience | Evidence bullets, metrics, stack | Message personalization |
| fits | Jobs that ranked high and why | Ranking model priors |
| interests | Domains, companies, people targets | Dreaming opportunities |
| market | Hiring/funding/news snapshots | Timing outreach |

Always scope retrieval to **Israel market**: IL locations, Hebrew/English JDs for IL employers, or remote roles explicitly open to Israeli candidates.

## Important

- Never call a site-provided free LLM. If no user key is configured, stop and ask.
- Do not store passwords, cookies, or LinkedIn session tokens in memory.
- Obsidian MCP (if connected) is optional export/import — canonical store remains `memory/`.

## Examples

**User:** "Remember I won't relocate outside Israel."
→ Extract constraint fact; update `seeker.md` Constraints; tag `constraint`.

**User:** "Index my resume for matching."
→ Chunk into `rag/resume/`; extract skills/roles facts; update manifest.
