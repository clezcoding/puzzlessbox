---
phase: 04-webapp
fixed_at: 2026-08-03T02:20:00Z
review_path: .planning/phases/04-webapp/04-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 04: Code Review Fix Report

**Fixed at:** 2026-08-03T02:20:00Z
**Source review:** `.planning/phases/04-webapp/04-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 3
- Fixed: 3
- Skipped: 0

## Fixed Issues

### WR-01: Gap-closure test never asserts `onMoved`

**Files modified:** `webapp/tests/dnd.test.tsx`
**Commit:** d60b9ec
**Applied fix:** Spy `onMoved` + `onClear` (state clear via `onClear.mockImplementation`); assert each called once and `onMoved` before `onClear` via `invocationCallOrder`.

### WR-02: Mid-loop failure leaves partial moves + false "zurück" toast

**Files modified:** `webapp/components/board/bulk-move-bar.tsx`, `webapp/tests/dnd.test.tsx`
**Commit:** 53293b3
**Status:** fixed: requires human verification
**Applied fix:** On catch, if `done > 0` call `onMoved()` and toast `${done}/${total} verschoben, Rest fehlgeschlagen.`; keep full-fail "zurück" copy when `done === 0`. Also pluralized success toast when `total > 1` (IN-01 one-liner on same path) and updated test expectation.

### WR-03: No in-flight lock — double destination click can double-PATCH

**Files modified:** `webapp/components/board/bulk-move-bar.tsx`
**Commit:** 1565b74
**Status:** fixed: requires human verification
**Applied fix:** `useState(busy)` before early return; guard + `setBusy(true)` / `finally setBusy(false)`; `disabled={busy}` on trigger Button and destination `DropdownMenuItem`s.

## Skipped Issues

None — Info findings IN-01/IN-02 out of scope (`fix_scope: critical_warning`). IN-01 plural toast applied opportunistically inside WR-02.

---

_Fixed: 2026-08-03T02:20:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
