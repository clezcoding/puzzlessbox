---
phase: 5
slug: coolify-deployment-ci-cd-h-rtung
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-08-02
validated: 2026-08-05
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest (webapp) & pytest (api) & node:test (workflows) |
| **Config file** | `webapp/vitest.config.ts`, `api/pytest.ini`, `tests/deploy-workflows.test.js` |
| **Quick run command** | `pnpm --filter puzzlessbox-webapp test` / `pytest api/ -q` / `node --test tests/deploy-workflows.test.js` |
| **Full suite command** | `pnpm --filter puzzlessbox-webapp test && pytest api/ -q && node --test tests/deploy-workflows.test.js` |
| **Estimated runtime** | ~60–120 seconds |

---

## Sampling Rate

- **After every task commit:** Run relevant quick suite (webapp health route → vitest; API/Dockerfile → pytest smoke if touched; workflows → node:test)
- **After every plan wave:** Full suite green
- **Before `/gsd-verify-work`:** Full suite must be green + live OPS smoke curls
- **Max feedback latency:** 120 seconds

---

Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|----------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 05-01 | W0 | OPS-03 | T-05-02 | Local backup schedule enabled | manual | `coolify --context hostunlimited database backup list pfqgb5pcvgi9oh64bpe3shtn` | ✅ Live | ✅ green |
| 05-03-01 | 05-03 | W0 | OPS-01 | T-05-01 | Webhook URLs only in GitHub Secrets (API) | manual | `curl -sS -o /dev/null -w '%{http_code}' https://api.puzzlesstool.online/health` | ✅ Live | ✅ green |
| 05-03-02 | 05-03 | W0 | OPS-02 | T-05-01 | No hardcoded Coolify webhook in YAML (API) | unit | `node --test tests/deploy-workflows.test.js` | ✅ Live | ✅ green |
| 05-04-01 | 05-04 | W0 | OPS-01 | T-05-01 | Webhook URLs only in GitHub Secrets (Web) | manual | `curl -sS -o /dev/null -w '%{http_code}' https://pbox.puzzlesstool.online/api/health` | ✅ Live | ✅ green |
| 05-04-02 | 05-04 | W0 | OPS-02 | T-05-01 | No hardcoded Coolify webhook in YAML (Web) | unit | `node --test tests/deploy-workflows.test.js` | ✅ Live | ✅ green |
| 05-02-01 | 05-02 | W0 | OPS-04 | — | Unauth `/health` liveness only (not `/ready` gate) | unit | `pnpm --filter puzzlessbox-webapp test run app/api/health/route.test.ts` | ✅ Live | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Planner fills concrete Task IDs after PLAN.md creation.*

---

## Wave 0 Requirements

- [x] WebApp unauthenticated health route test (e.g. `webapp` route handler returns 200) — if not covered by existing vitest
- [x] Workflow files present: `.github/workflows/deploy-api.yml`, `deploy-web.yml` — syntax via `actionlint` when installed
- Existing infrastructure: `api` `/health`+`/ready`, `deploy-mcp.yml` pattern, Coolify CLI/MCP for live smoke

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GitHub Secrets `COOLIFY_API_WEBHOOK` / `COOLIFY_WEB_WEBHOOK` set | OPS-02 | Secrets not readable after set | `gh secret list` shows names; trigger workflow and confirm deploy |
| Coolify health timings (10s/5s/5/15s) | OPS-04 | CLI/MCP cannot set interval/timeout/retries/start_period | Coolify UI → App → Health Check fields match D-14 |
| GHCR package public visibility | OPS-01 | Package settings UI after first push | GitHub Packages → `puzzlessbox-api` / `puzzlessbox-web` → Public |
| Baseline DB backup before API cutover | OPS-03 | Operator confirms backup exists | `coolify database backup list …` shows recent entry after trigger |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 120s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved
