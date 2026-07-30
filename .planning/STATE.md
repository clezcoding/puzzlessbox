---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 01
current_phase_name: Datenmodell & Backend-API
status: executing
stopped_at: Completed 01-02-PLAN.md
last_updated: "2026-07-30T02:51:09.272Z"
progress:
  total_phases: 2
  completed_phases: 1
  total_plans: 8
  completed_plans: 6
---

# State: Puzzlessbox

**Last updated:** 2026-07-30 (Phase 1 planned — 6 plans, 4 waves)
**Current milestone:** v1 (initial release)

## Project Reference

- **Core value:** Capture-Flow muss reibungslos sitzen: Nachricht rein → Bestätigung → Auto-Save → Eintrag landet kategorisiert in der WebApp — ohne manuelle Nacharbeit.
- **Project brief:** `PUZZLESSBOX_PROJECT_BRIEF.md`
- **Roadmap:** `.planning/ROADMAP.md`
- **Requirements:** `.planning/REQUIREMENTS.md` (28 v1 requirements)
- **Research:** `.planning/research/SUMMARY.md` (confidence: HIGH)

## Current Position

- **Phase:** 01 (Datenmodell & Backend-API) — EXECUTING
- **Plan:** 5 of 6
- **Status:** Ready to execute
- **Progress:** [████████░░] 75% execution

```
[0/6] ░░░░░░░░░░░░░░░░░░░░  0%
```

## Phase Plan

| Phase | Goal (short) | Requirements | Status |
|-------|-------------|--------------|--------|
| 0 | Branding & Design Tokens | BRAND-01, BRAND-02 | Complete (2 plans) |
| 1 | Datenmodell & Backend-API | AUTH-01..04, CAP-01, CAP-03, LINK-01..02, CAL-02, CAL-03 | Planned (6 plans) |
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

- **Last session:** 2026-07-30T02:51:09.265Z
- **Stopped at:** Completed 01-02-PLAN.md
- **Resume file:** None
- **Next recommended action:** `/gsd-execute-phase 1`
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
