---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 0
current_phase_name: Branding & Design System
status: "Brand locked: **Apollo** + Util. Sketch 003 **keep-all** — ~25 assets (must+nice). Pending HF credits: pose-wave/sleep. Gallery: `003-apollo-asset-pack/compare.html`."
stopped_at: Phase 0 context gathered
last_updated: "2026-07-29T02:49:39.492Z"
progress:
  total_phases: 1
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
---

# State: Puzzlessbox

**Last updated:** 2026-07-29 (Apollo full brand kit 003 keep-all)
**Current milestone:** v1 (initial release)

## Project Reference

- **Core value:** Capture-Flow muss reibungslos sitzen: Nachricht rein → Bestätigung → Auto-Save → Eintrag landet kategorisiert in der WebApp — ohne manuelle Nacharbeit.
- **Project brief:** `PUZZLESSBOX_PROJECT_BRIEF.md`
- **Roadmap:** `.planning/ROADMAP.md`
- **Requirements:** `.planning/REQUIREMENTS.md` (28 v1 requirements)
- **Research:** `.planning/research/SUMMARY.md` (confidence: HIGH)

## Current Position

- **Phase:** 0 (Branding & Design System) — discuss paused; sketch exploring DNA
- **Plan:** none yet
- **Status:** Brand locked: **Apollo** + Util. Sketch 003 **keep-all** — ~25 assets (must+nice). Pending HF credits: pose-wave/sleep. Gallery: `003-apollo-asset-pack/compare.html`.
- **Progress:** 0/6 phases complete

```
[0/6] ░░░░░░░░░░░░░░░░░░░░  0%
```

## Phase Plan

| Phase | Goal (short) | Requirements | Status |
|-------|-------------|--------------|--------|
| 0 | Branding & Design Tokens | BRAND-01, BRAND-02 | Not started |
| 1 | Datenmodell & Backend-API | AUTH-01..04, CAP-01, CAP-03, LINK-01..02, CAL-02, CAL-03 | Not started |
| 2 | MCP-Server | MCP-01, MCP-02 | Not started |
| 3 | Hermes-Plugin & Timeout-Spike | CAP-02, CAP-04, MCP-03, MCP-04 | Not started |
| 4 | WebApp (UI) | BOARD-01..04, CAP-05, CAL-01 | Not started |
| 5 | Coolify-Deployment, CI/CD & Härtung | OPS-01..04 | Not started |

## Performance Metrics

- Phases complete: 0
- Phases planned: 0
- Plans executed: 0
- Verifications passed: 0

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

- [ ] Phase 0: `/gsd-discuss-phase 0` — Critter/Util locked; rest: Name optional, Asset-Pack (favicon → OG), CONTEXT schreiben
- [ ] Phase 3: `/gsd-spike "Hermes Cron/dispatch_tool Timing für 30s-Bestätigungs-Flow"` vor `/gsd-plan-phase 3`

### Blockers

(none)

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260728-8an | GitHub-Repo puzzlessbox (privat) erstellen und einrichten | 2026-07-28 | 369af29 | [260728-8an-bevor-ich-phase-0-angehe-erstelle-via-gi](./quick/260728-8an-bevor-ich-phase-0-angehe-erstelle-via-gi/) |

**Last updated:** 2026-07-29 (session resumed)

## Session Continuity

- **Last session:** 2026-07-29T02:49:39.484Z
- **Stopped at:** Phase 0 context gathered
- **Resume file:** .planning/phases/00-branding-design-system/00-CONTEXT.md
- **Next recommended action:** Top up Higgsfield → gen pose-wave/sleep **oder** `/gsd-discuss-phase 0` → CONTEXT
- **Open assumptions** (aus Brief Abschnitt 11): WebApp-Auth-Umfang, FastAPI-Pin, Subdomain-Struktur, Backup-Retention — in den jeweiligen Discuss-Phasen klären.

---
*State initialized: 2026-07-28 after roadmap creation*
