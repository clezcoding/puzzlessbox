---
phase: 02-mcp-server
plan: 04
subsystem: infra
tags: [coolify, ghcr, docker, traefik, mcp, deploy-mcp, bearer-auth]

requires:
  - phase: 02-mcp-server
    provides: FastMCP server + /health from 02-01 (stateless_http, allowed_hosts)
provides:
  - mcp-server/Dockerfile (python:3.14-slim, uvicorn, no alembic)
  - mcp-server/.dockerignore
  - .github/workflows/deploy-mcp.yml (GHCR :latest + :sha-, Coolify webhook)
  - Live Coolify Docker-Image-App at mcp.puzzlesstool.online (D-20/D-23)
affects: [03-hermes-plugin, 05-coolify-deployment]

tech-stack:
  added: [deploy-mcp.yml GHCR pipeline, Coolify Docker-Image-App]
  patterns: [separate MCP image/app decoupled from API; SHA-pinned GitHub Actions; Coolify webhook post-push]

key-files:
  created:
    - mcp-server/Dockerfile
    - mcp-server/.dockerignore
    - .github/workflows/deploy-mcp.yml
  modified: []

key-decisions:
  - "D-23 separate-image topology confirmed — own GHCR package, Coolify app, domain mcp.puzzlesstool.online"
  - "Coolify webhook uses API bearer auth (cfdfb19) — not raw URL-only POST"
  - "MCP_API_BASE_URL=http://puzzlessbox-api:8000 on shared Docker network rmj3pan623pikht2yqq2efsd"

patterns-established:
  - "MCP deploy mirrors API pattern: GHCR build on main path filter → webhook → Coolify pull"
  - "Health check /health via curl in Dockerfile base image (matches api/)"

requirements-completed: [MCP-02]

coverage:
  - id: D1
    description: MCP Dockerfile + GHCR deploy-mcp.yml with SHA-pinned actions and Coolify webhook
    requirement: MCP-02
    verification:
      - kind: integration
        ref: "docker build -t puzzlessbox-mcp:test mcp-server; deploy-mcp.yml YAML + grep gates"
        status: pass
    human_judgment: false
  - id: D2
    description: Live /health 200 over HTTPS with valid TLS at mcp.puzzlesstool.online
    requirement: MCP-02
    verification:
      - kind: manual_procedural
        ref: "curl -sS https://mcp.puzzlesstool.online/health → 200 {\"status\":\"ok\",\"service\":\"mcp-server\"}"
        status: pass
    human_judgment: false
  - id: D3
    description: POST /mcp without Authorization rejected (SC2)
    requirement: MCP-02
    verification:
      - kind: manual_procedural
        ref: "curl -sS -o /dev/null -w '%{http_code}' -X POST https://mcp.puzzlesstool.online/mcp → 401"
        status: pass
    human_judgment: false
  - id: D4
    description: POST /mcp with invalid Bearer token returns 401 invalid_token
    requirement: MCP-02
    verification:
      - kind: manual_procedural
        ref: "curl -sS -X POST https://mcp.puzzlesstool.online/mcp -H 'Authorization: Bearer WRONG' → expected 401, observed 500"
        status: fail
    human_judgment: true
    rationale: "Live probe returned HTTP 500 instead of 401 — auth error path needs fix before Hermes integration"
  - id: D5
    description: Coolify app healthy with /health check path configured
    requirement: MCP-02
    verification:
      - kind: manual_procedural
        ref: "Coolify app n5frtiupale5c2zjm9fyk1qc — health check /health enabled, app LIVE"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-31
status: complete
---

# Phase 2 Plan 04: MCP Deploy Summary

**Separate MCP Coolify Docker-Image-App at mcp.puzzlesstool.online — GHCR deploy-mcp.yml, TLS /health 200, bearer gate live (wrong-token path returns 500, not 401)**

## Performance

- **Duration:** 20 min (Task 1 infra + Task 2 live verification)
- **Started:** 2026-07-31T02:30:00Z
- **Completed:** 2026-07-31T03:10:00Z
- **Tasks:** 2 (decision pre-confirmed D-23 separate-image)
- **Files modified:** 3 (Task 1 code) + 1 (this SUMMARY)

## Accomplishments

- `mcp-server/Dockerfile` — python:3.14-slim, curl for health, uvicorn `app.server:app`, no alembic (D-06)
- `.github/workflows/deploy-mcp.yml` — path-filtered main push, GHCR `puzzlessbox-mcp:latest` + `:sha-<sha>`, Coolify webhook with bearer auth
- Coolify app **LIVE** at `https://mcp.puzzlesstool.online` (UUID `n5frtiupale5c2zjm9fyk1qc`)
- SC2 infra proven: HTTPS + `/health` 200 + unauthenticated `POST /mcp` → 401

## Task Commits

1. **Task 1: Dockerfile + GHCR-Deploy-Workflow + Coolify-Wiring** — `8958f72` (feat, via PR #14) + `cfdfb19` (fix: Coolify webhook bearer auth)
2. **Task 2: Deploy-Verifikation (Health + TLS + Auth)** — docs-only (this commit)

**Plan metadata:** `7cfcdeb` (docs: complete plan)

## Live Verification Evidence

Coolify app `n5frtiupale5c2zjm9fyk1qc` on network `rmj3pan623pikht2yqq2efsd`.

| Check | Command | Expected | Observed |
|-------|---------|----------|----------|
| Health + TLS | `curl -sS https://mcp.puzzlesstool.online/health` | 200 `{"status":"ok","service":"mcp-server"}` | **PASS** |
| No auth | `curl -sS -o /dev/null -w "%{http_code}" -X POST https://mcp.puzzlesstool.online/mcp` | 401 | **PASS** (401) |
| Wrong bearer | `curl -sS -X POST https://mcp.puzzlesstool.online/mcp -H "Authorization: Bearer WRONG"` | 401 invalid_token | **FAIL** (500) |
| Coolify health | App dashboard, path `/health` | healthy | **PASS** (LIVE) |

**Env (Coolify):** `SERVICE_BEARER_TOKEN`, `MCP_API_BASE_URL=http://puzzlessbox-api:8000`, `ENV=prod`

**Image:** `ghcr.io/<owner>/puzzlessbox-mcp:latest` pushed via `deploy-mcp` workflow on `main`.

## Files Created/Modified

- `mcp-server/Dockerfile` — production image, no alembic
- `mcp-server/.dockerignore` — excludes tests, cache, .env
- `.github/workflows/deploy-mcp.yml` — GHCR build-push + Coolify webhook

## Decisions Made

- D-23 **separate-image** topology confirmed (one-way): own image, domain, GHCR package, CI workflow
- Coolify webhook authenticated with API bearer (not anonymous POST)
- Internal API reachability via Docker network hostname `puzzlessbox-api:8000`

## Deviations from Plan

### Live Verification Deviation (not auto-fixed — out of Task 2 scope)

**1. Wrong Bearer returns 500 instead of 401**
- **Found during:** Task 2 (Deploy-Verifikation)
- **Issue:** Plan acceptance: `POST /mcp` with invalid Bearer → 401 `invalid_token`. Live probe returned HTTP 500.
- **Impact:** SC2 partially met — missing-auth path correct; invalid-token path surfaces server error. Likely FastMCP/Starlette auth middleware gap — fix deferred to follow-up (not blocking deploy infra).
- **Files:** none changed in this task (verification-only)
- **Tracked:** WINDOWS.md `unmet-truth`

---

**Total deviations:** 1 documented (live auth behavior)
**Impact on plan:** Deploy infra complete; invalid-token 401 should be fixed before Hermes plugin relies on error semantics.

## Issues Encountered

None blocking deploy. Wrong-bearer 500 noted above for future fix.

## User Setup Required

Coolify configuration completed by operator:
- Docker-Image-App from GHCR `puzzlessbox-mcp:latest`
- Domain `mcp.puzzlesstool.online` (Traefik/Let's Encrypt)
- Health check `/health`
- Webhook secret `COOLIFY_MCP_WEBHOOK` in GitHub
- Env vars per plan `user_setup` block

## Next Phase Readiness

- Phase 2 deploy slice complete — MCP live at `mcp.puzzlesstool.online`
- Phase 3 Hermes plugin can target production MCP URL with `SERVICE_BEARER_TOKEN`
- **Follow-up:** fix invalid Bearer → 401 (not 500) before relying on auth error codes in Hermes

## Self-Check: PASSED

- FOUND: `.planning/phases/02-mcp-server/02-04-SUMMARY.md`
- FOUND: `mcp-server/Dockerfile`
- FOUND: `.github/workflows/deploy-mcp.yml`
- FOUND: commits 8958f72, cfdfb19

---
*Phase: 02-mcp-server*
*Completed: 2026-07-31*
