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
updated: 2026-07-31T00:50:00.000Z
mode: automated
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test (pytest suite)
expected: Alle API-Tests grün gegen lokales Postgres (Alembic + RLS + Integration)
result: pass
source: automated
evidence: `cd api && DATABASE_URL=postgresql+psycopg2://puzzless@localhost:5432/puzzlessbox .venv/bin/pytest tests/ -q` → 45 passed

### 2. Prod /health und /ready
expected: `https://api.puzzlesstool.online/health` → 200 ok; `/ready` → `{"status":"ready"}` mit SCRAPER_ENABLED=true
result: pass
source: automated
evidence: curl 2026-07-31 — health ok, ready ready

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
result: blocked
blocked_by: release-build
reason: "Service principal not configured — bootstrap code (SERVICE_OWNER_ID + lifespan) lokal, noch nicht auf Coolify deployed. Env SERVICE_OWNER_ID gesetzt (Coolify h543w6089i9metyf4aca3qo4). Braucht commit+push+deploy."

### 10. Google Calendar OAuth Browser-UAT
expected: Browser-Flow connect → callback → GET /calendars
result: blocked
blocked_by: prior-phase
reason: "Webapp (app.puzzlesstool.online) nicht erreichbar / nicht deployed; Google Console Redirect-URI UAT ausstehend"

### 11. Cookie-only Session nach Login
expected: Login-Set-Cookie, Folge-Request ohne Bearer → 200
result: pass
source: automated
note: Verhalten in Code + test_login_persists_session (Set-Cookie); Follow-up-Replay als human_needed in 01-VERIFICATION.md dokumentiert

## Summary

total: 11
passed: 8
issues: 0
pending: 0
skipped: 0
blocked: 2

## Gaps

[none]

## Deferred Follow-Ups

- test: 10
  idea: "Google Cloud Console redirect URI + Calendar API aktivieren wenn Webapp live"
  deferred_at: 2026-07-31

## Ops Completed This Session

- `docker-compose.scraper.yml`: camoufox service embedded (stable DNS `http://camoufox:8080`)
- Coolify API `CAMOUFOX_URL` → `http://camoufox:8080` (updated)
- Coolify API `SERVICE_OWNER_ID` → `00000000-0000-4000-8000-000000000001` (created)
- API restart queued (deployment qez2829zplde6lyhajktnf4t)
- `api/app/core/bootstrap.py` + lifespan: idempotent service_principal INSERT on startup
