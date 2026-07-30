# Phase 1: Datenmodell & Backend-API - Context

**Gathered:** 2026-07-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver Postgres schema with tenancy (`owner_id`), FastAPI CRUD, Better Auth bridge (JWKS), Capture draft/timeout state machine, Link metadata scrape (Firecrawl + Camoufox), and Google Calendar sync (OAuth + If-Match) — end-to-end over the API. No MCP server, no Hermes plugin, no WebApp UI screens (Auth lives in Next.js for JWKS; minimal auth wiring only as needed for API verification). Scraper Coolify services ship with Phase 1 Link endpoint.

</domain>

<decisions>
## Implementation Decisions

### Item data model
- **D-01:** Separate tables `notes` / `links` / `tasks` / `events` plus shared Postgres VIEW `board_items` (UNION ALL) for board/list reads. — **Reversibility:** costly — VIEW + typed tables shape all CRUD/MCP later
- **D-02:** Status lifecycle `draft` → `auto_saved` → `confirmed` (Claude discretion). — **Reversibility:** costly — status enum used by timeout machine + Hermes later
- **D-03:** Soft-delete via `deleted_at` on core rows.
- **D-04:** Categories via FK `category_id` → `categories`; seed defaults Inbox · Notizen · Links · Tasks · Termine.

### Capture timeout API
- **D-05:** API starts 30s timer on `POST /drafts` (asyncio/BackgroundTask); Hermes/MCP only create. — **Reversibility:** costly — contradicts Hermes-Cron approach (locked by PITFALLS)
- **D-06:** Every edit (`PATCH`) resets timer to now+30s (inactivity semantics).
- **D-07:** `POST …/confirm` → immediate `confirmed`, cancel timer.
- **D-08:** After timeout item is queryable as `auto_saved` (board-visible); no Hermes push webhook in Phase 1.

### Link scraper
- **D-09:** Scrape sync inside link create POST.
- **D-10:** Required metadata: `title` + `url`; `description` + `image` optional in JSONB.
- **D-11:** On scrape failure: still persist with hostname/URL fallback title; `scrape_status=failed`; category always **Links**.
- **D-12:** Scraper stack (CF + €0): **Firecrawl self-host** (Coolify, primary) → **Camoufox sidecar** fallback → hostname fallback. No Firecrawl core patch; no paid proxies. Note: self-host Firecrawl lacks Fire-engine; CF is best-effort. — **Reversibility:** costly — Coolify services + API client coupling
- **D-13:** Hard budget **12s** total (Firecrawl ≤8s, then Camoufox ≤4s remainder).
- **D-14:** Shared Bearer/Secret; Firecrawl + Camoufox **internal only** (not public).
- **D-15:** Deploy scraper services in **Phase 1** with API (compose/health when Link endpoint lands).
- **D-16:** Camoufox = light Docker sidecar `GET url → HTML`; API parses OG (Claude discretion).

### Google Calendar sync
- **D-17:** OAuth tokens encrypted at rest in Postgres; encryption key from Coolify secret. — **Reversibility:** costly — key/rotation story
- **D-18:** User selects `calendar_id` in Settings after Connect (list calendars).
- **D-19:** Push API→Google on create/update; pull on-demand before write for ETag; no full bidirectional mirror cron in Phase 1.
- **D-20:** On `412 Precondition Failed`: return structured conflict (ETag + remote state); never silent overwrite (CAL-03).

### Auth bridge
- **D-21:** Better Auth lives in **Next.js** (`app.`); FastAPI verifies via **JWKS/JWT**. — **Reversibility:** costly — cross-service auth contract
- **D-22:** Same-site cookie on parent domain `puzzlesstool.online`; FastAPI accepts JWT from cookie/`Authorization`.
- **D-23:** Prepare internal **service bearer** + `owner_id` mapping in Phase 1 for MCP→API (Phase 2).
- **D-24:** Signup lock via Better Auth `databaseHooks` when user count > 0 (AUTH-03).

### Infra / API shape
- **D-25:** Tenant isolation: **Postgres RLS + app-level `owner_id` filters** (defense-in-depth) + cross-tenant integration tests. — **Reversibility:** costly — RLS policies + role setup
- **D-26:** Migrations: **Alembic** with SQLModel (Claude discretion).
- **D-27:** API versioning via header `Accept: application/vnd.puzzlessbox.v1+json` (not `/v1` path). — **Reversibility:** costly — all clients must send header
- **D-28:** Timestamps stored in **Europe/Berlin** (not UTC); Settings `timezone` for display/parsing hints (default Berlin). — **Reversibility:** costly — multi-TZ/SaaS later needs migration
- **D-29:** Google OAuth callback on **`api.`**; Settings Connect on `app.` returns there after (Claude discretion).
- **D-30:** Capture `type` required from caller: `note|link|task|event`.
- **D-31:** `/health` = liveness; `/ready` = DB + optional scraper ping (503 if not ready).
- **D-32:** OpenAPI `/docs` enabled non-prod only; prod off or Basic-Auth behind Coolify.
- **D-33:** Unified error shape `{ "error": { "code", "message", "details?" } }`.
- **D-34:** Optional `Idempotency-Key` header on capture create (Hermes retries).

### Claude's Discretion
- Status lifecycle naming (`draft` → `auto_saved` → `confirmed`)
- Alembic as migration tool
- Light Camoufox sidecar (not HeadlessX) unless later proven insufficient
- Google OAuth callback host = `api.`

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — AUTH-01..04, CAP-01, CAP-03, LINK-01..02, CAL-02..03
- `.planning/ROADMAP.md` — Phase 1 goal + success criteria
- `.planning/PROJECT.md` — stack, tenancy, Better Auth, Calendar OAuth, MCP bearer (prep)
- `PUZZLESSBOX_PROJECT_BRIEF.md` — product brief / capture flow

### Research
- `.planning/research/STACK.md` — FastAPI, SQLModel, Better Auth JWKS, Google clients
- `.planning/research/PITFALLS.md` — Hermes cron timeout, Calendar dual-write, signup lock, owner_id leak, `/docs` exposure
- `.planning/research/ARCHITECTURE.md` — service topology

### Prior phase
- `.planning/phases/00-branding-design-system/00-CONTEXT.md` — brand tokens (not backend scope; UI later)

### External (scraper)
- `https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md` — self-host lacks Fire-engine
- `https://github.com/daijro/camoufox` — anti-detect Firefox sidecar
- `https://github.com/firecrawl/firecrawl/issues/2257` — self-host CF/WAF fingerprint failures

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Greenfield: no `api/` / `webapp/` implementation yet. Brand kit at `brand/` is for later WebApp UI only.
- Research stack pins: Python 3.14.6, FastAPI 0.13x, SQLModel, Better Auth JWKS → PyJWT, google-api-python-client.

### Established Patterns
- Monorepo layout planned: `api/`, `mcp-server/`, `webapp/`, `hermes-plugin/` (MCP/plugin out of Phase 1 scope).
- Coolify + GHCR deploy pattern already decided (Phase 5); Phase 1 still stands up scraper services on Coolify for Link.

### Integration Points
- Next.js Better Auth JWKS endpoint consumed by FastAPI auth dependency.
- Internal HTTP: FastAPI → Firecrawl → Camoufox (fallback).
- Google Calendar API v3 with ETag/If-Match on writes.
- Future MCP (Phase 2) uses Phase-1 service bearer + owner mapping.

</code_context>

<specifics>
## Specific Ideas

- User wants Cloudflare-capable link previews with **zero SaaS scraper cost**; VPS has 12 cores / 64GB RAM so Firecrawl weight is acceptable.
- Explicit rejection of patching Camoufox *into* Firecrawl core — sidecar fallback only.
- Header-based API versioning preferred over `/v1` path prefix.
- DB clock Europe/Berlin (user override of UTC recommendation).

</specifics>

<deferred>
## Deferred Ideas

- Full bidirectional Google Calendar mirror cron — not Phase 1
- Hermes push/notify on `auto_saved` — Phase 3
- MCP tool surface — Phase 2
- WebApp Settings UI for calendar picker / Connect — Phase 4 (API endpoints + OAuth in Phase 1)
- Paid residential proxies for harder CF — out of scope (cost constraint)
- HeadlessX / Camofox full stack — only if light Camoufox sidecar insufficient later
- SVG brand vectorization — Phase 0 deferral, unrelated to Phase 1

None — discussion stayed within phase scope (scraper Coolify deploy brought into Phase 1 by decision)

</deferred>

---

*Phase: 1-Datenmodell & Backend-API*
*Context gathered: 2026-07-30*
