# Phase 1: Datenmodell & Backend-API - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-30
**Phase:** 1-Datenmodell & Backend-API
**Areas discussed:** Item-Datenmodell, Capture-Timeout-API, Link-Scraper, Google-Calendar-Sync, Auth-Bridge, Infra-Extras, Ops-Extras
**Mode:** `--batch` (recommended options marked ★ during Q&A)

---

## Item-Datenmodell

| Option | Description | Selected |
|--------|-------------|----------|
| Polymorphic `items` + JSONB | Single table | |
| Separate tables + VIEW | notes/links/tasks/events | ✓ |
| Hybrid items + side tables | | |

**User's choice:** 1b; 2c; 3a; 4a  
**Notes:** Soft-delete; FK categories; status left to Claude → `draft`→`auto_saved`→`confirmed`

---

## Capture-Timeout-API

| Option | Description | Selected |
|--------|-------------|----------|
| API starts timer | BackgroundTask on POST | ✓ |
| Hermes local timer | | |
| Hybrid expires_at + Hermes cron | Against PITFALLS | |

| Edit behavior | | |
| Reset +30s on PATCH | ✓ |
| Stop until explicit confirm | User asked UX explain; chose reset |
| Timer runs through | |

**User's choice:** 1a; 2a; 3a; 4a  
**Notes:** Confirm cancels; `auto_saved` queryable; no Hermes push Phase 1

---

## Link-Scraper

| Option | Description | Selected |
|--------|-------------|----------|
| Sync POST | | ✓ |
| Async background | | |
| Hybrid timeout | | |

| Scraper stack | | |
| Firecrawl + Camoufox fallback | CF + €0 | ✓ |
| Firecrawl only | | |
| Camoufox primary | | |
| Scrapling in-api | | |

**User's choice:** 1a;2a;3a;4a then scraper **a**; ops 1a;2a;3a;4c  
**Notes:** Researched Firecrawl self-host lacks Fire-engine; issue #2257 CF failures; no Camoufox-in-Firecrawl patch. Timeout 12s (8+4). Phase 1 Coolify deploy. Camoufox light sidecar (discretion).

---

## Google-Calendar-Sync

| Option | Description | Selected |
|--------|-------------|----------|
| Encrypted Postgres tokens | | ✓ |
| Primary calendar only | | |
| Selectable calendar_id | | ✓ |
| Push + pull-on-demand ETag | | ✓ |
| Structured 412 conflict | | ✓ |

**User's choice:** 1a;2b;3a;4a

---

## Auth-Bridge API↔WebApp

| Option | Description | Selected |
|--------|-------------|----------|
| Better Auth in Next.js + JWKS | | ✓ |
| Parent-domain cookie | | ✓ |
| Service bearer Phase 1 | | ✓ |
| databaseHooks signup lock | | ✓ |

**User's choice:** 1a;2a;3a;4a

---

## Infra-Extras

| Option | Description | Selected |
|--------|-------------|----------|
| App-filter only | | |
| RLS + App-filter | | ✓ |
| Alembic (discretion) | | ✓ |
| Header API versioning | | ✓ |
| board_items VIEW | | ✓ |
| DB Europe/Berlin (not UTC) | User modified ★ UTC | ✓ |
| OAuth callback api. (discretion) | | ✓ |
| type required from caller | | ✓ |
| /health + /ready | | ✓ |

**User's choice:** 1b;2c;3c;4a then 1a aber DB Europe/Berlin;2c;3a;4a

---

## Ops-Extras

| Option | Description | Selected |
|--------|-------------|----------|
| /docs non-prod only | | ✓ |
| Unified error shape | | ✓ |
| Idempotency-Key optional | | ✓ |

**User's choice:** 1a;2a;3a

---

## Claude's Discretion

- Status lifecycle `draft` → `auto_saved` → `confirmed`
- Alembic migrations
- Light Camoufox Docker sidecar (HTML fetch; OG parse in API)
- Google OAuth callback on `api.`

## Deferred Ideas

- Bidirectional calendar mirror cron
- Hermes notify on auto_save
- MCP / WebApp UI (later phases)
- Paid CF proxies
- HeadlessX unless Camoufox insufficient
