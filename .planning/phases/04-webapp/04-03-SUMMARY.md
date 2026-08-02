---
phase: 04-webapp
plan: 03
subsystem: ui
tags: [nextjs, dnd, modal, autosave, categories, vitest, hello-pangea]

requires:
  - phase: 04-webapp
    plan: 01
    provides: Board shell, board-column/card, auth session
  - phase: 04-webapp
    plan: 02
    provides: Item/category PATCH, reorder, soft-delete, sort_order API
provides:
  - Cross-category + in-column DnD with optimistic move + revert (D-16..D-23)
  - Mobile single-column tabs + long-press category sheet (D-02, D-17)
  - Multi-select bulk move via sequential PATCHes (D-22)
  - Centered item modal with autosave, soft-delete undo, type-change, link OG (D-09..D-13)
  - Calendar 412 inline conflict panel (D-14)
  - Kategorien verwalten panel with create/rename/reorder (D-06)
affects: [04-04, 04-05]

tech-stack:
  added: [shadcn dialog/sheet/alert-dialog/checkbox/textarea]
  patterns:
    - "use-optimistic-move: optimistic DnD + toast revert on API failure"
    - "use-item-autosave: 300ms debounce + flush on modal close"
    - "updateItem 412 → inline conflict panel with force PATCH via If-None-Match: *"

key-files:
  created:
    - webapp/components/board/board-dnd.tsx
    - webapp/components/board/item-modal.tsx
    - webapp/components/board/categories-panel.tsx
    - webapp/components/board/mobile-category-sheet.tsx
    - webapp/components/board/bulk-move-bar.tsx
    - webapp/lib/api/items.ts
    - webapp/lib/api/categories.ts
    - webapp/lib/hooks/use-optimistic-move.ts
    - webapp/lib/hooks/use-item-autosave.ts
    - webapp/tests/dnd.test.tsx
    - webapp/tests/modal.test.tsx
    - webapp/tests/categories.test.tsx
  modified:
    - webapp/app/board/page.tsx
    - webapp/components/board/board-card.tsx
    - webapp/components/board/board-column.tsx
    - webapp/lib/api-client.ts

key-decisions:
  - "BoardDnd loaded via next/dynamic ssr:false to avoid hydration mismatch with @hello-pangea/dnd"
  - "Sequential PATCH for bulk move (UI-SPEC locked); progress toast when >5 items"
  - "Modal overlay click blocked; close via X/Escape only with autosave flush (D-15)"
  - "412 conflict handled client-side via updateItem returning conflict payload"

patterns-established:
  - "Drag handle only on desktop; card body opens modal (D-16)"
  - "Category rename inline on column header; create/reorder in side sheet (D-06)"

requirements-completed: [BOARD-02, BOARD-03, BOARD-04]

coverage:
  - id: D1
    description: "Cross-category DnD optimistic + revert + success/error toasts"
    requirement: BOARD-03
    verification:
      - kind: unit
        ref: "webapp/tests/dnd.test.tsx#moves item cross-category"
        status: pass
    human_judgment: false
  - id: D2
    description: "In-column reorder persists via POST /items/reorder"
    requirement: BOARD-03
    verification:
      - kind: unit
        ref: "webapp/tests/dnd.test.tsx#persists in-column reorder"
        status: pass
    human_judgment: false
  - id: D3
    description: "Mobile tabs + long-press sheet picker; bulk move bar"
    requirement: BOARD-03
    verification:
      - kind: unit
        ref: "webapp/tests/dnd.test.tsx#mobile single column"
        status: pass
    human_judgment: false
  - id: D4
    description: "Item modal autosave, soft-delete undo, type-change, link OG"
    requirement: BOARD-04
    verification:
      - kind: unit
        ref: "webapp/tests/modal.test.tsx"
        status: pass
    human_judgment: false
  - id: D5
    description: "Calendar 412 inline conflict panel with Übernehmen/Behalten/Abbrechen"
    requirement: BOARD-04
    verification:
      - kind: unit
        ref: "webapp/tests/modal.test.tsx#412 conflict panel"
        status: pass
    human_judgment: false
  - id: D6
    description: "Kategorien verwalten panel: create, rename max 40, reorder"
    requirement: BOARD-02
    verification:
      - kind: unit
        ref: "webapp/tests/categories.test.tsx"
        status: pass
    human_judgment: false
  - id: D7
    description: "pnpm build succeeds"
    requirement: BOARD-03
    verification:
      - kind: other
        ref: "cd webapp && pnpm build"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-08-02
status: complete
---

# Phase 4 Plan 03: Board Features Summary

**DnD + modal + categories panel on board tracer — optimistic moves, autosave edit, Calendar 412 conflict inline**

## Performance

- **Duration:** 8 min
- **Tasks:** 2
- **Files modified:** 24

## Accomplishments

- `@hello-pangea/dnd` board: cross-category drop + in-column reorder, optimistic UI + revert toast
- Desktop drag via handle only; card body opens modal; classic floating ghost class
- Mobile `<768px`: category tabs + long-press sheet picker
- Checkbox multi-select + bulk-move bar (sequential PATCH, progress toast >5)
- Item modal: centered 560px dialog, debounced autosave, soft-delete undo, type-change confirm, link OG block
- Calendar 412: inline conflict panel (Google hat / Du hast) + Übernehmen / Behalten / Abbrechen
- Kategorien verwalten sheet: create, inline rename (40 chars), drag reorder
- 31 Vitest tests green; `pnpm build` green

## Task Commits

1. **feat(04-webapp-03): DnD, mobile sheet, bulk move, a11y** - `7aafd47`
2. **feat(04-webapp-03): item modal, categories panel, autosave** - `4a11cbe`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Board page infinite render loop from onItemsChange sync**
- **Found during:** Task 1 board.test.tsx
- **Issue:** `onItemsChange` in BoardDnd triggered parent `setItems` → externalItems sync loop
- **Fix:** Removed `onItemsChange` prop; board refreshes via `loadBoard` after moves
- **Commit:** `7aafd47`

**2. [Rule 3 - Blocking] jsdom missing `window.matchMedia`**
- **Found during:** board page tests after useMediaQuery added
- **Fix:** Global matchMedia mock in `webapp/tests/setup.ts`
- **Commit:** `7aafd47`

---

**Total deviations:** 2 auto-fixed (2 blocking)

## TDD Gate Compliance

Tests and implementation committed together per task (no separate RED-only commits). All 20 new plan tests pass.

## Issues Encountered

None blocking.

## User Setup Required

None.

## Next Phase Readiness

- Plan 04-04+ can add CAP-05 polling on this board data layer
- Manual QA: drag between columns, modal edit/autosave, soft-delete undo, mobile long-press

## Self-Check: PASSED

- FOUND: webapp/components/board/board-dnd.tsx
- FOUND: webapp/components/board/item-modal.tsx
- FOUND: webapp/components/board/categories-panel.tsx
- FOUND: webapp/tests/dnd.test.tsx
- FOUND: webapp/tests/modal.test.tsx
- FOUND: webapp/tests/categories.test.tsx
- FOUND: 7aafd47
- FOUND: 4a11cbe

---
*Phase: 04-webapp*
*Completed: 2026-08-02*
