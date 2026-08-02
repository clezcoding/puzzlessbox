---
phase: 05-coolify-deployment-ci-cd-h-rtung
verified: 2026-08-02T21:25:00Z
status: passed
score: 4/4 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 5: Coolify-Deployment, CI/CD & Härtung — Verification Report

**Phase Goal:** Alle drei Apps laufen als separate Coolify-Docker-Image-Apps produktiv unter `*.puzzlesstool.online`, Builds laufen über GitHub Actions → GHCR → Coolify-Webhook, und Backups/Health Checks sind aktiv.

**Verified:** 2026-08-02T21:25:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | API, MCP und WebApp laufen als separate Coolify-Docker-Image-Apps unter `*.puzzlesstool.online` mit Traefik/Let's-Encrypt-HTTPS | ✓ VERIFIED | Coolify MCP: API `pasmduuzitoh21qipyq3ay1l` (`dockerimage`, `ghcr.io/clezcoding/puzzlessbox-api:latest`, fqdn `https://api.puzzlesstool.online`, `running:healthy`); MCP `n5frtiupale5c2zjm9fyk1qc` (`dockerimage`, mcp domain, healthy); Web `qxpgv6p1rp3vupue9al8hbzz` (`dockerimage`, `pbox…`, healthy). Old API `dxoflgio67786lc4yilhce43` `exited:unhealthy`, `fqdn: null`. Live curl all three health URLs HTTP 200; TLS issuer Let's Encrypt YR2 on all three hosts. |
| 2 | Ein Push auf `main` triggert pro Service einen GitHub-Actions-Build, pusht `:latest` und `:sha-<sha>` nach GHCR und löst den Coolify-Deploy-Webhook aus | ✓ VERIFIED | Workflows present: `deploy-api.yml`, `deploy-web.yml`, `deploy-mcp.yml` — path filters, `type=raw,value=latest` + `type=sha,prefix=sha-`, webhook steps with `secrets.COOLIFY_*`. Secrets: `COOLIFY_TOKEN`, `COOLIFY_API_WEBHOOK`, `COOLIFY_WEB_WEBHOOK`, `COOLIFY_MCP_WEBHOOK`. Successful runs: API `30765847051` (Trigger Coolify deploy = success), Web `30766860364` (same). Actions SHA-pinned (D-08). |
| 3 | PostgreSQL hat einen aktiven lokalen Backup-Schedule auf dem Coolify-Server | ✓ VERIFIED | Live `get_database_backups` on `pfqgb5pcvgi9oh64bpe3shtn`: schedule `jl0skzwpd3ot7hgfmohlny9s` `enabled=true`, cron `0 3 * * *`, retention 14/14 local, `save_s3=false`. Baseline execution `ibaby40uszso4coqgxjtgp1b` `status=success`, size 21052. Matches `05-01-backup-schedule.json` / `05-01-baseline-backup.json`. |
| 4 | Jede App hat einen Health-Check-Endpoint und Coolify ist so konfiguriert, dass abgestürzte Container nicht mehr geroutet werden | ✓ VERIFIED | Code: API `/health` (`api/app/routers/health.py`), MCP `/health` (`mcp-server/app/health.py`), Web `/api/health` (`webapp/app/api/health/route.ts` + vitest 3/3 pass). Coolify: all three `health_check_enabled=true`, paths `/health` \| `/api/health` (not `/ready`), timings 10s/5s/5/15s (D-14), `status=running:healthy`. Live endpoints 200. |

**Score:** 4/4 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `.github/workflows/deploy-api.yml` | GHCR + webhook CI for API | ✓ VERIFIED | Path-filtered, SHA-pinned actions, GET webhook + 200/202 assert |
| `.github/workflows/deploy-web.yml` | GHCR + webhook CI for Web | ✓ VERIFIED | `workflow_dispatch`, context `.` + `webapp/Dockerfile` |
| `.github/workflows/deploy-mcp.yml` | GHCR + webhook CI for MCP | ✓ VERIFIED | Exists from Phase 2; POST webhook left as-is (COVERAGE OPT-OUT) |
| `webapp/Dockerfile` | standalone multi-stage image | ✓ VERIFIED | `node:24-alpine`, pnpm frozen-lockfile, non-root `nextjs`, `EXPOSE 3000`, `CMD node server.js`, `curl` in runner |
| `webapp/app/api/health/route.ts` | unauth liveness | ✓ VERIFIED | Returns `{status:'ok'}`; live 200 |
| `webapp/app/api/health/route.test.ts` | unit coverage | ✓ VERIFIED | `pnpm exec vitest run` → 3 passed |
| `webapp/next.config.ts` | `output: 'standalone'` | ✓ VERIFIED | Present |
| `COVERAGE.md` | INTEGRATE/OPT-OUT matrix | ✓ VERIFIED | Present with Coolify/GHCR/Actions capabilities |
| Coolify apps (API/Web/MCP UUIDs) | dockerimage under domains | ✓ VERIFIED | Live MCP `get_application` |
| Backup schedule + baseline | OPS-03 | ✓ VERIFIED | Live `get_database_backups` |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `deploy-api.yml` | GHCR `puzzlessbox-api` → Coolify API | `COOLIFY_API_WEBHOOK` GET + Bearer | ✓ WIRED | Run 30765847051 Trigger Coolify deploy = success; live `/health` 200 |
| `deploy-web.yml` | GHCR `puzzlessbox-web` → Coolify Web | `COOLIFY_WEB_WEBHOOK` GET + Bearer | ✓ WIRED | Run 30766860364 success; live `/api/health` 200 |
| `deploy-mcp.yml` | GHCR `puzzlessbox-mcp` → Coolify MCP | `COOLIFY_MCP_WEBHOOK` POST | ✓ WIRED | Prior Phase-2 success runs; live `/health` 200; MCP POST `/mcp` no-auth → 401 |
| Coolify health probe | App `/health` or `/api/health` | Docker healthcheck → Traefik | ✓ WIRED | Paths ≠ `/ready`; apps `running:healthy` |
| Coolify CLI/MCP | `puzzlessbox-db` backup | schedule UUID | ✓ WIRED | Enabled schedule + successful baseline |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `/api/health` route | static `{status:'ok'}` | intentional liveness (D-13) | N/A (by design no DB) | ✓ FLOWING (liveness contract) |
| Coolify apps | GHCR image tags | `docker_registry_image_name` + `:latest` | Yes — containers healthy | ✓ FLOWING |
| Backup schedule | local pg-dump files | Coolify backup execution | Yes — 21KB dump on disk | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| API health live | `curl https://api.puzzlesstool.online/health` | HTTP 200 `{"status":"ok"}` | ✓ PASS |
| MCP health live | `curl https://mcp.puzzlesstool.online/health` | HTTP 200 + service field | ✓ PASS |
| Web health live | `curl https://pbox.puzzlesstool.online/api/health` | HTTP 200 `{"status":"ok"}` | ✓ PASS |
| MCP auth gate | `POST /mcp` no auth | HTTP 401 | ✓ PASS |
| TLS LE | openssl s_client ×3 hosts | issuer Let's Encrypt YR2 | ✓ PASS |
| Web health unit | `vitest run app/api/health/route.test.ts` | 3/3 passed | ✓ PASS |
| Coolify backup live | MCP `get_database_backups` | enabled cron + success baseline | ✓ PASS |
| CI webhook step | `gh run view` API+Web success runs | Trigger Coolify deploy = success | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No `scripts/*/tests/probe-*.sh` declared for this phase | SKIP |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| OPS-01 | 05-03, 05-04 | Separate Coolify dockerimage apps under `*.puzzlesstool.online` | ✓ SATISFIED | Three apps live; LE HTTPS; old API stopped |
| OPS-02 | 05-02, 05-03, 05-04 | GHA → GHCR `:latest`+`:sha-*` → Coolify webhook | ✓ SATISFIED | Three workflows; secrets; successful deploy steps |
| OPS-03 | 05-01 | Local Postgres backup schedule | ✓ SATISFIED | Live schedule enabled; baseline success |
| OPS-04 | 05-02–05-04 | Health endpoints + Coolify health checks | ✓ SATISFIED | Code + Coolify config + live 200s |

**Orphaned requirements:** none — all Phase-5 IDs (OPS-01..04) claimed by plans. OPS-05/OPS-06 are v2 deferred (explicitly out of this phase / prohibitions).

### Prohibitions

| Statement | Status | Evidence |
| --------- | ------ | -------- |
| No S3/offsite in Phase 5 (OPS-06 deferred) | ✓ held | `save_s3=false`, `s3_storage_id=null` |
| No hardcoded webhook URLs/tokens in YAML | ✓ held | Workflows only reference `secrets.*` |
| No `/ready` as Traefik/Coolify gate | ✓ held | Coolify paths `/health` or `/api/health` only |
| No `build_pack` switch on old API (D-02) | ✓ held | New dockerimage apps; old remains `dockerfile` + stopped |
| No GlitchTip / S3 / scraper harden in 05-04 | ✓ held | Not present; OPS-05/06 v2 |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | No TBD/FIXME/XXX/TODO in phase-modified deploy artifacts | — | — |
| Coolify API app env (runtime) | — | `BETTER_AUTH_BASE_URL` still `https://app.puzzlesstool.online/api/auth` (copied from old app); JWKS correctly `pbox…` | ℹ️ Info | Not roadmap SC failure; JWKS (D-research) correct. Consider aligning BASE_URL to `pbox` in a follow-up if auth edge cases appear. |

### Human Verification Required

None — live endpoints, Coolify MCP state, CI runs, backup schedule, and unit tests all verified programmatically. Phase checkpoints (05-03/05-04) already approved by operator; orchestrator smoke reconfirmed.

### Gaps Summary

No gaps. Phase goal achieved.

**Note (non-blocking):** GHCR package visibility API returned 403 (`read:packages` scope missing). Coolify successfully pulls and runs images (`running:healthy`) — pull path proven. Operator confirmed Public at 05-04 checkpoint (D-17).

---

_Verified: 2026-08-02T21:25:00Z_
_Verifier: Claude (gsd-verifier)_
