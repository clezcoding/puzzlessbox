# Phase 3: Hermes-Plugin & Timeout-Spike - Research

**Researched:** 2026-08-01  
**Domain:** Conversational Agent Plugins, MCP Client Integration, Timeout State Machines  
**Confidence:** HIGH  

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Edit flow (CAP-02)
- **D-01:** After the confirmation card, the next free-text / natural-language message is treated as an edit — no separate „Bearbeiten“ hop. Explicit confirm remains „Eintrag sichern“ / confirm affordance. — **Reversibility:** costly — Hermes plugin dialog state machine
- **D-02:** Hermes LLM maps edit text to draft fields and calls `update_item` with only changed keys. — **Reversibility:** costly — coupling to LLM field extraction
- **D-03:** After a successful edit: silent ACK only — do **not** re-send a full Stash-Check card. Timer reset still happens via API PATCH from `update_item` (Phase 1 D-06). — **Reversibility:** reversible

#### Discard / soft-delete
- **D-04:** Phase 3 adds MCP tool `discard_item(item_id)` that soft-deletes via API (`deleted_at`). German copy „Verworfen“ (Apollo voice). Expands tool surface beyond Phase-2 MCP-01 list. — **Reversibility:** costly — new MCP tool + API path + Hermes action mapping; Spike 004 had deferred delete

#### Post-autosave notify
- **D-05:** Always send a chat ping after status becomes `auto_saved` (e.g. gestasht / lands on board — Apollo voice per `brand/VOICE.md`). — **Reversibility:** reversible
- **D-06:** Detect `auto_saved` by polling item status ~30–35s after create — **no** API→Hermes webhook and **not** using 60s Hermes cron as the deadline driver. — **Reversibility:** costly — poll loop in plugin; webhook later would be a different design

#### Parallel captures
- **D-07:** At most one active pending draft per chat/session. A new capture while a draft is open asks the user: confirm old / discard old / wait. — **Reversibility:** costly — concurrency policy in plugin
- **D-08:** If user confirms after status is already `auto_saved`: idempotent success or friendly ACK („war schon gestasht“) — never punish late confirm. Planner must verify/extend API `confirm` on `auto_saved`. — **Reversibility:** costly — API confirm semantics

#### Type / category suggestion
- **D-09:** On first `create_item`, Hermes LLM chooses `type` + `category` after `list_categories`, with heuristic hints (URL→link, datetime→event/Termin). — **Reversibility:** costly — capture quality depends on this path
- **D-10:** When category confidence is low: fall back to **Inbox** and show Inbox honestly on the card — do not block on a pre-create clarification question. — **Reversibility:** reversible

#### Plugin packaging & config
- **D-11:** Ship plugin as top-level `hermes-plugin/` in the monorepo. Deploy to Hermes VPS via git pull or rsync + Hermes reload — no npm/pip publish, no Coolify app for the plugin. — **Reversibility:** reversible
- **D-12:** First-run interactive setup script collects MCP URL + bearer and writes them to Hermes env/secrets (`MCP_URL`, `MCP_BEARER`). Never commit secrets; never hardcode in plugin source. — **Reversibility:** reversible

#### Carried forward (spikes / prior phases — do not re-litigate)
- API owns 30s `DraftTimeoutManager`; Hermes cron must not drive the deadline (MCP-04 VALIDATED)
- Hermes → MCP HTTPS Bearer only; no direct DB from Hermes VPS (MCP-03)
- Confirmation formatter: German plain-text CAP-02 template from spike 004 / `format_confirmation` — port into `hermes-plugin/`; channel-specific buttons only in adapter layer
- Primary CTA: „Eintrag sichern“ (`brand/VOICE.md`); tool schemas stay English (Phase 2 D-14)
- Phase 2 tool/client contracts D-09…D-19 remain unless this phase’s `discard_item` / confirm-on-`auto_saved` explicitly extends them

### Claude's Discretion
- Exact German microcopy strings for silent edit ACK, autosave ping, discard, and dual-draft prompt (must follow `brand/VOICE.md`)
- Poll implementation details (sleep vs Hermes timer helper; one-shot vs short retry)
- Exact API route/shape for soft-delete if not already exposed; MCP error `code` mapping for discard
- Setup-script UX (prompts, validation, where Hermes stores env)
- Whether confirm buttons map per-channel inside Hermes adapters vs text-only v1

### Deferred Ideas (OUT OF SCOPE)
- API→Hermes webhook for autosave notify (rejected for v1 — poll instead)
- Parallel multi-draft queue in one chat (rejected — single active draft)
- Publishing hermes-plugin as npm/pip package or Coolify app (rejected — monorepo + rsync/pull)
- Live Hermes VPS E2E confirm still recommended as validation during execute (spike 002 PARTIAL) — not a separate product feature
- WebApp board surfacing of discarded/auto_saved items — Phase 4
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CAP-02 | User sieht formatierte Bestätigung mit Edit-Option vor dem Speichern | Spike 004 validiert plain-text Template; D-01/D-02/D-03 definieren den konversationellen Edit-Flow ohne extra Zwischenschritt. |
| CAP-04 | Capture funktioniert über alle Messaging-Kanäle, die Hermes bereits unterstützt | Spike 004 beweist, dass kanallose Plain-Text-Payloads auf Telegram/WhatsApp/Discord gleichermaßen funktionieren. |
| MCP-03 | Hermes-Plugin orchestriert Bestätigungs-Flow und ruft MCP-Tools auf | Spike 002 zeigt den korrekten Ablauf (`create_item` → optional `update_item` → `confirm_item` / `discard_item`) über HTTPS-MCP-Client-Aufrufe. |
| MCP-04 | Vor Plan/Execute der Plugin-Phase existiert Spike zu Hermes Timing/Hooks | Spike 001 beweist, dass der 30s-Timeout ausschließlich API-seitig (`DraftTimeoutManager`) laufen muss, da Hermes-Cron (60s) zu ungenau ist. |
</phase_requirements>

## Summary

Diese Forschungsphase befasst sich mit der Implementierung des Hermes-Plugins (`hermes-plugin/`) und der Integration mit der API-seitigen Timeout-State-Machine. Die Ergebnisse der Spikes 001 bis 004 haben kritische Entwurfsentscheidungen validiert und präzisiert. Insbesondere wurde festgestellt, dass eine zeitliche Steuerung über den Hermes-Cron-Dienst (60-Sekunden-Taktung) für den präzisen 30-Sekunden-Auto-Save-Timeout ungeeignet ist [CITED: .planning/spikes/001-hermes-cron-vs-api-timer/README.md]. Daher bleibt die API-seitige `DraftTimeoutManager`-Klasse die einzige Autorität für den Timeout-Übergang von `draft` zu `auto_saved`.

Das Hermes-Plugin wird als eigenständiges Verzeichnis im Monorepo entwickelt und per Git-Pull/Rsync auf dem externen Hermes-VPS bereitgestellt [CITED: .planning/phases/03-hermes-plugin-timeout-spike/03-CONTEXT.md]. Es agiert als reiner MCP-Client, der über HTTPS und ein statisches Bearer-Token mit der Produktions-MCP-Schnittstelle kommuniziert [CITED: .planning/spikes/003-remote-mcp-vps/README.md]. Das Plugin orchestriert den gesamten Bestätigungs-Flow, verarbeitet konventionelle Text-Edits direkt per LLM-Mapping und implementiert einen Polling-Mechanismus, um den Benutzer nach einem erfolgreichen Auto-Save per Chat-Ping zu benachrichtigen [CITED: .planning/phases/03-hermes-plugin-timeout-spike/03-CONTEXT.md].

**Primary recommendation:** Implementiere das Hermes-Plugin als leichtgewichtigen, zustandsgesteuerten Python-Dienst, der ausschließlich MCP-Tools aufruft, den 30s-Timeout der API überlagert, indem er nach 30-35s den Status pollt, und konversationelle Edits direkt per LLM-Mapping an `update_item` weiterreicht.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| **Draft-Erstellung & Timer-Start** | API / Backend | Browser / Client | Die API (`DraftTimeoutManager`) startet bei `POST /drafts` einen atomaren 30s-Asyncio-Task. Hermes stößt dies über das MCP-Tool `create_item` an. |
| **Bestätigungs-UX (CAP-02)** | Frontend Server (Hermes VPS) | — | Hermes formatiert das Plain-Text-Template (Stash-Check) und sendet es an den jeweiligen Messaging-Kanal. |
| **Konversationelles Editieren** | Frontend Server (Hermes VPS) | API / Backend | Hermes LLM extrahiert geänderte Felder aus der Freitext-Antwort des Users und ruft `update_item` auf; die API aktualisiert die DB und setzt den Timer zurück. |
| **Auto-Save-Zustandsübergang** | API / Backend | Database / Storage | Nach Ablauf von 30s Inaktivität ändert der API-Timer den Status in der DB atomar von `draft` zu `auto_saved`. |
| **Post-Autosave-Benachrichtigung** | Frontend Server (Hermes VPS) | API / Backend | Das Hermes-Plugin pollt nach 30-35s den Status des Items über MCP und sendet bei `auto_saved` einen Chat-Ping. |
| **Soft-Delete (discard_item)** | API / Backend | Database / Storage | Die API setzt `deleted_at = NOW()` auf dem Item; das MCP-Tool `discard_item` macht diese Funktionalität für Hermes zugänglich. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.14.6 | Laufzeitumgebung für das Hermes-Plugin | Projektheuristik und lokale Systemverfügbarkeit [VERIFIED: local env]. |
| FastAPI | 0.136.1 | Web-Framework für die Backend-API | Phase-1-Standard für performante, asynchrone APIs [CITED: .planning/STATE.md]. |
| FastMCP | 3.4.4 | MCP-Server-Framework | Phase-2-Standard für die Definition und Registrierung von MCP-Tools [CITED: .planning/STATE.md]. |
| Hermes | v0.19.0 | Conversational Agent Platform | Host-Plattform auf dem externen VPS für Messaging-Kanal-Integration [CITED: .planning/phases/03-hermes-plugin-timeout-spike/03-CONTEXT.md]. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| httpx | 0.28.1 | Asynchroner HTTP-Client für MCP- und API-Aufrufe | Für alle ausgehenden HTTP-Anfragen vom Hermes-Plugin zum MCP-Server [VERIFIED: PyPI registry]. |
| pydantic | v2.10.x | Datenvalidierung und Schemata | Für die Definition von Datenstrukturen und Validierung im Plugin [VERIFIED: PyPI registry]. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Polling via Plugin | API Webhooks | Webhooks erfordern eine feste, öffentlich erreichbare IP/URL für den Hermes-VPS und komplexe Listener-Logik; Polling ist robuster und einfacher für v1 [CITED: .planning/phases/03-hermes-plugin-timeout-spike/03-CONTEXT.md]. |
| Hermes Cron | API-Timer | Hermes Cron tickt nur alle 60s und ist für präzise 30s-Timeouts ungeeignet; API-asyncio-Timer bietet subsekunden-genaue Steuerung [CITED: .planning/spikes/001-hermes-cron-vs-api-timer/README.md]. |

**Installation:**
```bash
# Im hermes-plugin/ Verzeichnis auf dem VPS
pip install httpx>=0.28.1 pydantic>=2.10.0 pytest>=8.0.0 pytest-asyncio>=0.23.0
```

**Version verification:**
```bash
pip index versions httpx
```
*httpx 0.28.1 wurde am 2024-12-06 veröffentlicht und erfolgreich lokal verifiziert [VERIFIED: PyPI registry].*

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `httpx` | PyPI | 8 yrs | ~30M/wk | [github.com/encode/httpx](https://github.com/encode/httpx) | [SUS] | Approved (Flagged due to PyPI API download-count limitations, but verified as official library) |
| `pydantic` | PyPI | 7 yrs | ~120M/wk | [github.com/pydantic/pydantic](https://github.com/pydantic/pydantic) | [OK] | Approved |

**Packages removed due to [SLOP] verdict:** none  
**Packages flagged as suspicious [SUS]:** `httpx` (Aufgrund fehlender Download-Zahlen im PyPI-Schnittstellen-Audit als SUS markiert; manuell verifiziert und für die Installation freigegeben).

## Architecture Patterns

### System Architecture Diagram

```
[ User Chat (Telegram/WA/Discord) ]
       │              ▲
       │ (Text/Edit)  │ (Stash-Check / Notify)
       ▼              │
[ Hermes Agent (VPS) ] ────────────────────────┐
       │                                       │
       │ (MCP JSON-RPC over HTTPS)             │ (Poll status ~30s)
       ▼                                       ▼
[ MCP Server (mcp.puzzlesstool.online) ]       │
       │                                       │
       │ (Internal API Calls with Bearer)      │
       ▼                                       │
[ FastAPI Backend (api/app) ] ◄────────────────┘
       │
       ├─► [ DraftTimeoutManager (30s asyncio.sleep) ] ──► (State: auto_saved)
       │
       ▼
[ PostgreSQL Database ]
```

### Recommended Project Structure
```
hermes-plugin/
├── plugin.yaml          # Hermes Plugin-Manifest und Konfiguration
├── __init__.py          # Plugin-Initialisierung und Registrierung
├── config.py            # Lädt MCP_URL und MCP_BEARER aus der Umgebung
├── schemas.py           # Pydantic-Modelle für interne Datenstrukturen
├── tools.py             # Kapselt die Aufrufe der MCP-Tools (create, confirm, update, discard)
├── formatters.py        # Enthält format_confirmation() für CAP-02
└── dialog.py            # Zustandsmaschine für den Capture- und Edit-Flow
```

### Pattern 1: Conversational Edit Flow
Der Benutzer erhält die Bestätigungskarte. Jede darauffolgende Freitext-Nachricht (die nicht dem expliziten Bestätigungs-CTA entspricht) wird als Edit interpretiert. Das Hermes LLM mappt den Freitext auf die geänderten Felder und aktualisiert den Entwurf über `update_item`.

```python
# hermes-plugin/dialog.py
# Source: [ASSUMED] - Standard Hermes Dialog Pattern

async def handle_user_message(session, message_text: str) -> str:
    active_draft = await session.get_state("active_draft")
    if not active_draft:
        # Startet neuen Capture-Flow
        return await start_capture_flow(session, message_text)
        
    if message_text.strip().lower() in ["eintrag sichern", "sichern", "confirm"]:
        # Explizite Bestätigung
        await call_mcp_confirm_item(active_draft["id"])
        await session.clear_state("active_draft")
        return "✅ Eintrag erfolgreich gesichert!"
        
    if message_text.strip().lower() in ["verwerfen", "löschen", "discard"]:
        # Explizites Verwerfen (Soft-Delete)
        await call_mcp_discard_item(active_draft["id"])
        await session.clear_state("active_draft")
        return "🗑️ Eintrag verworfen."

    # Konversationelles Editieren (D-01/D-02)
    updated_fields = await llm_extract_edits(message_text, active_draft)
    if updated_fields:
        await call_mcp_update_item(active_draft["id"], **updated_fields)
        # Zustand aktualisieren
        active_draft.update(updated_fields)
        await session.set_state("active_draft", active_draft)
        # Silent ACK (D-03)
        return "✍️ Änderungen übernommen."
    
    return "Ich habe dich nicht verstanden. Antworte mit „Eintrag sichern“, „Verwerfen“ oder beschreibe deine Änderungen."
```

### Pattern 2: Post-Autosave Polling
Da kein Webhook von der API zu Hermes existiert (D-06), pollt das Plugin nach der Erstellung des Items im Hintergrund, um den Statusübergang zu `auto_saved` zu erkennen und den Benutzer zu benachrichtigen (D-05).

```python
# hermes-plugin/dialog.py
# Source: [ASSUMED] - Background Polling Pattern

async def schedule_autosave_poll(session, draft_id: str, delay_seconds: float = 32.0):
    await asyncio.sleep(delay_seconds)
    # Status über MCP abfragen
    status = await call_mcp_get_item_status(draft_id)
    if status == "auto_saved":
        # Benutzer benachrichtigen (D-05)
        await session.send_message("📦 Automatisch gestasht (lands on board).")
```

### Pattern 3: Single-Active-Draft Concurrency
Es darf maximal ein aktiver Entwurf pro Chat-Sitzung existieren (D-07). Wenn ein neuer Capture-Versuch unternommen wird, während ein Entwurf offen ist, muss eine Klärung erfolgen.

```python
# hermes-plugin/dialog.py
# Source: [ASSUMED] - Concurrency Policy Pattern

async def start_capture_flow(session, text: str) -> str:
    active_draft = await session.get_state("active_draft")
    if active_draft:
        # Konflikt auflösen (D-07)
        await session.set_state("pending_capture_text", text)
        return (
            "⚠️ Du hast noch einen offenen Entwurf.\n"
            "Möchtest du den alten Eintrag sichern oder verwerfen, bevor wir fortfahren?"
        )
    # Normaler Erstellungsprozess
    ...
```

### Anti-Patterns to Avoid
- **Direkter DB-Zugriff vom VPS:** Das Hermes-Plugin darf unter keinen Umständen direkt auf die PostgreSQL-Datenbank zugreifen. Alle Aktionen müssen über die MCP-Schnittstelle laufen (Erfolgskriterium 4).
- **Hermes Cron für Timeouts:** Verwende niemals den Hermes-Scheduler/Cron für die 30-Sekunden-Frist. Dies führt zu ungenauen Timeouts (bis zu 60s Verzögerung) und Race-Conditions [CITED: .planning/spikes/001-hermes-cron-vs-api-timer/README.md].
- **Hartcodierte Secrets:** Keine API-Keys oder Bearer-Tokens im Quellcode oder im Git-Repository hinterlegen. Verwende das interaktive Setup-Skript zur Generierung der `.env`-Datei auf dem VPS [CITED: .planning/phases/03-hermes-plugin-timeout-spike/03-CONTEXT.md].

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| **HTTP-Client-Verbindung** | Eigene Sockets / `urllib` | `httpx.AsyncClient` | Bietet standardmäßig asynchrone Verbindungspools, Timeout-Management und korrekte Header-Verarbeitung [VERIFIED: PyPI registry]. |
| **JSON-RPC MCP-Protokoll** | Manuelle JSON-Parser | `mcp` Python SDK | Das offizielle SDK garantiert die Einhaltung des MCP-Standards und verhindert Parsing-Fehler bei komplexen Tool-Aufrufen [CITED: .planning/spikes/002-mcp-confirm-flow/README.md]. |
| **UUID-Generierung** | Custom-Zufallsgeneratoren | `uuid.uuid4` (Python stdlib) | Garantiert RFC 4122-konforme, kollisionsfreie IDs für Entwürfe und Idempotenz-Schlüssel [VERIFIED: Python stdlib]. |

**Key insight:** Das Erfinden eigener Protokoll-Parser für MCP oder HTTP-Verbindungen erhöht die Fehleranfälligkeit drastisch. Die Verwendung etablierter Bibliotheken wie `httpx` und des offiziellen `mcp` SDKs stellt sicher, dass Verbindungsabbrüche und Protokoll-Grenzfälle korrekt behandelt werden.

## Common Pitfalls

### Pitfall 1: Hermes Cron 60s Resolution
- **What goes wrong:** Der Versuch, den 30-Sekunden-Timeout über den Hermes-Scheduler zu steuern, führt dazu, dass Timeouts erst nach 60 Sekunden oder unregelmäßig ausgelöst werden.
- **Why it happens:** Der native Hermes-Cron-Dienst arbeitet mit einer minimalen Auflösung von 60 Sekunden (1 Minute).
- **How to avoid:** Verwende den API-seitigen `DraftTimeoutManager`, der auf asynchronem `asyncio.sleep(30)` basiert [CITED: .planning/spikes/001-hermes-cron-vs-api-timer/README.md].
- **Warning signs:** Entwürfe verbleiben deutlich länger als 30 Sekunden im Zustand `draft`, obwohl keine Aktivität stattfindet.

### Pitfall 2: Blockieren des Hermes-Hauptthreads
- **What goes wrong:** Synchron ausgeführte HTTP-Aufrufe an den MCP-Server blockieren den gesamten Hermes-Agenten, wodurch andere Chats einfrieren.
- **Why it happens:** Verwendung von synchronen Bibliotheken (`requests`) oder fehlendes `await` bei asynchronen Aufrufen.
- **How to avoid:** Verwende konsequent `httpx.AsyncClient` und asynchrone Funktionsdefinitionen (`async def`) für alle Netzwerkanfragen.
- **Warning signs:** Hohe Latenzzeiten im Chat; Hermes reagiert nicht auf Nachrichten anderer Benutzer, während ein MCP-Aufruf läuft.

### Pitfall 3: Token-Leckage im Git-Repository
- **What goes wrong:** Das statische MCP-Bearer-Token wird versehentlich ins GitHub-Repository gepusht, wodurch unbefugte Dritte Vollzugriff auf die MCP-Tools erhalten.
- **Why it happens:** Hardcodieren des Tokens in `config.py` oder Fehlen von `.env` in `.gitignore`.
- **How to avoid:** Das Token darf nur über Umgebungsvariablen geladen werden. Das interaktive Setup-Skript muss die `.env`-Datei lokal auf dem VPS erstellen, und `.env` muss in `.gitignore` eingetragen sein [CITED: .planning/phases/03-hermes-plugin-timeout-spike/03-CONTEXT.md].
- **Warning signs:** Sicherheitswarnungen von GitHub; unbekannte Zugriffe im API-Log.

## Code Examples

### Formatter für die Bestätigungskarte (CAP-02)
```python
# hermes-plugin/formatters.py
# Source: [CITED: .planning/spikes/004-confirmation-payload/format_confirmation.py]

from typing import TypedDict

TYPE_LABELS = {
    "note": "Notiz",
    "task": "Task",
    "link": "Link",
    "event": "Termin",
}

class DraftPreview(TypedDict):
    title: str
    type: str
    category: str
    summary: str

def format_confirmation(draft: DraftPreview) -> str:
    type_label = TYPE_LABELS.get(draft["type"], draft["type"])
    return "\n".join(
        [
            "📥 Stash-Check — passt das so?",
            "",
            f"Titel: {draft['title']}",
            f"Typ: {type_label}",
            f"Kategorie: {draft['category']}",
            f"Kurz: {draft['summary']}",
            "",
            "Antworte mit „Eintrag sichern“ oder tippe Bearbeiten.",
            "(Auto-Save in 30s wenn du nichts tust — API-Timer, nicht Hermes-Cron.)",
        ]
    )
```

### Soft-Delete MCP-Tool Integration (discard_item)
```python
# mcp-server/app/tools/items.py
# Source: [ASSUMED] - Standard MCP Tool Extension Pattern

from typing import Annotated
from pydantic import Field
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_access_token
from app.api_client import call_api

async def discard_item(
    item_id: Annotated[str, Field(description="Draft UUID to discard/soft-delete")],
) -> dict:
    """Soft-delete a capture draft by setting deleted_at."""
    if _api_client is None:
        raise RuntimeError("MCP tools not registered")
    owner_id = get_access_token().claims["owner_id"]
    
    # Ruft den neuen Soft-Delete-Endpunkt der API auf (D-04)
    return await call_api(
        _api_client,
        "POST",
        f"/drafts/{item_id}/discard",
        owner_id,
    )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hermes-Cron steuert 30s-Timeout | API `DraftTimeoutManager` steuert Timeout | Spike 001 (2026-07-31) | Subsekunden-Präzision, keine Race-Conditions, Entlastung des VPS [CITED: .planning/spikes/001-hermes-cron-vs-api-timer/README.md]. |
| Direkter DB-Zugriff vom VPS | Reine MCP-Tool-Orchestrierung | Phase 3 Context (2026-08-01) | Erhöhte Sicherheit, saubere Schichtentrennung, keine DB-Credentials auf dem VPS [CITED: .planning/phases/03-hermes-plugin-timeout-spike/03-CONTEXT.md]. |
| Manuelle Bestätigung zwingend | Auto-Save bei Inaktivität | Phase 1 (2026-07-31) | Besseres UX, kein Datenverlust bei Verbindungsabbruch im Chat [CITED: .planning/STATE.md]. |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Hermes v0.19.0 unterstützt Python-basierte Plugins über ein Standard-Manifest (`plugin.yaml`) und Tool-Registrierung. | Standard Stack | Gering. Falls Hermes ein anderes Plugin-Format nutzt, muss die Registrierungs-Schnittstelle angepasst werden, das Kern-Python-Skript bleibt jedoch identisch. |
| A2 | Die Produktions-MCP-URL `https://mcp.puzzlesstool.online` ist dauerhaft erreichbar und für den VPS freigeschaltet. | Summary | Hoch. Verbindungsprobleme blockieren den gesamten Capture-Flow. Muss im Live-E2E-Test verifiziert werden. |

## Open Questions

1. **Live E2E Bestätigung auf dem VPS (Spike 002 PARTIAL)** — (RESOLVED)
   - *What we know:* Die Mock-Orchestrierung funktioniert fehlerfrei. Die Verbindung zum Produktions-MCP liefert bei `/health` korrekte Ergebnisse.
   - *What's unclear:* Das vollständige E2E-Szenario mit einer echten `category_id` und Live-Bestätigung über den VPS steht noch aus.
   - *Resolution:* Live-VPS-E2E ist als Manual-Only-Verifikation deklariert — siehe `03-VALIDATION.md` Abschnitt "Manual-Only Verifications" (Live E2E on Hermes VPS with real category_id). Automatisierte Phase-3-Tests decken Mock-Orchestrierung + kanalneutrale Payload ab; der Live-VPS-Check wird während `/gsd-execute-phase` manuell vom Operator durchgeführt (externe VPS-Abhängigkeit, kein CLI/API). Kein Plan-Blocker — alle automatisierten Success-Criteria sind ohne Live-VPS erfüllbar.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Plugin-Laufzeit | ✓ | 3.14.6 | — |
| FastAPI | Backend-API | ✓ | 0.136.1 | — |
| Docker | Containerisierung | ✓ | 29.4.0 | — |
| PostgreSQL | Persistenz | ✓ | 15.x | — |
| pip3 | Paketverwaltung | ✓ | 26.1.2 | — |

**Missing dependencies with no fallback:** none  
**Missing dependencies with fallback:** none  

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (v8.0.0+) |
| Config file | `api/tests/conftest.py`, `mcp-server/tests/conftest.py` |
| Quick run command | `pytest api/tests/unit/ -x` |
| Full suite command | `pytest api/tests/ mcp-server/tests/` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CAP-02 | Formatiertes Plain-Text-Template für Stash-Check wird korrekt erzeugt | unit | `pytest hermes-plugin/tests/test_formatter.py -x` | ❌ Wave 0 (wird erstellt) |
| CAP-04 | Capture-Flow funktioniert kanallos über alle Adapter | integration | `pytest hermes-plugin/tests/test_channels.py -x` | ❌ Wave 0 (wird erstellt) |
| MCP-03 | Plugin ruft ausschließlich MCP-Tools auf und steuert den Fluss | integration | `pytest hermes-plugin/tests/test_orchestration.py -x` | ❌ Wave 0 (wird erstellt) |
| MCP-04 | API-seitiger `DraftTimeoutManager` führt den 30s-Timeout präzise aus | integration | `pytest api/tests/integration/test_capture.py::test_autosave -x` | ✅ Vorhanden |

### Sampling Rate
- **Per task commit:** `pytest api/tests/unit/ -x`
- **Per wave merge:** `pytest api/tests/ mcp-server/tests/`
- **Phase gate:** Alle Tests grün (inklusive der neuen `hermes-plugin/tests/`) vor `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `hermes-plugin/tests/test_formatter.py` — verifiziert CAP-02 Template-Generierung.
- [ ] `hermes-plugin/tests/test_orchestration.py` — verifiziert MCP-Tool-Aufrufketten.
- [ ] `hermes-plugin/tests/test_channels.py` — verifiziert Kanalkompatibilität.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Statische Bearer-Token-Authentifizierung für den Zugriff auf `POST /mcp` [CITED: .planning/phases/02-mcp-server/02-CONTEXT.md]. |
| V4 Access Control | yes | Mandantentrennung über `X-Owner-Id` Header und Validierung der `owner_id` im API-Kontext [CITED: .planning/phases/02-mcp-server/02-CONTEXT.md]. |
| V5 Input Validation | yes | Pydantic-Validierung aller Parameter in den MCP-Tool-Definitionen und API-Endpunkten [VERIFIED: PyPI registry]. |
| V6 Cryptography | yes | HTTPS-erzwungene Verbindungen zwischen Hermes VPS und MCP-Server zur Vermeidung von Man-in-the-Middle-Angriffen [CITED: .planning/spikes/003-remote-mcp-vps/README.md]. |

### Known Threat Patterns for Python/FastAPI/MCP

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Token-Leckage im Quellcode | Information Disclosure | Einlesen von `MCP_BEARER` ausschließlich über Umgebungsvariablen; `.env` in `.gitignore` [CITED: .planning/phases/03-hermes-plugin-timeout-spike/03-CONTEXT.md]. |
| Unbefugter MCP-Zugriff | Elevation of Privilege | MCP-Server validiert jedes eingehende Bearer-Token und liefert bei Fehlschlag einen HTTP 401 Fehler [CITED: .planning/spikes/003-remote-mcp-vps/README.md]. |
| Mandantenübergreifender Datenzugriff | Spoofing | Die API erzwingt bei jeder DB-Abfrage die Filterung nach `owner_id` (RLS-Äquivalent) [CITED: .planning/phases/01-datenmodell-backend-api/01-CONTEXT.md]. |

## Sources

### Primary (HIGH confidence)
- `mcp-server/app/tools/items.py` - Definition der MCP-Tools und Registrierungs-Muster.
- `api/app/services/timeout.py` - Implementierung des `DraftTimeoutManager`.
- `.planning/phases/03-hermes-plugin-timeout-spike/03-CONTEXT.md` - Locked Decisions und Claude's Discretion.

### Secondary (MEDIUM confidence)
- `.planning/spikes/001-hermes-cron-vs-api-timer/README.md` - Validierung des API-Timers und Invalidierung des Hermes-Crons.
- `.planning/spikes/002-mcp-confirm-flow/README.md` - Nachweis der reinen MCP-Orchestrierung.
- `.planning/spikes/003-remote-mcp-vps/README.md` - Erreichbarkeit und Fehlerverhalten des remote MCP-Servers.
- `.planning/spikes/004-confirmation-payload/README.md` - Validierung des CAP-02 Plain-Text-Formats.

### Tertiary (LOW confidence)
- Hermes v0.19.0 Plugin-Dokumentation (Aus Trainingsdaten abgeleitet, muss bei der Implementierung verifiziert werden).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Alle Kernkomponenten sind lokal installiert und verifiziert.
- Architecture: HIGH - Die Spikes haben die Flussrichtung und Schichtentrennung eindeutig bewiesen.
- Pitfalls: HIGH - Die Einschränkungen von Hermes-Cron und Thread-Blockaden sind klar dokumentiert.

**Research date:** 2026-08-01  
**Valid until:** 2026-08-31 (30 Tage Gültigkeit für stabile Schnittstellen)  
