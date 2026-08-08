---
phase: 4
slug: webapp
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-08-02
validated: 2026-08-05
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
| 04-00-T1 | 00 | 1 | BOARD-01, CAP-05 | T-04-01..03,05 | shadcn init brand-mapped; middleware session cookie; api-client credentials include; auth-client session hook | unit/DOM | `pnpm test --run --passWithNoTests && pnpm build` | ✅ 04-00 | ✅ green |
| 04-01-T1 | 01 | 2 | BOARD-01, CAP-05 | T-04-06 | Login→Board tracer; 5 default categories; draft filter; empty-state Apollo PNG + VOICE (D-05) | unit/DOM | `pnpm test -- --run board auth` | ✅ 04-01 | ✅ green |
| 04-01-T2 | 01 | 2 | BOARD-01, CAP-05 | T-04-04 | Session refresh survival; ?next= open-redirect guard; logout | unit/DOM | `pnpm test -- --run auth` | ✅ 04-01 | ✅ green |
| 04-02-T1 | 02 | 1 | BOARD-02, BOARD-03 | T-04-07..09,12 | Category PATCH/DELETE/reorder owner-scoped; color hex validation; last-category guard | integration | `pytest tests/test_categories_color_sort.py -x` | ✅ 04-02 | ✅ green |
| 04-02-T2 | 02 | 1 | BOARD-03, BOARD-04 | T-04-10,11,12b | Item PATCH/DELETE/restore owner-scoped; type-change mapping; soft-delete + undo; POST /items/reorder; board_items VIEW sort_order; GET /board-items ORDER BY sort_order | integration | `pytest tests/test_items_edit_softdelete.py -x` | ✅ 04-02 | ✅ green |
| 04-03-T1 | 03 | 3 | BOARD-02, BOARD-03 | T-04-13..16 | DnD optimistic + revert; a11y keyboard; multi-select bulk move; in-column reorder via POST /items/reorder | unit/DOM | `pnpm test -- --run dnd` | ✅ 04-03 | ✅ green |
| 04-03-T2 | 03 | 3 | BOARD-02, BOARD-04, CAL-03 | T-04-17,18 | Modal autosave; soft-delete undo; type-change confirm; link OG; Calendar 412 inline Conflict-Panel (D-14); categories panel | unit/DOM | `pnpm test -- --run modal categories` | ✅ 04-03 | ✅ green |
| 04-04-T1 | 04 | 4 | CAP-05 | T-04-19,23 | Poll owner-scoped; backoff; offline banner; new-item feedback | integration | `pnpm test -- --run poll` | ✅ 04-04 | ✅ green |
| 04-04-T2 | 04 | 4 | CAL-01, CAP-05 | T-04-20..22 | OAuth state/session check; calendar list owner-scoped; theme/sound localStorage safe | unit/flow | `pnpm test -- --run settings calendar` | ✅ 04-04 | ✅ green |
| 04-05-T1 | 05 | 4 | CAL-01, AUTH-03, BOARD-01..03, OPS-01..02 | T-04-05-01..03 | Separate Coolify Docker-Image-Apps, JWKS URL canonical, CORS_ORIGINS explicit list, prod UAT curl verification | unit/flow/smoke | `pnpm test && curl -I https://pbox.puzzlesstool.online` | ✅ 04-05 | ✅ green |
| 04-06-T1 | 06 | 3 | BOARD-03 | T-04-06-01..02 | Bulk moveItem drag and drop optimistic move and bulk move bar verification | unit/DOM | `pnpm test -- --run dnd` | ✅ 04-06 | ✅ green |
| 04-07-T1 | 07 | 4 | AUTH-03, CAP-05 | T-04-07-01..03 | isSignupLockedError hardened to cover flat/nested/string errors with circular-ref safety | unit/DOM | `pnpm test -- --run auth` | ✅ 04-07 | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `webapp/vitest.config.ts` — Vitest environment configuration (created in 04-00 Task 1)
- [x] `webapp/tests/setup.ts` — React Testing Library / DOM mocks (created in 04-00 Task 1)
- [x] Stub test files for BOARD-01..04, CAP-05, CAL-01 per RESEARCH Validation Architecture (created in 04-01 Task 1 board/auth stubs; 04-03/04-04 own feature-specific stubs)

*Planner filled exact Wave 0 task paths: 04-00 Task 1 owns Wave 0 infra (vitest config + setup); 04-01 Task 1 owns board/auth stub test bodies; 04-03/04-04 own feature-specific stubs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Google OAuth browser round-trip to Google consent | CAL-01 | External IdP; needs real credentials | Connect Calendar in Settings on staging; confirm tokens stored and status shows connected |
| prefers-color-scheme + theme toggle visual | BOARD-01 (UX) | Visual/OS preference | Toggle light/dark; confirm brand tokens apply |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-08-05

---

## Validation Audit — 2026-08-05

Nyquist audit of Phase 4 (WebApp) complete.
- **Scope:** Tasks 04-00 through 04-07 verified.
- **Local Test Suite:** `pnpm test` (10 files / 77 tests) runs in ~5 seconds and passes with 100% success.
- **API Python Integration Suite:** 19 integration tests pass using pytest.
- **Prod UAT Suite:** r4 complete (18/18 pass), covering all behavior-dependent truths on prod including Google Calendar CTA and 5 default board categories.
- **Hardenings:**
  - `isSignupLockedError` in `login-form.tsx` is fully covered by envelope-shape mock unit tests inside `auth.test.tsx` (all 409 error structure styles covered: flat/nested/string/Response-wrapped/circular-safe).
  - Bulk-move destination-click is verified and covered inside `dnd.test.tsx`.
- **Verdict:** Nyquist compliant. Ready for final verification.
