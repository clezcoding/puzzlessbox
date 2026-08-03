---
phase: 04-webapp
reviewed: 2026-08-03T02:12:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - webapp/components/board/bulk-move-bar.tsx
  - webapp/tests/dnd.test.tsx
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
focus: 04-06 gap closure (e7cda0d, 7e53d94, 199049c)
---

# Phase 04: Code Review Report

**Reviewed:** 2026-08-03T02:12:00Z  
**Depth:** standard  
**Files Reviewed:** 2  
**Status:** issues_found  
**Focus:** Plan 04-06 bulk-move gap closure (`e7cda0d`, `7e53d94`, `199049c`)

## Summary

04-06 delta is tiny and mostly sound: two inert `data-testid`s plus a stateful Harness test that clicks destination, asserts `moveItem` ×2 with nth-call args, and proves bar unmount via `count===0`. Vitest bulk case green (118ms). Gap-closure claim for PATCH count + count delta holds. Holes remain: test never spies `onMoved` (plan must-have), and pre-existing `handleBulkMove` still mishandles mid-loop failure / re-entrancy. No critical/security issues in the 04-06 delta itself.

## Warnings

### WR-01: Gap-closure test never asserts `onMoved`

**File:** `webapp/tests/dnd.test.tsx:229`  
**Issue:** Plan must-have requires `onMoved` (board `refresh`) and `onClear` fire exactly once after moves resolve. Harness wires `onMoved={() => {}}` with no spy. Unmount only proves `onClear` zeroed `count`. Dropping `onMoved()` or swapping call order still passes CI while board stays stale after bulk move.  
**Fix:**

```tsx
const onMoved = vi.fn();
// in Harness:
onMoved={onMoved}
// after moveItem asserts:
expect(onMoved).toHaveBeenCalledTimes(1);
expect(onMoved.mock.invocationCallOrder[0]).toBeLessThan(
  // or assert onClear spy call order relative to onMoved
);
```

Prefer spies for both `onMoved` and `onClear`, then keep Harness state update inside the `onClear` spy implementation.

### WR-02: Mid-loop failure leaves partial moves + false "zurück" toast

**File:** `webapp/components/board/bulk-move-bar.tsx:38-50`  
**Issue:** Sequential `await moveItem` loop. If item *k* rejects after *0..k-1* succeeded: catch dismisses loading toast, shows `"Verschieben fehlgeschlagen. Eintrag ist zurück."`, skips `onMoved`/`onClear`. Already-PATCHed items stay on destination; UI selection unchanged; toast claims rollback that never happened. Pre-existing (04-06 only added testids) but lives in reviewed production file and undermines bulk-move trust.  
**Fix:** Track succeeded ids; on failure call `onMoved()` to refresh, toast partial failure with count, clear only fully-succeeded ids (or rollback via reverse PATCH — heavier). Minimum honest toast:

```tsx
} catch {
  if (toastId) toast.dismiss(toastId);
  if (done > 0) onMoved();
  toast.error(
    done > 0
      ? `${done}/${total} verschoben, Rest fehlgeschlagen.`
      : "Verschieben fehlgeschlagen. Eintrag ist zurück.",
  );
}
```

### WR-03: No in-flight lock — double destination click can double-PATCH

**File:** `webapp/components/board/bulk-move-bar.tsx:32-70`  
**Issue:** `handleBulkMove` has no busy/disabled guard. Dropdown stays interactive while awaits run. Second destination click starts another loop over same `selectedIds` → duplicate PATCH storm until first `onClear`. Pre-existing; test happy-path only.  
**Fix:**

```tsx
const [busy, setBusy] = useState(false);
async function handleBulkMove(categoryId: string) {
  if (busy) return;
  setBusy(true);
  try {
    // existing loop...
  } finally {
    setBusy(false);
  }
}
// disable trigger + items while busy
```

## Info

### IN-01: Success copy always singular

**File:** `webapp/components/board/bulk-move-bar.tsx:44`  
**Issue:** Bulk of N≥2 still toasts `"Eintrag verschoben."` (singular). Misleading copy, not a functional defect.  
**Fix:** Pluralize when `total > 1` (e.g. `"Einträge verschoben."`).

### IN-02: 04-06 testid + destination-click coverage is the right seam

**File:** `webapp/components/board/bulk-move-bar.tsx:61-69`, `webapp/tests/dnd.test.tsx:210-256`  
**Issue:** None — noting positive soundness. Testids match board-card sibling pattern; Radix `DropdownMenuItem` forwards `data-testid` via `{...props}`; Harness correctly proves count-delta unmount that plain `vi.fn()` onClear cannot. Replaces render-only `"shows bulk move bar when selection > 0"`.  
**Fix:** None required for the happy path; close WR-01 to match plan must-haves fully.

---

_Reviewed: 2026-08-03T02:12:00Z_  
_Reviewer: Claude (gsd-code-reviewer)_  
_Depth: standard_  
_Commits: e7cda0d, 7e53d94, 199049c_
