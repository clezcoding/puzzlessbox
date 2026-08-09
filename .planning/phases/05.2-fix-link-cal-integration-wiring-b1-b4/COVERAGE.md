# API Coverage — Phase 05.2 (LINK scrape + Google Calendar wiring)

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
> Phase 05.2 wires **existing** Phase-1 Firecrawl/Camoufox scrape + Google Calendar
> surfaces into Hermes capture + board/edit — no new vendor APIs.

## Firecrawl (self-host scrape)

| capability | decision | reason |
|---|---|---|
| Scrape URL → metadata (title/description/image) | INTEGRATE | LINK-01 async path via LinkScrapeManager after draft persist |
| Soft-timeout + fail → hostname + Links category | INTEGRATE | LINK-02 / D-02 |
| Single-flight cancel + 2 auto-retries + rescrape | INTEGRATE | D-19, D-26 |
| Crawl / map / extract bulk jobs | OPT-OUT | not needed yet — single-URL link preview only |
| Fire-engine / residential proxies | OPT-OUT | explicitly out of scope — self-host stack unchanged (Phase 5 D-04) |
| External job queue (Redis/ARQ) | OPT-OUT | explicitly out of scope — asyncio.create_task only (D-17) |

## Camoufox (sidecar fallback)

| capability | decision | reason |
|---|---|---|
| HTML fetch fallback after Firecrawl | INTEGRATE | inherited Phase-1 path inside scrape_service |
| Full browser automation / HeadlessX | OPT-OUT | not needed yet — light sidecar only |
| Public ingress | OPT-OUT | explicitly out of scope — internal Docker network |

## Google Calendar API v3

| capability | decision | reason |
|---|---|---|
| events.insert on first board-visible (confirm/autosave) | INTEGRATE | CAL-02 / D-09–D-11 soft-fail |
| events.update with ETag / 412 CONCURRENCY_CONFLICT | INTEGRATE | CAL-03 / D-14 |
| create-on-edit when Connected + no google_event_id | INTEGRATE | D-15 |
| events.delete on soft-delete | INTEGRATE | D-16 |
| FreeBusy / recurring expansion / ACL / watch | OPT-OUT | explicitly out of scope — unchanged from Phase 1 |
| Full bidirectional mirror cron | OPT-OUT | explicitly out of scope — push + on-demand only |
| Google Tasks (CAL-04) | OPT-OUT | explicitly out of scope — out of phase boundary |

**Matrix decided:** ✓ Firecrawl / Camoufox / Google Calendar surfaces for 05.2 wiring enumerated; OPT-OUTs reasoned.
