---
phase: 04-webapp
plan: 05
subsystem: infra
tags: [coolify, cors, nextjs, docker, ghcr, better-auth]

requires:
  - phase: 04-webapp
    provides: WebApp UI, login, board, deploy pipelines from plans 04-00..04-04
provides:
  - Prod CORS_ORIGINS on API (pbox + localhost + app subdomain)
  - NEXT_PUBLIC_* baked into GHCR web image at build time
  - apollo-onboard.png served from /public
  - SIGNUP_LOCKED sessionStorage persistence across remount
affects: [05-coolify-deployment-ci-cd-h-rtung, 04-UAT, 05-UAT]

tech-stack:
  added: []
  patterns:
    - "NEXT_PUBLIC_* via Dockerfile ARG/ENV + deploy-web build-args"
    - "Coolify CORS_ORIGINS comma-separated override of config.py default"

key-files:
  created:
    - webapp/public/apollo-onboard.png
  modified:
    - api/app/core/config.py
    - webapp/Dockerfile
    - .github/workflows/deploy-web.yml
    - webapp/app/login/login-form.tsx

key-decisions:
  - "CORS_ORIGINS set in Coolify API env (ops) + mirrored in config.py default"
  - "Web image rebuilt via workflow_dispatch on gsd/phase-04-webapp (main merge still pending for auto-push path)"
  - "SIGNUP_LOCKED: sessionStorage flag survives navigation remount on 409"

patterns-established:
  - "Prod web client URLs must be build-args; runtime Coolify env cannot fix baked Next.js bundle"

requirements-completed: [BOARD-01, BOARD-02, CAP-05, CAL-01, AUTH-03, OPS-01, OPS-02]

coverage:
  - id: D1
    description: "API CORS allows pbox Origin preflight"
    requirement: OPS-02
    verification:
      - kind: other
        ref: "curl OPTIONS https://api.puzzlesstool.online/categories -H Origin:pbox → 200"
        status: pass
    human_judgment: false
  - id: D2
    description: "JWKS reachable at pbox /api/auth/jwks"
    requirement: AUTH-03
    verification:
      - kind: other
        ref: "curl https://pbox.puzzlesstool.online/api/auth/jwks → 200"
        status: pass
    human_judgment: false
  - id: D3
    description: "Prod web bundle does not reference localhost:8000"
    requirement: OPS-01
    verification:
      - kind: other
        ref: "grep localhost:8000 across login page JS chunks → 0 matches"
        status: pass
    human_judgment: false
  - id: D4
    description: "apollo-onboard.png returns 200 on prod"
    requirement: BOARD-01
    verification:
      - kind: other
        ref: "curl https://pbox.puzzlesstool.online/apollo-onboard.png → 200"
        status: pass
    human_judgment: false
  - id: D5
    description: "Board + Calendar settings load data for authenticated session (UAT #7, #15)"
    requirement: BOARD-02
    verification: []
    human_judgment: true
    rationale: "Requires authenticated browser session; connectivity blockers cleared but full board/calendar UAT not re-run in this executor"
  - id: D6
    description: "SIGNUP_LOCKED UI shows VOICE copy on second register (UAT #6)"
    requirement: AUTH-03
    verification:
      - kind: unit
        ref: "webapp/tests/auth.test.tsx#SIGNUP_LOCKED"
        status: pass
    human_judgment: true
    rationale: "Prod repro after connectivity fix needs manual UAT; sessionStorage fix shipped as preventive"

duration: 5min
completed: 2026-08-03
status: complete
---

# Phase 4 Plan 5: Prod UAT Gap Closure Summary

**Coolify CORS + JWKS verified, NEXT_PUBLIC URLs baked into GHCR web image, onboard PNG shipped, SIGNUP_LOCKED remount fix**

## Performance

- **Duration:** 5 min
- **Started:** 2026-08-03T00:02:54Z
- **Completed:** 2026-08-03T00:08:00Z
- **Tasks:** 5
- **Files modified:** 5

## Accomplishments

- Coolify API `CORS_ORIGINS` created; OPTIONS preflight from pbox returns 200 with `access-control-allow-origin`
- `BETTER_AUTH_JWKS_URL` confirmed at `https://pbox.puzzlesstool.online/api/auth/jwks` (no drift)
- `config.py` default CORS includes pbox subdomain
- Web Dockerfile + deploy-web.yml pass `NEXT_PUBLIC_API_URL` / `NEXT_PUBLIC_APP_URL` build-args
- `apollo-onboard.png` copied to `webapp/public/`; prod returns 200 after redeploy
- Login form persists SIGNUP_LOCKED via sessionStorage across remount

## Task Commits

1. **Task 1: Coolify API env — CORS + JWKS** — ops only (Coolify MCP; no git commit)
2. **Task 2: Code default CORS_ORIGINS** — `21fd4df` (fix)
3. **Task 3+4: Web build-args + onboard PNG** — `9ea0f7d` (feat)
4. **Task 5: SIGNUP_LOCKED UI** — `dae24eb` (fix)

**Plan metadata:** pending (docs commit after STATE update)

## Files Created/Modified

- `api/app/core/config.py` — pbox in default CORS_ORIGINS
- `webapp/Dockerfile` — ARG/ENV for NEXT_PUBLIC_* before build
- `.github/workflows/deploy-web.yml` — build-args for GHCR image
- `webapp/public/apollo-onboard.png` — welcome page asset
- `webapp/app/login/login-form.tsx` — sessionStorage SIGNUP_LOCKED persistence

## Decisions Made

- Triggered `Deploy WebApp` via `workflow_dispatch` on `gsd/phase-04-webapp` (branch pushed; not yet merged to main)
- Coolify API needed deploy (not just restart) for CORS_ORIGINS to take effect

## Deviations from Plan

None - plan executed as written. Task 1 ops-only (no file commit per convention).

## Automated Verification Results

| Check | Result |
|-------|--------|
| CORS OPTIONS pbox → 200 | PASS |
| JWKS GET → 200 | PASS |
| apollo-onboard.png → 200 | PASS |
| signup POST → 409 | PASS |
| pbox/api health → ok | PASS |
| localhost:8000 in JS chunks | 0 matches (PASS) |
| api.puzzlesstool.online in initial chunks | not found (lazy-loaded modules; localhost absent is primary signal) |

## Deploy Status

- **API:** Coolify restart + deploy queued; CORS live
- **Web:** GHCR rebuild succeeded ([run 30773587394](https://github.com/clezcoding/puzzlessbox/actions/runs/30773587394)); Coolify webhook triggered; apollo PNG 200 confirms new image
- **Branch:** `gsd/phase-04-webapp` pushed; merge to `main` needed for path-filter auto-deploy on future commits

## Issues Encountered

- `workflow_dispatch` failed until branch pushed to origin
- First CORS check returned 400 until API deploy (restart alone insufficient)

## User Setup Required

None for this plan — Coolify env patched via MCP.

## Next Phase Readiness

- Re-run prod UAT #6–11, #15–18 on https://pbox.puzzlesstool.online
- Merge `gsd/phase-04-webapp` → `main` for standard CI path
- G-05-4 (`/openapi.json` public) still deferred per plan

---
*Phase: 04-webapp*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: .planning/phases/04-webapp/04-05-SUMMARY.md
- FOUND: 21fd4df, 9ea0f7d, dae24eb
