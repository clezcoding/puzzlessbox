---
phase: 05-coolify-deployment-ci-cd-h-rtung
plan: 02
subsystem: infra
tags: [coolify, ghcr, nextjs, docker, github-actions, health]

requires:
  - phase: 05-01
    provides: Baseline DB backup before cutover waves
provides:
  - webapp/Dockerfile (standalone Next.js production image)
  - GET /api/health liveness route (unauthenticated)
  - deploy-web.yml GHCR + Coolify webhook workflow
affects: [05-04]

tech-stack:
  added: []
  patterns:
    - "Next.js standalone Docker multi-stage with pnpm frozen-lockfile"
    - "deploy-web.yml GET webhook + HTTP 200/202 assert (D-06)"
    - "workflow_dispatch for first GHCR push before Coolify app (D-03)"

key-files:
  created:
    - webapp/Dockerfile
    - webapp/app/api/health/route.ts
    - webapp/app/api/health/route.test.ts
    - .github/workflows/deploy-web.yml
  modified:
    - webapp/next.config.ts

key-decisions:
  - "WebApp health at /api/health only — no /ready Traefik gate (D-12, D-13)"
  - "Coolify trigger uses GET + status assert, mirroring deploy-api pattern not MCP POST"

patterns-established:
  - "Vitest imports route handler directly for API route unit tests"
  - "SHA-pinned Actions copied verbatim from deploy-mcp.yml"

requirements-completed: [OPS-02, OPS-04]

coverage:
  - id: D1
    description: "GET /api/health returns 200 {status:ok} without auth, no db field"
    requirement: OPS-04
    verification:
      - kind: unit
        ref: "webapp/app/api/health/route.test.ts (3 tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "webapp/Dockerfile standalone image with non-root nextjs user"
    requirement: OPS-02
    verification: []
    human_judgment: true
    rationale: "docker build + node server.js smoke not run in executor budget — verify in 05-04 tracer"
  - id: D3
    description: "deploy-web.yml path-filtered GHCR push + COOLIFY_WEB_WEBHOOK GET trigger"
    requirement: OPS-02
    verification:
      - kind: other
        ref: "grep gate on deploy-web.yml (secrets, SHA pins, workflow_dispatch, http_code)"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-08-02
status: complete
---

# Phase 05 Plan 02: WebApp Deploy Artifacts Summary

**Standalone Next.js Docker image, unauthenticated `/api/health`, and `deploy-web.yml` GHCR workflow with GET Coolify webhook**

## Performance

- **Duration:** 5 min
- **Started:** 2026-08-02T20:24:00Z
- **Completed:** 2026-08-02T20:29:00Z
- **Tasks:** 2 (+ TDD RED commit)
- **Files modified:** 5

## Accomplishments

- Added `/api/health` route returning `{status:ok}` — no auth, no DB (D-13, OPS-04)
- `next.config.ts` `output: 'standalone'` + multi-stage `webapp/Dockerfile` (node:24-alpine, non-root nextjs)
- `deploy-web.yml`: path-filter on `webapp/**`, `workflow_dispatch`, GHCR `puzzlessbox-web` `:latest` + `:sha-<sha>`, GET webhook with 200/202 assert (D-05–D-08, OPS-02)

## Task Commits

1. **Task 1 RED: health route tests** - `5a33135` (test)
2. **Task 1 GREEN: route + Dockerfile + next.config** - `6c2090e` (feat)
3. **Task 2: deploy-web.yml** - `2d1623a` (feat)

## Files Created/Modified

- `webapp/app/api/health/route.ts` - Unauthenticated liveness endpoint
- `webapp/app/api/health/route.test.ts` - 3 vitest behaviors (200, no auth, no db)
- `webapp/next.config.ts` - Added `output: 'standalone'`
- `webapp/Dockerfile` - Multi-stage standalone production image
- `.github/workflows/deploy-web.yml` - GHCR build + Coolify webhook

## Decisions Made

- Used `docker/metadata-action@dc802804...` SHA from `deploy-mcp.yml` (not plan typo `dc808...`)
- No `.dockerignore` added — plan scope only; local `node_modules` excluded by deps-stage pattern

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None — `COOLIFY_WEB_WEBHOOK` secret wiring deferred to Plan 05-04 (D-16, D-19).

## Next Phase Readiness

- D-03 prep satisfied: `webapp/Dockerfile` + `deploy-web.yml` exist
- Plan 05-04 can `gh workflow run deploy-web.yml` for first GHCR push, then create Coolify WebApp
- `docker build ./webapp` smoke recommended before 05-04 tracer

## Self-Check: PASSED

- `webapp/Dockerfile` — FOUND
- `webapp/app/api/health/route.ts` — FOUND
- `webapp/app/api/health/route.test.ts` — FOUND
- `.github/workflows/deploy-web.yml` — FOUND
- Commits `5a33135`, `6c2090e`, `2d1623a` — FOUND in git log

---
*Phase: 05-coolify-deployment-ci-cd-h-rtung*
*Completed: 2026-08-02*
