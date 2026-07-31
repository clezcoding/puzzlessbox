---
phase: 02-mcp-server
plan: 01
subsystem: api
tags: [fastmcp, mcp, bearer-auth, httpx, internal-api]
requires:
  - phase: 01-datenmodell-backend-api
    provides: SERVICE_BEARER_TOKEN gateway, POST /drafts, Better Auth user table
provides:
  - mcp_clients table + POST /internal/mcp-auth owner resolution
  - X-Owner-Id guard on API service path (D-08)
  - mcp-server FastMCP app with create_item tracer + wave-0 tests
affects: [02-02, 02-03, 02-04]
tech-stack:
  added: [fastmcp==3.4.4, uvicorn==0.52.0]
  patterns: [OwnerResolvingVerifier two-hop auth, DB-free MCP proxy, factory split for tests]
key-files:
  created:
    - api/app/models/mcp_client.py
    - api/alembic/versions/0004_mcp_clients.py
    - api/app/routers/internal.py
    - mcp-server/app/factory.py
    - mcp-server/app/auth.py
    - mcp-server/app/api_client.py
    - mcp-server/app/tools/items.py
  modified:
    - api/app/auth/jwt.py
    - api/app/core/bootstrap.py
    - api/app/main.py
key-decisions:
  - "Split mcp-server/app/factory.py from server.py so tests import build_mcp_stack without module-level ASGI init"
  - "Pin uvicorn 0.52.0 in mcp-server — fastmcp 3.4.4 conflicts with api-aligned 0.34.0"
patterns-established:
  - "Hermes bearer -> sha256 -> /internal/mcp-auth -> AccessToken claims owner_id -> tool never accepts owner_id param"
  - "MCP httpx client sends Accept v1 + X-Service-Bearer + X-Owner-Id + Idempotency-Key on create_item"
requirements-completed: [MCP-01, MCP-02]
coverage:
  - id: D1
    description: POST /internal/mcp-auth resolves active bearer_hash to owner_id with service bearer gateway
    requirement: MCP-02
    verification:
      - kind: unit
        ref: "api import app.routers.internal + model MCPClient"
        status: pass
    human_judgment: false
  - id: D2
    description: MCP 401 on missing/invalid bearer (WWW-Authenticate + invalid_token)
    requirement: MCP-02
    verification:
      - kind: unit
        ref: "mcp-server/tests/test_auth.py"
        status: pass
    human_judgment: false
  - id: D3
    description: create_item end-to-end header contract to POST /drafts
    requirement: MCP-01
    verification:
      - kind: unit
        ref: "mcp-server/tests/test_api_contract.py"
        status: pass
    human_judgment: false
  - id: D4
    description: MCP /health 200 without authentication
    requirement: MCP-02
    verification:
      - kind: unit
        ref: "mcp-server/tests/test_health.py"
        status: pass
    human_judgment: false
duration: 6min
completed: 2026-07-31
status: complete
---

# Phase 2 Plan 01: MCP Tracer Summary

**Hermes bearer → OwnerResolvingVerifier → /internal/mcp-auth → create_item → POST /drafts with dual-hop service auth**

## Performance

- **Duration:** 6 min
- **Started:** 2026-07-31T02:44:00Z
- **Completed:** 2026-07-31T02:50:00Z
- **Tasks:** 2
- **Files modified:** 27

## Accomplishments

- API `mcp_clients` model + migration + bootstrap (`MCP_BOOTSTRAP_TOKEN`) and `POST /internal/mcp-auth`
- `X-Owner-Id` guard: UUID format + Better Auth `"user"` row required (403 otherwise)
- Greenfield `mcp-server/` FastMCP app: `create_item` tool, health routes, 7 wave-0 tests

## Task Commits

1. **Task 1: API Owner-Auflösung** - `45dc108` (feat)
2. **Task 2: MCP-Grundgerüst (tests RED)** - `8f59f3f` (test)
3. **Task 2: MCP-Grundgerüst (GREEN)** - `f3bd95c` (feat)
4. **Cleanup: pycache** - `972ea08` (chore)

**Plan metadata:** pending (docs commit)

## Files Created/Modified

- `api/app/routers/internal.py` - `POST /internal/mcp-auth` bearer_hash → owner_id
- `api/app/auth/jwt.py` - `X-Owner-Id` override on validated service path
- `mcp-server/app/auth.py` - `OwnerResolvingVerifier(TokenVerifier)`
- `mcp-server/app/api_client.py` - httpx client, resolve_owner, call_api retry D-18
- `mcp-server/app/tools/items.py` - `create_item` from token claims only

## Decisions Made

- `app/factory.py` holds `build_mcp_stack`; `app/server.py` is thin uvicorn entry — avoids import-time ASGI init in tests
- `uvicorn==0.52.0` in mcp-server (fastmcp 3.4.4 dependency conflict with api's 0.34.0)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] fastmcp/uvicorn version conflict**
- **Found during:** Task 2 (pip install)
- **Issue:** `fastmcp==3.4.4` requires `uvicorn==0.52.0`, not pinned `0.34.0`
- **Fix:** Pin `uvicorn==0.52.0` in `mcp-server/requirements.txt`
- **Files modified:** `mcp-server/requirements.txt`
- **Committed in:** `f3bd95c`

**2. [Rule 2 - Missing Critical] TokenVerifier super().__init__**
- **Found during:** Task 2 tests
- **Issue:** `OwnerResolvingVerifier` missing `resource_base_url` from parent init
- **Fix:** `super().__init__(base_url=...)`
- **Files modified:** `mcp-server/app/auth.py`
- **Committed in:** `f3bd95c`

**3. [Rule 1 - Bug] Accidental `__pycache__` commit**
- **Found during:** Task 2 commit review
- **Issue:** `.pyc` files staged from local pytest
- **Fix:** `git rm --cached`, add `__pycache__/` to `.gitignore`
- **Committed in:** `972ea08`

---

**Total deviations:** 3 auto-fixed (1 blocking, 1 missing critical, 1 bug)
**Impact on plan:** No scope change; tracer path intact.

## Issues Encountered

- In-memory FastMCP `Client` rejects `auth=` string — contract tests use patched `get_access_token` + direct `create_item` call (same header assertions)

## User Setup Required

Set before production bootstrap:
- `MCP_BOOTSTRAP_TOKEN` — Hermes bearer (openssl rand -hex 32); hashed at insert, never logged
- `SERVICE_OWNER_ID` — UUID of existing Better Auth user row

## Next Phase Readiness

- Tracer proven; ready for 02-02 (categories/move API) and 02-03 (remaining tools)
- Deploy path (02-04) still needs Dockerfile + GHCR workflow

## Self-Check: PASSED

- FOUND: `.planning/phases/02-mcp-server/02-01-SUMMARY.md`
- FOUND: `api/app/routers/internal.py`
- FOUND: `mcp-server/app/server.py`
- FOUND: commits 45dc108, 8f59f3f, f3bd95c, 972ea08

---
*Phase: 02-mcp-server*
*Completed: 2026-07-31*
