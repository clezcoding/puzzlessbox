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
| 04-01-01 | 01 | 1 | BOARD-01 | — | Session cookie required for board | unit/DOM | `pnpm test app/board/page.test.tsx` | ❌ W0 | ⬜ pending |
| 04-*-* | TBD | TBD | BOARD-02 | — | Category mutations scoped to owner | integration | `pnpm test app/board/categories.test.tsx` | ❌ W0 | ⬜ pending |
| 04-*-* | TBD | TBD | BOARD-03 | — | DnD moves persist via authenticated API | unit/DOM | `pnpm test app/board/dnd.test.tsx` | ❌ W0 | ⬜ pending |
| 04-*-* | TBD | TBD | BOARD-04 | — | Modal edit autosave authenticated | integration | `pnpm test app/board/modal.test.tsx` | ❌ W0 | ⬜ pending |
| 04-*-* | TBD | TBD | CAP-05 | — | Poll uses session; no cross-tenant leak | integration | `pnpm test app/board/poll.test.tsx` | ❌ W0 | ⬜ pending |
| 04-*-* | TBD | TBD | CAL-01 | — | OAuth connect behind auth middleware | unit/flow | `pnpm test app/settings/calendar.test.tsx` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `webapp/vitest.config.ts` — Vitest environment configuration
- [ ] `webapp/tests/setup.ts` — React Testing Library / DOM mocks
- [ ] Stub test files for BOARD-01..04, CAP-05, CAL-01 per RESEARCH Validation Architecture

*Planner fills exact Wave 0 task paths during planning.*

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
