---
phase: 04-webapp
plan: 07
subsystem: auth
tags: [better-auth, signup-locked, sessionStorage, vitest, prod-uat]

requires:
  - phase: 04-webapp
    provides: sessionStorage pb.signup_locked persistence from 04-05 login-form.tsx
provides:
  - Hardened isSignupLockedError across better-auth client error envelope shapes
  - Envelope-shape vitest coverage in auth.test.tsx
  - Prod UAT #6 / G-04-4 closed with sticky VOICE copy verified
affects: [04-UAT, 04-VERIFICATION, AUTH-03]

tech-stack:
  added: []
  patterns:
    - "isSignupLockedError: flat + nested body + stringify fallback with try/catch for circular refs"
    - "Prod signup UAT: browser_fill_form (userEvent-style) required for controlled React inputs"

key-files:
  created: []
  modified:
    - webapp/app/login/login-form.tsx
    - webapp/tests/auth.test.tsx
    - .planning/phases/04-webapp/04-UAT.md
    - .planning/phases/04-webapp/04-VERIFICATION.md

key-decisions:
  - "Export isSignupLockedError for direct envelope-shape unit tests"
  - "console.warn diagnostic on unrecognized register error shapes for prod follow-up"
  - "r3 UAT fail attributed to uncontrolled fill bypass; r4 pass with browser_fill_form"

patterns-established:
  - "SIGNUP_LOCKED detection must cover code/body/response.body/json/string + safe stringify fallback"

requirements-completed: [AUTH-03]

coverage:
  - id: D1
    description: "isSignupLockedError detects SIGNUP_LOCKED across better-auth envelope shapes"
    requirement: AUTH-03
    verification:
      - kind: unit
        ref: "webapp/tests/auth.test.tsx — describe isSignupLockedError envelope shapes"
        status: pass
    human_judgment: false
  - id: D2
    description: "Prod second registration shows sticky VOICE copy and sessionStorage pb.signup_locked=1"
    requirement: AUTH-03
    verification:
      - kind: automated_ui
        ref: "gsd-browser session uat-04-07 on https://pbox.puzzlesstool.online/login"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-05
status: complete
---

# Phase 4 Plan 07: SIGNUP_LOCKED Envelope Hardening Summary

**isSignupLockedError hardened for all better-auth 409 envelopes; prod UAT #6 shows sticky Apollo VOICE copy after second register**

## Performance

- **Duration:** ~45 min (Task 1 code + Task 2 prod UAT + Task 3 doc closure)
- **Started:** 2026-08-05T12:00:00Z (estimate)
- **Completed:** 2026-08-05T13:41:00Z
- **Tasks:** 3 completed
- **Files modified:** 4

## Accomplishments

- `isSignupLockedError` exported and hardened: flat message, code, nested body, Response-wrapped, json field, plain string, circular-ref-safe stringify fallback
- New `describe("isSignupLockedError envelope shapes")` vitest block — RED→GREEN in atomic commits
- Diagnostic `console.warn("[signup-locked] unrecognized error shape:", error)` in handleRegister else branches
- Prod UAT #6 r4 pass: VOICE copy sticky; `sessionStorage pb.signup_locked === "1"` after reload
- G-04-4 closed in `04-UAT.md` and `04-VERIFICATION.md`; Phase 4 UAT suite 18/18 pass

## Task Commits

1. **Task 1 RED: envelope-shape tests** — `f702ff2` (test)
2. **Task 1 GREEN: harden detector** — `ffd9dbd` (feat) — merged to main via PR #58
3. **Task 3: close G-04-4 docs** — (this commit)
4. **Plan metadata** — (docs commit with SUMMARY + STATE)

## Prod UAT #6 Evidence (gsd-browser uat-04-07)

Environment: https://pbox.puzzlesstool.online/login after PR #58 merge + deploy-web run 31011072659

- New bundle confirmed: `console.warn("[signup-locked]...")` in prod chunk `3janw2ynbrp4r.js`
- Register tab + `browser_fill_form` (E-Mail/Passwort, userEvent-style) + submit
- VOICE copy visible: „Registrierung ist geschlossen. Apollo lässt nur den ersten Nutzer rein.“
- Generic „Registrierung fehlgeschlagen.“ NOT present
- `sessionStorage pb.signup_locked === "1"`
- After reload: VOICE copy sticky immediately; Register tab active
- Fill method: `browser_fill_form` (not paste / not `evaluate value=`)

Prior r3 failure likely uncontrolled fill bypassing React `onChange` — not an envelope-shape miss after hardening.

## Files Created/Modified

- `webapp/app/login/login-form.tsx` — hardened `isSignupLockedError`, exported, diagnostic warn
- `webapp/tests/auth.test.tsx` — envelope-shape describe block + negative cases
- `.planning/phases/04-webapp/04-UAT.md` — test #6 pass; G-04-4 closed; status complete 18/18
- `.planning/phases/04-webapp/04-VERIFICATION.md` — G-04-4 moved to gaps_closed

## Decisions Made

- Export detector for direct unit tests rather than only form-integration mocks
- Keep existing flat mock shape from 04-05; add separate tests per envelope variant
- Attribute r3 fail to fill bypass; close gap on r4 pass without reopening closed gaps

## Deviations from Plan

None — plan executed exactly as written. Task 2 approved by orchestrator after gsd-browser UAT.

## Issues Encountered

None during Task 3 continuation.

## User Setup Required

None.

## Next Phase Readiness

- Phase 4 UAT complete (18/18); no open G-04-* gaps
- AUTH-03 satisfied on prod
- Branch `gsd/phase-04-webapp` holds code commits; docs on same branch — merge/PR as needed

## Self-Check: PASSED

- FOUND: `.planning/phases/04-webapp/04-07-SUMMARY.md`
- FOUND: commits f702ff2, ffd9dbd
- VERIFY: `result: pass` on UAT #6; no `status: failed` in 04-UAT.md

---
*Phase: 04-webapp*
*Completed: 2026-08-05*
