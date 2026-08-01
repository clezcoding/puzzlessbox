---
phase: 04-webapp
plan: 01
subsystem: ui
tags: [nextjs, better-auth, vitest, shadcn, kanban, brand-tokens]

requires:
  - phase: 04-webapp
    plan: 00
    provides: Vitest infra, apiFetch, authClient, middleware, shadcn primitives
provides:
  - Brand-hero login/register page (D-24, D-25)
  - Board page with 5 default categories and empty states (D-05)
  - Session survival, ?next= redirect, avatar logout (D-28)
affects: [04-03, 04-04, 04-05]

tech-stack:
  added: [@testing-library/user-event, shadcn tabs/avatar/dropdown-menu]
  patterns: [getSafeNextPath open-redirect guard, category empty-copy map, board status filter]

key-files:
  created:
    - webapp/app/login/page.tsx
    - webapp/app/login/login-form.tsx
    - webapp/app/board/page.tsx
    - webapp/components/board/board-column.tsx
    - webapp/components/board/board-card.tsx
    - webapp/components/board/board-header.tsx
    - webapp/components/ui/tabs.tsx
    - webapp/components/ui/avatar.tsx
    - webapp/components/ui/dropdown-menu.tsx
    - webapp/lib/redirect.ts
    - webapp/lib/empty-copy.ts
    - webapp/lib/category-style.ts
    - webapp/tests/board.test.tsx
    - webapp/tests/auth.test.tsx
  modified:
    - webapp/next.config.ts
    - webapp/package.json

key-decisions:
  - "Login split: page.tsx Suspense wrapper + login-form.tsx client (Next.js 16 useSearchParams requirement)"
  - "TabsContent forceMount so register fields stay in DOM for RTL tests and D-25 visibility"
  - "getSafeNextPath rejects absolute/foreign URLs; relative ?next= honored post-login (T-04-04)"

patterns-established:
  - "Board filters items to auto_saved|confirmed client-side (defense-in-depth, D-04)"
  - "Empty states: per-category Apollo PNG + VOICE copy via lib/empty-copy.ts"

requirements-completed: [BOARD-01, CAP-05]

coverage:
  - id: D1
    description: "Login→Board tracer with 5 default categories from API"
    requirement: BOARD-01
    verification:
      - kind: unit
        ref: "webapp/tests/board.test.tsx#renders 5 default categories"
        status: pass
    human_judgment: false
  - id: D2
    description: "Board excludes draft items; shows auto_saved and confirmed only"
    requirement: BOARD-01
    verification:
      - kind: unit
        ref: "webapp/tests/board.test.tsx#renders only auto_saved and confirmed"
        status: pass
    human_judgment: false
  - id: D3
    description: "Empty Inbox column shows Apollo PNG + VOICE copy (D-05)"
    requirement: BOARD-01
    verification:
      - kind: unit
        ref: "webapp/tests/board.test.tsx#Apollo empty PNG and VOICE copy"
        status: pass
    human_judgment: false
  - id: D4
    description: "Register tab always visible; SIGNUP_LOCKED shows VOICE copy (D-25)"
    requirement: BOARD-01
    verification:
      - kind: unit
        ref: "webapp/tests/auth.test.tsx#SIGNUP_LOCKED VOICE copy"
        status: pass
    human_judgment: false
  - id: D5
    description: "Session survives refresh; ?next= redirect; avatar logout (D-28)"
    requirement: BOARD-01
    verification:
      - kind: unit
        ref: "webapp/tests/auth.test.tsx#session/?next=/logout"
        status: pass
    human_judgment: false
  - id: D6
    description: "Open-redirect guard rejects absolute ?next= URLs (T-04-04)"
    requirement: BOARD-01
    verification:
      - kind: unit
        ref: "webapp/tests/auth.test.tsx#rejects absolute ?next="
        status: pass
    human_judgment: false
  - id: D7
    description: "pnpm build succeeds without type errors"
    requirement: BOARD-01
    verification:
      - kind: other
        ref: "cd webapp && pnpm build"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-02
status: complete
---

# Phase 4 Plan 01: Login→Board Tracer Summary

**Brand-hero auth + Kanban board skeleton with Apollo empty states, session/?next=/logout wired end-to-end**

## Performance

- **Duration:** 25 min
- **Tasks:** 2
- **Files modified:** 26

## Accomplishments

- Login page: Apollo splash + wordmark, Anmelden|Registrieren tabs (register always visible), SIGNUP_LOCKED VOICE copy
- Board page: parallel getCategories + getBoardItems, 5-column grid, draft filter, per-category empty states with Apollo PNGs
- Board header: manual refresh, avatar dropdown with email truncate + logout → /login
- `getSafeNextPath` open-redirect guard for `?next=` (T-04-04)
- 11 Vitest tests green; `pnpm build` green

## Task Commits

1. **test(04-webapp-01): add board and auth tracer tests** - `2a4d5d7`
2. **feat(04-webapp-01): login→board tracer with Apollo empty states** - `58e82e8`
3. **test(04-webapp-01): session survival, ?next= redirect, logout** - `db2237b`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Next.js 16 useSearchParams requires Suspense boundary**
- **Found during:** Task 1 build verification
- **Issue:** `/login` prerender failed without Suspense around `useSearchParams`
- **Fix:** Split into `page.tsx` (Suspense) + `login-form.tsx` (client)
- **Files modified:** webapp/app/login/page.tsx, webapp/app/login/login-form.tsx
- **Commit:** 58e82e8

**2. [Rule 3 - Blocking] Radix dropdown menu tests need user-event**
- **Found during:** Task 2 avatar menu tests
- **Issue:** fireEvent.click did not open DropdownMenu portal in jsdom
- **Fix:** Added `@testing-library/user-event` devDependency
- **Commit:** db2237b

---

**Total deviations:** 2 auto-fixed (2 blocking)

## Issues Encountered

None blocking.

## User Setup Required

None.

## Next Phase Readiness

- 04-03+ can add DnD, modal, polling on this board shell
- No DnD/modal/poll in this plan (deferred per plan scope)

## Self-Check: PASSED

- FOUND: webapp/app/login/page.tsx
- FOUND: webapp/app/board/page.tsx
- FOUND: webapp/components/board/board-column.tsx
- FOUND: webapp/tests/auth.test.tsx
- FOUND: webapp/tests/board.test.tsx
- FOUND: 2a4d5d7
- FOUND: 58e82e8
- FOUND: db2237b

---
*Phase: 04-webapp*
*Completed: 2026-08-02*
