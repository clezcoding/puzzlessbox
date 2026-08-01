---
phase: 03-hermes-plugin-timeout-spike
plan: 03
subsystem: api
tags: [hermes, mcp, dialog, concurrency, autosave-poll, pytest]

requires:
  - phase: 03-hermes-plugin-timeout-spike
    provides: discard_item, get_draft_status MCP tools (Plan 01)
  - phase: 03-hermes-plugin-timeout-spike
    provides: hermes-plugin tracer skeleton (Plan 02)
provides:
  - conversational edit flow with silent ACK (D-01/D-02/D-03)
  - single-active-draft concurrency with sichern/verwerfen/warten (D-07)
  - post-autosave poll via MCP get_draft_status (D-05/D-06)
  - status-aware confirm ACK from live MCP status (D-08)
  - list_categories + type/category heuristics before create_item (D-09/D-10)
affects: [03-04]

tech-stack:
  added: []
  patterns:
    - handle_user_message state machine (edit/confirm/discard/conflict)
    - schedule_autosave_poll fire-and-forget via asyncio.create_task
    - call_mcp_* wrappers sharing _call_mcp_tool helper

key-files:
  created: []
  modified:
    - hermes-plugin/dialog.py
    - hermes-plugin/tools.py
    - hermes-plugin/tests/test_orchestration.py
    - hermes-plugin/tests/conftest.py

key-decisions:
  - "Unrecognized free text with active draft routes to start_capture_flow → D-07 conflict (not edit fallback)"
  - "Note type category hints prefer Inbox first for plain captures"
  - "Inbox fallback UUID hardcoded when categories lack Inbox row (low-confidence D-10)"

patterns-established:
  - "Confirm ACK reads live call_mcp_get_item_status, not session snapshot (D-08)"
  - "Poll updates session status defense-in-depth but confirm still uses live MCP"

requirements-completed: [CAP-02, MCP-03]

coverage:
  - id: D1
    description: "Freitext-Edit nach Karte ruft update_item nur mit geänderten Keys auf"
    requirement: CAP-02
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_orchestration.py#test_edit_free_text_calls_update_item_only_changed_keys"
        status: pass
    human_judgment: false
  - id: D2
    description: "Silent ACK nach Edit — kein format_confirmation"
    requirement: CAP-02
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_orchestration.py#test_edit_silent_ack_no_new_card"
        status: pass
    human_judgment: false
  - id: D3
    description: "Status-aware ACK bei confirm (draft vs auto_saved) via live MCP"
    requirement: CAP-02
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_orchestration.py#test_explicit_confirm_status_aware_ack_auto_saved"
        status: pass
    human_judgment: false
  - id: D4
    description: "Single-active-draft Konflikt mit sichern/verwerfen/warten (D-07)"
    requirement: CAP-02
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_orchestration.py#test_single_active_draft_conflict"
        status: pass
    human_judgment: false
  - id: D5
    description: "list_categories vor create_item (D-09)"
    requirement: CAP-02
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_orchestration.py#test_list_categories_called_before_create_item"
        status: pass
    human_judgment: false
  - id: D6
    description: "Post-autosave poll ping bei auto_saved, asyncio.sleep kein cron (D-05/D-06/MCP-04)"
    requirement: MCP-03
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_orchestration.py#test_autosave_ping_sent_on_auto_saved"
        status: pass
    human_judgment: false
  - id: D7
    description: "Plugin nur MCP-Client — keine DB-Libs"
    requirement: MCP-03
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_orchestration.py#test_tools_only_mcp_client_path"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-08-01
status: complete
---

# Phase 03 Plan 03: Dialog Orchestration Summary

**Konversationeller Edit, Single-Active-Draft-Concurrency und MCP-Autosave-Poll mit live status-aware ACK**

## Performance

- **Duration:** 8 min
- **Started:** 2026-08-01T03:15:19Z
- **Completed:** 2026-08-01T03:23:00Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- `handle_user_message` Zustandsmaschine: Edit (D-01/D-02/D-03), confirm/discard, D-07 Konflikt
- `start_capture_flow`: list_categories → Heuristik (URL→link, datetime→event) → create_item
- `schedule_autosave_poll`: 32s asyncio.sleep → MCP status → Chat-Ping bei auto_saved
- MCP-Wrapper: update_item, confirm_item, discard_item, get_item_status, list_categories
- 21 neue Orchestration-Tests (12 Task 1 + 6 Task 2 + 3 bestehende angepasst)

## Task Commits

1. **Task 1+2 tests (RED)** - `5900a7b` (test)
2. **Task 1+2 implementation (GREEN)** - `0d83895` (feat)

**Plan metadata:** pending docs commit

## Files Created/Modified

- `hermes-plugin/dialog.py` — edit/confirm/discard/conflict/poll state machine
- `hermes-plugin/tools.py` — _call_mcp_tool + 5 neue MCP wrappers
- `hermes-plugin/tests/test_orchestration.py` — 18 neue Tests
- `hermes-plugin/tests/conftest.py` — MockSession + fixtures

## Decisions Made

- Unrecognized text with active draft → new capture attempt → D-07 conflict reply
- Note category hints: Inbox first (plain captures land in Inbox)
- Hardcoded Inbox UUID for D-10 fallback when category list lacks Inbox

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] D-07 conflict not triggered for new capture text**
- **Found during:** Task 1 verification
- **Issue:** Free text with active draft fell through to fallback hint instead of conflict
- **Fix:** Route empty edit extraction to `start_capture_flow` when no pending_capture_text
- **Files modified:** hermes-plugin/dialog.py
- **Committed in:** 0d83895

**2. [Rule 1 - Bug] Note category picked Notizen over Inbox**
- **Found during:** Task 1 verification (happy path regression)
- **Issue:** Category hint order preferred Notizen for note type
- **Fix:** Reorder hints to `["Inbox", "Notizen", "Notiz"]`
- **Files modified:** hermes-plugin/dialog.py
- **Committed in:** 0d83895

---

**Total deviations:** 2 auto-fixed (both Rule 1 bugs)
**Impact on plan:** Correctness fixes only; no scope creep.

## Issues Encountered

None beyond deviations above.

## User Setup Required

None — MCP_BEARER configured on Hermes VPS per D-12 (Plan 04).

## Next Phase Readiness

- Plan 04 can wire channel tests to `handle_user_message` + `format_confirmation`
- setup.sh for MCP_URL/MCP_BEARER env on Hermes VPS

## Self-Check: PASSED

- hermes-plugin/dialog.py — FOUND
- hermes-plugin/tools.py — FOUND
- hermes-plugin/tests/test_orchestration.py — FOUND
- Commits 5900a7b, 0d83895 — FOUND

---
*Phase: 03-hermes-plugin-timeout-spike*
*Completed: 2026-08-01*
