---
phase: 03-hermes-plugin-timeout-spike
plan: 02
subsystem: api
tags: [hermes, mcp, capture, pydantic, httpx, pytest]

requires:
  - phase: 02-mcp-server
    provides: create_item MCP tool, HTTPS Bearer auth
provides:
  - hermes-plugin skeleton with MCP-only orchestration
  - format_confirmation German Stash-Check template (spike 004 port)
  - handle_user_message happy path tracer
affects: [03-03, 03-04]

tech-stack:
  added: [httpx, pydantic, mcp, pydantic-settings, pytest-asyncio]
  patterns:
    - MCP client via streamable_http_client + Bearer from env
    - kanalneutraler Plain-Text formatter ohne Timer im Plugin

key-files:
  created:
    - hermes-plugin/config.py
    - hermes-plugin/schemas.py
    - hermes-plugin/tools.py
    - hermes-plugin/formatters.py
    - hermes-plugin/dialog.py
    - hermes-plugin/plugin.yaml
    - hermes-plugin/pyproject.toml
    - hermes-plugin/tests/test_formatter.py
    - hermes-plugin/tests/test_orchestration.py
  modified: []

key-decisions:
  - "streamable_http_client (MCP SDK) statt spike streamablehttp_client Alias"
  - "Inbox category_id stub via MCP_CATEGORY_ID env mit Test-UUID Fallback bis Plan 03 list_categories"

patterns-established:
  - "Plugin = reiner MCP-Client; keine DB-Libs, kein asyncio.sleep(30)"
  - "format_confirmation nutzt DraftPreview pydantic Model"

requirements-completed: [CAP-02, MCP-03, MCP-04]

coverage:
  - id: D1
    description: "handle_user_message happy path — MCP create_item mock → deutsche Stash-Check-Karte"
    requirement: CAP-02
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_orchestration.py#test_handle_user_message_happy_path"
        status: pass
    human_judgment: false
  - id: D2
    description: "format_confirmation für alle vier Typ-Labels mit Stash-Check-Template"
    requirement: CAP-02
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_formatter.py#test_format_confirmation_all_type_labels"
        status: pass
    human_judgment: false
  - id: D3
    description: "Plugin ohne direkten DB-Zugriff — nur MCP-Client-Pfad in tools.py"
    requirement: MCP-03
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_orchestration.py#test_tools_only_mcp_client_path"
        status: pass
    human_judgment: false
  - id: D4
    description: "Kein 30s-Timer im Plugin-Code"
    requirement: MCP-04
    verification:
      - kind: other
        ref: "grep -r asyncio.sleep(30) hermes-plugin/ → keine Treffer"
        status: pass
    human_judgment: false
  - id: D5
    description: "plugin.yaml + pyproject.toml + .gitignore — env-only Secrets, keine DB-deps"
    requirement: MCP-03
    verification:
      - kind: other
        ref: "task 2 automated verify (plugin.yaml, pyproject.toml, .gitignore, grep Bearer)"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-08-01
status: complete
---

# Phase 03 Plan 02: Hermes-Plugin Tracer Summary

**Hermes-Plugin Tracer: User-Text → MCP create_item → deutsche Stash-Check-Karte; reiner MCP-Client ohne Timer/DB**

## Performance

- **Duration:** 5 min
- **Started:** 2026-08-01T03:07:00Z
- **Completed:** 2026-08-01T03:12:11Z
- **Tasks:** 2
- **Files modified:** 14

## Accomplishments

- `hermes-plugin/` Skeleton mit config, schemas, tools, formatters, dialog (happy path only)
- `format_confirmation` identisch zu spike 004 (Stash-Check, Eintrag sichern, 30s-Hinweis)
- `call_mcp_create_item` via `streamable_http_client` + Bearer aus `MCP_BEARER`
- plugin.yaml / pyproject.toml / .gitignore für D-11/D-12 (env-only Secrets, keine DB-Libs)

## Task Commits

1. **Task 1: End-to-end tracer** - `1c11b9b` (feat)
2. **Task 2: Manifest + packaging** - `7e74a45` (chore)
3. **pyproject readme fix** - `d9c8d10` (fix)

**Plan metadata:** pending docs commit

## Files Created/Modified

- `hermes-plugin/config.py` — pydantic-settings MCP_URL, MCP_BEARER, ENV
- `hermes-plugin/tools.py` — async MCP create_item client
- `hermes-plugin/formatters.py` — CAP-02 Stash-Check template
- `hermes-plugin/dialog.py` — handle_user_message happy path
- `hermes-plugin/plugin.yaml` — Hermes manifest, requires_env MCP_BEARER
- `hermes-plugin/pyproject.toml` — httpx, pydantic, mcp, pydantic-settings
- `hermes-plugin/tests/test_formatter.py` — TYPE_LABELS coverage
- `hermes-plugin/tests/test_orchestration.py` — MCP-only orchestration mock

## Decisions Made

- MCP SDK import `streamable_http_client` (spike used outdated `streamablehttp_client` name)
- Inbox `category_id` stub until Plan 03 `list_categories`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] MCP SDK import name `streamable_http_client`**
- **Found during:** Task 1 verification
- **Issue:** `streamablehttp_client` import fails on installed mcp package
- **Fix:** Use `streamable_http_client` from `mcp.client.streamable_http`
- **Files modified:** hermes-plugin/tools.py, hermes-plugin/tests/test_orchestration.py
- **Committed in:** 1c11b9b

**2. [Rule 3 - Blocking] Local venv for pytest (PEP 668)**
- **Found during:** Task 1 verification
- **Issue:** System Python blocks pip install without venv
- **Fix:** `hermes-plugin/.venv` for local test runs; added `.venv/` to .gitignore
- **Files modified:** hermes-plugin/.gitignore
- **Committed in:** 7e74a45

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** Correctness fixes only; no scope creep.

## Issues Encountered

None beyond deviations above.

## User Setup Required

None — MCP_BEARER configured on Hermes VPS per D-12 (Plan 04 setup script).

## Next Phase Readiness

- Plan 03 can extend `dialog.handle_user_message` (edit, concurrency, poll)
- Plan 04 channel tests can import `format_confirmation` + dialog handler

## Self-Check: PASSED

- hermes-plugin/config.py — FOUND
- hermes-plugin/tools.py — FOUND
- hermes-plugin/plugin.yaml — FOUND
- Commits 1c11b9b, 7e74a45, d9c8d10 — FOUND

---
*Phase: 03-hermes-plugin-timeout-spike*
*Completed: 2026-08-01*
