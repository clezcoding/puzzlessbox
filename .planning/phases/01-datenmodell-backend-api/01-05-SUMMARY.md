---
phase: 01-datenmodell-backend-api
plan: 05
subsystem: database
tags: [sqlmodel, alembic, postgres, rls, tenancy, schema]

requires:
  - phase: 01-datenmodell-backend-api
    provides: FastAPI shell + Wave 0 pytest harness (Plan 01)
provides:
  - SQLModel tables for notes/links/tasks/events/categories
  - Alembic 0001 with RLS, board_items VIEW, service_principals, seed categories
  - database.py RLS session context (SET app.owner_id + ROLE)
  - test_draft_validation + test_rls + schema migration tests
affects: [01-06]

tech-stack:
  added: [alembic migrations, postgres RLS policies, board_items VIEW]
  patterns: [Better Auth user.id owner_id without FK, puzzlessbox_app role + SET LOCAL, DraftCreate validation]

key-files:
  created:
    - api/alembic/versions/0001_initial_schema.py
    - api/app/models/category.py
    - api/app/models/note.py
    - api/app/models/link.py
    - api/app/models/task.py
    - api/app/models/event.py
    - api/app/models/board.py
    - api/app/models/service_principal.py
    - api/tests/unit/test_models.py
    - api/tests/integration/test_tenancy.py
    - api/tests/integration/test_schema.py
  modified:
    - api/app/core/database.py
    - api/tests/conftest.py

key-decisions:
  - "Categories seed with NULL owner_id; RLS allows NULL OR matching owner_id"
  - "Link metadata uses portable JSON column in SQLModel; migration keeps JSONB"
  - "board_items VIEW projects empty summary for links (no summary column on links table)"

patterns-established:
  - "owner_id on core tables references Better Auth user.id without FK (D-21)"
  - "get_db + set_request_owner sets app.owner_id and SET LOCAL ROLE puzzlessbox_app"

requirements-completed: [AUTH-04, CAP-01]

coverage:
  - id: D1
    description: "Alembic 0001 schema with RLS, VIEW, service_principals, 5 seed categories"
    requirement: AUTH-04
    verification:
      - kind: integration
        ref: "api/tests/integration/test_schema.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "SQLModel draft validation for capture type enum"
    requirement: CAP-01
    verification:
      - kind: unit
        ref: "api/tests/unit/test_models.py::test_draft_validation"
        status: pass
    human_judgment: false
  - id: D3
    description: "Cross-tenant RLS isolation returns empty for foreign owner"
    requirement: AUTH-04
    verification:
      - kind: integration
        ref: "api/tests/integration/test_tenancy.py::test_rls"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-07-30
status: complete
---

# Phase 01 Plan 05: Schema + Migration Summary

**Postgres schema with SQLModel tables, Alembic 0001 (RLS + board_items VIEW + service_principals), and CAP-01/AUTH-04 tests green**

## Performance

- **Duration:** 8 min
- **Started:** 2026-07-30T02:34:00Z
- **Completed:** 2026-07-30T02:42:00Z
- **Tasks:** 2
- **Files modified:** 19

## Accomplishments

- SQLModel tables: notes, links, tasks, events, categories, service_principals
- Alembic `0001_initial_schema`: board_items VIEW, RLS on core tables, 5 seed categories, no `users` table (D-21)
- `database.py` extended: `set_request_owner` + `SET LOCAL app.owner_id` + `SET ROLE puzzlessbox_app`
- `test_draft_validation`, `test_rls`, and schema migration tests pass against local Postgres

## Task Commits

1. **Task 1: SQLModel tables + Alembic 0001** - `ab8703d` (feat)
2. **Task 2: Schema tests** - `bbeb75c` (test)

## Files Created/Modified

- `api/alembic/versions/0001_initial_schema.py` - tables, VIEW, RLS, role grants, category seeds
- `api/app/models/*.py` - SQLModel domain models + DraftCreate validator
- `api/app/core/database.py` - RLS session context wiring
- `api/tests/conftest.py` - Postgres engine fixture with alembic upgrade
- `api/tests/unit/test_models.py` - CAP-01 draft validation
- `api/tests/integration/test_tenancy.py` - AUTH-04 RLS boundary
- `api/tests/integration/test_schema.py` - migration behavior tests

## Decisions Made

- System categories use `owner_id IS NULL` with RLS policy allowing NULL or tenant match
- Link model uses SQLAlchemy `JSON` (sqlite-safe); migration still uses JSONB on Postgres
- `board_items` VIEW uses `''::text` for link summary column projection

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Portable JSON type for Link.metadata**
- **Found during:** Task 1 (pytest autouse sqlite schema)
- **Issue:** JSONB in SQLModel broke Wave 0 sqlite harness (`visit_JSONB` unsupported)
- **Fix:** SQLModel layer uses `JSON`; Alembic migration keeps Postgres JSONB
- **Files modified:** api/app/models/link.py
- **Committed in:** ab8703d

**2. [Rule 1 - Bug] board_items VIEW link branch**
- **Found during:** Task 1 verify (`alembic upgrade head`)
- **Issue:** links table has no `summary` column — VIEW creation failed
- **Fix:** Project `''::text AS summary` for links UNION branch
- **Files modified:** api/alembic/versions/0001_initial_schema.py
- **Committed in:** ab8703d

**3. [Rule 3 - Blocking] Local Postgres DATABASE_URL**
- **Found during:** Task 1 verify
- **Issue:** Default `postgres:postgres@localhost` user missing on dev machine
- **Fix:** Tests/migration use `postgresql+psycopg2://puzzless@localhost:5432/puzzlessbox` via `DATABASE_URL`
- **Files modified:** api/tests/conftest.py
- **Committed in:** ab8703d

---

**Total deviations:** 3 auto-fixed (1 missing critical, 1 bug, 1 blocking)
**Impact on plan:** Required for migration + test harness; no scope creep.

## Issues Encountered

None beyond deviations above.

## User Setup Required

None - local Postgres with `DATABASE_URL` pointing at migrated `puzzlessbox` database.

## Next Phase Readiness

- Plan 06 can wire auth router + draft CRUD on top of schema and RLS session
- `DraftCreate`, owner fixtures, and `set_request_owner` ready for capture endpoints

---
*Phase: 01-datenmodell-backend-api*
*Completed: 2026-07-30*

## Self-Check: PASSED

- FOUND: api/alembic/versions/0001_initial_schema.py
- FOUND: api/tests/unit/test_models.py
- FOUND: api/tests/integration/test_tenancy.py
- FOUND: ab8703d
- FOUND: bbeb75c
