---
phase: 01-datenmodell-backend-api
plan: 02
subsystem: api
tags: [asyncio, timeout, capture, draft-state-machine, cap-03]

requires:
  - phase: 01-datenmodell-backend-api
    provides: Auth + polymorphic POST /drafts (Plan 06)
provides:
  - DraftTimeoutManager in-process 30s inactivity auto-save (CAP-03, D-05)
  - PATCH /drafts/{id} timer reset (D-06)
  - POST /drafts/{id}/confirm timer cancel (D-07)
  - Polymorphic autosave routing to notes/links/tasks/events (D-01)
affects: [01-03, 01-04, phase-3-hermes]

tech-stack:
  added: []
  patterns: [asyncio.Task in-memory timer, board_items type lookup for polymorphic PATCH/confirm]

key-files:
  created:
    - api/app/services/timeout.py
    - api/app/services/__init__.py
  modified:
    - api/app/routers/capture.py
    - api/app/models/note.py
    - api/tests/integration/test_capture.py
    - api/tests/conftest.py

key-decisions:
  - "create_draft/PATCH/confirm are async endpoints so asyncio.create_task runs on ASGI loop"
  - "Integration timeout tests use AsyncClient + asyncio.sleep (TestClient does not pump background tasks)"
  - "DRAFT_TIMEOUT_SECONDS read at schedule time (not import) for test monkeypatch"

patterns-established:
  - "DraftTimeoutManager singleton: schedule_timeout cancels-then-spawns per draft_id"
  - "Autosave UPDATE guarded by status='draft' — confirmed drafts never overwritten (T-01-orphan-save)"

requirements-completed: [CAP-03]

coverage:
  - id: D1
    description: "Note draft auto-saves to notes table after 30s inactivity (1s test override)"
    requirement: CAP-03
    verification:
      - kind: integration
        ref: "api/tests/integration/test_capture.py::test_autosave"
        status: pass
    human_judgment: false
  - id: D2
    description: "Task draft auto-saves to tasks table (polymorphic routing, not notes)"
    requirement: CAP-03
    verification:
      - kind: integration
        ref: "api/tests/integration/test_capture.py::test_autosave_task_type"
        status: pass
    human_judgment: false
  - id: D3
    description: "PATCH resets inactivity timer — auto_save fires after PATCH not original POST"
    requirement: CAP-03
    verification:
      - kind: integration
        ref: "api/tests/integration/test_capture.py::test_patch_resets"
        status: pass
    human_judgment: false
  - id: D4
    description: "Confirm cancels timer; status stays confirmed after timeout window"
    requirement: CAP-03
    verification:
      - kind: integration
        ref: "api/tests/integration/test_capture.py::test_confirm_cancels"
        status: pass
    human_judgment: false
  - id: D5
    description: "Concurrent PATCHes succeed; single auto_save after timer"
    requirement: CAP-03
    verification:
      - kind: integration
        ref: "api/tests/integration/test_capture.py::test_parallel_edits"
        status: pass
    human_judgment: false
  - id: D6
    description: "Late auto_save cannot overwrite confirmed draft (WHERE status='draft' guard)"
    requirement: CAP-03
    verification:
      - kind: integration
        ref: "api/tests/integration/test_capture.py::test_no_orphan_autosave"
        status: pass
    human_judgment: false
  - id: D7
    description: "PATCH on task draft auto-saves to tasks table (polymorphic PATCH path)"
    requirement: CAP-03
    verification:
      - kind: integration
        ref: "api/tests/integration/test_capture.py::test_patch_task_type_resets"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-07-30
status: complete
---

# Phase 01 Plan 02: Capture Timeout State Machine Summary

**In-process asyncio 30s draft inactivity auto-save with polymorphic table routing, PATCH timer reset, and confirm cancel**

## Performance

- **Duration:** 15 min
- **Started:** 2026-07-30T02:48:11Z
- **Completed:** 2026-07-30T03:03:00Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- `DraftTimeoutManager` singleton: `schedule_timeout` / `cancel_timeout` with per-type autosave UPDATE
- `POST /drafts` schedules 30s timer after commit; `DRAFT_TIMEOUT_SECONDS` env for tests
- `PATCH /drafts/{id}` updates title/summary/category_id and resets timer (D-06)
- `POST /drafts/{id}/confirm` sets `confirmed` and cancels timer (D-07)
- 7 new integration tests + 13 total capture tests green

## Task Commits

1. **Task 1: Tracer — 30s auto-save path** - `06b3618` (feat)
2. **Task 2: Tests (TDD RED)** - `f3d1a3e` (test)
3. **Task 2: PATCH reset + confirm cancel** - `498838c` (feat)

**Plan metadata:** pending (docs commit)

## Files Created/Modified

- `api/app/services/timeout.py` - DraftTimeoutManager + polymorphic autosave
- `api/app/routers/capture.py` - async create + PATCH + confirm wired to timer
- `api/app/models/note.py` - DraftUpdate schema
- `api/tests/conftest.py` - async_api_client fixture for background task tests
- `api/tests/integration/test_capture.py` - autosave, patch reset, confirm, parallel, orphan guard

## Decisions Made

- Async endpoints for timer scheduling (sync threadpool had no running event loop)
- AsyncClient integration tests for timeout behavior (TestClient does not pump background tasks)
- Item type for PATCH/confirm resolved via `board_items` VIEW lookup

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Sync POST /drafts cannot asyncio.create_task**
- **Found during:** Task 1 verify
- **Issue:** `RuntimeError: no running event loop` when scheduling timer from sync endpoint in threadpool
- **Fix:** Changed `create_draft` to `async def`
- **Files modified:** api/app/routers/capture.py
- **Committed in:** 06b3618

**2. [Rule 3 - Blocking] TestClient does not run background asyncio tasks**
- **Found during:** Task 1 verify
- **Issue:** `time.sleep` after POST left draft status unchanged — timer never fired
- **Fix:** Added `async_api_client` fixture; autosave tests use `AsyncClient` + `asyncio.sleep`
- **Files modified:** api/tests/conftest.py, api/tests/integration/test_capture.py
- **Committed in:** 06b3618

**3. [Rule 1 - Bug] DRAFT_TIMEOUT_SECONDS captured at import**
- **Found during:** Task 1 verify
- **Issue:** `monkeypatch.setenv` ineffective when constant read at module load
- **Fix:** `_default_timeout_seconds()` reads env at schedule time
- **Files modified:** api/app/services/timeout.py
- **Committed in:** 06b3618

---

**Total deviations:** 3 auto-fixed (2 bugs, 1 blocking)
**Impact on plan:** Test/runtime correctness only; no scope change.

## Issues Encountered

None beyond deviations above.

## User Setup Required

None — uses existing Postgres + `DATABASE_URL`. Optional `DRAFT_TIMEOUT_SECONDS` override for local debugging.

## Next Phase Readiness

- Plans 03/04 can add type-specific read/update on top of timeout state machine
- Phase 3 Hermes plugin can rely on API-side 30s precision (not 60s cron)
- `GET /board-items` already returns `auto_saved` drafts via VIEW

---
*Phase: 01-datenmodell-backend-api*
*Completed: 2026-07-30*

## Self-Check: PASSED

- FOUND: api/app/services/timeout.py
- FOUND: api/app/routers/capture.py (PATCH + confirm)
- FOUND: api/tests/integration/test_capture.py
- FOUND: 06b3618
- FOUND: f3d1a3e
- FOUND: 498838c
