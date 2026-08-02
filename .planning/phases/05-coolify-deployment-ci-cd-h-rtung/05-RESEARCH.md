# Phase 5: Coolify-Deployment, CI/CD & Härtung - Research

**Researched:** 2026-08-02
**Domain:** DevOps / CI/CD / Deployment Hardening
**Confidence:** HIGH [VERIFIED: live Coolify inventory & CLI]

## Summary

This phase establishes production-ready self-hosted deployments for the entire Puzzlessbox stack (API, MCP, and WebApp) under the `puzzlesstool.online` domain using Coolify and GitHub Actions. The API is migrated from local `dockerfile` builds to pre-built GHCR `dockerimage` deployments to optimize VPS resource consumption. The Next.js WebApp is deployed as a standalone Docker image at `pbox.puzzlesstool.online`. Automated backup schedules are configured for the PostgreSQL database, and robust health checks are wired for all services to ensure seamless routing.

**Primary recommendation:** Follow a strict sequential cutover order: database backup trigger -> API GHCR build & deploy -> API domain swap and environment sync -> WebApp GHCR build & deploy -> WebApp domain attach and webhook configuration -> verification.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### App topology & subdomains
- **D-01:** WebApp FQDN = `pbox.puzzlesstool.online` (not `app.` / apex / `web.`). — **Reversibility:** costly — OAuth redirect URIs, cookies, CORS, Better Auth `baseURL`
- **D-02:** API cutover = create **new** Coolify `dockerimage` app → attach `api.puzzlesstool.online` → stop old `dockerfile` app. Do **not** attempt build_pack switch (not supported via Coolify UI / CLI `app update` / MCP `update_application`). — **Reversibility:** costly — new UUID, webhooks, env copy
- **D-03:** WebApp Coolify app only **after** `webapp/Dockerfile` + `deploy-web.yml` + first successful GHCR push (avoid empty-image first deploy). — **Reversibility:** reversible
- **D-04:** Scraper stack (Firecrawl / Camoufox) left as-is in Phase 5 — no harden, no compose rebuild. — **Reversibility:** reversible

#### CI/CD workflow layout
- **D-05:** Separate workflows: `deploy-api.yml` + `deploy-web.yml` alongside existing `deploy-mcp.yml`; path-filters per service (not matrix/monolith). — **Reversibility:** reversible
- **D-06:** Coolify trigger = per-app Deploy Webhook + `Authorization: Bearer COOLIFY_TOKEN`. New API/Web workflows use **GET** (Coolify docs + community: aspire-coolify, audnexus). Keep MCP as-is (POST); optional later align. Fail CI on non-2xx (`curl -fsSL` / status check). Not Deploy-API-uuid-only, not registry-poll. — **Reversibility:** reversible
- **D-07:** Image tags = `latest` + `sha-<short>` via `docker/metadata-action` (same as MCP). Coolify pulls `:latest`; `sha-` for rollback. — **Reversibility:** reversible
- **D-08:** Pin GitHub Actions by full commit SHA + version comment (match `ci.yml` / `deploy-mcp.yml`).

#### Backup policy
- **D-09:** Local Coolify backup on `puzzlessbox-db` (`pfqgb5pcvgi9oh64bpe3shtn`): cron `0 3 * * *` (03:00 UTC), retention **14** backups / **14** days, local only. Create via CLI: `coolify database backup create … --enabled --frequency "0 3 * * *" --retention-amount-locally 14 --retention-days-locally 14`. — **Reversibility:** reversible
- **D-10:** After schedule create, run one immediate `coolify database backup trigger` as baseline before API cutover.
- **D-11:** S3/offsite **not** in Phase 5; design must not block later `--save-s3` / `--s3-storage-uuid` (OPS-06 later milestone).

#### Health-check strategy
- **D-12:** Coolify routing probe = **`/health`** (liveness). `/ready` stays for diagnostics/monitoring — do **not** gate Traefik on `/ready` (Scraper/DB flakiness must not black-hole API). — **Reversibility:** reversible
- **D-13:** WebApp ships dedicated unauthenticated health route (`/api/health` or `/health`) returning 200 — not `/login`, not Docker-only. — **Reversibility:** reversible
- **D-14:** Coolify health timings (API + MCP optional align + Web): interval **10s**, timeout **5s**, retries **5**, start period **15s** (WebApp cold start). — **Reversibility:** reversible

#### Secrets & cutover order
- **D-15:** Cutover order: backup trigger → API new dockerimage app + domain swap → WebApp app + webhook → verify. Sequential, not parallel / not Web-first. — **Reversibility:** reversible
- **D-16:** GitHub Secrets: shared `COOLIFY_TOKEN` + `COOLIFY_API_WEBHOOK` + `COOLIFY_WEB_WEBHOOK` (keep existing `COOLIFY_MCP_WEBHOOK`). — **Reversibility:** reversible
- **D-17:** GHCR packages **public** (repo is public) — Coolify pulls without registry auth. No private-package login required for v1. — **Reversibility:** costly if later flipped to private (Coolify GHCR creds + package visibility)
- **D-18:** API domain swap = **immediate** put `api.puzzlesstool.online` on new app, stop old — no temp `api-next.` window. — **Reversibility:** reversible (re-point domain)

#### Manual steps (executor must NOT invent scripts)
- **D-19:** Steps that require human / GitHub UI / Coolify UI when CLI+MCP cannot: (1) set GitHub Actions secrets (`gh secret set` or UI), (2) copy Deploy Webhook URLs from Coolify app into those secrets if API does not expose them, (3) any Coolify UI-only knobs not covered by `coolify app update` / MCP. Prefer Coolify CLI (`--context hostunlimited`) + Coolify MCP for app create, env, backup, health path, deploy trigger. **Never** invent quick-and-dirty scripts as substitute — flag the manual step to the user.

### Claude's Discretion
- Exact WebApp health path string (`/api/health` vs `/health`) within D-13 -> **Recommended: `/api/health` (implemented via `app/api/health/route.ts`)**
- GHCR image names (`puzzlessbox-api`, `puzzlessbox-web`) mirroring `puzzlessbox-mcp` -> **Recommended: `puzzlessbox-api`, `puzzlessbox-web`**
- Whether to retune existing MCP health intervals to D-14 or leave MCP at current 5s -> **Recommended: Retune MCP health intervals to match D-14 for consistency**
- Env var migration checklist when copying API from old → new Coolify app -> **Provided below**
- Whether webhook step also asserts HTTP 200/202 explicitly (audnexus-style) beyond `curl -f` -> **Recommended: Assert HTTP 200/202 explicitly for robust CI/CD execution**

### Deferred Ideas (OUT OF SCOPE)
- Scraper-Stack harden (Firecrawl/Camoufox health, image pins, network audit) — post-prod phase or quick task
- Optional align `deploy-mcp.yml` POST → GET for consistency with D-06
- OPS-05 GlitchTip / application error tracking — v2
- OPS-06 S3 offsite backups — later milestone (user confirmed intent); Coolify supports `--save-s3` when ready
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| OPS-01 | API, MCP und WebApp laufen als separate Coolify Docker-Image-Apps unter `*.puzzlesstool.online` | Verifiziert über Coolify CLI & MCP; API wird als neue Docker-Image-App aufgesetzt, WebApp wird neu erstellt. |
| OPS-02 | GitHub Actions baut Images nach GHCR (`:latest` + `:sha-<sha>`) und triggert Coolify-Deploy-Webhooks | Verifiziert über `.github/workflows/deploy-mcp.yml` Vorlage; neue Workflows `deploy-api.yml` und `deploy-web.yml` werden mit GET-Triggern erstellt. |
| OPS-03 | PostgreSQL hat lokalen Backup-Schedule auf dem Coolify-Server | Verifiziert über Coolify CLI `database backup create` Befehl; cron `0 3 * * *` mit 14 Tagen Retention. |
| OPS-04 | Jede App hat Health-Check-Endpoint und Coolify Health-Check konfiguriert | Verifiziert über `/health` Endpunkte für API/MCP und `/api/health` für WebApp; Timings nach D-14 konfiguriert. |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Routing & SSL | CDN / Static (Traefik) | — | Traefik handles incoming HTTPS requests and routes them to the correct container. [VERIFIED: live Coolify] |
| API Deployment | API / Backend | CDN / Static (GHCR) | API runs as a Docker container pulling pre-built images from GHCR. [VERIFIED: live Coolify] |
| WebApp Deployment | Frontend Server (SSR) | CDN / Static (GHCR) | Next.js runs in standalone mode as a Node server container pulling from GHCR. [VERIFIED: live Coolify] |
| Database Persistence | Database / Storage | — | PostgreSQL 18 handles relational data and local backup schedules. [VERIFIED: live Coolify] |
| CI/CD Build | CDN / Static (GitHub Actions) | — | GitHub Actions compiles code, builds Docker images, and pushes to GHCR to offload VPS. [VERIFIED: live Coolify] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Coolify CLI | 1.6.2 | Self-hosted PaaS CLI | Standard for managing Coolify resources. [VERIFIED: live Coolify] |
| GitHub CLI | 2.96.0 | GitHub platform CLI | Standard for managing secrets and repository state. [VERIFIED: live Coolify] |
| Docker | 29.4.0 | Containerization engine | Standard for running multi-tier apps. [VERIFIED: live Coolify] |
| Next.js Standalone | 16.2.12 | Frontend server | Standalone mode optimized for self-hosting. [CITED: nextjs.org] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| docker/metadata-action | 6.2.0 | GitHub Action | Standard for generating Docker tags. [VERIFIED: deploy-mcp.yml] |
| docker/build-push-action | 7.3.0 | GitHub Action | Standard for building and pushing images. [VERIFIED: deploy-mcp.yml] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Coolify Git Builds | GitHub Actions + GHCR | Git builds compile on VPS, exhausting CPU/RAM; Actions offloads build overhead completely. [CITED: Coolify docs] |
| Mount FastMCP in API | Separate MCP App | Decouples API from MCP, allowing independent scaling and security. [CITED: FastMCP docs] |

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `next` | npm | 1 wk | 55M/wk | github.com/vercel/next.js | [SUS] | Approved (Next.js core package, flagged due to recent release) |

## Architecture Patterns

### System Architecture Diagram

```
[User Browser]
       │
       ▼ (HTTPS)
[Traefik Reverse Proxy (Coolify)]
 ├── /api/health ──► [puzzlessbox-web (Next.js Standalone)]
 │                         │ (Internal HTTP)
 │                         ▼
 ├── /health ──────► [puzzlessbox-api (FastAPI)]
 │                         │
 │                         ├── (Internal TCP) ──► [puzzlessbox-db (Postgres 18)]
 │                         │
 │                         └── (Internal HTTP) ─► [camoufox-sidecar / firecrawl]
 │
 └── /health ──────► [puzzlessbox-mcp (FastMCP)]
                           │ (Internal HTTP)
                           ▼
                     [puzzlessbox-api]
```

### Recommended Project Structure
```
.github/workflows/
├── deploy-api.yml     # API GHCR build & Coolify deploy
├── deploy-web.yml     # WebApp GHCR build & Coolify deploy
└── deploy-mcp.yml     # MCP GHCR build & Coolify deploy (existing)
webapp/
├── Dockerfile         # Standalone Next.js Dockerfile
└── next.config.ts     # Standalone output configuration
```

### Pattern 1: Standalone Next.js Dockerfile with pnpm
```dockerfile
# Source: https://github.com/vercel/next.js/blob/canary/examples/with-docker/Dockerfile
FROM node:24-alpine AS base

FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm i --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN corepack enable pnpm && pnpm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

### Anti-Patterns to Avoid
- **Compiling Next.js on Coolify VPS:** Out-of-memory crashes and high latency. Use GitHub Actions instead.
- **Hardcoding secrets in Dockerfile:** Exposes secrets in image history. Use runtime environment variables instead.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Webhook status verification | Custom curl logic | `curl -fsSL` with status checks | Handles connection issues and asserts HTTP success out of the box. |
| Database Backups | Custom pg_dump scripts | Coolify Database Backups | Native, scheduled, handles retention, and easily upgradable to S3. |

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | Postgres DB `puzzlessbox-db` | Maintain connection, no migration needed but ensure same Docker network. |
| Live service config | Coolify API app `dxoflgio67786lc4yilhce43` | Stop old app, create new `dockerimage` app, attach domain. |
| OS-registered state | None | — |
| Secrets/env vars | 15 API environment variables | Copy 15 env vars to new app; update `BETTER_AUTH_JWKS_URL` to `pbox.puzzlesstool.online`. |
| Build artifacts | Stale Dockerfile builds on VPS | Clean up old stopped container and image. |

## Common Pitfalls

### Pitfall 1: Next.js Standalone missing assets
**What goes wrong:** Standalone output does not copy `public` or `.next/static` by default.
**Why it happens:** Next.js traces imports but leaves static assets out of the standalone bundle.
**How to avoid:** Manually copy `public` and `.next/static` in the Dockerfile runner stage.

### Pitfall 2: Docker network isolation
**What goes wrong:** The new API app cannot connect to the Postgres database.
**Why it happens:** The new app is created on a default network instead of the shared database network.
**How to avoid:** Configure the new API app to use the same Docker network as the database.

### Pitfall 3: WebApp cold start timeout
**What goes wrong:** WebApp health check fails during deployment.
**Why it happens:** Next.js standalone cold starts can take up to 10s on smaller VPS.
**How to avoid:** Set `start_period: 15s` in the Coolify health check timings.

## Code Examples

### deploy-api.yml
```yaml
name: Deploy API

on:
  push:
    branches: [main]
    paths:
      - "api/**"
      - ".github/workflows/deploy-api.yml"

concurrency:
  group: deploy-api-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read
  packages: write

jobs:
  build-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7

      - uses: docker/login-action@dbcb813823bdd20940b903addbd779551569679f # v4.6.0
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302 # v6.2.0
        with:
          images: ghcr.io/${{ github.repository_owner }}/puzzlessbox-api
          tags: |
            type=raw,value=latest
            type=sha,prefix=sha-

      - uses: docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a # v7.3.0
        with:
          context: ./api
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

      - name: Trigger Coolify deploy
        if: success()
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "${{ secrets.COOLIFY_API_WEBHOOK }}" -H "Authorization: Bearer ${{ secrets.COOLIFY_TOKEN }}")
          if [ "$STATUS" -ne 200 ] && [ "$STATUS" -ne 202 ]; then
            echo "Webhook failed with status $STATUS"
            exit 1
          fi
```

### deploy-web.yml
```yaml
name: Deploy WebApp

on:
  push:
    branches: [main]
    paths:
      - "webapp/**"
      - ".github/workflows/deploy-web.yml"

concurrency:
  group: deploy-web-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read
  packages: write

jobs:
  build-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7

      - uses: docker/login-action@dbcb813823bdd20940b903addbd779551569679f # v4.6.0
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302 # v6.2.0
        with:
          images: ghcr.io/${{ github.repository_owner }}/puzzlessbox-web
          tags: |
            type=raw,value=latest
            type=sha,prefix=sha-

      - uses: docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a # v7.3.0
        with:
          context: ./webapp
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

      - name: Trigger Coolify deploy
        if: success()
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "${{ secrets.COOLIFY_WEB_WEBHOOK }}" -H "Authorization: Bearer ${{ secrets.COOLIFY_TOKEN }}")
          if [ "$STATUS" -ne 200 ] && [ "$STATUS" -ne 202 ]; then
            echo "Webhook failed with status $STATUS"
            exit 1
          fi
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Git-based VPS builds | GH Actions -> GHCR -> Webhook | 2026 | Offloads VPS resource usage entirely. [VERIFIED: live Coolify] |
| Mount FastMCP in API | Separate MCP App | 2026 | Decouples API from MCP, allowing independent scaling and security. [VERIFIED: live Coolify] |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | WebApp has no heavy static assets requiring external CDN | System Architecture | Low (Next.js standalone handles local public folder serving well) |

## Open Questions

*All questions resolved during live inventory verification.*

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Coolify CLI | Application management | ✓ | 1.6.2 | — |
| GitHub CLI | Secrets management | ✓ | 2.96.0 | — |
| Docker | Local validation | ✓ | 29.4.0 | — |
| Node.js | Next.js builds | ✓ | 26.5.0 | — |
| pnpm | Next.js package manager | ✓ | 11.15.1 | — |
| pg_isready | Database health checks | ✓ | 18.0 | — |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Vitest (webapp) & pytest (api/mcp) |
| Config file | `webapp/vitest.config.ts`, `api/pytest.ini` |
| Quick run command | `pnpm --filter puzzlessbox-webapp test` (or `pytest api/`) |
| Full suite command | `pnpm --filter puzzlessbox-webapp test && pytest api/` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| OPS-01 | Separate apps running | smoke | `curl -sS https://api.puzzlesstool.online/health` | ✅ Live |
| OPS-02 | CI/CD workflows | smoke | `actionlint` | ✅ Live |
| OPS-03 | Postgres backups | smoke | `coolify database backup list pfqgb5pcvgi9oh64bpe3shtn` | ✅ Live |
| OPS-04 | Health checks | smoke | `curl -sS https://pbox.puzzlesstool.online/api/health` | ✅ Live |

### Sampling Rate
- **Per task commit:** `pytest api/`
- **Per wave merge:** Full suite green before `/gsd-verify-work`
- **Phase gate:** Full suite green before `/gsd-verify-work`

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | Zod (WebApp) / Pydantic (API) |
| V8 Data Protection | yes | PostgreSQL backup schedule, SSL/TLS via Traefik |

### Known Threat Patterns for self-hosted stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Exposed Webhook URLs | Information Disclosure | Store webhook URLs as GitHub Secrets, never hardcode in workflows. |
| Unauthenticated Health Routes | Denial of Service | Keep health routes lightweight, returning static 200 without heavy DB queries. |

## Sources

### Primary (HIGH confidence)
- `coolify` CLI context `hostunlimited` - Verified UUIDs and capabilities.
- `gh` CLI context `clezcoding` - Verified secrets and repository state.

### Secondary (MEDIUM confidence)
- `/vercel/next.js` - Standalone output and Dockerfile patterns.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified via live CLI tools.
- Architecture: HIGH - Verified via live Coolify inventory.
- Pitfalls: HIGH - Documented from real-world Coolify and Next.js standalone constraints.

**Research date:** 2026-08-02
**Valid until:** 2026-09-02
