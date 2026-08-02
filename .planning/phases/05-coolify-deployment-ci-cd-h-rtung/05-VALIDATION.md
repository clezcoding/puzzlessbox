---
phase: 5
slug: coolify-deployment-ci-cd-h-rtung
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-02
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest (webapp) & pytest (api) |
| **Config file** | `webapp/vitest.config.ts`, `api/pytest.ini` |
| **Quick run command** | `pnpm --filter puzzlessbox-webapp test` / `pytest api/ -q` |
| **Full suite command** | `pnpm --filter puzzlessbox-webapp test && pytest api/ -q` |
| **Estimated runtime** | ~60–120 seconds |

---

## Sampling Rate

- **After every task commit:** Run relevant quick suite (webapp health route → vitest; API/Dockerfile → pytest smoke if touched)
- **After every plan wave:** Full suite green
- **Before `/gsd-verify-work`:** Full suite must be green + live OPS smoke curls
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|----------------|-----------------|-----------|-------------------|-------------|--------|
| 05-*-* | TBD | TBD | OPS-01 | T-05-01 | Webhook URLs only in GitHub Secrets | smoke | `curl -sS -o /dev/null -w '%{http_code}' https://api.puzzlesstool.online/health` | ✅ Live | ⬜ pending |
| 05-*-* | TBD | TBD | OPS-02 | T-05-01 | No hardcoded Coolify webhook in YAML | smoke | `actionlint` / `gh workflow view` | ✅ Live | ⬜ pending |
| 05-*-* | TBD | TBD | OPS-03 | T-05-02 | Local backup schedule enabled | smoke | `coolify --context hostunlimited database backup list pfqgb5pcvgi9oh64bpe3shtn` | ✅ Live | ⬜ pending |
| 05-*-* | TBD | TBD | OPS-04 | — | Unauth `/health` liveness only (not `/ready` gate) | smoke | `curl -sS https://pbox.puzzlesstool.online/api/health` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Planner fills concrete Task IDs after PLAN.md creation.*

---

## Wave 0 Requirements

- [ ] WebApp unauthenticated health route test (e.g. `webapp` route handler returns 200) — if not covered by existing vitest
- [ ] Workflow files present: `.github/workflows/deploy-api.yml`, `deploy-web.yml` — syntax via `actionlint` when installed
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

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
