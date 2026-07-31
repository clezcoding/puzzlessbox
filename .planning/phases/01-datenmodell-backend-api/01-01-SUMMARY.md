---
phase: 01-datenmodell-backend-api
plan: 01
subsystem: api
tags: [fastapi, pytest, sqlmodel, health, versioning, jwks]

requires: []
provides:
  - FastAPI shell with /health and /ready
  - Accept-header API versioning middleware
  - Unified error response shape
  - Wave 0 pytest harness (mock Postgres + JWKS + owner fixtures)
affects: [01-05, 01-06]

tech-stack:
  added: [fastapi==0.138.0, sqlmodel==0.0.22, pydantic-settings, pytest, pytest-asyncio]
  patterns: [Accept-versioning middleware, unified error handler, transactional test sessions]

key-files:
  created:
    - api/app/main.py
    - api/app/routers/health.py
    - api/app/core/config.py
    - api/app/core/database.py
    - api/app/core/errors.py
    - api/tests/conftest.py
    - api/tests/unit/test_health.py
    - api/pytest.ini
    - api/Dockerfile
    - api/.env.example
  modified:
    - .gitignore

key-decisions:
  - "Lazy SQLAlchemy engine init so app imports without live Postgres"
  - "Normalize postgres:// and postgresql:// URLs to postgresql+psycopg2://"
  - "Versioning test targets /__test-error__ because /ready is exempt per D-27"

patterns-established:
  - "Accept: application/vnd.puzzlessbox.v1+json required except /health, /ready, /docs"
  - "Error shape {error:{code,message,details?}} via centralized handlers"

requirements-completed: []

coverage:
  - id: D1
    description: "FastAPI shell with /health liveness and /ready DB ping"
    verification:
      - kind: unit
        ref: "api/tests/unit/test_health.py::test_health"
        status: pass
      - kind: unit
        ref: "api/tests/unit/test_health.py::test_ready_db_up"
        status: pass
      - kind: unit
        ref: "api/tests/unit/test_health.py::test_ready_db_down"
        status: pass
    human_judgment: false
  - id: D2
    description: "Accept-header versioning returns 415 on missing header"
    verification:
      - kind: unit
        ref: "api/tests/unit/test_health.py::test_versioning_415"
        status: pass
    human_judgment: false
  - id: D3
    description: "OpenAPI docs disabled when ENV=prod"
    verification:
      - kind: unit
        ref: "api/tests/unit/test_health.py::test_docs_disabled_prod"
        status: pass
    human_judgment: false
  - id: D4
    description: "Unified error response shape"
    verification:
      - kind: unit
        ref: "api/tests/unit/test_health.py::test_error_shape"
        status: pass
    human_judgment: false
  - id: D5
    description: "Wave 0 pytest harness with mock Postgres and JWKS"
    verification:
      - kind: unit
        ref: "cd api && pytest --co -q tests/"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-07-30
status: complete
---

# Phase 01 Plan 01: FastAPI Shell Summary

**FastAPI shell with /health+/ready, Accept-header versioning, unified errors, prod docs off, and Wave 0 pytest harness**

## Performance

- **Duration:** 5 min
- **Started:** 2026-07-30T02:29:00Z
- **Completed:** 2026-07-30T02:34:00Z
- **Tasks:** 2
- **Files modified:** 18

## Accomplishments

- Runnable `Puzzlessbox API` FastAPI app with liveness and readiness endpoints
- Accept-versioning middleware (415 without header; exempt /health, /ready, /docs)
- Unified `{error:{code,message,details?}}` handlers; stack traces hidden in prod
- pytest.ini + conftest with transactional sqlite sessions, RS256 JWKS mock, two owner_id fixtures
- Dockerfile (python:3.14-slim) and `.env.example`

## Task Commits

1. **Task 1: FastAPI shell + health router + unified errors + Accept versioning** - `b63a646` (feat)
2. **Task 2: Wave 0 pytest harness** - `5133540` (feat)

## Files Created/Modified

- `api/app/main.py` - FastAPI app, versioning middleware, error handlers, prod docs gate
- `api/app/routers/health.py` - `/health` and `/ready` endpoints
- `api/app/core/config.py` - pydantic-settings with env normalization
- `api/app/core/database.py` - lazy engine, session stub, `check_db_connection`
- `api/app/core/errors.py` - unified error handlers
- `api/tests/unit/test_health.py` - six behavior tests (D-27, D-31, D-32, D-33)
- `api/tests/conftest.py` - mock Postgres sessions, JWKS, owner fixtures
- `api/pytest.ini` - asyncio_mode=auto
- `api/Dockerfile` - container entrypoint
- `api/.env.example` - documented env vars
- `.gitignore` - ignore `api/.venv/`

## Decisions Made

- Lazy engine creation avoids import failure when Postgres is unreachable
- `postgres://` URLs normalized to `postgresql+psycopg2://` for SQLAlchemy compatibility
- Versioning 415 test uses `/__test-error__` because `/ready` is intentionally exempt

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added pydantic-settings dependency**
- **Found during:** Task 1
- **Issue:** BaseSettings requires pydantic-settings package
- **Fix:** Pinned pydantic-settings==2.7.1 in requirements.txt
- **Files modified:** api/requirements.txt
- **Committed in:** b63a646

**2. [Rule 3 - Blocking] DATABASE_URL dialect normalization**
- **Found during:** Task 1 verify
- **Issue:** Host env `postgres://` URL caused `NoSuchModuleError: sqlalchemy.dialects:postgres`
- **Fix:** Validator rewrites postgres/postgresql URLs to postgresql+psycopg2
- **Files modified:** api/app/core/config.py
- **Committed in:** b63a646

**3. [Rule 1 - Bug] Versioning test endpoint**
- **Found during:** Task 1 tests
- **Issue:** `/ready` exempt from versioning per plan — test got 503 not 415
- **Fix:** `test_versioning_415` targets `/__test-error__` instead
- **Files modified:** api/tests/unit/test_health.py
- **Committed in:** b63a646

---

**Total deviations:** 3 auto-fixed (1 missing critical, 1 blocking, 1 bug)
**Impact on plan:** All required for correct behavior; no scope creep.

## Issues Encountered

None beyond deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 05 can wire SQLModel models, Alembic migrations, and RLS on `get_db`
- Plan 06 can consume `mock_jwks_keypair`, `mock_jwks_client`, and owner fixtures for auth tests
- `api/.venv` created locally for dev; not committed

---
*Phase: 01-datenmodell-backend-api*
*Completed: 2026-07-30*

## Self-Check: PASSED

- FOUND: api/app/main.py
- FOUND: api/tests/conftest.py
- FOUND: api/pytest.ini
- FOUND: b63a646
- FOUND: 5133540
