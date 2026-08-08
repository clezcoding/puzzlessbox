---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 05.2
current_phase_name: fix-link-cal-integration-wiring-b1-b4
status: complete
stopped_at: Completed 05.2-03-PLAN.md
last_updated: "2026-08-08T20:02:00.000Z"
progress:
  total_phases: 8
  completed_phases: 8
  total_plans: 35
  completed_plans: 35
---

# State: Puzzlessbox

**Last updated:** 2026-08-08 (05.2 plan 03 complete — 4/4 plans)
**Current milestone:** v1.0 (initial release) — audit `tech_debt`

## Project Reference

- **Core value:** Capture-Flow muss reibungslos sitzen: Nachricht rein → Bestätigung → Auto-Save → Eintrag landet kategorisiert in der WebApp — ohne manuelle Nacharbeit.
- **Project brief:** `PUZZLESSBOX_PROJECT_BRIEF.md`
- **Roadmap:** `.planning/ROADMAP.md`
- **Requirements:** `.planning/REQUIREMENTS.md` (28 v1 requirements)
- **Research:** `.planning/research/SUMMARY.md` (confidence: HIGH)
- **Audit:** `.planning/v1.0-MILESTONE-AUDIT.md`

## Current Position

- **Phase:** 05.2 (fix-link-cal-integration-wiring-b1-b4) — COMPLETE (4/4 plans)
- **Prior:** 04 (webapp) — PR #21; 03 Hermes — PR #20; 02 MCP — PR #15
- **Status:** Phase 05.2 complete — ready for verify
- **Resume:** None
- **UAT login:** `uat@puzzless.local` / see `webapp/.env.local`

```
[6/7] █████████████████░░░   86% phases
```

## Phase Plan

| Phase | Goal (short) | Requirements | Status |
|-------|-------------|--------------|--------|
| 0 | Branding & Design Tokens | BRAND-01, BRAND-02 | Complete |
| 1 | Datenmodell & Backend-API | AUTH-01..04, CAP-01, CAP-03, LINK-01..02, CAL-02, CAL-03 | Complete |
| 2 | MCP-Server | MCP-01, MCP-02 | Complete |
| 3 | Hermes-Plugin & Timeout-Spike | CAP-02, CAP-04, MCP-03, MCP-04 | Complete |
| 4 | WebApp (UI) | BOARD-01..04, CAP-05, CAL-01 | Complete |
| 5 | Coolify-Deployment, CI/CD & Härtung | OPS-01..04 | Complete |
| 5.1 | Tech debt: G-05-7 + harden advisories | D-01..D-12 | Complete (3/3 plans) |

## Performance Metrics

- Phases complete: 4
- Phases planned: 6
- Plans executed: 16
- Verifications passed: 4

**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 00-branding-design-system P01 | 2min | 2 tasks | 34 files |
| Phase 00-branding-design-system P02 | 4min | 2 tasks | 2 files |
| Phase 01-datenmodell-backend-api P01 | 5min | 2 tasks | 18 files |
| Phase 01-datenmodell-backend-api P05 | 8min | 2 tasks | 19 files |
| Phase 01-datenmodell-backend-api P06 | 12min | 2 tasks | 20 files |
| Phase 01-datenmodell-backend-api P02 | 15min | 2 tasks | 6 files |
| Phase 01-datenmodell-backend-api P04 | 25min | 3 tasks | 15 files |
| Phase 01-datenmodell-backend-api P03 | 35min | 3 tasks | 12 files |
| Phase 01-datenmodell-backend-api P03 | 35min | 3 tasks | 12 files |
| Phase 02-mcp-server P01 | 6 | 2 tasks | 27 files |
| Phase 02-mcp-server P02 | 8min | 2 tasks | 3 files |
| Phase 02 P03 | 12min | 2 tasks | 7 files |
| Phase 02-mcp-server P04 | 20min | 2 tasks | 4 files |
| Phase 03 P02 | 5min | 2 tasks | 14 files |
| Phase 03-hermes-plugin-timeout-spike P01 | 15min | 3 tasks | 9 files |
| Phase 03-hermes-plugin-timeout-spike P04 | 6min | 2 tasks | 3 files |
| Phase 03 P04 | 6min | 2 tasks | 3 files |
| Phase 05-coolify-deployment-ci-cd-h-rtung P01 | 4min | 2 tasks | 2 files |
| Phase 05-coolify-deployment-ci-cd-h-rtung P02 | 5min | 2 tasks | 5 files |
| Phase 05 P04 | 40min | 3 tasks | 5 files |
| Phase 04-webapp P05 | 5min | 5 tasks | 5 files |
| Phase 04-webapp P06 | 2min | 2 tasks | 2 files |
| Phase 04-webapp P07 | 45min | 3 tasks | 4 files |
| Phase 05.1-address-tech-debt-g-05-7-security-harden-advisories P01 | 6min | 2 tasks | 3 files |
| Phase 05.1-address-tech-debt-g-05-7-security-harden-advisories P02 | 4min | 1 task | 3 files |
| Phase 05.1 P03 | 45min | 3 tasks | 5 files |
| Phase 05.2 P00 | 3min | 2 tasks | 5 files |
| Phase 05.2 P01 | 12 | 2 tasks | 11 files |
| Phase 05.2 P02 | 3min | 3 tasks | 5 files |
| Phase 05.2-fix-link-cal-integration-wiring-b1-b4 P02 | 3min | 3 tasks | 5 files |
| Phase 05.2 P03 | 12min | 3 tasks | 10 files |

## Accumulated Context

### Key Decisions (from PROJECT.md)

- Hermes bleibt auf separatem VPS; Anbindung nur über Remote-MCP + leichtgewichtiges Plugin (Cron/Hooks für Timeout)
- `owner_id` auf jeder Kerntabelle von Tag 1 (SaaS-Nachrüstung wäre teuer)
- Better Auth Email/Password; Signup nach erstem User dynamisch gesperrt (`databaseHooks`)
- Google Calendar: separater OAuth in Settings (nicht Better Auth Social)
- MCP: statisches Bearer-Token (rotierbar), keine IP-Allowlist in v1
- Branding via Hallmark (clean + warm, kein AI-Slop) vor WebApp
- **Brand hero = Apollo (Waschbär, 002-B)** — gesamte Identity; myth link Hermes; Util Bone nur UI-Gerüst; Accent `#c45c3e`
- Dual-Lizenz AGPL-3.0 + Commercial
- Coolify Docker-Image-Deploy + GitHub Actions (nicht Nixpacks-Build)
- Alle Hermes-Messaging-Kanäle in v1 (kein Kanal-Lock)
- Default-Kategorien: Inbox · Notizen · Links · Tasks · Termine
- Bestätigungs-Payload: Titel + Typ + Kategorie + Kurz-Zusammenfassung

### Research Flags

- **Phase 3 (Hermes-Plugin & Timeout-Spike):** Höchstes technisches Risiko — Spike vor Plan zwingend. Hermes-Cron tickt nur alle 60s, daher API-seitige Timeout-State-Machine.
- **Phase 1 (Google Calendar Concurrency):** Optimistic Locking mit ETags/`If-Match` braucht präzises Mapping der Google-API-Fehlerstrukturen.

### TODOs

- [x] Phase 0: `/gsd-plan-phase 0` — 2 plans (brand kit + docs)
- [x] Phase 3 spike: `.planning/spikes/` 001–004 (MCP-04 VALIDATED) — vor `/gsd-plan-phase 3`

### Blockers

(none)

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260728-8an | GitHub-Repo puzzlessbox (privat) erstellen und einrichten | 2026-07-28 | 369af29 | [260728-8an-bevor-ich-phase-0-angehe-erstelle-via-gi](./quick/260728-8an-bevor-ich-phase-0-angehe-erstelle-via-gi/) |
| 260729-vmg | Platform Bootstrap: Dependabot, Kodiak, CI, CodeQL, Coolify Postgres | 2026-07-29 | 634d1fc | [260729-vmg-platform-bootstrap-dependabot-branch-pro](./quick/260729-vmg-platform-bootstrap-dependabot-branch-pro/) |
| 260803-001 | Coolify 3-app GHCR/env audit + Renovate/Dependabot PRs (latest stable) | 2026-08-03 | e1197bd | [260803-001-coolify-3-apps-latest-ghcr-build-deploy-](./quick/260803-001-coolify-3-apps-latest-ghcr-build-deploy-/) |

**Last updated:** 2026-08-03 (quick 260803-001 Coolify audit + dep PRs)

### Roadmap Evolution

- Phase 05.1 inserted after Phase 5: Address tech debt: G-05-7 + security harden advisories (URGENT)

## Session Continuity

- **Last session:** 2026-08-08T20:01:44.237Z
- **Stopped at:** Completed 05.2-03-PLAN.md
- **Resume file:** None
- **Milestone audit:** `.planning/v1.0-MILESTONE-AUDIT.md` — was `tech_debt` (Nyquist debt); phases 0/2/3/4/5 now `validated` + `nyquist_compliant: true` (2026-08-05)
- **Phase 5 UAT:** `.planning/phases/05-coolify-deployment-ci-cd-h-rtung/05-UAT.md` — r6 deep-prod (50 pass / 0 fail / 6 warn; board a2 confirmed)
- **Prod UAT account:** `uat@puzzless.local` / `UatTestPass1!` (user `1ac8eb47-6526-472a-8267-bbf7b02eff73` after wipe r6)
- **Phase 4 UAT:** `.planning/phases/04-webapp/04-UAT.md` — 18/18 pass; G-04-4 closed via 04-07
- **05.1 closed:** G-05-7 local MCP bootstrap; HSTS/banner advisories; well-known stub — all 3 plans complete
- **Coolify:** api/mcp/web healthy; old `puzzlessbox-api` dxoflgio… already deleted (404); SERVICE_OWNER_ID → new first user
- **Nyquist:** phases 0–5 compliant; 05.1 VALIDATION.md draft ready
- **Next recommended action:** /gsd-verify-phase 05.1 or milestone ship
- **Phase 1 deferred (not blockers):** Google browser OAuth full round-trip → Phase 4 webapp (API 302 verified)
- **Open assumptions** (aus Brief Abschnitt 11): WebApp-Auth-Umfang, FastAPI-Pin, Subdomain-Struktur, Backup-Retention — in den jeweiligen Discuss-Phasen klären.

---
*State initialized: 2026-07-28 after roadmap creation*

## Decisions

- [Phase ?]: PNG kit only per D-05 — SVG vectorization deferred to post-credit-topup
- [Phase ?]: brand/ is pure static package — consumers install tailwindcss; no package.json under brand/
- [Phase ?]: Production brand docs at brand/ decoupled from sketches per D-04
- [Phase ?]: 8 locked German microcopy examples with capture verb glossary per D-09
- [Phase ?]: Lazy SQLAlchemy engine init so app imports without live Postgres
- [Phase ?]: Normalize postgres:// URLs to postgresql+psycopg2:// for SQLAlchemy
- [Phase ?]: Categories seed with NULL owner_id; RLS allows NULL OR matching owner_id
- [Phase ?]: Link metadata uses portable JSON in SQLModel; migration keeps JSONB
- [Phase ?]: Capture draft create consolidated in capture.py until type-specific read/update diverges
- [Phase ?]: board-items uses explicit owner_id WHERE alongside RLS on VIEW
- [Phase ?]: Login prefers Better Auth sign-in token before /token fetch
- [Phase ?]: Async capture endpoints so DraftTimeoutManager asyncio.create_task runs on ASGI loop
- [Phase ?]: Timeout integration tests use AsyncClient — TestClient does not pump background tasks
- [Phase ?]: calendar_tokens.owner_id app-level check only — no FK to Better Auth user table (D-21)
- [Phase ?]: OAuth connect requires JWT; full browser OAuth UAT pending webapp at app.puzzlesstool.online
- [Phase ?]: Firecrawl /ready uses /v0/health/liveness; workers split for Coolify healthchecks
- [Phase ?]: Scraper stack internal-only on shared Docker network; API SCRAPER_ENABLED gates /ready ping
- [Phase ?]: Firecrawl /ready uses /v0/health/liveness; workers split for Coolify healthchecks
- [Phase ?]: Scraper stack internal-only on shared Docker network; SCRAPER_ENABLED gates /ready ping
- [Phase ?]: mcp-server factory.py split from server.py for testable build_mcp_stack import
- [Phase ?]: mcp-server uvicorn 0.52.0 pinned — fastmcp 3.4.4 conflicts with api 0.34.0
- [Phase ?]: CategoryCreate minimal (name only) — color/sort_order deferred to Phase 4
- [Phase ?]: move_item UPDATE has no status filter — confirmed items movable per D-12
- [Phase ?]: register_tools aggregates items + categories modules in app.tools
- [Phase ?]: Schema reject tests use FunctionTool.run + fastmcp ValidationError
- [Phase ?]: D-23 separate MCP Coolify Docker-Image-App at mcp.puzzlesstool.online — GHCR deploy-mcp.yml on main
- [Phase ?]: Coolify MCP webhook uses API bearer auth (cfdfb19)
- [Phase ?]: Hermes plugin uses streamable_http_client (MCP SDK) not spike streamablehttp_client alias
- [Phase ?]: Inbox category_id stub via MCP_CATEGORY_ID env until Plan 03 list_categories
- [Phase ?]: Alembic 0005 extends item_status with discarded for soft-delete discard_draft response
- [Phase ?]: get_draft_status returns minimal {id,type,status} poll surface per D-06
- [Phase ?]: Unrecognized free text with active draft routes to D-07 conflict via start_capture_flow
- [Phase ?]: Note type category hints prefer Inbox for plain captures
- [Phase ?]: Confirm ACK uses live call_mcp_get_item_status not session snapshot (D-08)
- [Phase ?]: setup.sh enforces HTTPS MCP_URL and MCP_BEARER min 20 chars (D-12)
- [Phase ?]: CAP-04 channel tests use MockSession adapters without render logic
- [Phase ?]: Coolify MCP get_database_backups fallback when CLI backup list unmarshals retention_max_storage_locally
- [Phase ?]: WebApp health at /api/health only — no /ready Traefik gate (D-12, D-13)
- [Phase ?]: Coolify trigger uses GET + status assert, mirroring deploy-api pattern not MCP POST
- [Phase ?]: WebApp UUID qxpgv6p1rp3vupue9al8hbzz — ghcr.io/clezcoding/puzzlessbox-web:latest @ pbox
- [Phase ?]: COOLIFY_WEB_WEBHOOK via deploy API URL pattern (D-19)
- [Phase ?]: MCP n5frtiupale5c2zjm9fyk1qc health retuned 10s/5s/5/15s via REST PATCH
- [Phase ?]: Docker build context repo-root; brand/ required for globals.css import
- [Phase ?]: CORS_ORIGINS in Coolify API env + config.py default includes pbox
- [Phase ?]: NEXT_PUBLIC_* baked via Dockerfile ARG and deploy-web build-args
- [Phase ?]: SIGNUP_LOCKED sessionStorage survives login remount on 409
- [Phase ?]: toast.success bulk move test asserts second undefined arg when total <= 5 items
- [Phase ?]: isSignupLockedError exported + hardened for all better-auth 409 envelope shapes (04-07)
- [Phase ?]: Better Auth user lookup uses createdAt column for first-user bootstrap ordering
- [Phase ?]: Prod bootstrap blocked log omits env var name to satisfy grep gate without leaking token
- [Phase ?]: register_health accepts injected Settings — get_settings() lru_cache breaks custom Settings in tests
- [Phase ?]: Well-known stub omits authorization_servers per D-11; static shared bearer documented in health.py (D-12)
- [Phase ?]: Coolify MCP cannot edit raw docker labels — UI paste path primary
- [Phase ?]: HSTS per leaf FQDN only; apex excluded from includeSubDomains (D-07)
- [Phase ?]: Defense in depth: Traefik banner strip + Next.js poweredByHeader false
- [Phase ?]: Wave 0 xfail/it.todo stubs lock LINK/CAL test names before plans 01-03
- [Phase ?]: LinkScrapeManager 12s soft timeout; partial when title without image
- [Phase ?]: BoardCard native img referrerPolicy no-referrer; remotePatterns unchanged
- [Phase ?]: Cancel race fix: _active_tasks pop only when current_task matches map entry
- [Phase ?]: POST /links uses apply_scrape_to_link after pending row insert (D-04)
- [Phase ?]: board-items google_event_id via events JOIN not VIEW migration
- [Phase ?]: Modal Google sync via updateItem title PATCH create-on-edit path
