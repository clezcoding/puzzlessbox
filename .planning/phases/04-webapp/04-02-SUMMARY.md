---
phase: 04-webapp
plan: 02
subsystem: api
tags: [fastapi, alembic, postgres, board-items, sort_order, soft-delete]

requires:
  - phase: 01-datenmodell-backend-api
    provides: board_items VIEW, RLS, draft/capture lifecycle, category seed data
provides:
  - Alembic 0006 color/sort_order/deleted_at on categories and sort_order on item tables
  - Category PATCH/DELETE/reorder with hex color validation
  - Item PATCH with type-specific fields, type-change, sort_order
  - Item soft-delete, restore, and POST /items/reorder
  - GET /board-items stable in-column ordering (category_id, sort_order, created_at DESC)
affects:
  - 04-webapp-03
  - webapp board UI DnD and category management

tech-stack:
  added: []
  patterns:
    - "Hex color validation via Pydantic StringConstraints on category payloads"
    - "Polymorphic item updates via table_for_item_type + transactional type-change (DELETE old row, INSERT new)"
    - "board_items VIEW exposes sort_order; list endpoint filters draft/deleted"

key-files:
  created:
    - api/alembic/versions/0006_board_color_sortorder.py
    - api/tests/test_categories_color_sort.py
    - api/tests/test_items_edit_softdelete.py
  modified:
    - api/app/routers/categories.py
    - api/app/routers/items.py
    - api/app/routers/capture.py
    - api/app/models/category.py
    - api/app/models/board.py

key-decisions:
  - "Category DELETE blocks when ≤1 active category visible to owner (system + owned)"
  - "Deleted category items reassigned to system Inbox before category soft-delete"
  - "POST /categories/reorder allows system default categories (owner_id IS NULL) plus owned categories"
  - "GET /board-items excludes draft and deleted; orders by category_id, sort_order ASC, created_at DESC"

patterns-established:
  - "Reorder payloads capped at 100 entries (T-04-12 / T-04-12b mitigation)"
  - "Integration tests use DATABASE_URL-scoped engine helper to avoid get_engine() default mismatch"

requirements-completed: [BOARD-02, BOARD-03, BOARD-04]

coverage:
  - id: D1
    description: "Categories expose color/sort_order; PATCH/DELETE/reorder owner-scoped with hex validation"
    requirement: BOARD-02
    verification:
      - kind: integration
        ref: "api/tests/test_categories_color_sort.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "Items support sort_order PATCH/reorder and stable GET /board-items column ordering"
    requirement: BOARD-03
    verification:
      - kind: integration
        ref: "api/tests/test_items_edit_softdelete.py#test_patch_item_sort_order"
        status: pass
      - kind: integration
        ref: "api/tests/test_items_edit_softdelete.py#test_reorder_items"
        status: pass
      - kind: integration
        ref: "api/tests/test_items_edit_softdelete.py#test_board_items_sorted_by_category_sort_order_created_at"
        status: pass
    human_judgment: false
  - id: D3
    description: "Item field edit, type-change mapping, soft-delete and restore"
    requirement: BOARD-04
    verification:
      - kind: integration
        ref: "api/tests/test_items_edit_softdelete.py"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-08-02
status: complete
---

# Phase 4 Plan 2: Board API Extensions Summary

**Alembic 0006 plus category/item endpoints for color, sort_order, in-column reorder, type-change, and soft-delete with restore**

## Performance

- **Duration:** 12 min
- **Started:** 2026-08-02T23:15:00Z
- **Completed:** 2026-08-02T23:27:00Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- Migration 0006 adds `categories.color`, `categories.sort_order`, `categories.deleted_at`, item `sort_order`, and rebuilds `board_items` VIEW
- Category API: list with sort, PATCH (name/color/sort_order), DELETE with last-category guard + Inbox reassignment, POST `/categories/reorder`
- Item API: PATCH with type-specific fields and type-change, DELETE soft-delete, POST restore, POST `/items/reorder`
- GET `/board-items` filters `draft`/`deleted` and sorts `(category_id, sort_order ASC, created_at DESC)`
- 19 new integration tests green; Alembic downgrade/upgrade roundtrip clean

## Task Commits

1. **Task 1: Alembic 0006 + Category PATCH/DELETE/reorder** - `13e11a2` (feat)
2. **Task 2: Item PATCH/type-change/soft-delete/reorder** - `1e3bb78` (feat)

## Files Created/Modified

- `api/alembic/versions/0006_board_color_sortorder.py` - Schema + VIEW migration
- `api/app/routers/categories.py` - BOARD-02 category mutations
- `api/app/routers/items.py` - BOARD-03/04 item mutations
- `api/app/routers/capture.py` - board list ordering/filter
- `api/app/models/category.py` - color/sort_order/deleted_at fields
- `api/app/models/board.py` - `sort_order` on BoardItem read model
- `api/tests/test_categories_color_sort.py` - 7 category tests
- `api/tests/test_items_edit_softdelete.py` - 12 item tests

## Decisions Made

- Category reorder permits system defaults (`owner_id IS NULL`) so board column order can include seeded categories
- Type-change deletes old polymorphic row and inserts new row preserving id, title, sort_order, status
- Tests assert DB state via `DATABASE_URL`-scoped engine to avoid `get_engine()` default URL mismatch

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] SQLModel Field lacks `pattern` kwarg**
- **Found during:** Task 1
- **Issue:** `Field(pattern=...)` raised TypeError at import
- **Fix:** Use `Annotated[str, StringConstraints(pattern=...)]` for hex color fields
- **Files modified:** `api/app/routers/categories.py`
- **Committed in:** `13e11a2`

**2. [Rule 1 - Bug] Integration DB assertions used wrong engine**
- **Found during:** Task 2 tests
- **Issue:** `get_engine()` default URL differed from pytest `DATABASE_URL`, causing false failures
- **Fix:** `_test_engine()` helper reads `DATABASE_URL` in both test modules
- **Files modified:** `api/tests/test_categories_color_sort.py`, `api/tests/test_items_edit_softdelete.py`
- **Committed in:** `1e3bb78`

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug)
**Impact on plan:** No scope change; correctness fixes only.

## Issues Encountered

None beyond deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 03 (Board UI) can consume `/categories`, `/items/*`, `/board-items` with sort_order and soft-delete
- Run `alembic upgrade head` on deployed API DB before webapp board work

## Self-Check: PASSED

- FOUND: api/alembic/versions/0006_board_color_sortorder.py
- FOUND: api/tests/test_categories_color_sort.py
- FOUND: api/tests/test_items_edit_softdelete.py
- FOUND: commit 13e11a2
- FOUND: commit 1e3bb78

---
*Phase: 04-webapp*
*Completed: 2026-08-02*
