---
phase: 01-datenmodell-backend-api
plan: 06
subsystem: auth
tags: [better-auth, jwks, jwt, fastapi, idempotency, draft-crud, signup-lock]

requires:
  - phase: 01-datenmodell-backend-api
    provides: FastAPI shell + schema/RLS (Plans 01, 05)
provides:
  - Better Auth webapp bootstrap (JWKS, email/password, signup lock D-24)
  - FastAPI auth proxy + JWKS verify + session cookie (D-21, D-22)
  - Service bearer auth via service_principals (D-23)
  - POST /drafts polymorphic draft create + GET /board-items (CAP-01)
  - Idempotency-Key replay on POST /drafts (D-34)
affects: [01-02, 01-03, 01-04, phase-2-mcp]

tech-stack:
  added: [better-auth@1.6.25, next@16]
  patterns: [Better Auth databaseHooks signup lock, PyJWKClient RS256 verify, capture router consolidation]

key-files:
  created:
    - webapp/lib/auth.config.ts
    - webapp/app/api/auth/[...all]/route.ts
    - api/app/auth/jwt.py
    - api/app/routers/auth.py
    - api/app/routers/capture.py
    - api/alembic/versions/0002_idempotency.py
    - api/tests/unit/test_auth.py
    - api/tests/integration/test_auth.py
    - api/tests/integration/test_capture.py
  modified:
    - api/app/main.py
    - api/app/core/config.py
    - api/app/models/board.py
    - api/tests/conftest.py
    - api/tests/integration/test_tenancy.py

key-decisions:
  - "Capture draft create consolidated in capture.py (not per-type routers) until Plans 03/04"
  - "board-items adds explicit owner_id WHERE alongside RLS (VIEW security invoker gap)"
  - "Login prefers Better Auth sign-in token before /token fetch"

patterns-established:
  - "puzzlessbox_session cookie on .puzzlesstool.online + Bearer JWT both accepted (D-22)"
  - "X-Service-Bearer constant-time compare + bearer_hash lookup (D-23)"

requirements-completed: [AUTH-01, AUTH-02, AUTH-03, AUTH-04, CAP-01]

coverage:
  - id: D1
    description: "Email/password signup via Better Auth proxy when user_count==0"
    requirement: AUTH-01
    verification:
      - kind: integration
        ref: "api/tests/integration/test_auth.py::test_registration"
        status: pass
    human_judgment: false
  - id: D2
    description: "JWT verified via JWKS; invalid/expired returns 401"
    requirement: AUTH-02
    verification:
      - kind: unit
        ref: "api/tests/unit/test_auth.py::test_jwt_decode"
        status: pass
      - kind: unit
        ref: "api/tests/unit/test_auth.py::test_jwt_decode_expired"
        status: pass
    human_judgment: false
  - id: D3
    description: "Second signup returns 409 SIGNUP_LOCKED"
    requirement: AUTH-03
    verification:
      - kind: integration
        ref: "api/tests/integration/test_auth.py::test_signup_lock"
        status: pass
    human_judgment: false
  - id: D4
    description: "Cross-tenant board-items isolation returns empty for foreign JWT"
    requirement: AUTH-04
    verification:
      - kind: integration
        ref: "api/tests/integration/test_capture.py::test_cross_tenant_board_items_empty"
        status: pass
    human_judgment: false
  - id: D5
    description: "POST /drafts persists polymorphic draft; GET /board-items lists caller rows"
    requirement: CAP-01
    verification:
      - kind: integration
        ref: "api/tests/integration/test_capture.py::test_draft_roundtrip"
        status: pass
    human_judgment: false
  - id: D6
    description: "Login sets parent-domain httponly session cookie"
    requirement: AUTH-02
    verification:
      - kind: integration
        ref: "api/tests/integration/test_auth.py::test_login_persists_session"
        status: pass
    human_judgment: false
  - id: D7
    description: "Service bearer resolves owner without JWT"
    requirement: AUTH-02
    verification:
      - kind: unit
        ref: "api/tests/unit/test_auth.py::test_service_bearer"
        status: pass
    human_judgment: false
  - id: D8
    description: "Idempotency-Key replay returns identical 201 without duplicate draft"
    requirement: CAP-01
    verification:
      - kind: integration
        ref: "api/tests/integration/test_capture.py::test_idempotency"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-07-30
status: complete
---

# Phase 01 Plan 06: Auth + Draft CRUD Summary

**Better Auth JWKS shell + FastAPI RS256 verify, signup lock, service bearer, and polymorphic draft CRUD with idempotency**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-30T02:40:00Z
- **Completed:** 2026-07-30T02:52:00Z
- **Tasks:** 2
- **Files modified:** 20

## Accomplishments

- Minimal `webapp/` Better Auth bootstrap: email/password, JWT plugin/JWKS, `databaseHooks` signup lock (D-24)
- FastAPI `/auth/signup|login|verify` proxy + `get_current_owner` via PyJWKClient (D-21) and `puzzlessbox_session` cookie (D-22)
- `POST /drafts` routes note/link/task/event inserts; `GET /board-items` reads VIEW with owner filter
- `X-Service-Bearer` + `0002_idempotency` migration for MCP prep and Hermes retries (D-23, D-34)
- 24 pytest cases green against migrated Postgres

## Task Commits

1. **Task 1: Tracer end-to-end** - `53053a3` (feat)
2. **Task 2: Tests (TDD RED)** - `f93e045` (test)
3. **Task 2: Service bearer + idempotency** - `0eb6d5d` (feat)
4. **RLS test isolation fix** - `1ecce13` (fix)

**Plan metadata:** `805b46c` (docs: complete plan)

## Files Created/Modified

- `webapp/lib/auth.config.ts` - Better Auth Postgres adapter + signup lock hook
- `webapp/app/api/auth/[...all]/route.ts` - `/api/auth/*` including JWKS
- `api/app/auth/jwt.py` - JWKS verify, cookie/bearer, service bearer
- `api/app/routers/auth.py` - signup/login/verify proxy to Better Auth
- `api/app/routers/capture.py` - draft CRUD + idempotency
- `api/alembic/versions/0002_idempotency.py` - idempotency_keys table
- `api/tests/unit/test_auth.py` - JWT + service bearer unit tests
- `api/tests/integration/test_auth.py` - signup lock + login cookie tests
- `api/tests/integration/test_capture.py` - draft roundtrip, cross-tenant, idempotency

## Decisions Made

- Consolidated polymorphic draft create in `capture.py` (documented in module docstring)
- Added explicit `owner_id` filter on `board_items` query (RLS on VIEW insufficient alone)
- Login checks sign-in JSON token before calling Better Auth `/token`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] BoardItem JSON serializes `type` not `board_type`**
- **Found during:** Task 1 verify
- **Issue:** GET /board-items response lacked `type` key expected by tests
- **Fix:** Added `serialization_alias="type"` on `BoardItem.board_type`
- **Files modified:** api/app/models/board.py
- **Committed in:** 53053a3

**2. [Rule 1 - Bug] Draft inserts missing timestamps**
- **Found during:** Task 1 verify
- **Issue:** SQLModel insert sent NULL `created_at`/`updated_at` despite DB defaults
- **Fix:** Set UTC timestamps in `_insert_draft` before commit
- **Files modified:** api/app/routers/capture.py
- **Committed in:** 53053a3

**3. [Rule 2 - Missing Critical] board-items owner filter**
- **Found during:** Task 2 cross-tenant test
- **Issue:** `board_items` VIEW query returned all tenants without explicit filter
- **Fix:** `WHERE owner_id = :owner_id` using authenticated context (D-25)
- **Files modified:** api/app/routers/capture.py
- **Committed in:** 0eb6d5d

**4. [Rule 1 - Bug] Idempotency JSONB insert**
- **Found during:** Task 2 verify
- **Issue:** psycopg2 could not adapt Python dict for JSONB column
- **Fix:** `json.dumps` + `CAST(:response AS jsonb)`
- **Files modified:** api/app/routers/capture.py
- **Committed in:** 0eb6d5d

**5. [Rule 1 - Bug] RLS test polluted by integration commits**
- **Found during:** Full suite verify
- **Issue:** `test_rls` used shared `owner_id_a` with committed draft rows from API tests
- **Fix:** Per-test random owner UUIDs in `test_tenancy.py`
- **Files modified:** api/tests/integration/test_tenancy.py

---

**Total deviations:** 5 auto-fixed (4 bugs, 1 missing critical)
**Impact on plan:** Correctness/security fixes only; no scope creep.

## Issues Encountered

None beyond deviations above.

## User Setup Required

None - requires local Postgres with `DATABASE_URL` and migrated schema (`alembic upgrade head`). Better Auth webapp needs `npm install` under `webapp/` before running Next.js in deployment.

## Next Phase Readiness

- Plan 02 can wire timeout state machine on `POST /drafts` / PATCH paths
- Plans 03/04 can split type-specific routers; auth + draft create path proven
- Phase 2 MCP can use `X-Service-Bearer` + `service_principals` mapping

---
*Phase: 01-datenmodell-backend-api*
*Completed: 2026-07-30*

## Self-Check: PASSED

- FOUND: webapp/lib/auth.config.ts
- FOUND: api/app/auth/jwt.py
- FOUND: api/alembic/versions/0002_idempotency.py
- FOUND: api/tests/integration/test_capture.py
- FOUND: 53053a3
- FOUND: f93e045
- FOUND: 0eb6d5d
