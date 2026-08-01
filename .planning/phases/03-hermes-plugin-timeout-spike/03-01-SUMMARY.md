---
phase: 03-hermes-plugin-timeout-spike
plan: 01
subsystem: api
tags: [fastapi, mcp, soft-delete, discard, draft-poll, autosave]

requires:
  - phase: 02-mcp-server
    provides: MCP tool registration pattern, call_api, owner_id from access token claims
  - phase: 01-datenmodell-backend-api
    provides: capture router, DraftTimeoutManager, board_items view
provides:
  - POST /drafts/{id}/discard soft-delete endpoint
  - GET /drafts/{id} poll read path
  - MCP discard_item and get_draft_status tools
  - item_status enum value discarded (migration 0005)
affects:
  - 03-02-PLAN.md
  - 03-03-PLAN.md

tech-stack:
  added: []
  patterns:
    - "Soft-delete via deleted_at + status discarded on type-specific table"
    - "MCP poll surface reduced to {id,type,status} for get_draft_status"

key-files:
  created:
    - api/alembic/versions/0005_item_status_discarded.py
    - mcp-server/tests/test_items.py
  modified:
    - api/app/routers/capture.py
    - api/app/models/enums.py
    - api/tests/integration/test_capture.py
    - mcp-server/app/tools/items.py
    - mcp-server/app/tools/__init__.py
    - mcp-server/tests/conftest.py
    - mcp-server/tests/test_api_contract.py

key-decisions:
  - "Added Alembic 0005 to extend item_status enum with discarded — required for plan response shape"
  - "get_draft_status strips title/summary/category_id per minimal poll surface (D-06)"

patterns-established:
  - "discard_draft cancels DraftTimeoutManager after commit"
  - "get_draft filters deleted_at IS NULL for tenant-safe poll reads"

requirements-completed: [CAP-02, MCP-03, MCP-04]

coverage:
  - id: D1
    description: POST /drafts/{id}/discard soft-deletes draft/auto_saved with deleted_at and timer cancel
    requirement: CAP-02
    verification:
      - kind: integration
        ref: "api/tests/integration/test_capture.py#test_discard_draft_204"
        status: pass
      - kind: integration
        ref: "api/tests/integration/test_capture.py#test_discard_draft_auto_saved"
        status: pass
    human_judgment: false
  - id: D2
    description: GET /drafts/{id} returns poll fields; 404 for foreign/deleted/unknown
    requirement: MCP-04
    verification:
      - kind: integration
        ref: "api/tests/integration/test_capture.py#test_get_draft_returns_status_and_fields"
        status: pass
      - kind: integration
        ref: "api/tests/integration/test_capture.py#test_get_draft_not_found"
        status: pass
    human_judgment: false
  - id: D3
    description: confirm_draft idempotent on auto_saved (D-08)
    requirement: CAP-02
    verification:
      - kind: integration
        ref: "api/tests/integration/test_capture.py#test_confirm_after_autosave_idempotent"
        status: pass
    human_judgment: false
  - id: D4
    description: MCP discard_item calls API discard with owner from token claims
    requirement: MCP-03
    verification:
      - kind: unit
        ref: "mcp-server/tests/test_items.py#test_discard_item_calls_api"
        status: pass
    human_judgment: false
  - id: D5
    description: MCP get_draft_status polls GET /drafts/{id}, returns {id,type,status}
    requirement: MCP-03
    verification:
      - kind: unit
        ref: "mcp-server/tests/test_items.py#test_get_draft_status_calls_api"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-08-01
status: complete
---

# Phase 03 Plan 01: Discard API + MCP Tools Summary

**Soft-delete discard endpoint, draft poll GET, and MCP discard_item/get_draft_status with discarded enum migration**

## Performance

- **Duration:** 15 min
- **Started:** 2026-08-01T03:09:00Z
- **Completed:** 2026-08-01T03:24:00Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- `POST /drafts/{id}/discard` sets `deleted_at`, `status=discarded`, cancels timeout timer
- `GET /drafts/{id}` returns `{id,type,status,title,category_id,summary}` for active drafts
- `confirm_draft` already accepted `auto_saved`; integration test added for D-08
- MCP `discard_item` and `get_draft_status` registered (8 tools total)
- 8 API + 9 MCP new tests; 21 API + 32 MCP suite green

## Task Commits

1. **Task 1: API discard + get_draft** — `b8c515b` (test), `03bbe71` (feat)
2. **Task 2+3: MCP discard_item + get_draft_status** — `1bd3cc0` (test), `f5aebc6` (feat)

## Files Created/Modified

- `api/alembic/versions/0005_item_status_discarded.py` — enum `discarded`
- `api/app/routers/capture.py` — `discard_draft`, `get_draft`
- `api/tests/integration/test_capture.py` — 8 new integration tests
- `mcp-server/app/tools/items.py` — `discard_item`, `get_draft_status`
- `mcp-server/tests/test_items.py` — 9 MCP tool tests

## Decisions Made

- Extended PostgreSQL `item_status` enum via migration — plan requires `status:'discarded'` but schema only had draft/auto_saved/confirmed

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Alembic migration for discarded enum value**
- **Found during:** Task 1 (discard_draft implementation)
- **Issue:** `item_status` enum lacked `discarded`; UPDATE would fail at DB layer
- **Fix:** Added `0005_item_status_discarded.py` and `ItemStatus.discarded`
- **Files modified:** `api/alembic/versions/0005_item_status_discarded.py`, `api/app/models/enums.py`
- **Verification:** `test_discard_draft_204` passes with status discarded in DB
- **Committed in:** `03bbe71`

---

**Total deviations:** 1 auto-fixed (Rule 2)
**Impact on plan:** Required for correctness; no scope creep.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 02/03 can call `discard_item` and `get_draft_status` from Hermes plugin
- Run `alembic upgrade head` on deploy targets before using discard

## Self-Check: PASSED

- `03-01-SUMMARY.md` — FOUND
- Commits `b8c515b`, `03bbe71`, `1bd3cc0`, `f5aebc6` — FOUND

---
*Phase: 03-hermes-plugin-timeout-spike*
*Completed: 2026-08-01*
