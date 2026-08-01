---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 03
current_phase_name: Hermes-Plugin & Timeout-Spike
status: complete
stopped_at: Completed 03-04-PLAN.md
last_updated: "2026-08-01T03:19:20.864Z"
progress:
  total_phases: 4
  completed_phases: 4
  total_plans: 16
  completed_plans: 16
---

# State: Puzzlessbox

**Last updated:** 2026-07-31 (Phase 1 merged via PR #13)
**Current milestone:** v1 (initial release)

## Project Reference

- **Core value:** Capture-Flow muss reibungslos sitzen: Nachricht rein → Bestätigung → Auto-Save → Eintrag landet kategorisiert in der WebApp — ohne manuelle Nacharbeit.
- **Project brief:** `PUZZLESSBOX_PROJECT_BRIEF.md`
- **Roadmap:** `.planning/ROADMAP.md`
- **Requirements:** `.planning/REQUIREMENTS.md` (28 v1 requirements)
- **Research:** `.planning/research/SUMMARY.md` (confidence: HIGH)

## Current Position

- **Phase:** 03 (Hermes-Plugin & Timeout-Spike) — COMPLETE (UAT passed)
- **Prior:** 02 (MCP-Server) — PR #15 open (PR #14 partial merge on main)
- **Plan:** 4 of 4 complete
- **Status:** Phase 3 verified — 121/121 automated tests green on OrbStack stack
- **Progress Phase 3:** [██████████] 100% verified (4/4 plans)

```
[2/6] ██████░░░░░░░░░░░░░░  33% phases
```

## Phase Plan

| Phase | Goal (short) | Requirements | Status |
|-------|-------------|--------------|--------|
| 0 | Branding & Design Tokens | BRAND-01, BRAND-02 | Complete (2 plans) |
| 1 | Datenmodell & Backend-API | AUTH-01..04, CAP-01, CAP-03, LINK-01..02, CAL-02, CAL-03 | Complete (6 plans) |
| 2 | MCP-Server | MCP-01, MCP-02 | Complete (4 plans) |
| 3 | Hermes-Plugin & Timeout-Spike | CAP-02, CAP-04, MCP-03, MCP-04 | Complete (4 plans, UAT passed) |
| 4 | WebApp (UI) | BOARD-01..04, CAP-05, CAL-01 | Not started |
| 5 | Coolify-Deployment, CI/CD & Härtung | OPS-01..04 | Not started |

## Performance Metrics

- Phases complete: 0
- Phases planned: 1
- Plans executed: 0
- Verifications passed: 0

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

**Last updated:** 2026-07-29 (session resumed)

## Session Continuity

- **Last session:** 2026-08-01T03:19:20.845Z
- **Stopped at:** Completed 03-04-PLAN.md
- **Resume file:** None
- **Next recommended action:** `/gsd-plan-phase 4` or `/gsd-execute-phase 4`
- **Pre-execute artifacts:** `02-RESEARCH.md` (open Qs resolved), `02-VALIDATION.md` (populated), `02-DEPLOY-SPEC.md` (pinned GHCR workflow), D-23 `separate-image` pre-confirmed in deploy spec
- **Phase 1 deferred (not blockers):** Google browser OAuth UAT → Phase 4 webapp
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
