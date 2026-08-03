---
phase: 04-webapp
plan: 06
subsystem: testing
tags: [vitest, react-testing-library, bulk-move, data-testid, board]

requires:
  - phase: 04-webapp
    provides: BulkMoveBar mit sequentiellem moveItem-Loop (Plan 04-03)
provides:
  - Stabile data-testid-Hooks für Bulk-Move-Trigger und Zielkategorien
  - CI-Regressionstest für Bulk-Destination-Commit inkl. PATCH-Count und Count-Delta
affects: [04-webapp UAT, BOARD-03]

tech-stack:
  added: []
  patterns:
    - "data-testid bulk-move-trigger / bulk-move-destination-{id} für Radix-Dropdown-Automation"
    - "Stateful Harness in Vitest für onClear → count===0 → Bar-Unmount"

key-files:
  created: []
  modified:
    - webapp/components/board/bulk-move-bar.tsx
    - webapp/tests/dnd.test.tsx

key-decisions:
  - "toast.success-Assertion mit zweitem undefined-Arg — entspricht handleBulkMove bei ≤5 Items"

patterns-established:
  - "Bulk-Destination-Tests klicken Trigger + findByTestId auf portaliertem DropdownMenuItem"

requirements-completed: [BOARD-03]

coverage:
  - id: D1
    description: "BulkMoveBar Trigger und Zielkategorien per data-testid automatisierbar"
    requirement: BOARD-03
    verification:
      - kind: unit
        ref: "webapp/tests/dnd.test.tsx#bulk move: clicking destination fires moveItem per selected id, resets selection, and unmounts bulk bar"
        status: pass
    human_judgment: false
  - id: D2
    description: "Bulk-Destination-Commit ruft moveItem pro selectedId auf und setzt Auswahl zurück"
    requirement: BOARD-03
    verification:
      - kind: unit
        ref: "webapp/tests/dnd.test.tsx#bulk move: clicking destination fires moveItem per selected id, resets selection, and unmounts bulk bar"
        status: pass
    human_judgment: false
  - id: D3
    description: "Prod-UAT #11 Bulk-Multi-Select-Move manuell auf Deploy"
    requirement: BOARD-03
    verification: []
    human_judgment: true
    rationale: "Code-Level-Gap geschlossen; Prod-Re-Run nach nächstem Web-Deploy erforderlich"

duration: 2min
completed: 2026-08-03
status: complete
---

# Phase 4 Plan 6: Bulk-Move Gap Closure Summary

**Stabile testids + Vitest-Regression beweisen Bulk-Destination-Commit (moveItem × N, Bar-Unmount)**

## Performance

- **Duration:** 2 min
- **Started:** 2026-08-03T02:09:00Z
- **Completed:** 2026-08-03T02:10:47Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `bulk-move-trigger` und `bulk-move-destination-{category.id}` auf BulkMoveBar — UAT-Automation kann Zielkategorie deterministisch klicken
- Neuer End-to-End-Test: Destination-Klick → `moveItem` zweimal mit korrekten Args → Toast → Bar verschwindet (count===0)
- UAT-Gap G-04-bulk-move / Test #11 auf Code-Ebene geschlossen; Prod-Re-Run nach Deploy offen

## Task Commits

1. **Task 1: Add data-testid to bulk-move-bar trigger + destination items** - `e7cda0d` (feat)
2. **Task 2: Strengthen dnd.test.tsx bulk test** - `7e53d94` (test)

## Files Created/Modified

- `webapp/components/board/bulk-move-bar.tsx` — testids auf Trigger-Button und DropdownMenuItems
- `webapp/tests/dnd.test.tsx` — stateful Harness + Destination-Click-Regressionstest

## Decisions Made

- Toast-Assertion nutzt `("Eintrag verschoben.", undefined)` weil `handleBulkMove` bei ≤5 Items keinen loading-toastId setzt und `undefined` explizit übergibt

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] toast.success-Assertion an Implementierung angepasst**
- **Found during:** Task 2
- **Issue:** Plan forderte `toHaveBeenCalledWith("Eintrag verschoben.")` — Implementierung übergibt zweites Arg `undefined`
- **Fix:** Assertion auf `("Eintrag verschoben.", undefined)` geändert
- **Files modified:** `webapp/tests/dnd.test.tsx`
- **Committed in:** `7e53d94`

---

**Total deviations:** 1 auto-fixed (Rule 1)
**Impact on plan:** Kein Verhaltensänderung — nur präzisere Test-Assertion.

## Issues Encountered

None

## User Setup Required

None

## Next Phase Readiness

- BOARD-03 Bulk-Move mit CI-Regression abgedeckt
- Nach Web-Deploy: UAT #11 auf Prod erneut ausführen
- Verbleibende Phase-4-Gaps: G-04-4 sticky SIGNUP_LOCKED copy

## Self-Check: PASSED

- FOUND: webapp/components/board/bulk-move-bar.tsx
- FOUND: webapp/tests/dnd.test.tsx
- FOUND: .planning/phases/04-webapp/04-06-SUMMARY.md
- FOUND commit: e7cda0d
- FOUND commit: 7e53d94

---
*Phase: 04-webapp*
*Completed: 2026-08-03*
