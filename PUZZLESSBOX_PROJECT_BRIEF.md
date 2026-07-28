# Project Brief: Puzzlessbox

Stand: Ende Juli 2026 · Format: GSD-Project-Brief (Input für `/gsd-new-project` in Cursor)

---

## 1. Vision

Puzzlessbox ist der moderne Nachfolger des klassischen Handheld-Sprachrekorders: Man schickt seinem Hermes Agent eine Sprach- oder Textnachricht — eine Notiz, einen Termin, eine Projektidee, einen Link — Hermes verarbeitet sie, schickt eine sauber formatierte Rückfrage mit Änderungsoption, und wenn nach 30 Sekunden keine Reaktion kommt, wird der Eintrag automatisch gespeichert und erscheint kategorisiert in der Puzzlessbox-WebApp.

Kernprinzip: **Erfassen ohne Reibung, Ordnung im Hintergrund.** Der Nutzer denkt laut, Puzzlessbox sortiert.

### Primäre Use Cases

1. **Capture-Flow**: Sprach-/Textnachricht an Hermes → strukturierte Verarbeitung → formatierte Bestätigung mit Edit-Option → Auto-Save nach 30s Inaktivität → Anzeige in der WebApp.
2. **Link-Ablage**: Link zu Produkt/Artikel/Video/Sonstigem an Hermes → automatische Kategorisierung → Ablage mit Metadaten (Titel, Vorschaubild, Beschreibung).
3. **Task- & Kalenderverwaltung**: Termine und Aufgaben werden aus Nachrichten extrahiert, angelegt und verwaltbar (perspektivisch mit externem Kalender synchronisierbar).
4. **Kategorien-Board**: Vordefinierte und frei erstellbare Kategorien, Einträge per Drag & Drop verschiebbar.
5. **Einheitliches Markenerlebnis**: Die WebApp folgt einem durchgängigen Designkonzept (eigenes Brandkit — Logo, Farbpalette, Typografie, Icon-/Illustrationsstil), nicht nur einer Funktions-UI. Assets (Logo-Varianten, Grafiken, Icons) werden mit der Higgsfield CLI generiert.

### Nicht-Ziele (v1)

- Keine Multi-User-/Team-**Funktion** in der UI (Single-User-Nutzung für den Betreiber) — das Datenmodell wird aber von Anfang an tenant-fähig angelegt (siehe Abschnitt 3), damit ein späterer Ausbau kein Rewrite erfordert.
- Keine native Mobile App — WebApp ist responsive, aber kein App-Store-Release.
- Keine eigene STT/TTS-Pipeline — Hermes' eingebautes Voice Mode (lokal Whisper / Groq / OpenAI) wird wiederverwendet, nicht dupliziert.

### Zukunftsrichtung: privat → öffentlich/SaaS (offen, aber vorbereitet)

Puzzlessbox startet als reines Privatprojekt (Repo privat, ein Nutzer), aber ein späteres öffentliches GitHub-Repo und/oder ein SaaS-Abomodell sind ausdrücklich nicht ausgeschlossen — die Richtung ist noch offen. Zwei Konsequenzen werden deshalb **jetzt schon** mitgedacht, weil sie später teuer nachzurüsten wären, aktuell aber fast keinen Mehraufwand bedeuten:

- **Datenmodell tenant-fähig von Anfang an** (Abschnitt 3) — laut aktueller Best-Practice-Literatur zu SaaS-Architektur ist das Nachrüsten von Multi-Tenancy in ein bestehendes Schema ein aufwändiger Umbau, während eine von Beginn an mitgeführte (zunächst immer gleiche) Owner-Spalte praktisch kostenlos ist.
- **Lizenzmodell jetzt festlegen** (Abschnitt 9) — solange du alleiniger Autor bist, lässt sich ein Dual-Lizenz-Modell (AGPL-3.0 für die Community-Nutzung, kommerzielle Lizenz für SaaS-Anbieter/Firmen) sauber aufsetzen. Das ist exakt das Modell, das z. B. Sentry, Plausible, Cal.com und auch die Andoriña-WhatsApp-Bridge aus der Hermes-Recherche fahren — es verhindert, dass jemand den Code 1:1 als Konkurrenz-SaaS betreibt, ohne den Code selbst geschlossen zu halten. Bei mehreren späteren Contributors wird das ohne Copyright Assignment/CLA komplizierter — daher lieber jetzt entscheiden.

Das MCP-Architektur-Muster passt übrigens bereits zu einem möglichen SaaS-Szenario: In der aktuellen Multi-Tenant-MCP-Literatur ist "ein personalisiertes Bearer-Token pro Kunde, das serverseitig einem Tenant zugeordnet wird, während jeder Kunde seinen eigenen Agenten betreibt" ein etabliertes Muster — genau das, was Puzzlessbox mit dem Hermes-MCP-Token schon tut. Ein SaaS-Ausbau würde also eher die Backend-/WebApp-Seite betreffen (Tenant-Isolation, Billing, Rate-Limiting), nicht Hermes selbst.

---

## 2. Architektur-Überblick

```
┌─────────────────────────┐        ┌──────────────────────────────────┐
│  Hermes Agent            │        │  Puzzlessbox-Stack (Coolify)      │
│  (separater Ubuntu-24-VPS)│        │                                    │
│                          │        │  ┌────────────┐   ┌─────────────┐ │
│  Messaging-Gateway       │        │  │ WebApp      │   │ Backend-API │ │
│  (Telegram/WhatsApp/...) │        │  │ Next.js 16  │──▶│ FastAPI     │ │
│  Voice Mode (STT/TTS)    │        │  └────────────┘   └──────┬──────┘ │
│  Plugin: puzzlessbox-    │        │                          │        │
│  bridge (Cron, Timeout-  │───────▶│  ┌────────────────┐      │        │
│  Logik, pre_llm_call)    │  MCP   │  │ MCP-Server      │◀────┘        │
│  MCP-Client              │  (HTTP)│  │ (FastMCP, Auth) │              │
└─────────────────────────┘        │  └────────┬───────┘              │
                                    │           │                      │
                                    │  ┌────────▼───────┐              │
                                    │  │ PostgreSQL 18.4 │              │
                                    │  └────────────────┘              │
                                    └──────────────────────────────────┘
```

**Warum getrennt von Hermes:** Hermes läuft bewusst auf einem eigenen V-Server und wird nicht angetastet. Die Verbindung erfolgt ausschließlich über einen öffentlich erreichbaren, authentifizierten MCP-Server (Streamable HTTP, kein stdio) sowie ein leichtgewichtiges Hermes-Plugin auf der Hermes-Seite, das die Bestätigungs-/Timeout-Orchestrierung übernimmt (dafür sind MCP-Tools allein nicht geeignet, da sie kein „warten und dann selbstständig pushen" können — das braucht Hermes' Cron-/Hook-System).

### Komponenten

| Komponente | Zweck | Ort |
|---|---|---|
| **puzzlessbox-api** | REST-API, Datenmodell, Business-Logik (Items, Kategorien, Status) | Coolify |
| **puzzlessbox-mcp** | MCP-Server (Tools: `create_item`, `list_categories`, `create_category`, `move_item`, `confirm_item`, `update_item`) | Coolify, gleicher Stack wie API |
| **puzzlessbox-webapp** | Kategorien-Board, Drag & Drop, Item-Detailansicht | Coolify |
| **puzzlessbox-db** | PostgreSQL 18.4 | Coolify (Managed DB) |
| **hermes-plugin-puzzlessbox** | Bestätigungs-Flow, 30s-Timeout, Kategorisierungs-Vorschlag, MCP-Client-Aufrufe | Hermes-Server (separat) |

---

## 3. Datenmodell (Entwurf, wird in Phase 1 verfeinert)

**Tenant-Vorbereitung:** Jede Kerntabelle bekommt von Anfang an eine `owner_id`-Spalte (Foreign Key auf eine minimale `Owner`/`User`-Tabelle mit vorerst genau einer Zeile — dir). Alle Queries filtern von Tag 1 an nach `owner_id`, auch wenn es aktuell nur einen Wert gibt. Das ist der einzige Mehraufwand für die spätere SaaS-Option — der Rest (Auth-System, Billing, Rate-Limiting pro Tenant) bleibt bewusst außerhalb von v1.

- **Owner**: `id`, `email`, `created_at` — minimal, keine Rollen/Billing-Logik in v1.
- **Item**: `id`, `owner_id`, `type` (note | task | calendar_event | link), `title`, `content`, `category_id`, `status` (pending_confirmation | confirmed | auto_saved), `source` (telegram | whatsapp | web | ...), `metadata` (JSONB — z. B. Link-Vorschau, Termin-Datum), `created_at`, `confirmed_at`
- **Category**: `id`, `owner_id`, `name`, `icon`, `color`, `is_default` (bool), `position` (für Board-Reihenfolge)
- **ConfirmationWindow**: verknüpft mit Item, hält `expires_at` für die 30s-Logik (wird primär serverseitig/Hermes-seitig gesteuert, in der DB nur als Audit-Trail)

---

## 4. Tech-Stack (gepinnt, Stand Ende Juli/Anfang August 2026)

| Bereich | Wahl | Version |
|---|---|---|
| Laufzeit (Backend) | Python | 3.14.6 |
| Backend-Framework | FastAPI | aktuelle 0.13x-Linie (exakt bei Implementierung pinnen) |
| MCP-Server-Framework | FastMCP (Python) | 3.4.4 (stabil — **nicht** 4.0.0-alpha) |
| Datenbank | PostgreSQL | 18.4 |
| Frontend-Framework | Next.js | 16.2.7 (React 19.2, Turbopack) |
| Laufzeit (Frontend-Tooling) | Node.js | 24 LTS (nicht 26 — das ist bis Okt. 2026 nur „Current") |
| Agent-Plattform | Hermes Agent | v0.19.0 „Quicksilver" (ggf. vorher `hermes update`) |
| Hosting/PaaS | Coolify | v4.1.2 |
| Spec-Driven-Dev-Framework | GSD (open-gsd/gsd-core) | aktuell installierte Version |

---

## 5. Coolify-Hosting & Automatisierung

Die gesamte Puzzlessbox-Infrastruktur (API, MCP-Server, WebApp, Postgres) läuft als ein Docker-Compose-Stack auf der bestehenden Coolify-Instanz (4+ vCPU / 16+ GB RAM). Hermes bleibt ausdrücklich außen vor.

**Automatisierung läuft dreigleisig — Erstellung, CI/CD-Build und operativer Alltag sind bewusst getrennt:**

- **coolify-mcp** ([StuMason/coolify-mcp](https://github.com/StuMason/coolify-mcp), 42 Tools) übernimmt die *einmalige Erstellung* der Infrastruktur direkt aus Cursor heraus: Projekt „Puzzlessbox" anlegen, Environments (z. B. `production`, optional `staging`), PostgreSQL-Datenbank (`database` mit `action: create, type: postgresql`), Env-Vars setzen (`env_vars`), sowie laufende Diagnose (`diagnose_app`, `find_issues`). Das schließt die Lücke der reinen CLI, die keine `project create`/`app create`-Befehle kennt.
  - **Wichtig für die drei Puzzlessbox-Apps** (API, MCP-Server, WebApp): Sie werden **nicht** als Git-basierte Nixpacks-/Dockerfile-Builds angelegt (`action: create_github`), sondern als **Docker-Image-Deployments** (`action: create_dockerimage`, Image z. B. `ghcr.io/<user>/puzzlessbox-api:latest`) — denn das Bauen übernimmt GitHub Actions, nicht Coolify selbst. Das ist Coolifys offiziell empfohlenes Muster, wenn der Build extern (GitHub Actions) statt auf dem Coolify-Server passiert.
- **GitHub Actions** übernimmt den *Build*: Push auf `main` (bzw. Merge eines GSD-Phasen-Branches) triggert einen Workflow pro Service, der das jeweilige Docker-Image baut und nach GHCR (`ghcr.io`) pusht — mit `GITHUB_TOKEN` (automatisch vorhanden, kein eigenes Secret nötig), danach per `curl` den Coolify-**Deploy-Webhook** der jeweiligen App aufruft (Secrets: `COOLIFY_TOKEN`, `COOLIFY_WEBHOOK_API`, `COOLIFY_WEBHOOK_MCP`, `COOLIFY_WEBHOOK_WEBAPP`). Coolify zieht dann automatisch das frisch gepushte Image. Das entlastet zusätzlich den Coolify-Server selbst vom Build (kein CPU-Peak während Deploys — offizieller Coolify-Tipp gegen Server-Überlastung bei Builds).
  - GitHub-CLI (`gh`, bereits installiert) wird genutzt, um die nötigen Repo-Secrets zu setzen (`gh secret set COOLIFY_TOKEN`, etc.) sowie — passend dazu — nutzt GSDs eigener `/gsd-ship`-Befehl intern ebenfalls `gh`, um Phasen-Branches als Pull Request gegen `main` zu öffnen. Dieselbe CLI bedient also sowohl den GSD-Phasenfluss als auch das CI/CD-Secret-Management.
- **coolify-cli** übernimmt den *operativen Alltag außerhalb des CI-Flows*: `coolify app logs`/`coolify app restart` für Debugging, `coolify app env sync --file .env` zum Synchronisieren von Umgebungsvariablen, manuelle Force-Deploys (`coolify deploy name <app> --force`) falls der Webhook-Weg mal umgangen werden muss.

**Sicherheitsaspekt:** Da der MCP-Server öffentlich über HTTPS erreichbar sein muss (Hermes verbindet sich remote), wird er zwingend hinter Coolifys Traefik-Reverse-Proxy mit eigenem Auth-Token/Bearer-Header betrieben — kein offener Endpunkt. Gleiches gilt für die Backend-API, falls sie zusätzliche Endpunkte für die WebApp exponiert. Die Coolify-Deploy-Webhooks selbst sind bereits token-geschützt (Bearer-Auth beim Aufruf).

**Image-Tagging-Strategie:** Jeder GitHub-Actions-Build pusht **zwei Tags** pro Image — `:latest` (für den Standard-Deploy-Webhook) und `:sha-<kurze-git-sha>` (unveränderlich, für Nachvollziehbarkeit und echtes Rollback). Coolify unterstützt Tag-Overrides beim Deploy (`--docker-tag` in coolify-cli bzw. per API/coolify-mcp), sodass sich bei Bedarf gezielt auf eine bestimmte SHA zurückrollen lässt, statt nur "der letzte Stand vor dem kaputten Deploy" zu sein.

**Deployment-Reihenfolge (grob):** Postgres zuerst (coolify-mcp `database create`) → Backend-API (coolify-mcp `application create_dockerimage`, Platzhalter-Image bis der erste GH-Actions-Build existiert, env vars für DB-Connection) → MCP-Server (eigene App, `create_dockerimage`, env vars für API-Anbindung + Auth-Token) → WebApp (eigene App, `create_dockerimage`, env var für API-Basis-URL) → Domains/HTTPS über Coolify automatisch (Let's Encrypt) → GitHub-Actions-Workflows + Repo-Secrets einrichten → erster Push löst echten Build+Deploy aus.

---

## 6. Design & Branding

Puzzlessbox bekommt ein eigenständiges, einheitliches Markenauftreten statt einer reinen Funktions-UI — Brandkit und Designsystem sind fester Projektbestandteil, nicht Nebensache.

- **Brandkit-Umfang**: Logo (Wortmarke + Icon/Symbolmarke + Kombinationsmarke), Farbpalette, Typografie-Paar, Icon-/Illustrationsstil, Tonalität (kurz beschrieben, kein vollständiges Styleguide-Dokument nötig).
- **Design-Entscheidungen** (Farben, Typografie, "verspielt vs. clean", Logo-Richtung) werden **nicht** in diesem Brief vorweggenommen, sondern interaktiv in der `/gsd-discuss-phase` der Branding-Phase geklärt — das ist der richtige Ort für kreative Entscheidungen im GSD-Loop.
- **Asset-Erstellung via Higgsfield CLI**: Logo-Generierung (Higgsfield AI Logo Generator, mehrere Varianten + Export als SVG/PNG), weitere Grafiken/Icons über die reguläre Higgsfield-Bildgenerierung, sowie der `higgsfield-brand-visual-kit`-Skill, der Logo/Farben/Voice über mehrere Sessions hinweg konsistent hält — wichtig, damit spätere Asset-Generierungen (z. B. zusätzliche Icons in Phase 4) nicht vom Look der ersten Charge abweichen.
- **Output der Phase**: fertige Asset-Bibliothek (Logo-Dateien, Favicon, Social-Preview-Bild, Farbwerte als Design-Tokens z. B. CSS-Variablen/Tailwind-Theme) — direkt verwendbar in der Next.js-WebApp (Phase 4/5) ohne Nacharbeit.
- **Anschluss an GSDs UI-Design-Contract**: GSD hat einen eigenen Workflow dafür — `/gsd-ui-phase 4` erzeugt vor dem Planen von Phase 4 eine `UI-SPEC.md` (Layout, Typografie, Farben, Spacing, Copy, Registry-Safety als 6 geprüfte Dimensionen) und bietet bei Next.js/React-Projekten automatisch die shadcn-Initialisierung an. Die Design-Tokens aus dieser Branding-Phase (0) sind der Input, den `/gsd-ui-phase` abfragt — dadurch entsteht kein zweiter, widersprüchlicher Design-Entscheidungsprozess. Nach der Umsetzung prüft `/gsd-ui-review 4` das Ergebnis visuell gegen den Contract.

---

## 7. Integration mit Hermes Agent

- **MCP-Anbindung**: `hermes mcp add puzzlessbox --url https://mcp.puzzlessbox.<domain> --headers "Authorization: Bearer ***"`, danach `tools.include` auf die tatsächlich benötigten Tools beschränken (Least-Privilege, analog zum offiziellen Hermes-Pattern für sensible Systeme).
- **Hermes-Plugin** (`~/.hermes/plugins/puzzlessbox-bridge/`): registriert Tools/Hooks für die Bestätigungs-Logik — `pre_llm_call` für Kategorisierungs-Kontext, Cron/Timer für die 30-Sekunden-Regel, `dispatch_tool` zum Aufruf des Puzzlessbox-MCP-Servers nach Ablauf des Timeouts.
- **Voice Mode**: nutzt Hermes' eingebaute STT/TTS (empfohlen: lokal Whisper für STT + Edge TTS für Antworten, wie im offiziellen Hermes-Setup-Guide empfohlen) — keine eigene Transkriptions-Pipeline in Puzzlessbox.
- **Messaging-Gateway**: Telegram/WhatsApp/Discord/etc. laufen weiterhin über Hermes' bestehende 18+-Plattform-Anbindung — Puzzlessbox selbst hat keine eigene Messaging-Integration.

---

## 8. Sicherheit & Betrieb

**MCP-Server-Authentifizierung:** Aktuelle Best Practice (Stand 2026) für produktive Remote-MCP-Server ist eigentlich OAuth 2.1 mit externem Identity-Provider statt eigenem Token-Handling. Für Puzzlessbox ist das bewusst überdimensioniert — es gibt genau einen Client (Hermes), keine mehreren Nutzer/Scopes. Entscheidung: **statisches Bearer-Token** (rotierbar, in Coolify als Secret verwaltet) **plus** IP-Allowlist auf dem Reverse-Proxy für die bekannte IP des Hermes-V-Servers. Das deckt den tatsächlichen Bedrohungsvektor ab, ohne einen kompletten OAuth-Server für einen Single-Client-Anwendungsfall zu bauen. Token-Rotation (manuell, z. B. alle paar Monate) sollte trotzdem eingeplant sein.

**Datenbank-Backups:** Die Postgres-DB enthält die eigentlichen Nutzdaten (Notizen, Termine, Tasks) ohne Zweitsystem — Datenverlust wäre nicht wiederherstellbar. Coolify hat eingebaute Backup-Schedules (über coolify-mcp: `database_backups` mit `action: create`, `--frequency` als Cron-Ausdruck, lokale und/oder S3-Retention). Wird in Phase 5 eingerichtet, nicht erst "wenn Zeit ist".

**Health Checks:** Jede der drei Apps (API, MCP-Server, WebApp) bekommt in Coolify einen aktiven Health-Check (`--health-check-enabled`, `--health-check-path`, z. B. `/health`-Endpunkt pro Service). Ohne das routet Traefik im Zweifel auch auf einen abgestürzten Container weiter — leicht zu vergessen, aber Teil der Standard-Deployment-Konfiguration in Phase 5, nicht nachträglich.

**Monitoring/Error-Tracking (optional):** Coolify selbst zeigt nur Server-Ressourcen (CPU/RAM/Disk), aber kein Application-Error-Tracking. Da die Coolify-Instanz genug Ressourcenpuffer hat, ist [GlitchTip](https://glitchtip.com) (leichtgewichtige, self-hostbare, Sentry-SDK-kompatible Alternative) eine günstige Ergänzung, um Fehler aus API/MCP-Server/WebApp zentral statt nur in Logs zu sehen — kein Muss für v1, aber eine naheliegende spätere Ergänzung ohne Architekturänderung.

---

## 9. Repo- & GSD-Setup (Voraussetzung vor Phase 0)

GSD geht von einem bereits existierenden (auch leeren) Git-Repo aus — es legt kein GitHub-Repo an und entscheidet nicht über `.gitignore`. Das passiert einmalig **vor** `/gsd-new-project`:

**Sichtbarkeit & Lizenz:** Repo wird als **privat** angelegt (`gh repo create puzzlessbox --private`). Lizenz wird trotzdem von Anfang an gesetzt: **AGPL-3.0** als `LICENSE`-Datei im Root, mit einem kurzen Hinweis in der README, dass eine kommerzielle Lizenz für SaaS-/Firmennutzung separat verfügbar ist (Dual-Licensing-Modell, analog zu Sentry/Plausible/Cal.com und der Andoriña-WhatsApp-Bridge). Das kostet jetzt nichts, verhindert aber später eine rechtliche Nacharbeit, falls das Repo doch öffentlich wird — die Sichtbarkeit (privat/öffentlich) lässt sich jederzeit ohne Aufwand ändern, die Lizenz nachträglich zu ändern wäre bei mehreren Contributors schwierig (aktuell kein Problem, da alleiniger Autor).

**Repo-Struktur:** Monorepo `puzzlessbox` mit den Ordnern `api/` (FastAPI), `mcp-server/` (FastMCP), `webapp/` (Next.js), `hermes-plugin/` (separat gepflegt, da es physisch auf dem Hermes-Server liegt), `.planning/` (GSD-Zustand, siehe unten). Ein `.planning/`-Ordner pro Repo — bei GSD ist das Standard; mehrere Repos/Worktrees liefen nur über GSDs Workstream-/Workspace-Feature, das wir hier nicht brauchen.

**`.gitignore` (Kernpunkte):**
- Python: `__pycache__/`, `*.pyc`, `.venv/`, `.env`
- Node/Next.js: `node_modules/`, `.next/`, `.env.local`
- Docker/Build: `*.log`, `dist/`, `.DS_Store`
- Secrets grundsätzlich nie committen (`.env*` außer `.env.example`)
- `.planning/ui-reviews/` (Screenshots aus `/gsd-ui-review`, GSD ignoriert das selbst standardmäßig)
- `.planning/` selbst **nicht** ignorieren — siehe `commit_docs` unten (bei einem Solo-Projekt ohne sensible Inhalte spricht nichts dagegen, die Planungs-Historie mit zu versionieren, das dokumentiert später auch Entscheidungen nachvollziehbar in der Git-Historie)

**GSD-Konfiguration (`.planning/config.json`, wird bei `/gsd-new-project` erfragt — hier schon vorentschieden, damit GSD nicht raten muss):**

| Setting | Empfehlung | Begründung |
|---|---|---|
| `git.branching_strategy` | `phase` | Ein Branch pro Phase (`gsd/phase-00-branding`, `gsd/phase-01-backend-api`, …) — passt exakt auf unseren Phasenplan, macht jede Phase als eigener PR gegen `main` review- und revertierbar. |
| `workflow.use_worktrees` | `true` | Erlaubt parallele Ausführung unabhängiger Plan-Wellen ohne Build-Lock-Konflikte (relevant, da Backend/MCP/WebApp teils unabhängig entwickelt werden können). |
| `commit_docs` | `true` | `.planning/` wird mitversioniert (kein sensibles Projekt, Nachvollziehbarkeit gewünscht). |
| `mode` | `interactive` zu Beginn, später ggf. `yolo` für Routine-Phasen | Erst Vertrauen in die Ergebnisse aufbauen, danach beschleunigen. |
| `model_profile` | `balanced` | Guter Kompromiss aus Qualität/Kosten für ein Solo-Projekt dieser Größe. |

**Ablaufreihenfolge:**
1. GitHub-Repo `puzzlessbox` **privat** anlegen (`gh repo create puzzlessbox --private --clone`).
2. `.gitignore` + `LICENSE` (AGPL-3.0) + kurzer Lizenz-Hinweis in README gemäß oben committen (erster Commit).
3. `npx @opengsd/gsd-core@latest` im Repo-Root ausführen (Cursor als Ziel-Runtime wählen).
4. In Cursor: `/gsd-new-project`, dieses Brief als Grundlage einspeisen, Konfiguration gemäß Tabelle oben bestätigen.
5. Ab da normaler GSD-Loop pro Phase (siehe Abschnitt 10).

---

## 10. Phasenplan (GSD-Loop)

Wird von GSD nach `/gsd-new-project` im Detail in `ROADMAP.md` abgebildet, grobe Erwartung:

0. **Phase 0 — Branding & Design System** (Higgsfield CLI: Logo, Farbpalette, Typografie, Asset-Bibliothek als Design-Tokens) — bewusst **vor** der WebApp-Phase, damit Phase 4 nicht zweimal gebaut wird.
1. **Phase 1 — Datenmodell & Backend-API** (FastAPI, Postgres, CRUD für Items/Kategorien)
2. **Phase 2 — MCP-Server** (FastMCP-Layer über der API, Bearer-Auth + IP-Allowlist, Tool-Schemas)
3. **Phase 3 — Hermes-Plugin** (Bestätigungs-Flow, Timeout-Logik, Kategorisierung) — **vor** `/gsd-plan-phase 3` empfiehlt sich `/gsd-spike "Hermes Cron/dispatch_tool Timing für 30s-Bestätigungs-Flow"`: Das ist der technisch unsicherste Teil des gesamten Projekts (kein bekanntes Referenzbeispiel für genau dieses Cross-Server-Timeout-Muster), ein VALIDATED/INVALIDATED-Ergebnis vorab verhindert eine Phase, die auf einer falschen Annahme über Hermes' Timing-Zuverlässigkeit aufbaut.
4. **Phase 4 — WebApp** (`/gsd-ui-phase 4` für UI-SPEC.md auf Basis der Design-Tokens aus Phase 0, Kategorien-Board, Drag & Drop, Item-Ansichten, `/gsd-ui-review 4` nach Umsetzung)
5. **Phase 5 — Coolify-Deployment, CI/CD & Härtung** (Infrastruktur via coolify-mcp anlegen als Docker-Image-Apps, GitHub-Actions-Workflows pro Service für Build→GHCR (`:latest` + `:sha-<sha>`)→Coolify-Webhook-Deploy, Repo-Secrets via `gh`, DB-Backup-Schedule, Auth/Reverse-Proxy, Monitoring)

Jede Phase folgt intern dem GSD-Loop: `/gsd-discuss-phase` → `/gsd-plan-phase` → `/gsd-execute-phase` → `/gsd-verify-work` → `/gsd-ship`. GSDs eingebaute Nyquist-Validierung ordnet dabei automatisch jedem Requirement einen Test/Verify-Befehl zu, bevor Code geschrieben wird — keine gesonderte Konfiguration nötig, außer man will sie für schnelle Prototyping-Phasen bewusst abschalten (`workflow.nyquist_validation: false`).

---

## 11. Offene Annahmen (zur Bestätigung während `/gsd-new-project`)

- Auth für die WebApp selbst (Single-User — reicht ein einfacher Login/Token, oder soll das ganz entfallen und nur über Netzwerk-Restriktion abgesichert werden?)
- Ob Kalender/Tasks in v1 nur intern in der Puzzlessbox-DB geführt werden oder direkt mit einem externen Kalender (Google/CalDAV) synchronisiert werden sollen.
- Exakte FastAPI-Version zum Implementierungszeitpunkt (Release-Cadence ist hoch — kurz vor Phase 1 nochmal aktuellsten stabilen Stand prüfen).
- Domain-/Subdomain-Struktur für die drei Coolify-Apps (z. B. `app.puzzlessbox.<domain>`, `api.puzzlessbox.<domain>`, `mcp.puzzlessbox.<domain>`).
- Grober Stil-Anker fürs Branding (z. B. "minimalistisch/clean" vs. "verspielt/warm") — hilfreich als Startpunkt für die Discuss-Phase in Phase 0, muss aber nicht jetzt schon final sein.
- Bestätigung der Empfehlungen aus Abschnitt 9 (branching_strategy: `phase`, commit_docs: `true`, use_worktrees: `true`) — sind als Vorschlag gedacht, keine Festlegung.
- Backup-Retention-Präferenz für die Postgres-DB (nur lokal auf dem Coolify-Server, oder zusätzlich S3-Ziel? Wie viele Tage/Versionen vorhalten?).
- Bestätigung der MCP-Auth-Entscheidung aus Abschnitt 8 (statisches Bearer-Token + IP-Allowlist) — Alternative wäre vollwertiges OAuth 2.1, aber für einen Single-Client-Fall (nur Hermes) vermutlich unnötiger Aufwand.
- **Geklärt:** Tenant-Vorbereitung im Datenmodell (Abschnitt 3, `owner_id` von Anfang an) und Repo-Strategie (Abschnitt 9, privat + AGPL-3.0/Commercial-Dual-Lizenz) sind entschieden — keine offenen Punkte mehr, nur zur Erinnerung hier gelistet.
- Falls der Public-/SaaS-Schritt konkret wird: Terms of Service, Datenschutzerklärung (Notizen/Termine sind personenbezogene Daten) und ein echtes Auth-/Billing-System sind dann eigene, spätere GSD-Milestones — bewusst **kein** Teil von v1, nur als Hinweis, dass das nicht "nebenbei" passiert.
