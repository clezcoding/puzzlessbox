# Phase 05 — Coolify / GHCR / GitHub Actions API Coverage

Capability matrix for Phase 5 deployment automation. Classifications: **INTEGRATE** (used in phase), **OPT-OUT** (evaluated, not used), **MANUAL** (human/UI step per D-19).

| Capability | Class | Reason |
|------------|-------|--------|
| `coolify app create dockerimage` (CLI) | INTEGRATE | Primary path for API + WebApp dockerimage apps (D-02). CLI `create dockerimage` with `--domains`, `--health-check-path`. |
| `create_dockerimage_application` (MCP) | INTEGRATE | WebApp app created when CLI returned 422; MCP succeeded (`qxpgv6p1rp3vupue9al8hbzz`). |
| `coolify app update` — domains | INTEGRATE | Set `pbox.puzzlesstool.online` / `api.puzzlesstool.online` via `--domains "https://…"`. |
| `coolify app update` — health path | INTEGRATE | `--health-check-enabled --health-check-path /api/health` or `/health`. |
| `coolify app update` — health timings (interval/timeout/retries/start_period) | INTEGRATE | CLI/MCP `update_application` lacks timing fields; **Coolify REST PATCH** `/api/v1/applications/{uuid}` used (D-14). |
| `coolify app update` — `build_pack` switch dockerfile→dockerimage | OPT-OUT | Not supported; new-app cutover required (D-02, RESEARCH Pitfall 1). |
| `coolify app update` — `force_domain_override` | INTEGRATE | API cutover 05-03: CLI lacks flag; PATCH with `force_domain_override=true` (D-18). |
| `update_application_envs_bulk` (MCP) | INTEGRATE | WebApp + API env copy (DATABASE_URL, BETTER_AUTH_*, NEXT_PUBLIC_*). |
| `deploy_application` / Deploy Webhook GET | INTEGRATE | `deploy-api.yml` / `deploy-web.yml` curl GET + 200/202 assert (D-06). |
| `coolify database backup create` | INTEGRATE | Plan 05-01 baseline schedule on `pfqgb5pcvgi9oh64bpe3shtn` (D-09). |
| `coolify database backup trigger` | INTEGRATE | Baseline backup before API cutover (D-10). |
| `gh secret set` | INTEGRATE | `COOLIFY_API_WEBHOOK`, `COOLIFY_WEB_WEBHOOK` (D-16). |
| `gh workflow run deploy-web.yml` / `deploy-api.yml` | INTEGRATE | First GHCR push before Coolify app pull (D-03 workflow_dispatch). |
| GHCR `docker/build-push-action` | INTEGRATE | `puzzlessbox-api`, `puzzlessbox-web`, `puzzlessbox-mcp` :latest + :sha-* (D-07). |
| GHCR package visibility → Public (API) | MANUAL | GitHub Packages UI after first push (D-17); `gh api` package visibility returned 404 for org packages — user must confirm Public in UI. |
| Coolify Deploy Webhook URL discovery | MANUAL | Pattern `https://puzzlesstool.online/api/v1/deploy?uuid={app-uuid}` documented; no dedicated list API in CLI/MCP (D-19). |
| `execute_command` (MCP) | OPT-OUT | Documented as unavailable in Coolify API; not used. |
| MCP `update_application` — health timings only | OPT-OUT | Schema exposes name/description only; timings via REST PATCH instead. |
| `deploy-mcp.yml` POST webhook | OPT-OUT | Left as-is; API/Web use GET per D-06 (optional later align). |
| Custom docker network (`--network rmj3pan623pikht2yqq2efsd`) | INTEGRATE | PATCH `custom_docker_run_options` for Postgres/scraper reachability (05-03 Pitfall 2). |
| WebApp image `curl` for Coolify healthcheck | INTEGRATE | Added `apk add curl` in `webapp/Dockerfile` runner — alpine image lacked curl/wget for deploy health probe. |

## Notes

- **Health timings:** All three apps target D-14 (10s / 5s / 5 / 15s). MCP retuned in 05-04 via REST PATCH on `n5frtiupale5c2zjm9fyk1qc`.
- **MANUAL fallbacks:** If PATCH/CLI unavailable, Coolify UI → app → Health Checks (D-19).
- **Phase verification:** Final human checkpoint in 05-04-PLAN.md Task 3.
