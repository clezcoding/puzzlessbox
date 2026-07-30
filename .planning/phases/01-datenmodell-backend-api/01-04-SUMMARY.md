---
phase: 01-datenmodell-backend-api
plan: 04
subsystem: api
tags: [google-calendar, oauth, aes-gcm, if-match, etag, concurrency, cal-02, cal-03]

requires:
  - phase: 01-datenmodell-backend-api
    provides: Schema + events table + auth JWKS (Plans 05, 06)
provides:
  - Separate Google Calendar OAuth on api. with encrypted token storage (D-17, D-21, D-29)
  - GET /calendars + POST /calendars/{id}/select (D-18)
  - POST/GET/PATCH /events with google_event_id + etag (CAL-02, D-19)
  - If-Match optimistic concurrency → 412 CONCURRENCY_CONFLICT (CAL-03, D-20)
affects: [phase-4-webapp, phase-5-coolify]

tech-stack:
  added: [google-api-python-client==2.160.0, google-auth-oauthlib==1.2.1]
  patterns: [AES-256-GCM token encryption, OAuth state CSRF, pull-before-write + If-Match, structured 412 conflict]

key-files:
  created:
    - api/app/services/calendar.py
    - api/app/routers/calendar.py
    - api/app/routers/events.py
    - api/app/core/security.py
    - api/app/models/calendar_token.py
    - api/alembic/versions/0003_calendar_tokens.py
    - api/tests/integration/test_calendar.py
  modified:
    - api/app/core/config.py
    - api/app/main.py
    - api/requirements.txt
    - api/.env.example

key-decisions:
  - "calendar_tokens.owner_id references Better Auth user.id via app check — no FK (D-21 cross-service contract)"
  - "OAuth callback on api.puzzlesstool.online, separate from Better Auth Social (D-21, D-29)"
  - "No unconditional events().update — every write path sets If-Match (CAL-03)"

patterns-established:
  - "encrypt_token/decrypt_token in core/security.py using ENCRYPTION_KEY (32-byte AES-256-GCM)"
  - "412 CONCURRENCY_CONFLICT with details:{etag, remote_state} on stale etag or Google 412 race"

requirements-completed: [CAL-02, CAL-03]

coverage:
  - id: D1
    description: "OAuth connect/callback stores AES-256-GCM encrypted tokens in calendar_tokens (not plaintext)"
    requirement: CAL-02
    verification:
      - kind: integration
        ref: "api/tests/integration/test_calendar.py::test_sync"
        status: pass
    human_judgment: false
  - id: D2
    description: "GET /calendars lists Google calendars after connect; POST /calendars/{id}/select persists selection"
    requirement: CAL-02
    verification:
      - kind: integration
        ref: "api/tests/integration/test_calendar.py::test_sync"
        status: pass
    human_judgment: false
  - id: D3
    description: "POST /events creates Google event + local row with google_event_id + etag; GET /events returns caller rows"
    requirement: CAL-02
    verification:
      - kind: integration
        ref: "api/tests/integration/test_calendar.py::test_sync"
        status: pass
    human_judgment: false
  - id: D4
    description: "PATCH /events/{id} matching etag → 200; stale etag → 412 CONCURRENCY_CONFLICT; no silent overwrite"
    requirement: CAL-03
    verification:
      - kind: integration
        ref: "api/tests/integration/test_calendar.py::test_patch_matching_etag"
        status: pass
      - kind: integration
        ref: "api/tests/integration/test_calendar.py::test_conflict"
        status: pass
      - kind: integration
        ref: "api/tests/integration/test_calendar.py::test_pull_before_write"
        status: pass
      - kind: integration
        ref: "api/tests/integration/test_calendar.py::test_no_silent_overwrite"
        status: pass
    human_judgment: false
  - id: D5
    description: "Production Coolify deploy: health/ready, migrations 0001–0003, OAuth secrets configured"
    requirement: CAL-02
    verification:
      - kind: manual_procedural
        ref: "GET https://api.puzzlesstool.online/health → 200; GET /ready → 200; alembic 0001–0003 applied; GOOGLE_CLIENT_ID/SECRET/ENCRYPTION_KEY in Coolify"
        status: pass
    human_judgment: true
    rationale: "Infra checkpoint approved by user; deploy UUID dxoflgio67786lc4yilhce43"
  - id: D6
    description: "Full browser OAuth round-trip with Better Auth session (connect → grant → callback → list → create event in Google UI)"
    requirement: CAL-02
    verification: []
    human_judgment: true
    rationale: "/auth/google/connect returns 401 without JWT (expected). Full manual OAuth browser test pending webapp deploy at app.puzzlesstool.online for Better Auth session cookie."

duration: 25min
completed: 2026-07-30
status: complete
---

# Phase 01 Plan 04: Google Calendar Sync Summary

**Separate Google OAuth on api. with AES-256-GCM encrypted tokens, event CRUD via Calendar API, and If-Match 412 conflict on concurrent writes**

## Performance

- **Duration:** 25 min
- **Started:** 2026-07-30T03:03:00Z
- **Completed:** 2026-07-30T03:28:00Z
- **Tasks:** 3 (2 auto + 1 checkpoint)
- **Files modified:** 15

## Accomplishments

- `GoogleCalendarService`: OAuth Flow, list/select calendars, create/list events, `update_event_with_etag` with pull-before-write
- `calendar_tokens` migration (0003): encrypted access/refresh, selected_calendar_id, no FK to Better Auth `user` (D-21)
- Routers: `/auth/google/connect`, `/auth/google/callback`, `/calendars`, `/events` with JWT gate on connect
- 5 integration tests: sync, matching etag, conflict, pull-before-write, no silent overwrite
- Coolify `puzzlessbox-api` live at `https://api.puzzlesstool.online` — `/health` 200, `/ready` 200, secrets + migrations applied

## Task Commits

1. **Task 1: Tracer — OAuth → list → create event** - `d91bf75` (feat)
2. **Task 2: If-Match optimistic concurrency + 412** - `d91bf75` (feat, same commit as tracer)
3. **Env docs** - `292e40c` (chore)

**Supporting deploy fixes:** `d58e5c3` (alembic in Docker + migrate on start), `07e98d0` (curl for healthchecks)

**Plan metadata:** pending (docs commit)

## Checkpoint (Task 3) — Approved

User approved infrastructure setup:

| Check | Result |
|-------|--------|
| Coolify app `puzzlessbox-api` | `https://api.puzzlesstool.online` (UUID `dxoflgio67786lc4yilhce43`) |
| `GET /health` | 200 |
| `GET /ready` | 200 |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `ENCRYPTION_KEY` | Set in Coolify |
| Alembic | 0001–0003 applied |
| `GET /auth/google/connect` without JWT | 401 (expected — needs Better Auth session) |

**Pending:** Full manual OAuth browser test (connect → Google grant → callback → create event in Google Calendar UI) blocked until webapp deploy at `app.puzzlesstool.online` provides Better Auth session cookie for JWT-authenticated connect flow.

## Files Created/Modified

- `api/app/services/calendar.py` - GoogleCalendarService + If-Match update
- `api/app/routers/calendar.py` - OAuth connect/callback, list/select calendars
- `api/app/routers/events.py` - POST/GET/PATCH events
- `api/app/core/security.py` - AES-256-GCM encrypt_token/decrypt_token
- `api/alembic/versions/0003_calendar_tokens.py` - calendar_tokens table + event etag columns
- `api/tests/integration/test_calendar.py` - sync + conflict boundary tests
- `api/.env.example` - GOOGLE_CLIENT_ID/SECRET/REDIRECT_URI documented

## Decisions Made

- Tracer and If-Match expansion shipped in single atomic commit (both green before commit)
- OAuth connect requires JWT — browser flow needs webapp session, not raw API URL visit
- Production redirect URI: `https://api.puzzlesstool.online/auth/google/callback` (D-29)

## Deviations from Plan

None - plan executed as written. Task 1+2 combined in one feat commit (scope unchanged).

## Issues Encountered

- Production `/auth/google/connect` 401 without session is by design (JWT dependency) — not a deploy bug
- Full E2E OAuth verification deferred to post-webapp-deploy (documented in coverage D6)

## User Setup Required

Google Cloud Console (completed per checkpoint):

- OAuth client with redirect `https://api.puzzlesstool.online/auth/google/callback`
- Calendar API v3 enabled
- Coolify secrets: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `ENCRYPTION_KEY` (32-byte)

## Next Phase Readiness

- Calendar API endpoints ready for Phase 4 Settings UI (connect button, calendar picker)
- Manual OAuth UAT after `app.puzzlesstool.online` webapp deploy
- Phase 1 remaining: Plan 03 (link scrape) summary pending

---
*Phase: 01-datenmodell-backend-api*
*Completed: 2026-07-30*

## Self-Check: PASSED

- FOUND: .planning/phases/01-datenmodell-backend-api/01-04-SUMMARY.md
- FOUND: api/app/services/calendar.py
- FOUND: api/app/routers/calendar.py
- FOUND: api/tests/integration/test_calendar.py
- FOUND: d91bf75
- FOUND: 292e40c
