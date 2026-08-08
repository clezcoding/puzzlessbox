# API Coverage — Phase 1 (Firecrawl + Camoufox + Google Calendar)

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
> Phase 1 owns the FastAPI surface that consumes Firecrawl (self-host), Camoufox
> sidecar, and Google Calendar API v3. Better Auth JWKS is first-party (Next.js),
> not an external vendor surface — listed only where the API verifies tokens.

## Firecrawl (self-host scrape primary)

| capability | decision | reason |
|---|---|---|
| Scrape URL → markdown/HTML (`/v0/scrape` or equivalent) | INTEGRATE | LINK-01 primary path; ≤8s budget (D-13) |
| Health / liveness for Coolify | INTEGRATE | `/ready` gates SCRAPER_ENABLED |
| Fire-engine / residential proxies | OPT-OUT | explicitly out of scope — self-host has no Fire-engine; CF best-effort (D-12) |
| Crawl / map / extract bulk jobs | OPT-OUT | not needed yet — single-URL link preview only |
| Webhooks / async job queue from Firecrawl | OPT-OUT | not needed yet — sync scrape inside draft create |

## Camoufox (sidecar fallback)

| capability | decision | reason |
|---|---|---|
| `GET url → HTML` fetch | INTEGRATE | Fallback after Firecrawl; ≤4s remainder (D-13, D-16) |
| OG / title parse in API after HTML | INTEGRATE | API-side parse, not Camoufox feature |
| Full browser automation / HeadlessX | OPT-OUT | not needed yet — light sidecar only until proven insufficient (D-16) |
| Public ingress | OPT-OUT | explicitly out of scope — internal-only on shared Docker network (D-14) |

## Google Calendar API v3

| capability | decision | reason |
|---|---|---|
| OAuth connect + callback token persist | INTEGRATE | CAL-02; tokens encrypted at rest (D-17) |
| List calendars | INTEGRATE | CAL-02 |
| Create/update events with If-Match / ETag | INTEGRATE | CAL-03 optimistic locking (D-19) |
| Pull ETag before write | INTEGRATE | on-demand conflict check (D-19) |
| FreeBusy query | OPT-OUT | not needed yet — no availability UI in v1 |
| Recurring event expansion | OPT-OUT | not needed yet — single instances only |
| Calendar ACL / sharing | OPT-OUT | explicitly out of scope — single-owner v1 |
| Push notifications / watch channels | OPT-OUT | not needed yet — no Google push in Phase 1 |
| Full bidirectional mirror cron | OPT-OUT | explicitly out of scope — Phase 1 push + on-demand pull only (D-19) |
| Secondary Google account linking | OPT-OUT | explicitly out of scope — one Google account per user |

**Matrix decided:** ✓ Firecrawl / Camoufox / Google Calendar surfaces enumerated; OPT-OUTs reasoned.
