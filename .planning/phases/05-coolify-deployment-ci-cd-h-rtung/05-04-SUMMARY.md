---
phase: 05-coolify-deployment-ci-cd-h-rtung
plan: 04
subsystem: infra
tags: [coolify, ghcr, github-actions, webapp, nextjs, traefik, webhook, coverage]

requires:
  - phase: 05-02
    provides: webapp/Dockerfile, deploy-web.yml, /api/health route
  - phase: 05-03
    provides: API live at api.puzzlesstool.online (WebApp env dependency)
provides:
  - WebApp Coolify dockerimage app qxpgv6p1rp3vupue9al8hbzz @ pbox.puzzlesstool.online (OPS-01)
  - deploy-web.yml GHCR + COOLIFY_WEB_WEBHOOK pipeline green (OPS-02)
  - MCP health retuned to D-14; all three apps /health live (OPS-04)
  - COVERAGE.md INTEGRATE/OPT-OUT/MANUAL matrix for phase 5 APIs
affects: []

tech-stack:
  added: []
  patterns:
    - "Monorepo Docker build context (brand/tokens.css) for webapp GHCR image"
    - "curl in alpine runner for Coolify dockerimage health probe"
    - "Coolify REST PATCH for health timings when CLI/MCP schema lacks fields"

key-files:
  created:
    - .planning/phases/05-coolify-deployment-ci-cd-h-rtung/05-04-web-cutover.json
    - .planning/phases/05-coolify-deployment-ci-cd-h-rtung/COVERAGE.md
    - webapp/.dockerignore
  modified:
    - webapp/Dockerfile
    - .github/workflows/deploy-web.yml

key-decisions:
  - "WebApp UUID qxpgv6p1rp3vupue9al8hbzz — ghcr.io/clezcoding/puzzlessbox-web:latest @ pbox"
  - "COOLIFY_WEB_WEBHOOK via deploy API URL pattern (D-19)"
  - "MCP n5frtiupale5c2zjm9fyk1qc health retuned 10s/5s/5/15s via REST PATCH"
  - "Docker build context repo-root; brand/ required for globals.css import"

patterns-established:
  - "05-04-web-cutover.json audit trace mirrors 05-03-api-cutover.json"

requirements-completed: [OPS-01, OPS-02, OPS-04]

coverage:
  - id: D1
    description: "WebApp dockerimage app live at pbox.puzzlesstool.online pulling GHCR latest"
    requirement: OPS-01
    verification:
      - kind: manual_procedural
        ref: "curl https://pbox.puzzlesstool.online/api/health → 200; Coolify qxpgv6p1rp3vupue9al8hbzz running:healthy"
        status: pass
    human_judgment: true
    rationale: "Production cutover verified by human checkpoint approval"
  - id: D2
    description: "deploy-web.yml workflow_dispatch GHCR push + Coolify GET webhook 200/202"
    requirement: OPS-02
    verification:
      - kind: other
        ref: "GH Actions run 30766860364 success; COOLIFY_WEB_WEBHOOK secret set"
        status: pass
    human_judgment: false
  - id: D3
    description: "All three apps /health + WebApp /api/health; MCP D-14 timings; COVERAGE.md written"
    requirement: OPS-04
    verification:
      - kind: manual_procedural
        ref: "api/mcp/pbox health 200; backup schedule enabled + baseline; MCP POST /mcp → 401"
        status: pass
    human_judgment: true
    rationale: "Final phase verification — human signed off post-cutover"

duration: 40min
completed: 2026-08-02
status: complete
---

# Phase 05 Plan 04: WebApp GHCR Deploy Summary

**WebApp live at pbox.puzzlesstool.online via GHCR dockerimage Coolify app, MCP health aligned to D-14, COVERAGE.md API matrix complete — all three apps healthy**

## Performance

- **Duration:** 40 min
- **Started:** 2026-08-02T20:40:00Z
- **Completed:** 2026-08-02T21:16:00Z
- **Tasks:** 3 (tracer + auto + human-verify checkpoint)
- **Files modified:** 5

## Accomplishments

- First GHCR push via `deploy-web.yml` workflow_dispatch (run 30766860364 green after Docker fixes)
- Coolify dockerimage app `qxpgv6p1rp3vupue9al8hbzz` (`puzzlessbox-web`) @ `https://pbox.puzzlesstool.online`
- `/api/health` returns **200 `{"status":"ok"}`** over HTTPS (D-13); health probe D-14 (10s/5s/5/15s)
- `COOLIFY_WEB_WEBHOOK` secret set; webhook GET returns 200/202 on deploy
- Env: `BETTER_AUTH_URL`, `NEXT_PUBLIC_APP_URL`, `NEXT_PUBLIC_API_URL`, `DATABASE_URL`, `BETTER_AUTH_SECRET`
- MCP app `n5frtiupale5c2zjm9fyk1qc` health timings retuned to D-14
- `COVERAGE.md` documents Coolify/GHCR/Actions capabilities with INTEGRATE/OPT-OUT/MANUAL
- Final verification: API + MCP + WebApp healthy; backup schedule enabled + baseline success

## Coolify Inventory

| Resource | UUID | Notes |
|----------|------|-------|
| WebApp app | `qxpgv6p1rp3vupue9al8hbzz` | dockerimage, `puzzlessbox-web` |
| MCP app (retuned) | `n5frtiupale5c2zjm9fyk1qc` | D-14 timings via REST PATCH |
| GHCR image | `ghcr.io/clezcoding/puzzlessbox-web:latest` | Public (D-17, user confirmed) |
| Webhook secret | `COOLIFY_WEB_WEBHOOK` | Deploy API URL for WebApp |
| Last workflow | `30766860364` | success (webhook 200/202) |
| Backup schedule | `jl0skzw…` | enabled; baseline `ibaby40…` success |

## Task Commits

1. **Task 1: End-to-end WebApp dockerimage deploy (tracer)** — `0415694` (feat); Docker fixes on main via PR #26 (`b53b210`), PR #27 (`6004fc9`)
2. **Task 2: MCP health retune + COVERAGE.md** — `620f372` (docs)
3. **Task 3: Final phase verification checkpoint** — approved by user (no commit)

**Plan metadata:** pending final docs commit

## Files Created/Modified

- `.planning/phases/05-coolify-deployment-ci-cd-h-rtung/05-04-web-cutover.json` — WebApp cutover audit trace
- `.planning/phases/05-coolify-deployment-ci-cd-h-rtung/COVERAGE.md` — API capability matrix
- `webapp/Dockerfile` — monorepo context, pnpm-workspace.yaml, curl for healthcheck
- `webapp/.dockerignore` — exclude node_modules/.next from build context
- `.github/workflows/deploy-web.yml` — repo-root build context + brand/** path filter

## Decisions Made

- WebApp created via Coolify MCP when CLI `create dockerimage` returned 422
- Domain set via CLI `--domains "https://pbox.puzzlesstool.online"`
- Health timings via Coolify REST PATCH (CLI `update_application` lacks interval fields)
- `curl` added to runner image — Coolify deploy health probe requires curl/wget in container

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Docker build pnpm lockfile overrides mismatch**
- **Found during:** Task 1 (first deploy-web workflow run 30766157919)
- **Issue:** `pnpm-workspace.yaml` not copied — frozen-lockfile overrides mismatch
- **Fix:** Copy workspace yaml; switch build context to repo root for `brand/tokens.css`
- **Files modified:** `webapp/Dockerfile`, `deploy-web.yml`, `webapp/.dockerignore`
- **Commit:** PR #26 (`b53b210`)

**2. [Rule 1 - Bug] Coolify healthcheck rollback — no curl in alpine image**
- **Found during:** Task 1 (Coolify deploy rth4ce9w9lswdiqq9hcysi33)
- **Issue:** Container started but health probe failed (`curl: not found`, wget connection refused during start period)
- **Fix:** `RUN apk add --no-cache curl` in Dockerfile runner stage
- **Files modified:** `webapp/Dockerfile`
- **Commit:** PR #27 (`6004fc9`)

**3. [Rule 3 - Blocking] First webhook step failed (COOLIFY_WEB_WEBHOOK missing)**
- **Found during:** Task 1 (run 30766598688)
- **Issue:** Secret not set before first successful GHCR push webhook trigger
- **Fix:** `gh secret set COOLIFY_WEB_WEBHOOK` after app UUID known
- **Verification:** Re-run 30766860364 green including webhook step

---

**Total deviations:** 3 auto-fixed (2 bugs, 1 blocking)
**Impact on plan:** Ops/build fixes only; acceptance criteria met after fixes and user approval.

## Issues Encountered

- Coolify CLI `app create dockerimage` 422 — MCP `create_dockerimage_application` succeeded
- Coolify CLI `database backup list` JSON unmarshal error — verified via UI (user confirmed schedule + baseline)
- MCP GET `/mcp` returns 405; POST without auth returns 401 (expected MCP-02)

## User Setup Required

None remaining — `COOLIFY_WEB_WEBHOOK` configured; GHCR packages public (user confirmed at checkpoint).

## Next Phase Readiness

- Phase 5 all four plans complete; OPS-01..04 satisfied for API/MCP/WebApp slices
- Phase verification green; ready for phase-level verifier or milestone ship gate
- Deferred: OPS-05 GlitchTip, OPS-06 S3 offsite (later milestone)

## Self-Check: PASSED

- `.planning/phases/05-coolify-deployment-ci-cd-h-rtung/05-04-web-cutover.json` — FOUND
- `.planning/phases/05-coolify-deployment-ci-cd-h-rtung/COVERAGE.md` — FOUND
- Commits `0415694`, `620f372`, `6004fc9`, `b53b210` — FOUND in git log

---
*Phase: 05-coolify-deployment-ci-cd-h-rtung*
*Completed: 2026-08-02*
