# Puzzlessbox

## What This Is

Puzzlessbox ist der moderne Nachfolger des klassischen Handheld-Sprachrekorders: Sprach- oder Textnachricht an den Hermes Agent → strukturierte Verarbeitung → formatierte Bestätigung mit Edit-Option → Auto-Save nach 30s Inaktivität → kategorisierte Anzeige in der WebApp. Kernprinzip: **Erfassen ohne Reibung, Ordnung im Hintergrund.** Primär für den Betreiber (Single-User), architektonisch vorbereitet für späteren Public-/SaaS-Ausbau.

## Core Value

Capture-Flow muss reibungslos sitzen: Nachricht rein → Bestätigung → Auto-Save → Eintrag landet kategorisiert in der WebApp — ohne manuelle Nacharbeit.

## Business Context

- **Customer**: Solo-Betreiber (privat); später ggf. öffentliche Nutzer / SaaS offen
- **Revenue model**: v1 kein Monetarisieren; Dual-Lizenz (AGPL-3.0 + Commercial) bereitet SaaS vor
- **Success metric**: Typischer Tag: Sprachnotiz→Board, Link→Preview, Termin→Google Calendar — alle drei ohne Reibung
- **Strategy notes**: Siehe `PUZZLESSBOX_PROJECT_BRIEF.md`

## Requirements

### Validated

- [x] Einheitliches Branding (Hallmark: clean + warm, kein AI-Slop) inkl. Design-Tokens vor WebApp-Bau — **Phase 0** (`brand/` kit: 25 Apollo PNGs, `tokens.css`, Tailwind preset, `BRAND.md`, `VOICE.md`)
- [x] Coolify-Deploy (Docker-Image via GHCR + GitHub Actions), lokale DB-Backups, Health Checks — **Phase 5** (API/MCP/WebApp dockerimage apps, deploy-*.yml, backup schedule)
- [x] Link-Ablage mit Metadaten (Titel, Vorschaubild, Beschreibung), async scrape, rescrape, Board scrape_status — **Phase 05.2** (B1/B2)
- [x] Google Calendar OAuth + create/sync/ETag-412 + delete wiring (CAL-02/03) — **Phase 05.2** (B3/B4 + OAuth Accept fix)
- [x] Residual v1.0 audit polish: title-only Calendar sync (1h default window), 05.1 verification closeout, dbhub posture docs, Hermes test mock hygiene — **Phase 05.4**

### Active

- [ ] Capture-Flow: Sprach-/Textnachricht an Hermes → strukturierte Verarbeitung → Bestätigung (Titel, Typ, Kategorie, Kurz-Zusammenfassung) → Auto-Save nach 30s → Anzeige in WebApp
- [ ] Tasks & Kalender: Extraktion aus Nachrichten; intern speichern (Google write path shipped Phase 05.2)
- [ ] Kategorien-Board: Defaults Inbox · Notizen · Links · Tasks · Termine; frei erstellbar; Drag & Drop
- [ ] WebApp-Auth: Better Auth — Email/Password Register + Login; nach erstem Account `disableSignUp: true`
- [ ] MCP-Server (FastMCP) für Hermes: create/list/move/confirm/update Items & Categories; Bearer-Token-Auth
- [ ] Hermes-Plugin: Bestätigungs-Flow, 30s-Timeout, Kategorisierungs-Vorschlag, MCP-Client

### Out of Scope

- Multi-User-/Team-UI in v1 — Single-User; Datenmodell trotzdem tenant-fähig (`owner_id`)
- Native Mobile App / App-Store — nur responsive WebApp
- Eigene STT/TTS-Pipeline — Hermes Voice Mode wiederverwenden
- IP-Allowlist für MCP — nur Bearer-Token (Entscheidung aus Questioning)
- OAuth 2.1 für MCP — überdimensioniert für einen Client (Hermes)
- Google Tasks API in v1 — nur Google Calendar read/write
- GlitchTip/Error-Tracking — optional später, kein v1-Muss
- Terms/Privacy/Billing für Public-SaaS — eigene spätere Milestones
- Eigene Projektdomain — vorerst Subdomains unter `puzzlesstool.online`

## Context

- Hermes läuft auf separatem Ubuntu-24-VPS und wird nicht angefasst; Anbindung nur über Remote-MCP (Streamable HTTP) + leichtgewichtiges Hermes-Plugin (Cron/Hooks für Timeout — MCP allein kann nicht „warten und pushen“).
- Messaging: alle Kanäle, die Hermes bereits unterstützt (Telegram/WhatsApp/Discord/…) — kein Kanal-Lock in v1.
- Hosting: bestehendes Coolify (`https://puzzlesstool.online/`); Stack als Docker-Compose (API, MCP, WebApp, Postgres); Hermes außen vor.
- Deploy-Muster: GitHub Actions baut Images → GHCR (`:latest` + `:sha-<sha>`) → Coolify Webhook; coolify-mcp für einmalige Infrastruktur; coolify-cli für Ops.
- Branding: **Phase 0 complete** — `brand/` package (Apollo PNG kit, light/dark tokens, Tailwind preset, `BRAND.md`, `VOICE.md`). Downstream WebApp consumes `brand/tokens.css` + `brand/tailwind.preset.ts`.
- Phase 3 (Hermes-Plugin / 30s-Timeout) ist technisch unsicherster Teil — Spike vor Plan empfohlen.
- Brief: `PUZZLESSBOX_PROJECT_BRIEF.md` (Ende Juli 2026).

## Constraints

- **Stack**: Python 3.14.6 · FastAPI 0.13x · FastMCP 3.4.4 (nicht 4.0-alpha) · PostgreSQL 18.4 · Next.js 16.2.7 · Node 24 LTS · Hermes v0.19.0 · Coolify v4.1.2
- **Auth WebApp**: Better Auth (Email/Password); Postgres-Adapter; nach erstem User Signup sperren
- **Auth Calendar**: Separater Google-OAuth (nicht Better Auth Social) — Connect in Settings
- **Auth MCP**: Statisches Bearer-Token (rotierbar, Coolify Secret); keine IP-Allowlist
- **Tenancy**: Jede Kerntabelle mit `owner_id` von Tag 1; Queries immer filtern
- **Repo**: Privat; AGPL-3.0 + Commercial Dual-Lizenz; Monorepo (`api/`, `mcp-server/`, `webapp/`, `hermes-plugin/`)
- **Domains**: `pbox.` / `api.` / `mcp.` unter `puzzlesstool.online` (Phase 5)
- **Backups**: Nur lokal auf Coolify-Server (Phase 5)
- **Branding**: Hallmark — kein AI-Slop; Design-Entscheidungen in Discuss Phase 0

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Hermes getrennt, Anbindung nur MCP + Plugin | Hermes-VPS unangetastet; Timeout braucht Cron/Hooks | — Pending |
| Tenant-fähig (`owner_id`) von Anfang an | SaaS-Nachrüstung teuer; Spalte jetzt fast kostenlos | — Pending |
| Better Auth Email/Password; Signup nach erstem User zu | Solo-Privat + voller Auth-Flow ohne offene Registrierung | — Pending |
| Google Calendar: separater OAuth in Settings | Login und Calendar-Scopes entkoppelt; Email/Password bleibt Primär-Auth | — Pending |
| MCP: nur Bearer, keine IP-Allowlist | Einfacher Ops; Token rotierbar; Single-Client | — Pending |
| Branding via Hallmark (clean+warm) vor WebApp | Kein AI-Slop; Tokens füttern `/gsd-ui-phase` | ✓ Phase 0 |
| Dual-Lizenz AGPL-3.0 + Commercial jetzt | Verhindert 1:1 SaaS-Kopie; alleiniger Autor → jetzt einfach | — Pending |
| Coolify Docker-Image + GH Actions (nicht Nixpacks-Build) | Build extern; Coolify-Server nicht überlasten | ✓ Phase 5 |
| Alle Hermes-Messaging-Kanäle in v1 | Kein Kanal-Lock; Capture überall wo Hermes erreichbar | — Pending |
| Default-Kategorien: Inbox · Notizen · Links · Tasks · Termine | Sofort nutzbares Board ohne Setup-Reibung | — Pending |
| Bestätigungs-Payload: Titel + Typ + Kategorie + Kurz-Zusammenfassung | Editierbar ohne Voll-Draft-Überladung | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-08-09 after Phase 05.2 completion*
