# Job platform MCP research (Israel-first)

Research snapshot for Job Pilot integrations. Prefer MCP over ad-hoc scraping in the agent.

## Recommended primary path: Apify MCP

**Why:** One MCP surface (`https://mcp.apify.com`) can expose Actors for Israeli boards, Google Jobs, and LinkedIn jobs without maintaining separate scrapers. Auth is OAuth or Bearer token (user's Apify account — aligns with BYO-keys philosophy).

Project config: `.cursor/mcp.json` → server `apify-jobs`.

### Israeli boards (AllJobs and peers)

| Resource | Actor | Covers |
|----------|-------|--------|
| [Israeli Job Boards Scraper](https://apify.com/amrameng/israeli-job-boards-scraper) | `amrameng/israeli-job-boards-scraper` | AllJobs, Drushim, JobMaster, JobNet, GotFriends, Ethosia |

Normalized fields: `title`, `company`, `location`, `jobType`, `postedDate`, `url` + `raw`.

Unified filters useful for Job Pilot: `categoryFilter=software-it|cyber`, `regionFilter`, `scopeFilter=remote|hybrid`, `seniorityFilter`.

MCP docs: https://apify.com/amrameng/israeli-job-boards-scraper/api/mcp

### Google Jobs

| Resource | Notes |
|----------|-------|
| [johnvc/Google-Jobs-Scraper](https://github.com/johnisanerd/Apify-Google-Jobs-Scraper) | MCP URL pattern via Apify; query with Israel / remote-for-IL keywords |
| [khadinakbar/google-jobs-scraper](https://apify.com/khadinakbar/google-jobs-scraper) | Alternate Actor with MCP setup |

Use location queries like `Israel`, `Tel Aviv`, `Remote Israel`, Hebrew role titles as needed.

### LinkedIn Jobs

| Resource | Notes |
|----------|-------|
| [shahidirfan/linkedin-jobs-mcp-server](https://apify.com/shahidirfan/linkedin-jobs-mcp-server) | LinkedIn job search via Apify MCP Actor |
| HarvestAPI / similar LinkedIn Actors | Prefer **jobs** Actors; avoid storing session cookies in-repo |

LinkedIn messaging/outreach should stay **human-approved** (ToS + spam risk). Job Pilot drafts; user sends in LinkedIn UI or a separate approved connector later.

## Strong secondary: unified Go MCP (`go-job`)

[anatolykoptev/go-job](https://github.com/anatolykoptev/go-job) — single Go MCP with ~28 tools: LinkedIn, Google Jobs, Greenhouse, Lever, Indeed, remote boards, match scoring.

**Use when:** You want one local binary for multi-platform search without Apify spend.

**Gap:** Weak native coverage of Hebrew Israeli boards (AllJobs/Drushim) — keep Apify Israeli Actor as the IL source of truth.

## Other IL-relevant sources (future Actors / adapters)

- GotFriends / Ethosia — already in Israeli Job Boards Scraper
- Company career pages (Greenhouse/Lever) via `go-job` `platform=greenhouse|lever`
- Coming Soon / Tech career pages — evaluate case-by-case; prefer official APIs

## Auth & compliance posture

1. User owns Apify (and any SerpAPI) keys — no shared Job Pilot cloud key for scrapers either if we mirror the AI policy.
2. Never commit tokens; use Cursor MCP OAuth or env-injected Bearer headers locally.
3. Do not automate LinkedIn connection spam; dream proposals require explicit send confirmation.
4. Respect robots/ToS of each board; prefer maintained Actors over custom scrapers.

## Suggested tool URL (explicit Actors)

```
https://mcp.apify.com/?tools=actors,docs,amrameng/israeli-job-boards-scraper,johnvc/Google-Jobs-Scraper,shahidirfan/linkedin-jobs-mcp-server
```

After connecting: Cursor Settings → MCP → confirm `apify-jobs` is green. First chat may need an explicit "using Apify MCP" mention if tool discovery lags.

## Open questions for product grill

- Apify pay-per-result vs local `go-job` for daily scans
- Whether LinkedIn **messaging** ever gets an MCP or stays copy-paste drafts
- Hebrew-first search defaults vs bilingual
