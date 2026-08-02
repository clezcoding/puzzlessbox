# Phase 5: Coolify-Deployment, CI/CD & Härtung - Context

**Gathered:** 2026-08-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Ship production Coolify deploy for the remaining public apps: migrate API from Coolify `dockerfile` builds to GHCR `dockerimage`, add WebApp as Docker-Image app under `pbox.puzzlesstool.online`, mirror the existing MCP GitHub Actions → GHCR → Coolify-webhook pattern for API + WebApp, enable local Postgres backup schedule on `puzzlessbox-db`, and wire Coolify health checks so crashed containers are not routed. Requirements: OPS-01..04. MCP deploy/health slice already done in Phase 2 (D-20/D-22). Scraper stack (Firecrawl/Camoufox) out of scope. No GlitchTip (OPS-05) / S3 offsite (OPS-06) in this phase — later milestone.

</domain>

<decisions>
## Implementation Decisions

### App topology & subdomains
- **D-01:** WebApp FQDN = `pbox.puzzlesstool.online` (not `app.` / apex / `web.`). — **Reversibility:** costly — OAuth redirect URIs, cookies, CORS, Better Auth `baseURL`
- **D-02:** API cutover = create **new** Coolify `dockerimage` app → attach `api.puzzlesstool.online` → stop old `dockerfile` app. Do **not** attempt build_pack switch (not supported via Coolify UI / CLI `app update` / MCP `update_application`). — **Reversibility:** costly — new UUID, webhooks, env copy
- **D-03:** WebApp Coolify app only **after** `webapp/Dockerfile` + `deploy-web.yml` + first successful GHCR push (avoid empty-image first deploy). — **Reversibility:** reversible
- **D-04:** Scraper stack (Firecrawl / Camoufox) left as-is in Phase 5 — no harden, no compose rebuild. — **Reversibility:** reversible

### CI/CD workflow layout
- **D-05:** Separate workflows: `deploy-api.yml` + `deploy-web.yml` alongside existing `deploy-mcp.yml`; path-filters per service (not matrix/monolith). — **Reversibility:** reversible
- **D-06:** Coolify trigger = per-app Deploy Webhook + `Authorization: Bearer COOLIFY_TOKEN`. New API/Web workflows use **GET** (Coolify docs + community: aspire-coolify, audnexus). Keep MCP as-is (POST); optional later align. Fail CI on non-2xx (`curl -fsSL` / status check). Not Deploy-API-uuid-only, not registry-poll. — **Reversibility:** reversible
- **D-07:** Image tags = `latest` + `sha-<short>` via `docker/metadata-action` (same as MCP). Coolify pulls `:latest`; `sha-` for rollback. — **Reversibility:** reversible
- **D-08:** Pin GitHub Actions by full commit SHA + version comment (match `ci.yml` / `deploy-mcp.yml`).

### Backup policy
- **D-09:** Local Coolify backup on `puzzlessbox-db` (`pfqgb5pcvgi9oh64bpe3shtn`): cron `0 3 * * *` (03:00 UTC), retention **14** backups / **14** days, local only. Create via CLI: `coolify database backup create … --enabled --frequency "0 3 * * *" --retention-amount-locally 14 --retention-days-locally 14`. — **Reversibility:** reversible
- **D-10:** After schedule create, run one immediate `coolify database backup trigger` as baseline before API cutover.
- **D-11:** S3/offsite **not** in Phase 5; design must not block later `--save-s3` / `--s3-storage-uuid` (OPS-06 later milestone).

### Health-check strategy
- **D-12:** Coolify routing probe = **`/health`** (liveness). `/ready` stays for diagnostics/monitoring — do **not** gate Traefik on `/ready` (Scraper/DB flakiness must not black-hole API). — **Reversibility:** reversible
- **D-13:** WebApp ships dedicated unauthenticated health route (`/api/health` or `/health`) returning 200 — not `/login`, not Docker-only. — **Reversibility:** reversible
- **D-14:** Coolify health timings (API + MCP optional align + Web): interval **10s**, timeout **5s**, retries **5**, start period **15s** (WebApp cold start). — **Reversibility:** reversible

### Secrets & cutover order
- **D-15:** Cutover order: backup trigger → API new dockerimage app + domain swap → WebApp app + webhook → verify. Sequential, not parallel / not Web-first. — **Reversibility:** reversible
- **D-16:** GitHub Secrets: shared `COOLIFY_TOKEN` + `COOLIFY_API_WEBHOOK` + `COOLIFY_WEB_WEBHOOK` (keep existing `COOLIFY_MCP_WEBHOOK`). — **Reversibility:** reversible
- **D-17:** GHCR packages **public** (repo is public) — Coolify pulls without registry auth. No private-package login required for v1. — **Reversibility:** costly if later flipped to private (Coolify GHCR creds + package visibility)
- **D-18:** API domain swap = **immediate** put `api.puzzlesstool.online` on new app, stop old — no temp `api-next.` window. — **Reversibility:** reversible (re-point domain)

### Manual steps (executor must NOT invent scripts)
- **D-19:** Steps that require human / GitHub UI / Coolify UI when CLI+MCP cannot: (1) set GitHub Actions secrets (`gh secret set` or UI), (2) copy Deploy Webhook URLs from Coolify app into those secrets if API does not expose them, (3) any Coolify UI-only knobs not covered by `coolify app update` / MCP. Prefer Coolify CLI (`--context hostunlimited`) + Coolify MCP for app create, env, backup, health path, deploy trigger. **Never** invent quick-and-dirty scripts as substitute — flag the manual step to the user.

### Claude's Discretion
- Exact WebApp health path string (`/api/health` vs `/health`) within D-13
- GHCR image names (`puzzlessbox-api`, `puzzlessbox-web`) mirroring `puzzlessbox-mcp`
- Whether to retune existing MCP health intervals to D-14 or leave MCP at current 5s
- Env var migration checklist when copying API from old → new Coolify app
- Whether webhook step also asserts HTTP 200/202 explicitly (audnexus-style) beyond `curl -f`

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — OPS-01..04 (in scope); OPS-05/06 v2 deferred
- `.planning/ROADMAP.md` — Phase 5 goal + success criteria
- `.planning/PROJECT.md` — Coolify Docker-Image + GH Actions → GHCR → webhook; local backups; domains under `puzzlesstool.online`

### Prior phase deploy contracts
- `.planning/phases/02-mcp-server/02-CONTEXT.md` — D-20/D-22/D-23 MCP deploy + health
- `.planning/phases/02-mcp-server/02-DEPLOY-SPEC.md` — pinned Actions SHAs, secrets checklist, Coolify user_setup
- `.github/workflows/deploy-mcp.yml` — canonical workflow template (path-filter, metadata tags, Coolify trigger)
- `.github/workflows/ci.yml` — Action SHA-pinning convention

### Live Coolify inventory (hostunlimited)
- Project `Puzzlessbox` uuid `nlm9h0u5lh2rnf2fg10vuf16`
- `puzzlessbox-api` uuid `dxoflgio67786lc4yilhce43` — currently `dockerfile` @ `api.puzzlesstool.online` (to be replaced per D-02)
- `puzzlessbox-mcp` uuid `n5frtiupale5c2zjm9fyk1qc` — `dockerimage` `ghcr.io/clezcoding/puzzlessbox-mcp` @ `mcp.puzzlesstool.online`
- `puzzlessbox-db` uuid `pfqgb5pcvgi9oh64bpe3shtn` — Postgres 18; no backup schedule yet
- Server uuid `ozwpdpj5bgxax8v6gfs5lolv` (localhost / Coolify host)

### External references (workflow patterns researched)
- https://coolify.io/docs/applications/ci-cd/other-providers — Deploy Webhook + `Authorization: Bearer`
- https://github.com/laxamentumtech/audnexus/blob/main/.github/workflows/deploy-coolify.yml — GHCR build-push + webhook status check
- https://github.com/funsjanssen/aspire-coolify/blob/main/.github/workflows/coolify-deploy.yml — multi-image GHCR + webhook + token
- https://github.com/reloop-labs/reloop/blob/main/.github/workflows/be-webhook.yml — path-filter + Deploy API alternative (not chosen)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.github/workflows/deploy-mcp.yml` — copy pattern for `deploy-api.yml` / `deploy-web.yml` (swap context, image name, webhook secret, paths)
- `api/Dockerfile` — exists; wire into GHCR build context `./api`
- `mcp-server/Dockerfile` + health routes — reference for WebApp health + Coolify probe
- `api/app/routers/health.py` — `/health` + `/ready` already split (supports D-12)
- Coolify CLI v1.6.2 context `hostunlimited` → `https://puzzlesstool.online`
- Coolify MCP: `create_dockerimage_application`, `create_database_backup`, `create_application_env`, deploy/start/stop

### Established Patterns
- Docker-Image apps on this host (clared-*, puzzlessbox-mcp) already prove GHCR → Coolify path
- Action pinning by full SHA
- MCP webhook uses Bearer token (add GET for new workflows per D-06)

### Integration Points
- New API Coolify app must share Docker network with Postgres + scraper services (existing API uses custom network — copy from current app)
- WebApp needs Coolify env: Better Auth URL, API base URL, Google OAuth redirect host `pbox.puzzlesstool.online`
- GitHub Packages under `ghcr.io/clezcoding/…`

### Gaps
- No `webapp/Dockerfile` yet — must be created in this phase
- API Coolify app still `build_pack: dockerfile` — replace per D-02
- `puzzlessbox-db` backup list empty — D-09/D-10

</code_context>

<specifics>
## Specific Ideas

- User chose hostname **`pbox.puzzlesstool.online`** explicitly (not recommended `app.`).
- User confirmed build_pack cannot be switched in UI → new-app cutover mandatory.
- Repo is **public** → public GHCR packages (D-17); private-registry path not needed now.
- User wants **S3 offsite later** (milestone / OPS-06); Phase 5 local-only but attachable.
- Prefer Coolify CLI + Coolify MCP; flag manual gaps instead of ad-hoc scripts (D-19).

</specifics>

<deferred>
## Deferred Ideas

- Scraper-Stack harden (Firecrawl/Camoufox health, image pins, network audit) — post-prod phase or quick task
- Optional align `deploy-mcp.yml` POST → GET for consistency with D-06
- OPS-05 GlitchTip / application error tracking — v2
- OPS-06 S3 offsite backups — later milestone (user confirmed intent); Coolify supports `--save-s3` when ready

</deferred>

---

*Phase: 5-Coolify-Deployment, CI/CD & Härtung*
*Context gathered: 2026-08-02*
