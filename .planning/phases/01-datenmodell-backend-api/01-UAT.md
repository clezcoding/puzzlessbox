---
status: complete
phase: 01-datenmodell-backend-api
source:
  - 01-01-SUMMARY.md
  - 01-02-SUMMARY.md
  - 01-03-SUMMARY.md
  - 01-04-SUMMARY.md
  - 01-05-SUMMARY.md
  - 01-06-SUMMARY.md
started: 2026-07-31T00:48:00.000Z
updated: 2026-07-31T01:02:00.000Z
mode: automated
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test (pytest suite)
expected: Alle API-Tests grün gegen lokales Postgres (Alembic + RLS + Integration)
result: pass
source: automated
evidence: `DATABASE_URL=postgresql+psycopg2://puzzless@localhost:5432/puzzlessbox .venv/bin/pytest tests/ -q` → 45 passed (2026-07-31T01:01Z)

### 2. Prod /health und /ready
expected: `https://api.puzzlesstool.online/health` → 200 ok; `/ready` → `{"status":"ready"}` mit SCRAPER_ENABLED=true
result: pass
source: automated
evidence: health 200; ready 200 `{"status":"ready"}` after CAMOUFOX_URL=http://fvcvmku7pt1ehl1r6oi6erwd-005606252626:8080

### 3. Coverage — FastAPI Shell + Versioning (01-01)
expected: /health, /ready, Accept-Header 415
result: pass
source: automated
coverage_id: D1-D2

### 4. Coverage — Schema RLS + Seeds (01-05)
expected: Alembic 0001, RLS, board_items VIEW, 5 Kategorien
result: pass
source: automated
coverage_id: D1-D2

### 5. Coverage — Auth JWKS + Service Bearer (01-06)
expected: JWT verify, signup lock, service bearer mapping
result: pass
source: automated
coverage_id: D1-D4

### 6. Coverage — 30s Timeout State Machine (01-02)
expected: autosave, PATCH reset, confirm cancel, parallel-safe
result: pass
source: automated
coverage_id: D1-D5

### 7. Coverage — Link Scrape Pipeline (01-03)
expected: Firecrawl→Camoufox→hostname, SSRF guards, Links-Kategorie
result: pass
source: automated
coverage_id: D1-D4

### 8. Coverage — Google Calendar OAuth + If-Match (01-04)
expected: encrypted tokens, sync, 412 on conflict
result: pass
source: automated
coverage_id: D1-D3

### 9. Prod POST /links mit X-Service-Bearer
expected: 201 mit title, scrape_status, category_id (Links)
result: pass
source: automated
evidence: HTTP 201 `title=Example Domain` `scrape_status=ok` id=3030310c-98ef-413b-a347-000ef26394ae after deploy 7d50346 + SERVICE_OWNER_ID bootstrap

### 10. Google Calendar OAuth Browser-UAT
expected: Browser-Flow connect → callback → GET /calendars
result: skipped
reason: "Deferred follow-up: Webapp nicht deployed; GET /auth/google/connect returns 302 with service bearer (API-side connect redirect OK). Full browser UAT needs app.puzzlesstool.online + Google Console."

### 11. Cookie-only Session nach Login
expected: Login-Set-Cookie, Folge-Request ohne Bearer → 200
result: pass
source: automated
evidence: `test_cookie_session_replays_on_verify` — cookie replay on GET /auth/verify

### 12. Prod Google OAuth connect redirect
expected: Authenticated GET /auth/google/connect redirects (302) to Google
result: pass
source: automated
evidence: HTTP 302 with X-Service-Bearer

## Summary

total: 12
passed: 11
issues: 0
pending: 0
skipped: 1
blocked: 0

## Gaps

[none]

## Deferred Follow-Ups

- test: 10
  idea: "Google Cloud Console redirect URI + Calendar API + Webapp UI when Phase 4 ships"
  deferred_at: 2026-07-31

## Ops Completed This Session

- Commit `7d50346` pushed; Coolify deploy `paj08ifk828x6h6oro0mwmpw` finished
- SERVICE_OWNER_ID bootstrap works in prod
- CAMOUFOX_URL set to live container hostname (alias still fragile across redeploys)
- docker-compose.scraper.yml includes camoufox service for future stack embed
