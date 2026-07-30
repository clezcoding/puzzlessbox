# Requirements: Puzzlessbox

**Defined:** 2026-07-28
**Core Value:** Capture-Flow muss reibungslos sitzen: Nachricht rein → Bestätigung → Auto-Save → Eintrag landet kategorisiert in der WebApp — ohne manuelle Nacharbeit.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Capture

- [x] **CAP-01**: User sendet Sprach- oder Textnachricht an Hermes; System erzeugt strukturierten Draft (Titel, Typ, Kategorie, Kurz-Zusammenfassung)
- [ ] **CAP-02**: User sieht formatierte Bestätigung mit Edit-Option vor dem Speichern
- [x] **CAP-03**: Nach 30s Inaktivität speichert System den Draft automatisch (Timeout-State-Machine serverseitig in der API, nicht nur Hermes-Cron)
- [ ] **CAP-04**: Capture funktioniert über alle Messaging-Kanäle, die Hermes bereits unterstützt (kein eigener Messenger in Puzzlessbox)
- [ ] **CAP-05**: Gespeicherte Items erscheinen kategorisiert in der WebApp

### Board & Categories

- [ ] **BOARD-01**: User sieht Kanban-/Board-Ansicht mit Default-Kategorien: Inbox, Notizen, Links, Tasks, Termine
- [ ] **BOARD-02**: User kann eigene Kategorien anlegen, umbenennen, einfärben und sortieren
- [ ] **BOARD-03**: User verschiebt Items per Drag & Drop zwischen Kategorien
- [ ] **BOARD-04**: User öffnet Item-Detail und bearbeitet Felder in der WebApp

### Authentication & Tenancy

- [x] **AUTH-01**: User kann sich mit Email und Passwort registrieren (Better Auth)
- [x] **AUTH-02**: User kann sich einloggen und Session bleibt über Browser-Refresh erhalten
- [x] **AUTH-03**: Nach dem ersten Account ist weitere Registrierung dynamisch gesperrt (`databaseHooks` / User-Count > 0)
- [x] **AUTH-04**: Alle Kerntabellen haben `owner_id`; alle Queries filtern danach

### MCP & Hermes

- [ ] **MCP-01**: Remote-MCP-Server (FastMCP) exponiert Tools: `create_item`, `list_categories`, `create_category`, `move_item`, `confirm_item`, `update_item`
- [ ] **MCP-02**: MCP ist nur mit Bearer-Token über HTTPS erreichbar (separate Coolify-App)
- [ ] **MCP-03**: Hermes-Plugin orchestriert Bestätigungs-Flow und ruft MCP-Tools auf
- [ ] **MCP-04**: Vor Plan/Execute der Plugin-Phase existiert Spike zu Hermes Timing/Hooks (VALIDATED/INVALIDATED)

### Links

- [x] **LINK-01**: User sendet Link an Hermes; System speichert Item mit Metadaten (Titel, Vorschaubild, Beschreibung) in JSONB
- [x] **LINK-02**: Link-Items landen in sinnvoller Kategorie (Default oder Vorschlag)

### Calendar

- [ ] **CAL-01**: User verbindet Google Calendar in WebApp-Settings via separatem OAuth (nicht Better Auth Social)
- [x] **CAL-02**: Aus Nachrichten extrahierte Termine werden als Calendar-Events lesbar und schreibbar mit Google Calendar synchronisiert
- [x] **CAL-03**: Calendar-Writes nutzen Optimistic Concurrency (ETag / If-Match); Konflikte werden nicht still überschrieben

### Branding

- [x] **BRAND-01**: Hallmark-basiertes Brandkit (Logo-Varianten, Palette, Typografie, Tonalität) — clean + warm, kein AI-Slop
- [x] **BRAND-02**: Design-Tokens (CSS/Tailwind) und Asset-Bibliothek existieren vor WebApp-UI-Bau und speisen `/gsd-ui-phase`

### Deployment & Ops

- [ ] **OPS-01**: API, MCP und WebApp laufen als separate Coolify Docker-Image-Apps unter `*.puzzlesstool.online`
- [ ] **OPS-02**: GitHub Actions baut Images nach GHCR (`:latest` + `:sha-<sha>`) und triggert Coolify-Deploy-Webhooks
- [ ] **OPS-03**: PostgreSQL hat lokalen Backup-Schedule auf dem Coolify-Server
- [ ] **OPS-04**: Jede App hat Health-Check-Endpoint und Coolify Health-Check konfiguriert

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Collaboration & SaaS

- **SAAS-01**: Multi-User-/Team-UI und Tenant-Verwaltung
- **SAAS-02**: Billing, Rate-Limiting, öffentliche Registrierung
- **SAAS-03**: Terms of Service und Datenschutzerklärung für Public-Launch

### Productivity

- **CAL-04**: Google Tasks API Sync
- **AI-01**: Semantische Suche / „Ask AI“ über historische Notizen
- **MOB-01**: Native Mobile App / App-Store-Release

### Security Hardening

- **MCP-05**: OAuth 2.1 für MCP
- **MCP-06**: IP-Allowlist für Hermes-VPS am Reverse-Proxy (optional Hardening)
- **OPS-05**: GlitchTip / Application Error-Tracking
- **OPS-06**: S3-Offsite-Backups

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Eigene STT/TTS-Pipeline | Hermes Voice Mode wiederverwenden |
| Eigener Messaging-Gateway | Hermes 18+-Plattformen nutzen |
| Multi-User-UI in v1 | Solo-Betreiber; Datenmodell trotzdem tenant-fähig |
| MCP OAuth 2.1 in v1 | Ein Client (Hermes) — Bearer reicht |
| IP-Allowlist in v1 | Bewusst nur Bearer (Questioning) |
| Eigene Projektdomain | Vorerst `puzzlesstool.online` |
| Nixpacks-/Coolify-native Builds | Builds in GitHub Actions, Images nach GHCR |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| BRAND-01 | Phase 0 | Complete |
| BRAND-02 | Phase 0 | Complete |
| AUTH-01 | Phase 1 | Complete |
| AUTH-02 | Phase 1 | Complete |
| AUTH-03 | Phase 1 | Complete |
| AUTH-04 | Phase 1 | Complete |
| CAP-01 | Phase 1 | Complete |
| CAP-03 | Phase 1 | Complete |
| LINK-01 | Phase 1 | Complete |
| LINK-02 | Phase 1 | Complete |
| CAL-02 | Phase 1 | Complete |
| CAL-03 | Phase 1 | Complete |
| MCP-01 | Phase 2 | Pending |
| MCP-02 | Phase 2 | Pending |
| CAP-02 | Phase 3 | Pending |
| CAP-04 | Phase 3 | Pending |
| MCP-03 | Phase 3 | Pending |
| MCP-04 | Phase 3 | Pending |
| BOARD-01 | Phase 4 | Pending |
| BOARD-02 | Phase 4 | Pending |
| BOARD-03 | Phase 4 | Pending |
| BOARD-04 | Phase 4 | Pending |
| CAP-05 | Phase 4 | Pending |
| CAL-01 | Phase 4 | Pending |
| OPS-01 | Phase 5 | Pending |
| OPS-02 | Phase 5 | Pending |
| OPS-03 | Phase 5 | Pending |
| OPS-04 | Phase 5 | Pending |

**Coverage:**

- v1 requirements: 28 total
- Mapped to phases: 28 ✓
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-28*
*Last updated: 2026-07-28 after initialization*
