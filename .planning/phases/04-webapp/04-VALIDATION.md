---
phase: 4
slug: webapp
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-02
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest + React Testing Library |
| **Config file** | `webapp/vitest.config.ts` (Wave 0) |
| **Quick run command** | `pnpm --filter puzzlessbox-webapp test` |
| **Full suite command** | `pnpm --filter puzzlessbox-webapp test run` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pnpm --filter puzzlessbox-webapp test`
- **After every plan wave:** Run `pnpm --filter puzzlessbox-webapp test run`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-T1 | 01 | 1 | BOARD-01, CAP-05 | T-04-01..06 | Session cookie required for board; middleware redirect; brand tokens no hex | unit/DOM | `pnpm test -- --run board auth` | ❌ W0 → 04-01 | ⬜ pending |
| 04-01-T2 | 01 | 1 | BOARD-01, CAP-05 | T-04-04 | Session refresh survival; ?next= open-redirect guard; logout | unit/DOM | `pnpm test -- --run auth` | ✅ 04-01 | ⬜ pending |
| 04-02-T1 | 02 | 1 | BOARD-02, BOARD-03 | T-04-07..09,12 | Category PATCH/DELETE/reorder owner-scoped; color hex validation; last-category guard | integration | `pytest tests/test_categories_color_sort.py -x` | ✅ 04-02 | ⬜ pending |
| 04-02-T2 | 02 | 1 | BOARD-04 | T-04-10,11 | Item PATCH/DELETE/restore owner-scoped; type-change mapping; soft-delete + undo | integration | `pytest tests/test_items_edit_softdelete.py -x` | ✅ 04-02 | ⬜ pending |
| 04-03-T1 | 03 | 2 | BOARD-02, BOARD-03 | T-04-13..16 | DnD optimistic + revert; a11y keyboard; multi-select bulk move | unit/DOM | `pnpm test -- --run dnd` | ✅ 04-03 | ⬜ pending |
| 04-03-T2 | 03 | 2 | BOARD-02, BOARD-04 | T-04-17 | Modal autosave; soft-delete undo; type-change confirm; link OG; categories panel | unit/DOM | `pnpm test -- --run modal categories` | ✅ 04-03 | ⬜ pending |
| 04-04-T1 | 04 | 3 | CAP-05 | T-04-18,22 | Poll owner-scoped; backoff; offline banner; new-item feedback | integration | `pnpm test -- --run poll` | ✅ 04-04 | ⬜ pending |
| 04-04-T2 | 04 | 3 | CAL-01, CAP-05 | T-04-19..21 | OAuth state/session check; calendar list owner-scoped; theme/sound localStorage safe | unit/flow | `pnpm test -- --run settings calendar` | ✅ 04-04 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `webapp/vitest.config.ts` — Vitest environment configuration (created in 04-01 Task 1)
- [x] `webapp/tests/setup.ts` — React Testing Library / DOM mocks (created in 04-01 Task 1)
- [x] Stub test files for BOARD-01..04, CAP-05, CAL-01 per RESEARCH Validation Architecture (created in 04-01 Task 1 + 04-03/04-04)

*Planner filled exact Wave 0 task paths: 04-01 Task 1 owns Wave 0 infra + board/auth stubs; 04-03/04-04 own feature-specific stubs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Google OAuth browser round-trip to Google consent | CAL-01 | External IdP; needs real credentials | Connect Calendar in Settings on staging; confirm tokens stored and status shows connected |
| prefers-color-scheme + theme toggle visual | BOARD-01 (UX) | Visual/OS preference | Toggle light/dark; confirm brand tokens apply |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
