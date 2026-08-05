# Roadmap: Puzzlessbox

**Created:** 2026-07-28
**Granularity:** standard
**Phase ID convention:** sequential
**Project mode:** standard

## Core Value

Capture-Flow muss reibungslos sitzen: Nachricht rein → Bestätigung → Auto-Save → Eintrag landet kategorisiert in der WebApp — ohne manuelle Nacharbeit.

## Phases

- [x] **Phase 0: Branding & Design System** - Hallmark-Brandkit und Design-Tokens vor WebApp-Bau (completed 2026-07-29)
- [x] **Phase 1: Datenmodell & Backend-API** - Postgres-Schema mit `owner_id`, FastAPI-CRUD, Better Auth, Link-Scraper, Google-Calendar-Sync (completed 2026-07-30)
- [x] **Phase 2: MCP-Server** - Remote-FastMCP-Server mit Bearer-Token-Auth über HTTPS (completed 2026-07-31)
- [x] **Phase 3: Hermes-Plugin & Timeout-Spike** - Bestätigungs-Flow, 30s-API-Timeout-State-Machine, Spike vor Plan (completed 2026-08-01)
- [ ] **Phase 4: WebApp** - Next.js-Kategorien-Board, Drag & Drop, Auth-UI, Google-OAuth-Settings, Link-Anzeige
- [x] **Phase 5: Coolify-Deployment, CI/CD & Härtung** - Docker-Image-Apps, GitHub-Actions-Builds, GHCR, Backups, Health Checks (completed 2026-08-02)

## Phase Details

### Phase 0: Branding & Design System

**Goal**: Einheitliches Markenauftreten (clean + warm, kein AI-Slop) liegt als Asset-Bibliothek und Design-Tokens vor und speist `/gsd-ui-phase 4`.
**Depends on**: Nothing (first phase)
**Requirements**: BRAND-01, BRAND-02
**Success Criteria** (what must be TRUE):

  1. Logo-Varianten (Wortmarke, Symbolmarke, Kombination) liegen als SVG/PNG vor und sind im Repo versioniert
  2. Farbpalette und Typografie-Paar sind als Design-Tokens (CSS-Variablen / Tailwind-Theme) exportiert und von Next.js konsumierbar
  3. Tonalität und Icon-/Illustrationsstil sind kurz dokumentiert und machen spätere Asset-Generierungen (z. B. weitere Icons in Phase 4) ohne Look-Drift reproduzierbar

**Plans**: 2/2 plans executed
Plans:
**Wave 1**

- [x] 00-01-PLAN.md — Ship Hallmark brand kit package: 25-PNG Apollo asset library, light + dark tokens.css, Tailwind v4 preset, node:test validation

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 00-02-PLAN.md — Write brand/BRAND.md identity bible + brand/VOICE.md 8 German microcopy examples

### Phase 1: Datenmodell & Backend-API

**Goal**: Backend-API und Datenmodell stehen mit Mehrmandantenfähigkeit (`owner_id`) von Tag 1, Auth ist integriert, und Capture/Link/Kalender-Backendlösungen sind end-to-end über die API nutzbar.
**Depends on**: Phase 0
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, CAP-01, CAP-03, LINK-01, LINK-02, CAL-02, CAL-03
**Success Criteria** (what must be TRUE):

  1. Ein Aufrufer kann sich per Email/Passwort registrieren und einloggen; die Session bleibt über API-Aufrufe hinweg bestehen; nach dem ersten Account wird weitere Registrierung serverseitig abgewiesen
  2. Alle Kerntabellen (Item, Category, Owner) tragen `owner_id` und jede API-Query filtert danach — ein fremder Tenant sieht keine Daten eines anderen
  3. Ein per API angelieferter Draft (Titel, Typ, Kategorie, Kurz-Zusammenfassung) wird persistiert und die 30s-Timeout-State-Machine speichert ihn ohne weiteren Eingriff automatisch als `auto_saved` ab
  4. Ein Link wird mit Metadaten (Titel, Vorschaubild, Beschreibung) in JSONB gespeichert und einer sinnvollen Kategorie zugeordnet
  5. Aus Terminen generierte Calendar-Events werden mit Google Calendar gelesen/geschrieben; bei konkurrierenden Writes schlägt `If-Match`-Precondition fehl und überschreibt nicht still

**Plans**: 6/6 plans executed
Plans:
**Wave 1**

- [x] 01-01-PLAN.md — FastAPI shell + Wave 0 test infra (pytest.ini, conftest with mock Postgres + mock JWKS, /health+/ready, Accept versioning, unified errors, /docs-prod-off)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-05-PLAN.md — SQLModel tables + Alembic 0001 migration (RLS + board_items VIEW + service_principals + seed categories) + test_draft_validation + test_rls

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 01-06-PLAN.md — Better Auth webapp bootstrap (JWKS, email/password, databaseHooks signup lock D-24) + FastAPI JWKS verify (D-21) + cookie/bearer (D-22) + service bearer (D-23) + draft CRUD tracer + idempotency (D-34)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 01-02-PLAN.md — Capture 30s timeout state machine (asyncio.Task, PATCH reset, confirm cancel, parallel-safe)
- [x] 01-03-PLAN.md — Link scrape pipeline (Firecrawl+Camoufox, 12s budget, SSRF guards, hostname fallback, Links category)
- [x] 01-04-PLAN.md — Google Calendar OAuth + encrypted tokens + If-Match optimistic concurrency (412 on conflict) + GET /events

### Phase 2: MCP-Server

**Goal**: Ein remote MCP-Server exponiert die Tool-Oberfläche für Hermes sicher über HTTPS mit Bearer-Token und ist als eigene Coolify-App vom Haupt-API entkoppelt.
**Depends on**: Phase 1
**Requirements**: MCP-01, MCP-02
**Success Criteria** (what must be TRUE):

  1. FastMCP-Server exponiert `create_item`, `list_categories`, `create_category`, `move_item`, `confirm_item`, `update_item` mit validierten Schemas und spricht die Backend-API als internen Client an
  2. Der MCP-Endpunkt ist nur über HTTPS mit gültigem Bearer-Token erreichbar; Anfragen ohne/mit falschem Token werden mit 401/403 abgewiesen

**Plans**: 4/4 plans executed
Plans:
**Wave 1**

- [x] 02-01-PLAN.md — TRACER: API Owner-Auth (mcp_clients + POST /internal/mcp-auth + X-Owner-Id-Guard) + MCP create_item end-to-end + Wave-0-Tests

**Wave 2** *(blocked on Wave 1)*

- [x] 02-02-PLAN.md — API-Board-Endpunkte: GET/POST /categories + PATCH /items/{id} (Move)
- [x] 02-04-PLAN.md — Deploy: mcp-server/ Dockerfile + GHCR-Workflow (deploy-mcp.yml) + Coolify-App (D-20/D-23)

**Wave 3** *(blocked on Wave 2)*

- [x] 02-03-PLAN.md — MCP-Tool-Expansion: confirm_item/update_item/move_item + list_categories/create_category + Schema/Contract-Tests

### Phase 3: Hermes-Plugin & Timeout-Spike

**Goal**: Hermes orchestriert den Bestätigungs-Flow über alle Messaging-Kanäle und treibt den 30s-Timeout über die API-State-Machine; das Cross-Server-Timing-Muster ist vorab per Spike validiert.
**Depends on**: Phase 2
**Requirements**: CAP-02, CAP-04, MCP-03, MCP-04
**Success Criteria** (what must be TRUE):

  1. Ein Spike zu Hermes-Cron/`dispatch_tool`-Timing für die 30s-Bestätigung liegt mit VALIDATED/INVALIDATED-Ergebnis vor, bevor die Plugin-Phase geplant wird
  2. User erhält nach einer Nachricht an Hermes eine formatierte Bestätigung (Titel, Typ, Kategorie, Kurz-Zusammenfassung) mit Edit-Option im Chat
  3. Capture-Flow funktioniert über alle Hermes-unterstützten Messaging-Kanäle (Telegram/WhatsApp/Discord/…) ohne Kanal-spezifische Anpassung in Puzzlessbox
  4. Hermes-Plugin ruft ausschließlich die MCP-Tools auf; kein direkter Datenbankzugriff vom Hermes-VPS

**Plans**: 4/4 plans executed
Plans:
**Wave 1**

- [x] 03-01-PLAN.md — API POST /drafts/{id}/discard + GET /drafts/{id} + MCP discard_item/get_draft_status Tools + idempotente confirm auf auto_saved (D-04, D-08, D-06 read path)
- [x] 03-02-PLAN.md — TRACER: hermes-plugin Skeleton — config + MCP-Client + format_confirmation + dialog happy path (CAP-02, MCP-03, MCP-04 spike landed)

**Wave 2** *(blocked on Wave 1)*

- [x] 03-03-PLAN.md — hermes-plugin Expansion: konversationeller Edit + Single-Active-Draft (sichern/verwerfen/warten) + list_categories + status-aware confirm ACK + Post-Autosave Poll via get_draft_status (D-01..D-09)

**Wave 3** *(blocked on Wave 2)*

- [x] 03-04-PLAN.md — setup.sh + kanalneutrale CAP-04 Tests über Telegram/WhatsApp/Discord (D-12, CAP-04; setzt Edit-Flow aus Plan 03 voraus)

### Phase 4: WebApp

**Goal**: Nutzer sieht und pflegt seine Items in einer responsiven Board-UI, kann sich einloggen und Google Calendar in den Settings verbinden — auf Basis der Design-Tokens aus Phase 0.
**Depends on**: Phase 3
**Requirements**: BOARD-01, BOARD-02, BOARD-03, BOARD-04, CAP-05, CAL-01
**Success Criteria** (what must be TRUE):

  1. User sieht ein Kanban-Board mit Default-Kategorien (Inbox, Notizen, Links, Tasks, Termine) und kann eigene Kategorien anlegen, umbenennen, einfärben und sortieren
  2. User verschiebt Items per Drag & Drop zwischen Kategorien und öffnet/bearbeitet Item-Details in der WebApp
  3. Gespeicherte Items erscheinen nach Auto-Save kategorisiert im Board ohne manuelle Nacharbeit
  4. User kann sich über die WebApp-UI mit Email/Passwort einloggen (Better Auth) und bleibt über Browser-Refresh eingeloggt
  5. User kann in den Settings Google Calendar über separatem OAuth verbinden (nicht Better Auth Social)

**Plans**: 7/7 plans executed
Plans:

- [x] 04-05-PLAN.md

**Wave 1** *(parallel — no file overlap)*

- [x] 04-00-PLAN.md — Infra: Wave 0 Vitest/RTL config + shadcn init + Brand-Token-Wiring + api-client + auth-client + middleware (BOARD-01, CAP-05)
- [x] 04-02-PLAN.md — API extensions: Alembic 0006 (categories.color/sort_order/deleted_at + items.sort_order + board_items VIEW migration) + PATCH/DELETE/reorder categories + PATCH items (Feld-Edit + Type-Change + sort_order) + POST /items/reorder + soft-delete + restore + GET /board-items ORDER BY sort_order (BOARD-02, BOARD-03, BOARD-04)

**Wave 2** *(blocked on Wave 1)*

- [x] 04-01-PLAN.md — TRACER (slim): Brand-Hero Login/Register + Board skeleton (5 Default-Kategorien) + Empty-States mit Apollo PNGs (D-05) + session survival + ?next= + logout (BOARD-01, CAP-05)

**Wave 3** *(blocked on Wave 2)*

- [x] 04-03-PLAN.md — Board features: DnD (@hello-pangea/dnd, cross-category + in-column reorder via POST /items/reorder, optimistic + revert) + Mobile Single-Column + Tabs + long-press Sheet + Multi-Select + Bulk Move + A11y + Item-Modal (centered, autosave, soft-delete undo, type-change, link OG, Calendar 412 inline Conflict-Panel D-14) + Kategorien-verwalten Panel (BOARD-02, BOARD-03, BOARD-04)

**Wave 4** *(blocked on Wave 3)*

- [x] 04-04-PLAN.md — Live update + Settings + Calendar: Board Poll (10s + backoff) + Offline-Banner + New-Item Toast/Pulse + Sound + Manual Refresh + Settings Hub (/settings Account/Calendar/Appearance) + Google Calendar 3-step Wizard + Disconnect + Theme toggle (header + settings) + First-Login Apollo Welcome (CAP-05, CAL-01)

**Gap Closure** *(post-execution)*

- [x] 04-06-PLAN.md — Bulk-move destination commit testid + strengthened dnd.test.tsx bulk destination-click test (G-04-bulk-move / UAT #11, BOARD-03)
- [ ] 04-07-PLAN.md — Harden isSignupLockedError against better-auth client envelope shapes + envelope-shape tests + prod UAT #6 re-run checkpoint (G-04-4, AUTH-03)

### Phase 5: Coolify-Deployment, CI/CD & Härtung

**Goal**: Alle drei Apps laufen als separate Coolify-Docker-Image-Apps produktiv unter `*.puzzlesstool.online`, Builds laufen über GitHub Actions → GHCR → Coolify-Webhook, und Backups/Health Checks sind aktiv.
**Depends on**: Phase 4
**Requirements**: OPS-01, OPS-02, OPS-03, OPS-04
**Success Criteria** (what must be TRUE):

  1. API, MCP und WebApp laufen als separate Coolify-Docker-Image-Apps unter `*.puzzlesstool.online` mit Traefik/Let's-Encrypt-HTTPS
  2. Ein Push auf `main` triggert pro Service einen GitHub-Actions-Build, pusht `:latest` und `:sha-<sha>` nach GHCR und löst den Coolify-Deploy-Webhook aus
  3. PostgreSQL hat einen aktiven lokalen Backup-Schedule auf dem Coolify-Server
  4. Jede App hat einen Health-Check-Endpoint und Coolify ist so konfiguriert, dass abgestürzte Container nicht mehr geroutet werden

**Plans**: 4/4 plans executed
Plans:
**Wave 1** *(parallel — no file overlap)*

- [x] 05-01-PLAN.md — Local Postgres backup schedule on puzzlessbox-db (cron 0 3 * * *, retention 14/14) + baseline backup trigger (OPS-03, D-09, D-10, D-11)
- [x] 05-02-PLAN.md — WebApp deploy artifacts: standalone Dockerfile + /api/health route + test + next.config standalone + deploy-web.yml GHCR workflow (OPS-02, OPS-04 web slice, D-05..D-08, D-13)

**Wave 2** *(blocked on Wave 1 — 05-01)*

- [x] 05-03-PLAN.md — TRACER: API cutover dockerfile → dockerimage — deploy-api.yml + new Coolify dockerimage app + domain swap api.puzzlesstool.online + /health verify + stop old (OPS-01, OPS-02, OPS-04 API slice, D-02, D-12, D-14, D-15, D-16, D-17, D-18)

**Wave 3** *(blocked on Wave 2 — 05-02 + 05-03)*

- [x] 05-04-PLAN.md — WebApp Coolify app + domain pbox.puzzlesstool.online + webhook + first deploy + /api/health verify + MCP health retune to D-14 + COVERAGE.md + final phase verification (OPS-01, OPS-02, OPS-04 web+MCP slice, D-01, D-03, D-13, D-14, D-15, D-19)

## Coverage

| Requirement | Phase |
|-------------|-------|
| BRAND-01 | Phase 0 |
| BRAND-02 | Phase 0 |
| AUTH-01 | Phase 1 |
| AUTH-02 | Phase 1 |
| AUTH-03 | Phase 1 |
| AUTH-04 | Phase 1 |
| CAP-01 | Phase 1 |
| CAP-03 | Phase 1 |
| LINK-01 | Phase 1 |
| LINK-02 | Phase 1 |
| CAL-02 | Phase 1 |
| CAL-03 | Phase 1 |
| MCP-01 | Phase 2 |
| MCP-02 | Phase 2 |
| CAP-02 | Phase 3 |
| CAP-04 | Phase 3 |
| MCP-03 | Phase 3 |
| MCP-04 | Phase 3 |
| BOARD-01 | Phase 4 |
| BOARD-02 | Phase 4 |
| BOARD-03 | Phase 4 |
| BOARD-04 | Phase 4 |
| CAP-05 | Phase 4 |
| CAL-01 | Phase 4 |
| OPS-01 | Phase 5 |
| OPS-02 | Phase 5 |
| OPS-03 | Phase 5 |
| OPS-04 | Phase 5 |

**Coverage:** 28/28 v1 requirements mapped ✓ — keine Orphans, keine Duplikate.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 0. Branding & Design System | 2/2 | Complete    | 2026-07-29 |
| 1. Datenmodell & Backend-API | 6/6 | Complete    | 2026-07-30 |
| 2. MCP-Server | 4/4 | Complete    | 2026-07-31 |
| 3. Hermes-Plugin & Timeout-Spike | 4/4 | In Progress|  |
| 4. WebApp | 6/6 | In Progress|  |
| 5. Coolify-Deployment, CI/CD & Härtung | 4/4 | Complete    | 2026-08-02 |

---
*Roadmap created: 2026-07-28*
*Next: `/gsd-plan-phase 0` (oder `/gsd-discuss-phase 0` für Branding-Entscheidungen)*
