---
phase: 05-coolify-deployment-ci-cd-h-rtung
plan: 03
subsystem: infra
tags: [coolify, ghcr, github-actions, api, dockerimage, traefik, webhook]

requires:
  - phase: 05-01
    provides: Baseline DB backup before API cutover (D-15)
provides:
  - deploy-api.yml GHCR build + Coolify GET webhook (OPS-02 API slice)
  - New Coolify dockerimage app pasmduuzitoh21qipyq3ay1l @ api.puzzlesstool.online (OPS-01)
  - /health liveness probe 10s/5s/5/15s on new API app (OPS-04)
affects: [05-04]

tech-stack:
  added: []
  patterns:
    - "deploy-api.yml GET webhook + HTTP 200/202 assert (D-06)"
    - "Coolify force_domain_override PATCH for immediate D-18 domain swap"
    - "workflow_dispatch + PR merge path when main branch protected"

key-files:
  created:
    - .github/workflows/deploy-api.yml
    - .planning/phases/05-coolify-deployment-ci-cd-h-rtung/05-03-api-cutover.json
  modified: []

key-decisions:
  - "New app UUID pasmduuzitoh21qipyq3ay1l — dockerimage ghcr.io/clezcoding/puzzlessbox-api:latest"
  - "COOLIFY_API_WEBHOOK via deploy API URL (D-19); secret set before webhook re-run"
  - "Domain swap via force_domain_override + old app domain cleared (D-18)"

patterns-established:
  - "Cutover trace JSON records Coolify UUIDs + workflow run for audit"

requirements-completed: [OPS-01, OPS-02, OPS-04]

coverage:
  - id: D1
    description: "deploy-api.yml path-filtered GHCR push + GET COOLIFY_API_WEBHOOK with 200/202 assert"
    requirement: OPS-02
    verification:
      - kind: other
        ref: "grep gate on deploy-api.yml; GH Actions run 30765847051 success"
        status: pass
    human_judgment: false
  - id: D2
    description: "New Coolify dockerimage app live at api.puzzlesstool.online pulling GHCR latest"
    requirement: OPS-01
    verification:
      - kind: manual_procedural
        ref: "Coolify app pasmduuzitoh21qipyq3ay1l fqdn https://api.puzzlesstool.online"
        status: pass
    human_judgment: true
    rationale: "Production cutover verified by human checkpoint approval"
  - id: D3
    description: "GET /health returns 200 {status:ok} over HTTPS; old dockerfile app stopped"
    requirement: OPS-04
    verification:
      - kind: manual_procedural
        ref: "curl https://api.puzzlesstool.online/health → 200; old app dxoflgio67786lc4yilhce43 exited"
        status: pass
    human_judgment: true
    rationale: "End-to-end tracer slice — human signed off post-cutover"

duration: 13min
completed: 2026-08-02
status: complete
---

# Phase 05 Plan 03: API GHCR Cutover Summary

**API migrated from Coolify dockerfile builds to GHCR dockerimage app with deploy-api.yml webhook pipeline and live /health at api.puzzlesstool.online**

## Performance

- **Duration:** 13 min
- **Started:** 2026-08-02T20:26:16Z
- **Completed:** 2026-08-02T20:39:00Z
- **Tasks:** 2 (tracer + human-verify checkpoint)
- **Files modified:** 2

## Accomplishments

- Added `deploy-api.yml`: path-filter `api/**`, GHCR `puzzlessbox-api` `:latest` + `:sha-<sha>`, GET webhook + 200/202 assert (D-05–D-08)
- Created Coolify dockerimage app `pasmduuzitoh21qipyq3ay1l` (`puzzlessbox-api-ghcr`) pulling `ghcr.io/clezcoding/puzzlessbox-api:latest`
- Domain `api.puzzlesstool.online` attached with Traefik/Let's Encrypt; `/health` returns **200 `{"status":"ok"}`**
- Health probe `/health` (D-12), timings 10s/5s/5/15s (D-14); Docker network `rmj3pan623pikht2yqq2efsd` (Pitfall 2)
- 15 env vars copied; `BETTER_AUTH_JWKS_URL` → `https://pbox.puzzlesstool.online/.well-known/jwks.json`
- Old dockerfile app `dxoflgio67786lc4yilhce43` stopped 2026-08-02T20:31:23Z; domain removed
- `COOLIFY_API_WEBHOOK` secret set; Deploy API workflow run `30765847051` green

## Coolify Inventory

| Resource | UUID | Notes |
|----------|------|-------|
| New API app | `pasmduuzitoh21qipyq3ay1l` | dockerimage, `puzzlessbox-api-ghcr` |
| Old API app | `dxoflgio67786lc4yilhce43` | dockerfile, stopped, no domain |
| GHCR image | `ghcr.io/clezcoding/puzzlessbox-api:latest` | Public (D-17) |
| Webhook secret | `COOLIFY_API_WEBHOOK` | Deploy API URL for new app |
| Last workflow | `30765847051` | success (webhook 200/202) |

## Task Commits

1. **Task 1: End-to-end API dockerimage cutover (tracer)** - `72cb6c9` (feat), `edeceb9` (feat)
2. **Task 2: Checkpoint human-verify** - approved by user (no commit)

**Plan metadata:** `0603bad` (docs: complete plan)

## Files Created/Modified

- `.github/workflows/deploy-api.yml` - GHCR build + Coolify GET webhook workflow
- `.planning/phases/05-coolify-deployment-ci-cd-h-rtung/05-03-api-cutover.json` - Cutover audit trace

## Decisions Made

- PR [#24](https://github.com/clezcoding/puzzlessbox/pull/24) squash-merge to main (branch protection blocked direct push)
- Domain conflict resolved via Coolify API `force_domain_override=true` (CLI lacks flag)
- Webhook URL pattern: `https://puzzlesstool.online/api/v1/deploy?uuid=<app-uuid>`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Main branch protection blocked direct workflow push**
- **Found during:** Task 1 (first GHCR build trigger)
- **Issue:** `deploy-api.yml` not on main → `gh workflow run` 404; direct push rejected by branch rules
- **Fix:** Opened PR #24, merged after CI green; first Deploy API run on main
- **Files modified:** none (process)
- **Verification:** Workflow registered; run 30765715720 started

**2. [Rule 3 - Blocking] Domain conflict on api.puzzlesstool.online**
- **Found during:** Task 1 (Coolify app update)
- **Issue:** CLI `app update --domains` returned 409 — old app still held domain
- **Fix:** Stopped old app, cleared its domain, PATCH new app with `force_domain_override=true`
- **Files modified:** none (Coolify ops)
- **Verification:** New app fqdn `https://api.puzzlesstool.online`; curl /health → 200

**3. [Rule 3 - Blocking] First workflow webhook failed (secret missing)**
- **Found during:** Task 1 (Deploy API run 30765715720)
- **Issue:** `COOLIFY_API_WEBHOOK` not set before first main push — webhook step exit 3
- **Fix:** Set secret via `gh secret set COOLIFY_API_WEBHOOK`; re-ran workflow_dispatch → run 30765847051 green
- **Files modified:** none (GitHub secret)
- **Verification:** Webhook step passed on re-run

---

**Total deviations:** 3 auto-fixed (3 blocking)
**Impact on plan:** Ops workarounds only; acceptance criteria met after fixes.

## Issues Encountered

- Coolify MCP `create_dockerimage_application` requires separate `docker_registry_image_tag` field
- Coolify CLI `app update` lacks `force_domain_override` — used direct API PATCH
- SERVICE_BEARER_TOKEN + SERVICE_OWNER_ID added post-bulk-env via MCP (Coolify-managed vars)

## User Setup Required

None remaining — `COOLIFY_API_WEBHOOK` configured during execution.

## Next Phase Readiness

- OPS-01/02/04 API slices satisfied; tracer proven end-to-end
- Plan 05-04 can reuse pattern for WebApp (`deploy-web.yml` already exists from 05-02)
- GHCR `puzzlessbox-api` package should stay Public (D-17)

## Self-Check: PASSED

- `.github/workflows/deploy-api.yml` — FOUND
- `05-03-api-cutover.json` — FOUND
- Commits `72cb6c9`, `edeceb9` — FOUND in git log
- `curl https://api.puzzlesstool.online/health` — 200

---
*Phase: 05-coolify-deployment-ci-cd-h-rtung*
*Completed: 2026-08-02*
