---
phase: 04-webapp
plan: 04
subsystem: ui
tags: [nextjs, polling, settings, calendar-oauth, theme, vitest]

requires:
  - phase: 04-webapp
    plan: 03
    provides: Board shell, DnD, modal, categories panel
provides:
  - 10s board poll with backoff merge + offline banner (CAP-05, D-32..D-37)
  - Settings hub /settings with Account, Calendar wizard, Appearance (D-26)
  - Google Calendar 3-step connect wizard + disconnect (CAL-01, D-27, D-30)
  - Theme + sound toggles; first-login Apollo welcome (D-07, D-31, D-36)
affects: [04-05]

tech-stack:
  added: [radix switch, webapp calendar API client]
  patterns:
    - "use-board-poll: 10s interval, exponential backoff + jitter, merge-by-id"
    - "calendar-wizard: connect → pick → done state machine via URL step param"
    - "pb.welcome.seen localStorage gate with ?next= override"

key-files:
  created:
    - webapp/lib/hooks/use-board-poll.ts
    - webapp/lib/hooks/use-sound.ts
    - webapp/lib/hooks/use-theme.ts
    - webapp/lib/api/calendar.ts
    - webapp/components/board/offline-banner.tsx
    - webapp/components/board/new-item-feedback.tsx
    - webapp/components/settings/calendar-wizard.tsx
    - webapp/app/settings/page.tsx
    - webapp/app/welcome/page.tsx
    - webapp/tests/poll.test.tsx
    - webapp/tests/settings.test.tsx
    - webapp/tests/calendar.test.tsx
  modified:
    - webapp/app/board/page.tsx
    - webapp/components/board/board-header.tsx
    - webapp/app/page.tsx
    - webapp/middleware.ts
    - api/app/routers/calendar.py
    - api/app/services/calendar.py

key-decisions:
  - "Poll always-on (no visibility pause); manual refresh resets backoff"
  - "New-item toast + optional WebAudio tick (sound default off, respects reduced-motion)"
  - "Calendar OAuth uses Phase 1 paths (/auth/google/connect, /calendars, /calendars/{id}/select)"
  - "Added API /auth/google/status + /auth/google/disconnect for wizard connected/disconnect states"
  - "Welcome routing via client HomeRedirect; ?next= wins over pb.welcome.seen"

patterns-established:
  - "Offline banner persistent with Erneut versuchen; last board data kept on screen"
  - "Settings sections: Account (password change + logout), Calendar wizard, Appearance"

requirements-completed: [CAP-05, CAL-01]

coverage:
  - id: D1
    description: "Board polls every ~10s, merges new/updated items, backoff on error"
    requirement: CAP-05
    verification:
      - kind: unit
        ref: "webapp/tests/poll.test.tsx"
        status: pass
    human_judgment: false
  - id: D2
    description: "Offline banner + retry; new-item toast + optional sound"
    requirement: CAP-05
    verification:
      - kind: unit
        ref: "webapp/tests/poll.test.tsx#offline banner"
        status: pass
    human_judgment: false
  - id: D3
    description: "Settings hub Account/Calendar/Appearance + password change"
    requirement: CAL-01
    verification:
      - kind: unit
        ref: "webapp/tests/settings.test.tsx"
        status: pass
    human_judgment: false
  - id: D4
    description: "Calendar 3-step wizard connect/pick/done + disconnect confirm"
    requirement: CAL-01
    verification:
      - kind: unit
        ref: "webapp/tests/calendar.test.tsx"
        status: pass
    human_judgment: false
  - id: D5
    description: "Theme toggle header+settings; first-login welcome flow"
    requirement: CAP-05
    verification:
      - kind: unit
        ref: "webapp/tests/settings.test.tsx#Welcome flow"
        status: pass
    human_judgment: false
  - id: D6
    description: "pnpm build succeeds"
    requirement: CAP-05
    verification:
      - kind: other
        ref: "cd webapp && pnpm build"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-08-02
status: complete
---

# Phase 4 Plan 04: Poll + Settings Summary

**10s live board poll with backoff/offline UX; Settings hub with Google Calendar wizard, theme/sound toggles, and first-login welcome**

## Performance

- **Duration:** 12 min
- **Tasks:** 2
- **Files modified:** 24

## Accomplishments

- `use-board-poll`: 10s base interval, 10→20→40→60s backoff + ±20% jitter, merge-by-id, always-on
- Offline banner (VOICE copy) + manual refresh; new-item sonner toast + terracotta pulse via existing board card styling
- `use-sound`: localStorage toggle default off; WebAudio tick respects `prefers-reduced-motion`
- `/settings` hub: Account (email, password change, logout), Google Calendar wizard, Appearance (theme + sound)
- Calendar wizard: Connect → Pick calendar → Done; disconnect confirm dialog
- `use-theme`: system/light/dark via `pb.theme` + `document.documentElement.dark`
- Board header: theme toggle + settings link in avatar menu
- First login `/welcome` → board; `pb.welcome.seen`; `?next=` overrides welcome
- 24 new Vitest tests (poll 11 + settings 8 + calendar 5); full suite 55 green; `pnpm build` green

## Task Commits

1. **feat(04-webapp-04): board poll, offline banner, new-item feedback** - `a57d150`
2. **feat(04-webapp-04): settings hub, calendar wizard, theme, welcome** - `f0c5b15`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical] API calendar status + disconnect endpoints**
- **Found during:** Task 2 calendar wizard connected/disconnect flows
- **Issue:** Phase 1 API had connect/list/select only; D-30 disconnect and connected-state detection missing
- **Fix:** Added `GET /auth/google/status` and `POST /auth/google/disconnect` in calendar router/service
- **Files modified:** `api/app/routers/calendar.py`, `api/app/services/calendar.py`
- **Commit:** `f0c5b15`

**2. [Rule 3 - Blocking] zodResolver type mismatch on build**
- **Found during:** `pnpm build` after Account password form
- **Issue:** `@hookform/resolvers/zod` incompatible with installed zod types
- **Fix:** Manual password validation in `account.tsx` (same UX, no new dependency)
- **Commit:** `f0c5b15`

**3. [Rule 1 - Asset] apollo-offline.png missing**
- **Found during:** Task 1 offline banner
- **Fix:** Used `apollo-avatar.png` with reduced opacity as offline icon placeholder
- **Commit:** `a57d150`

---

**Total deviations:** 3 auto-fixed (1 critical API, 1 blocking build, 1 asset)

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| threat_flag: new_endpoint | api/app/routers/calendar.py | GET /auth/google/status exposes selected_calendar_id to authenticated owner |

## TDD Gate Compliance

Tests and implementation committed per task (combined RED/GREEN). All 20 plan-specified tests covered across poll/settings/calendar suites.

## Issues Encountered

None blocking.

## User Setup Required

- `NEXT_PUBLIC_API_URL` — API base for OAuth connect redirect
- `NEXT_PUBLIC_APP_URL` — WebApp base for post-login routing
- Google OAuth credentials (Phase 1) for live calendar connect roundtrip

## Next Phase Readiness

- Plan 04-05+ can add deploy/hardening or manual QA OAuth roundtrip on staging
- Manual QA: poll while Hermes captures item; calendar OAuth on api.* callback redirect (may need API callback → app redirect hardening for production)

## Self-Check: PASSED

- FOUND: webapp/lib/hooks/use-board-poll.ts
- FOUND: webapp/components/settings/calendar-wizard.tsx
- FOUND: webapp/app/settings/page.tsx
- FOUND: webapp/app/welcome/page.tsx
- FOUND: webapp/tests/poll.test.tsx
- FOUND: webapp/tests/settings.test.tsx
- FOUND: webapp/tests/calendar.test.tsx
- FOUND: a57d150
- FOUND: f0c5b15

---
*Phase: 04-webapp*
*Completed: 2026-08-02*
