# Phase 2 — API Coverage Matrix

**Detector:** external API integration **detected = true** — Phase 2 MCP-Server konsumiert die Phase-1 FastAPI als interner httpx-Client (D-15, D-16).
**Default disposition:** INTEGRATE. Jede OPT-OUT trägt eine Ein-Zeilen-Begründung.
**Produced:** 2026-07-31 (plan time). Gate: `api-coverage.verify-pre` blockt Seal ohne entschiedene Matrix.

## Capability Surface (consumed by MCP tools)

| # | API Capability | HTTP + Path | Consuming MCP Tool | Status | Disposition | Plan |
|---|----------------|-------------|--------------------|--------|-------------|------|
| C1 | Draft erstellen (startet 30s-Timer) | `POST /drafts` | `create_item` | exists (Phase 1 `capture.py`) | INTEGRATE | 02-01 |
| C2 | Draft patchen | `PATCH /drafts/{id}` | `confirm_item`, `update_item` | exists | INTEGRATE | 02-03 |
| C3 | Draft bestätigen | `POST /drafts/{id}/confirm` | `confirm_item` | exists | INTEGRATE | 02-03 |
| C4 | Kategorien lesen | `GET /categories` | `list_categories` | **NEU (Phase 2)** | INTEGRATE | 02-02 |
| C5 | Kategorie anlegen | `POST /categories` | `create_category` | **NEU (Phase 2)** | INTEGRATE | 02-02 |
| C6 | Item Category verschieben | `PATCH /items/{id}` `{category_id}` | `move_item` | **NEU (Phase 2)** | INTEGRATE | 02-02 |
| C7 | Owner-Auflösung (bearer_hash → owner_id) | `POST /internal/mcp-auth` | MCP `TokenVerifier` (nicht Tool) | **NEU (Phase 2)** | INTEGRATE | 02-01 |

## OPT-OUT (Phase-1 endpoints NOT wrapped as MCP tools this phase)

| Phase-1 Endpoint | Reason (one line) |
|------------------|-------------------|
| `GET /events` (calendar read) | Kalender-Sync ist kein Capture-Tool; nicht in MCP-01 6-Tool-Fence. |
| Google Calendar OAuth (`/auth/google/*`) | Browser-OAuth-Flow, kein Hermes-Tool; WebApp-Settings Phase 4 (CAL-01). |
| Link-Scrape-Pipeline (intern via `POST /drafts` type=link) | Kein dediziertes Scrape-Tool; Links laufen über `create_item` type=`link`. |
| `GET /board-items` (board read) | Board-Anzeige ist WebApp-Concern (Phase 4 BOARD-*); Hermes liest kein Board. |
| Better-Auth `/verify`, JWKS cookie/JWT path | Nur WebApp-User-Auth; Hermes nutzt statischen Bearer, nicht JWT. |

**Scope fence (prohibition, D-06/scope):** MCP exponiert **ausschließlich** die 6 MCP-01-Tools. Kein `calendar`/`link`/`board`/`events`-Endpoint wird als Tool exponiert.

**Matrix decided:** ✓ alle 7 konsumierten Capabilities INTEGRATE, 5 OPT-OUT begründet.
