---
phase: 02-mcp-server
plan: 03
subsystem: mcp
tags: [fastmcp, mcp-tools, httpx, pydantic, mcp-01]
requires:
  - phase: 02-mcp-server
    provides: create_item tracer + call_api retry from 02-01
  - phase: 02-mcp-server
    provides: GET/POST /categories + PATCH /items from 02-02
provides:
  - Six MCP-01 tools with validated schemas and API mapping
  - confirm_item optional PATCH then POST confirm (D-10)
  - update_item PATCH /drafts; move_item PATCH /items (D-11/D-12)
  - list_categories GET /categories; create_category POST /categories
  - Schema reject + error-map + retry contract tests
affects: [02-04, 03-hermes-plugin]
tech-stack:
  added: []
  patterns: [register_tools split items/categories aggregated in app.tools, FunctionTool.run for schema reject tests]
key-files:
  created:
    - mcp-server/app/tools/categories.py
    - mcp-server/tests/test_tools_schema.py
  modified:
    - mcp-server/app/tools/items.py
    - mcp-server/app/tools/__init__.py
    - mcp-server/app/factory.py
    - mcp-server/tests/conftest.py
    - mcp-server/tests/test_api_contract.py
key-decisions:
  - "register_tools in app.tools aggregates items + categories register functions"
  - "Schema reject tests invoke FunctionTool.run with bad args — fastmcp ValidationError before network"
  - "create_category ships name-only — matches 02-02 CategoryCreate minimal contract"
patterns-established:
  - "confirm_item: optional patch dict then POST /drafts/{id}/confirm"
  - "Scope fence: exactly 6 mcp.tool() registrations across items.py + categories.py"
requirements-completed: [MCP-01]
coverage:
  - id: D1
    description: Six tools registered with validated schemas mapping to internal API
    requirement: MCP-01
    verification:
      - kind: unit
        ref: "mcp-server pytest tests -q (22 passed); test_six_tools_registered"
        status: pass
    human_judgment: false
  - id: D2
    description: confirm_item optional PATCH then POST confirm (D-10)
    requirement: MCP-01
    verification:
      - kind: unit
        ref: "test_confirm_item_patch_then_confirm"
        status: pass
    human_judgment: false
  - id: D3
    description: API errors map to ToolError code:message (D-13)
    requirement: MCP-01
    verification:
      - kind: unit
        ref: "test_error_map_not_found"
        status: pass
    human_judgment: false
  - id: D4
    description: Retry 502 once; 500 no retry; 503 twice fails (D-18)
    requirement: MCP-01
    verification:
      - kind: unit
        ref: "test_call_api_retries_502_once; test_call_api_no_retry_on_500; test_call_api_503_twice_raises"
        status: pass
    human_judgment: false
  - id: D5
    description: Schema-invalid tool args rejected before network hop
    requirement: MCP-01
    verification:
      - kind: unit
        ref: "mcp-server/tests/test_tools_schema.py"
        status: pass
    human_judgment: false
duration: 12min
completed: 2026-07-31
status: complete
---

# Phase 2 Plan 03: MCP Tool Expansion Summary

**Six FastMCP tools — create/confirm/update/move items + list/create categories — with Pydantic schema gates and httpx API contract tests**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-31T03:00:00Z
- **Completed:** 2026-07-31T03:12:00Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- `confirm_item`, `update_item`, `move_item` on `/drafts` and `/items` with owner from token claims
- `list_categories`, `create_category` on `/categories`
- Mock transport tracks all API calls; retry and NOT_FOUND error-map tests
- Full suite: 22 tests passed

## Task Commits

1. **Task 1: Item tools** - `53ffdc3` (feat)
2. **Task 2: Category tools + schema tests** - `e40b1ad` (feat)

**Plan metadata:** pending (docs commit)

## Files Created/Modified

- `mcp-server/app/tools/items.py` — confirm_item, update_item, move_item
- `mcp-server/app/tools/categories.py` — list_categories, create_category
- `mcp-server/app/tools/__init__.py` — aggregated register_tools for all 6 tools
- `mcp-server/app/factory.py` — import register_tools from app.tools
- `mcp-server/tests/test_api_contract.py` — mapping, retry, error-map, six-tool gate
- `mcp-server/tests/test_tools_schema.py` — Pydantic reject before network
- `mcp-server/tests/conftest.py` — expanded mock transport for all endpoints

## Decisions Made

- `app.tools.register_tools` delegates to items + categories modules — factory imports single entry
- Schema tests use `FunctionTool.from_function` + `await tool.run({...})` for validation errors
- `create_category` accepts `name` only — aligned with 02-02 minimal API

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- SC1 complete: all 6 MCP-01 tools registered and contract-tested
- Ready for Hermes plugin integration (Phase 3) and deploy verification (02-04)

## Self-Check: PASSED

- FOUND: `.planning/phases/02-mcp-server/02-03-SUMMARY.md`
- FOUND: `mcp-server/app/tools/categories.py`
- FOUND: `mcp-server/tests/test_tools_schema.py`
- FOUND: commits 53ffdc3, e40b1ad

---
*Phase: 02-mcp-server*
*Completed: 2026-07-31*
