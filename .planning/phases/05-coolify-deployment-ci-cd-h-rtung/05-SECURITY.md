---
phase: 05
slug: coolify-deployment-ci-cd-h-rtung
status: verified
threats_open: 0
asvs_level: 1
created: 2026-08-02
---

# Phase 05 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Coolify CLI → Coolify API | hostunlimited context token; backup schedule/config | Schedule UUIDs, retention settings |
| GitHub Actions → GHCR | `GITHUB_TOKEN` push of public images | Image layers (api/web) |
| GHCR → Coolify pull | Public `ghcr.io/clezcoding/puzzlessbox-{api,web}:latest` (D-17) | Image digests |
| Workflow → Coolify webhook | curl GET + Bearer `COOLIFY_TOKEN` | Deploy trigger only |
| New API app → Postgres + scraper | Internal Docker network (`rmj3pan623pikht2yqq2efsd`) | DB creds, scraper traffic |
| Public internet → api.*/health | Unauthenticated liveness (no DB) | Static `{status:ok}` |
| Public internet → pbox.*/api/health | Unauthenticated liveness (no DB/auth) | Static `{status:ok}` |
| WebApp → API | Session cookie + service bearer over HTTPS | JWT, board/item payloads |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-05-01 | Information Disclosure | backup retention | low | accept | Local-only backups on Coolify host; `save_s3=false`; VPS gated by Coolify auth (D-11) | closed |
| T-05-02 | Tampering | backup schedule config | medium | mitigate | Coolify CLI/MCP hostunlimited; schedule `jl0skzwpd3ot7hgfmohlny9s` + baseline `ibaby40uszso4coqgxjtgp1b` recorded in 05-01-SUMMARY | closed |
| T-05-03 | Information Disclosure | deploy-web.yml webhook URLs/tokens | high | mitigate | Only `secrets.COOLIFY_WEB_WEBHOOK` / `secrets.COOLIFY_TOKEN`; no hardcoded URLs; Actions pinned by SHA | closed |
| T-05-04 | Denial of Service | /api/health route | low | mitigate | Static `{status:ok}`; no DB/fetch; vitest asserts no `db` field (D-13) | closed |
| T-05-05 | Information Disclosure | deploy-api.yml webhook URL/token | high | mitigate | Only `secrets.COOLIFY_API_WEBHOOK` / `secrets.COOLIFY_TOKEN`; no hardcoded URLs; Actions pinned by SHA | closed |
| T-05-06 | Denial of Service | /health (public) | low | mitigate | `api/app/routers/health.py` liveness-only; `/ready` not Traefik gate (D-12) | closed |
| T-05-07 | Spoofing | old dockerfile app left running | medium | mitigate | Domain swap + stop `dxoflgio67786lc4yilhce43` at 2026-08-02T20:31:23Z (05-03-SUMMARY) | closed |
| T-05-08 | Tampering | env var migration (15 vars) | medium | mitigate | 15 vars copied verbatim; only `BETTER_AUTH_JWKS_URL` → pbox; DB connectivity verified post-swap | closed |
| T-05-09 | Information Disclosure | deploy-web.yml webhook URL/token | high | mitigate | Same as T-05-03 — secrets-only refs in `deploy-web.yml` (05-02 authored, 05-04 cutover) | closed |
| T-05-10 | Denial of Service | /api/health (public) | low | mitigate | Same as T-05-04 — live `https://pbox.puzzlesstool.online/api/health` → 200 (D-13) | closed |
| T-05-11 | Spoofing | WebApp → API calls | medium | mitigate | Coolify env: `BETTER_AUTH_URL` + API base pinned to `pbox` / `api.puzzlesstool.online` (HTTPS); session cookies scoped to pbox | closed |
| T-05-12 | Tampering | MCP health retune | low | mitigate | Authenticated Coolify REST PATCH on `n5frtiupale5c2zjm9fyk1qc` → D-14 timings 10s/5s/5/15s | closed |
| T-05-SC | Tampering | npm/docker supply chain | high | mitigate | `webapp/pnpm-lock.yaml` + `frozen-lockfile` in Dockerfile; `api/requirements.txt` pinned; no new installs in phase | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above `workflow.security_block_on` count toward `threats_open`*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-05-01 | T-05-01 | Local-only Postgres backups on Coolify host; no offsite/S3 in v1 (D-11). VPS access already gated by Coolify auth. Confirmed `save_s3=false` on schedule `jl0skzwpd3ot7hgfmohlny9s`. | gsd-secure-phase L1 | 2026-08-02 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-02 | 13 | 13 | 0 | gsd-secure-phase (L1 short-circuit) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-02

### L1 Classification Notes

- `register_authored_at_plan_time: true` — all four PLAN files had parseable `<threat_model>` blocks
- `workflow.security_asvs_level: 1` + `threats_open: 0` → auditor short-circuit (grep-depth sufficient)
- No `## Threat Flags` in SUMMARY files
- Duplicate `T-05-SC` rows from 05-02/03/04 collapsed to one register entry
