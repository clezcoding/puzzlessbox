# Phase 2: MCP-Server - Context

**Gathered:** 2026-07-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a remote FastMCP 3.4.4 server as its own Coolify Docker-Image app under `mcp.puzzlesstool.online` (HTTPS), exposing MCP-01 tools with validated schemas. Hermes authenticates with a rotatable Bearer; MCP calls the Phase-1 FastAPI as an internal HTTP client (service bearer + `X-Owner-Id`). Phase 2 also ships MCP GHCR/GitHub Actions deploy, categories/move API endpoints needed by tools, and `mcp_clients` auth plumbing. No Hermes plugin / confirmation chat UX (Phase 3). No WebApp UI (Phase 4).

</domain>

<decisions>
## Implementation Decisions

### Auth & tenancy (Hermes → MCP → API)
- **D-01:** Two secrets — Hermes Bearer validated only at MCP; MCP→API uses existing `SERVICE_BEARER_TOKEN` via `X-Service-Bearer` (Phase-1 D-23). — **Reversibility:** costly — two Coolify secrets + Hermes header config
- **D-02:** Owner resolution via Postgres `mcp_clients` mapping (bearer_hash → owner_id), SaaS-ready; not a single hard-coded env-only owner. — **Reversibility:** costly — new table + auth path
- **D-03:** After lookup, MCP sends `X-Owner-Id` to API; service bearer remains gateway auth. API trusts `X-Owner-Id` only when service bearer is valid. — **Reversibility:** costly — new header contract on all MCP→API calls
- **D-04:** Token rotation = dual-token grace per `mcp_clients` row (`active|grace` + expiry timestamp), not env PRIMARY/PREVIOUS. — **Reversibility:** costly — schema + rotation ops
- **D-05:** Hermes Bearer validated in FastMCP/app (401/403 testable); Traefik provides TLS only (no IP allowlist — already locked out of v1).
- **D-06:** MCP does **not** open `mcp_clients` itself — API owns table; MCP calls internal `POST /internal/mcp-auth` (service bearer) → `{owner_id}` (and reject if invalid/expired). — **Reversibility:** costly — internal auth endpoint contract
- **D-07:** Solo bootstrap: when `MCP_BOOTSTRAP_TOKEN` + `SERVICE_OWNER_ID` set and `mcp_clients` empty, Alembic/bootstrap inserts hash-only row; never log plaintext; env may be cleared after. — **Reversibility:** reversible
- **D-08:** API `X-Owner-Id` guard: UUID format **and** Better Auth `user` row must exist; else 403. — **Reversibility:** costly — couples MCP path to auth user table

### Tool semantics & API surface
- **D-09:** `create_item` always maps to `POST /drafts` (starts 30s timer per D-05 Phase 1); `type` required `note|link|task|event`. — **Reversibility:** costly — Hermes/Capture contract
- **D-10:** `confirm_item` = optional field patch then `POST /drafts/{id}/confirm`.
- **D-11:** Phase 2 ships API endpoints for tools: `GET/POST /categories`, item category move (`PATCH` category_id / dedicated move). — **Reversibility:** costly — board API surface early vs Phase 4
- **D-12:** `update_item`: title, summary, category (+ type-specific fields where API already supports); editable when status `draft|auto_saved`; `confirmed` → category move only.
- **D-13:** Tool errors to Hermes: short MCP text + `code`; richer payload in `details` (not raw API dump, not opaque "failed").
- **D-14:** Tool descriptions / schemas in **English**; German user-facing confirm copy stays Phase 3.

### MCP ↔ API client contract
- **D-15:** MCP→API base URL = internal Docker network (e.g. `http://puzzlessbox-api:8000`). Hermes→MCP remains public `https://mcp.puzzlesstool.online`. — **Reversibility:** reversible (env)
- **D-16:** MCP always sends: `Accept: application/vnd.puzzlessbox.v1+json`, `X-Service-Bearer`, `X-Owner-Id`; on `create_item` also `Idempotency-Key`.
- **D-17:** HTTP timeout MCP→API = **15s** (covers ~12s link-scrape budget D-13 Phase 1).
- **D-18:** Retries: **1×** on 502/503 only (not blanket write retries).
- **D-19:** `Idempotency-Key`: Hermes provides when possible; if missing MCP generates a UUID once and forwards.

### Deploy & packaging
- **D-20:** Phase 2 includes full MCP deploy path: `mcp-server/` + Dockerfile + Coolify docker-image app + `mcp.puzzlesstool.online` + GitHub Actions → GHCR (`:latest` + `:sha-<sha>`) → Coolify webhook. Pulls MCP slice of OPS-01/02/04 into Phase 2. — **Reversibility:** costly — CI/CD owned early; Phase 5 focuses remaining apps/backups
- **D-21:** Transport: Streamable HTTP (exact FastMCP path left to research/planner; not SSE legacy, not stdio).
- **D-22:** MCP `/health` + `/ready` (ready may ping API) **and** Coolify health-check wiring in Phase 2.
- **D-23:** Repo layout: top-level `mcp-server/` with its own image (not FastMCP mounted inside `api/`). — **Reversibility:** one-way for deploy topology — matches MCP-02 separate Coolify app

### Claude's Discretion
- Exact FastMCP Streamable HTTP mount path / version pin within 3.4.x
- `mcp_clients` column names and grace default TTL
- Internal route path naming (`/internal/mcp-auth` vs equivalent)
- Categories create fields (color/sort) beyond name if API needs them for BOARD later
- GHCR image name / workflow file layout (mirror API patterns)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — MCP-01, MCP-02 (phase scope); MCP-05/06 out of v1
- `.planning/ROADMAP.md` — Phase 2 goal + success criteria
- `.planning/PROJECT.md` — FastMCP 3.4.4, Bearer auth, domains `mcp.` / `api.`, monorepo layout
- `PUZZLESSBOX_PROJECT_BRIEF.md` — Hermes remote MCP, tool list, Coolify docker-image deploy

### Prior phase (contracts to reuse)
- `.planning/phases/01-datenmodell-backend-api/01-CONTEXT.md` — D-05..D-08 drafts/timer, D-23 service bearer, D-27 Accept versioning, D-33 errors, D-34 Idempotency-Key
- `api/app/auth/jwt.py` — `X-Service-Bearer` + `get_current_owner`
- `api/app/core/bootstrap.py` — `service_principals` bootstrap pattern
- `api/app/routers/capture.py` — `POST/PATCH /drafts`, `POST …/confirm`

### Research
- `.planning/research/STACK.md` — FastMCP 3.4.4 (not 4.0-alpha)
- `.planning/research/ARCHITECTURE.md` — separate `mcp-server/` Coolify app, Bearer over HTTPS
- `.planning/research/SUMMARY.md` — MCP pitfalls (token exposure)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `SERVICE_BEARER_TOKEN` / `SERVICE_OWNER_ID` + `service_principals` + `X-Service-Bearer` already implemented for MCP→API (extend with `X-Owner-Id` + `mcp_clients`).
- Capture draft CRUD + confirm + Idempotency-Key + Accept middleware ready for MCP client.
- API Dockerfile / Coolify patterns exist under `api/` — mirror for `mcp-server/`.

### Established Patterns
- Unified error shape `{error:{code,message,details?}}` (D-33) — MCP maps to tool text+code.
- Header versioning required on every API call (D-27).
- Monorepo: `api/` done; `mcp-server/` greenfield; `webapp/` / `hermes-plugin/` later.

### Integration Points
- Hermes (external VPS) → public MCP HTTPS + Bearer.
- MCP → internal API URL + service bearer + owner header.
- Coolify Traefik TLS for `mcp.`; health checks configured Phase 2.
- Categories/move endpoints new on API, consumed only by MCP tools in this phase (WebApp later).

</code_context>

<specifics>
## Specific Ideas

- User initially assumed public API URL for MCP→API; clarified two-hop model → locked internal Docker URL for hop 2.
- User preferred SaaS-ready mapping (`mcp_clients` + DB grace) over solo-only env tokens.
- User chose to pull full MCP GHCR/Actions into Phase 2 (not wait for Phase 5).
- Flipped MCP DB access: first lean to direct DB, then locked API-owned `/internal/mcp-auth` (1b).

</specifics>

<deferred>
## Deferred Ideas

- Hermes plugin, confirm chat UX, channel orchestration — Phase 3 (MCP-03, CAP-02, CAP-04)
- Hermes Cron/dispatch_tool spike — Phase 3 (MCP-04)
- WebApp board UI consuming categories — Phase 4 (BOARD-*)
- Phase 5 OPS for API/WebApp/backups — MCP GHCR/health slice already in Phase 2 (D-20/D-22)
- MCP OAuth 2.1 / IP allowlist — v2 (MCP-05, MCP-06)

</deferred>

---

*Phase: 2-MCP-Server*
*Context gathered: 2026-07-31*
