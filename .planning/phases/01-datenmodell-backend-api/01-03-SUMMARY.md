---
phase: 01-datenmodell-backend-api
plan: 03
subsystem: api
tags: [firecrawl, camoufox, scraper, httpx, ssrf, opengraph, coolify, link-metadata]

requires:
  - phase: 01-datenmodell-backend-api
    provides: Schema + RLS + Links model (Plan 05), auth JWKS (Plan 06)
provides:
  - ScrapeService Firecrawl→Camoufox→hostname pipeline with 12s budget (D-09..D-16)
  - POST /links synchronous scrape + JSONB metadata persist (LINK-01)
  - Links category invariant regardless of scrape outcome (LINK-02)
  - /ready scraper health ping when SCRAPER_ENABLED=true (D-31)
  - docker-compose.scraper.yml for Coolify-internal Firecrawl + Camoufox stack (D-14)
affects: [phase-2-mcp, phase-3-hermes, phase-4-webapp]

tech-stack:
  added: [camoufox-sidecar (FastAPI), firecrawl self-host compose stack]
  patterns: [SSRF guard before outbound scrape, httpx bearer + hard timeouts, regex OG parse]

key-files:
  created:
    - api/app/services/scraper.py
    - api/app/routers/links.py
    - api/camoufox-sidecar/main.py
    - api/camoufox-sidecar/Dockerfile
    - docker-compose.scraper.yml
    - api/tests/integration/test_scraper.py
    - api/tests/unit/test_scraper.py
  modified:
    - api/app/routers/health.py
    - api/app/core/config.py
    - api/app/main.py
    - api/app/services/__init__.py

key-decisions:
  - "Firecrawl /ready ping uses /v0/health/liveness (not /health) — matches self-host image"
  - "Firecrawl workers split into API + queue-worker containers for Coolify healthchecks"
  - "API container joins scraper Docker network via Coolify custom_docker_run_options"
  - "OpenGraph parse via regex — no BeautifulSoup dependency (T-01-SC accept)"
  - "Camoufox sidecar returns raw HTML; API parses OG tags (D-16)"

patterns-established:
  - "ScrapeService.scrape: SSRF guard → Firecrawl 8s → Camoufox 4s → hostname fallback"
  - "Links always resolve category_id to seeded 'Links' row (NULL owner_id)"

requirements-completed: [LINK-01, LINK-02]

coverage:
  - id: D1
    description: "POST /links scrapes metadata via Firecrawl and persists JSONB with scrape_status=ok"
    requirement: LINK-01
    verification:
      - kind: integration
        ref: "api/tests/integration/test_scraper.py::test_scrape"
        status: pass
    human_judgment: false
  - id: D2
    description: "Firecrawl failure falls back to Camoufox; scrape_status=ok when Camoufox returns OG title"
    requirement: LINK-01
    verification:
      - kind: integration
        ref: "api/tests/integration/test_scraper.py::test_camoufox_fallback"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both scrapers fail → link persists with hostname title and scrape_status=failed"
    requirement: LINK-01
    verification:
      - kind: integration
        ref: "api/tests/integration/test_scraper.py::test_scrape_fail_fallback"
        status: pass
    human_judgment: false
  - id: D4
    description: "Link always lands in seeded Links category even when scrape fails"
    requirement: LINK-02
    verification:
      - kind: integration
        ref: "api/tests/integration/test_scraper.py::test_default_cat"
        status: pass
      - kind: unit
        ref: "api/tests/unit/test_scraper.py::test_default_cat"
        status: pass
    human_judgment: false
  - id: D5
    description: "Total scrape budget ≤ 12s (Firecrawl 8s + Camoufox 4s httpx timeouts)"
    requirement: LINK-01
    verification:
      - kind: integration
        ref: "api/tests/integration/test_scraper.py::test_12s_budget"
        status: pass
    human_judgment: false
  - id: D6
    description: "/ready returns 503 SCRAPER_UNHEALTHY when scraper ping fails; 200 when both up"
    requirement: LINK-01
    verification:
      - kind: integration
        ref: "api/tests/integration/test_scraper.py::test_ready_scraper_ping"
        status: pass
    human_judgment: false
  - id: D7
    description: "SSRF guard blocks private IPs and non-http(s) schemes with SSRF_BLOCKED"
    requirement: LINK-01
    verification:
      - kind: integration
        ref: "api/tests/integration/test_scraper.py::test_ssrf_blocked"
        status: pass
    human_judgment: false
  - id: D8
    description: "Firecrawl + Camoufox deployed Coolify-internal; API reaches scrapers; public routes blocked (D-14)"
    requirement: LINK-01
    verification:
      - kind: manual_procedural
        ref: "Coolify deploy checkpoint — firecrawl/camoufox healthy, API /ready ready, public scraper domains 503"
        status: pass
    human_judgment: true
    rationale: "Network topology and internal-only routing require production infra verification beyond httpx mocks"

duration: 35min
completed: 2026-07-30
status: complete
---

# Phase 01 Plan 03: Link Scrape Pipeline Summary

**Synchronous POST /links with Firecrawl→Camoufox scrape fallback, SSRF guards, JSONB metadata, and Coolify-internal scraper stack**

## Performance

- **Duration:** 35 min (code + Coolify deploy checkpoint)
- **Started:** 2026-07-30T02:30:00Z
- **Completed:** 2026-07-30T04:15:00Z
- **Tasks:** 3 (2 auto + 1 checkpoint)
- **Files modified:** 12

## Accomplishments

- `ScrapeService`: SSRF guard, Firecrawl 8s primary, Camoufox 4s fallback, hostname title on double-fail (D-11)
- `POST /links` persists url + JSONB metadata + scrape_status; category always seeded Links (LINK-02)
- `/ready` pings Firecrawl liveness + Camoufox health when `SCRAPER_ENABLED=true` (D-31)
- `docker-compose.scraper.yml`: full Firecrawl self-host stack + Camoufox sidecar, internal-only (D-14)
- Coolify production: firecrawl + camoufox services healthy; API on shared Docker network; `/ready` returns ready

## Task Commits

1. **Task 1: Tracer — POST /links → Firecrawl → persist** - `5baeddb` (feat)
2. **Task 2: Camoufox fallback + hostname failure + /ready ping** - `d2c911a` (feat)
3. **Deploy compose expansion** - `ef2f2a3` (feat)
4. **Deploy fix: liveness path + split workers** - `c1feb85` (fix)

**Plan metadata:** pending (docs commit)

## Checkpoint (Task 3) — Approved

Parent session verified Coolify internal scraper deploy:

| Check | Result |
|-------|--------|
| `puzzlessbox-firecrawl` (`rmj3pan623pikht2yqq2efsd`) | running:healthy (split API/worker containers) |
| `puzzlessbox-camoufox` (`fvcvmku7pt1ehl1r6oi6erwd`) | running:healthy |
| `puzzlessbox-api` (`dxoflgio67786lc4yilhce43`) | `SCRAPER_ENABLED=true`, `/ready` → `{"status":"ready"}` |
| API network | `--network rmj3pan623pikht2yqq2efsd` |
| Camoufox alias | `--network-alias camoufox` on scraper network |
| Env | `FIRECRAWL_URL=http://firecrawl-rmj3pan623pikht2yqq2efsd:3002`, `CAMOUFOX_URL=http://camoufox:8080` |
| D-14 public routes | Public scraper domains return 503 (internal-only OK) |

## Files Created/Modified

- `api/app/services/scraper.py` - ScrapeService + SSRF + OG regex parse
- `api/app/routers/links.py` - POST /links endpoint
- `api/app/routers/health.py` - scraper ping on /ready
- `api/camoufox-sidecar/` - lightweight Camoufox HTML fetch sidecar
- `docker-compose.scraper.yml` - Firecrawl stack + Camoufox for Coolify
- `api/tests/integration/test_scraper.py` - scrape, fallback, budget, ready ping, SSRF
- `api/tests/unit/test_scraper.py` - Links category resolution unit test

## Decisions Made

- Firecrawl health endpoint: `/v0/health/liveness` (self-host image contract)
- Worker containers split from API container for independent Coolify healthchecks
- API joins scraper Docker network via Coolify `custom_docker_run_options` (not Traefik public route)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Full Firecrawl compose + Camoufox sidecar for Coolify**
- **Found during:** Task 2 / checkpoint prep
- **Issue:** Initial compose insufficient for self-host Firecrawl (missing redis/rabbitmq/playwright workers)
- **Fix:** Expanded `docker-compose.scraper.yml`; added `api/camoufox-sidecar` FastAPI wrapper
- **Files modified:** docker-compose.scraper.yml, api/camoufox-sidecar/*
- **Committed in:** ef2f2a3

**2. [Rule 1 - Bug] Firecrawl /ready ping wrong health path**
- **Found during:** Coolify deploy (services unhealthy)
- **Issue:** `/health` returned non-200 on self-host image; compose healthcheck failed
- **Fix:** Switch to `/v0/health/liveness`; split `firecrawl-queue-worker` container
- **Files modified:** api/app/services/scraper.py, docker-compose.scraper.yml
- **Committed in:** c1feb85

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug)
**Impact on plan:** Deploy correctness only; scrape logic unchanged.

## Issues Encountered

None beyond deviations above.

## User Setup Required

Coolify scraper stack (completed per checkpoint):

- Deploy `docker-compose.scraper.yml` as internal-only apps (no Traefik public route)
- Set `FIRECRAWL_URL`, `FIRECRAWL_BEARER`, `CAMOUFOX_URL`, `CAMOUFOX_BEARER` on API app
- Join API container to scraper Docker network
- Set `SCRAPER_ENABLED=true` on API when scrapers are live

## Next Phase Readiness

- Phase 1 complete — all 6 plans executed
- Link capture ready for Hermes/MCP `create_item` with URL type
- Phase 4 WebApp can show link previews from persisted JSONB metadata

---
*Phase: 01-datenmodell-backend-api*
*Completed: 2026-07-30*

## Self-Check: PASSED

- FOUND: .planning/phases/01-datenmodell-backend-api/01-03-SUMMARY.md
- FOUND: api/app/services/scraper.py
- FOUND: api/app/routers/links.py
- FOUND: docker-compose.scraper.yml
- FOUND: api/tests/integration/test_scraper.py
- FOUND: 5baeddb
- FOUND: d2c911a
- FOUND: ef2f2a3
- FOUND: c1feb85
