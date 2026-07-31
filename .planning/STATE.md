---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 02
current_phase_name: MCP-Server
status: Phase 2 planned — pre-execute prep complete, ready for execute
stopped_at: Phase 2 pre-execute prep complete
last_updated: "2026-07-31T02:40:00.000Z"
progress:
  total_phases: 6
  completed_phases: 2
  total_plans: 12
  completed_plans: 8
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

- **Phase:** 02 (MCP-Server) — planned, pre-execute prep done
- **Prior:** 01 (Datenmodell & Backend-API) — MERGED (PR #13 → `main` @ `890703e`)
- **Plan:** Phase 1 = 6/6 complete; Phase 2 = 4 plans ready (0 executed)
- **Status:** Research/Validation/Deploy-Spec closed — next `/gsd-execute-phase 2`
- **Progress Phase 1:** [██████████] 100%

```
[2/6] ██████░░░░░░░░░░░░░░  33% phases
```

## Phase Plan

| Phase | Goal (short) | Requirements | Status |
|-------|-------------|--------------|--------|
| 0 | Branding & Design Tokens | BRAND-01, BRAND-02 | Complete (2 plans) |
| 1 | Datenmodell & Backend-API | AUTH-01..04, CAP-01, CAP-03, LINK-01..02, CAL-02, CAL-03 | Complete (6 plans) |
| 2 | MCP-Server | MCP-01, MCP-02 | Not started |
| 3 | Hermes-Plugin & Timeout-Spike | CAP-02, CAP-04, MCP-03, MCP-04 | Not started |
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
- [ ] Phase 3: `/gsd-spike "Hermes Cron/dispatch_tool Timing für 30s-Bestätigungs-Flow"` vor `/gsd-plan-phase 3`

### Blockers

(none)

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260728-8an | GitHub-Repo puzzlessbox (privat) erstellen und einrichten | 2026-07-28 | 369af29 | [260728-8an-bevor-ich-phase-0-angehe-erstelle-via-gi](./quick/260728-8an-bevor-ich-phase-0-angehe-erstelle-via-gi/) |
| 260729-vmg | Platform Bootstrap: Dependabot, Kodiak, CI, CodeQL, Coolify Postgres | 2026-07-29 | 634d1fc | [260729-vmg-platform-bootstrap-dependabot-branch-pro](./quick/260729-vmg-platform-bootstrap-dependabot-branch-pro/) |

**Last updated:** 2026-07-29 (session resumed)

## Session Continuity

- **Last session:** 2026-07-31T02:40:00.000Z
- **Stopped at:** Phase 2 pre-execute prep complete
- **Resume file:** .planning/phases/02-mcp-server/02-01-PLAN.md (Wave 1 tracer)
- **Next recommended action:** `/gsd-execute-phase 2`
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
