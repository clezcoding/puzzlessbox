# Architecture Research

**Domain:** Hermes-MCP-Bridged Multi-Tenant-Ready Capture System
**Researched:** 2026-07-28
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       Hermes Agent Layer                     │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────────────────┐     ┌────────────────────────┐  │
│  │  Voice Mode (STT/TTS)  │     │   puzzlessbox-plugin   │  │
│  │  (Whisper / Edge TTS)  │     │   (30s Timeout Cron)   │  │
│  └───────────┬────────────┘     └───────────┬────────────┘  │
│              │                              │               │
└──────────────┼──────────────────────────────┼───────────────┘
               │ (Voice to Text)              │
               ▼                              │ MCP (HTTP Streamable)
┌─────────────────────────────────────────────┼───────────────┐
│                    Traefik Reverse Proxy    │               │
├─────────────────────────────────────────────┼───────────────┤
│  Bearer Token Security + IP Allowlist       │               │
└──────────────────────┬──────────────────────┼───────────────┘
                       │                      ▼
┌──────────────────────┼──────────────────────────────────────┐
│                      │ Puzzlessbox PaaS Stack (Coolify)     │
│  ┌───────────────────▼──┐   ┌────────────────────────────┐  │
│  │   puzzlessbox-webapp  │   │      puzzlessbox-mcp       │  │
│  │ (Next.js 16 / React)  │   │    (FastMCP Python SDK)    │  │
│  └───────────┬──────────┘   └───────────────┬────────────┘  │
│              │                              │               │
│              ▼ REST / Better Auth           │ REST / DB     │
│  ┌──────────────────────────────────────────▼────────────┐  │
│  │                    puzzlessbox-api                       │  │
│  │                (FastAPI / Python 3.14.6)                 │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ SQLAlchemy / SQLModel        │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    puzzlessbox-db                     │  │
│  │                  (PostgreSQL 18.4)                    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **hermes-plugin-puzzlessbox** | Intercepts inbound voice/text messages, schedules 30s auto-save windows, manages user-facing confirmation dialogs, and triggers the MCP client to persist confirmed payloads. | Python plugin executed in Hermes context, leveraging its cron and hook registry (`pre_llm_call`, `on_message`). |
| **puzzlessbox-mcp** | Exposes the standard Model Context Protocol (MCP) Streamable HTTP endpoint. Translates LLM semantic actions into typed backend queries. Handles Bearer token validation. | Python FastMCP (3.4.4 SDK) container, running as an independent service in Coolify behind Traefik. |
| **puzzlessbox-api** | Exposes REST CRUD interfaces, executes system automation (metadata scraping for links, Google Calendar sync), integrates Better Auth, and enforces `owner_id` tenant scoping. | Python 3.14.6 / FastAPI monolith. Shares the Postgres instance with WebApp/MCP. |
| **puzzlessbox-webapp** | Single-user dashboard representing items on a drag-and-drop board. Features detail panels, Quick Add, and Google Calendar Settings OAuth integration. | Next.js 16.2.7 (React 19.2), utilizing Tailwind CSS, shadcn/ui components, and Better Auth SDK. |
| **puzzlessbox-db** | Persists relational application state with strict schema validation. Employs `owner_id` indexing on every operational table for future multi-tenant segregation. | PostgreSQL 18.4 managed by Coolify. |

---

## Recommended Project Structure

```
puzzlessbox/
├── api/                           # puzzlessbox-api (FastAPI)
│   ├── app/
│   │   ├── auth/                  # Better Auth API integrations
│   │   ├── core/                  # DB connection, security middleware, settings
│   │   ├── models/                # SQLModel definitions (Owner, Item, Category)
│   │   ├── routers/               # FastAPI route definitions (items.py, settings.py)
│   │   ├── services/              # External sync services (Calendar, Link Scraper)
│   │   └── main.py                # API Entrypoint
│   ├── Dockerfile
│   └── requirements.txt
├── mcp-server/                    # puzzlessbox-mcp (FastMCP)
│   ├── src/
│   │   ├── client.py              # API client communicating with puzzlessbox-api
│   │   └── server.py              # FastMCP Server registering semantic tools
│   ├── Dockerfile
│   └── requirements.txt
├── webapp/                        # puzzlessbox-webapp (Next.js)
│   ├── src/
│   │   ├── app/                   # App Router pages (board, settings, login)
│   │   ├── components/            # UI components (Board, ItemCard, DragDrop)
│   │   ├── lib/                   # Better Auth setup, utility functions
│   │   └── styles/                # Global styles (Tailwind tokens)
│   ├── package.json
│   └── next.config.ts
├── hermes-plugin/                 # hermes-plugin-puzzlessbox
│   └── puzzlessbox_bridge/
│       ├── __init__.py            # Hook registrations & Cron setup
│       └── mcp_client.py          # Minimal MCP communication layer
└── .planning/                     # GSD specifications and research
    └── research/
        └── ARCHITECTURE.md        # This file
```

### Structure Rationale

- **`api/` and `mcp-server/` Separation:** Separating FastMCP from the FastAPI backend ensures that the semantic tool layer can scale or restart independently of the main API. If Hermes times out or experiences connectivity issues, the core REST API for the WebApp remains responsive.
- **`hermes-plugin/` as an Isolated Module:** Since Hermes resides on an external VPS, this module is developed as a standalone Python package within the Monorepo to facilitate direct SFTP/SCP synchronization, completely decoupled from the Next.js/FastAPI runtime.
- **`owner_id` Multi-Tenancy Scaffold:** Standardizing all models under `api/app/models/` ensures consistent application of the `owner_id` foreign key. Every database query in FastAPI will explicitly enforce `where(Item.owner_id == current_user.id)` from Day 1.

---

## Architectural Patterns

### Pattern 1: 30-Second Confirmation & Timeout Orchestration

**What:** The state machine for message capture sits on the Hermes Agent host, which can intercept actions, notify users, and schedule future executions. When a user submits a note, Hermes schedules a 30-second cron/timer. If the user edits or manually confirms within that period, the scheduled timer is revoked, and the customized payload is sent. If the timeout expires without user input, an auto-save handler triggers.

**When to use:** Crucial for voice-based or unstructured messaging capture where the user wants immediate confirmation without waiting for an active UI loop.

**Trade-offs:** 
- *Pros:* Highly interactive; doesn't block the messaging pipeline; zero UI latency for the user.
- *Cons:* Requires local state or a durable scheduling pool (e.g., SQLite/cron) on the Hermes VPS to track pending timeouts reliably.

**Example:**
```python
# hermes-plugin/puzzlessbox_bridge/timeout_manager.py
import asyncio
from typing import Dict, Callable

class TimeoutOrchestrator:
    def __init__(self):
        self._pending_tasks: Dict[str, asyncio.Task] = {}

    def schedule_auto_save(self, item_id: str, delay: float, save_callback: Callable):
        # Cancel any pre-existing timer for this item
        self.cancel_timer(item_id)
        
        async def _timer():
            await asyncio.sleep(delay)
            await save_callback(item_id)
            self._pending_tasks.pop(item_id, None)

        self._pending_tasks[item_id] = asyncio.create_task(_timer())

    def cancel_timer(self, item_id: str) -> bool:
        task = self._pending_tasks.pop(item_id, None)
        if task and not task.done():
            task.cancel()
            return True
        return False
```

### Pattern 2: Bearer-Authenticated Remote MCP over HTTPS

**What:** FastMCP natively supports HTTP transport but typically runs locally via stdio. To enable secure remote access from Hermes, FastMCP is exposed over public HTTPS behind Traefik. The MCP container intercepts requests, extracts the `Authorization: Bearer <token>` header, and validates it against the shared Coolify secret.

**When to use:** Required for remote multi-server architectures where the client (Hermes) and the server (Puzzlessbox DB/API) live on separate VPS hosts.

**Trade-offs:**
- *Pros:* Simpler than full OAuth 2.1; highly secure when paired with IP-allowlisting and TLS.
- *Cons:* Relies on manual token rotation if compromised; no granular scope management (all-or-nothing access).

---

## Data Flow

### Capture Request Flow

```
[User Message]
     │ (Voice / Text)
     ▼
[Hermes Agent] ──▶ [puzzlessbox-plugin] (Intercept & propose structure)
                         │
                         ├─▶ Propose to User: "Save 'X' as 'Task' in 30s?"
                         │
                         ├─▶ [Option A: User Edits/Confirms] ─▶ Cancel timer ─▶ MCP Server
                         │
                         └─▶ [Option B: 30s Timer Expires] ──▶ Trigger Save ──▶ MCP Server
                                                                                   │
                                                                                   ▼
                                                                           [puzzlessbox-mcp]
                                                                                   │
                                                                                   ▼
[Postgres DB] ◀── [puzzlessbox-api] ◀── [HTTP POST /items] ◀─ (Bearer-Auth) ──────┘
      │
      ▼ (Database State Change)
[WebApp UI] (Refreshed via SSE/Poll)
```

### Key Data Flows

1. **Structured Voice/Text Capture:**
   - User speaks into messaging gateway.
   - Hermes STT converts voice to text, feeding it to the LLM agent.
   - `puzzlessbox-plugin` intercepts the output, parsing the semantic attributes (Title, Type, Category, Summary).
   - A draft is outputted to the user. A 30s scheduler starts on Hermes.
   - Upon timer expiry or explicit confirm, the plugin invokes the remote `puzzlessbox-mcp` endpoint `create_item`.
   - `puzzlessbox-mcp` forwards the parameters to `puzzlessbox-api` (validating scopes/owner context) and writes to `puzzlessbox-db`.

2. **Link Metadata Scraping:**
   - User inputs a link (`https://example.com`) to Hermes.
   - Hermes matches the input as a link type, then dispatches `create_item` with `type=link` to MCP.
   - `puzzlessbox-api` intercepts the insert, initiates an asynchronous HTTP metadata fetch (extracting `og:title`, `og:description`, `og:image`), populates the `metadata` JSONB column, and saves.

3. **Google Calendar Sync (Decoupled Auth):**
   - User authenticates via Google Calendar OAuth in WebApp Settings. This flow is managed completely separate from Better Auth.
   - Authorization credentials (access & refresh tokens) are encrypted and saved in `puzzlessbox-db` under the owner's record.
   - When `puzzlessbox-api` processes an item of `type=calendar_event` (from Hermes or WebApp), it reads the encrypted credentials, decrypts them, and uses the Google Calendar API to push the event.

---

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| **0-1k users (Single-User/SaaS Beta)** | Single SQLite/Postgres DB on Coolify. Monolithic Next.js + FastAPI. Synchronous Link scraping and Calendar pushes. This is the v1 standard. |
| **1k-10k users** | Implement Celery/Redis for background jobs (metadata scraping and third-party API syncing). Scale WebApp and API independently to 2 containers each in Coolify. |
| **10k+ users** | Partition PostgreSQL schemas. Set up Read Replicas. Upgrade the Bearer MCP pattern to OAuth 2.1 to dynamic-allocate keys per Tenant directly. |

### Scaling Bottlenecks

1. **Dynamic Scraping Latency:** Scraping link metadata during an HTTP transaction blocks FastAPI workers. *Mitigation:* Offload scraping to an asynchronous background worker (FastAPI `BackgroundTasks` or Celery) immediately returning HTTP 202 to the client.
2. **Google OAuth Token Expiration:** Google Access tokens expire every hour. *Mitigation:* Ensure robust token decryption and auto-refresh logic inside the FastAPI middleware using the saved Refresh Token.

---

## Anti-Patterns

### Anti-Pattern 1: Merging Better Auth and Google Calendar OAuth

**What people do:** Attempt to integrate Google Calendar sync as part of Next-Auth/Better Auth social login scopes, forcing the user to log into the application via Google.

**Why it's wrong:** Limits core WebApp auth to Google-only users. If the login scopes are ever revoked or require modification, it breaks the primary application authentication flow.

**Do this instead:** Keep Better Auth purely Email/Password based. Google Calendar integration is implemented as an explicit "Connect" button in Settings, isolated from login sessions, storing OAuth tokens as separate schema relations.

### Anti-Pattern 2: Orchestrating Timer Logic on the Database/API

**What people do:** Write the 30-second confirmation window logic into the central Postgres DB or FastAPI using database triggers or long-running async sleep loops in web-threads.

**Why it's wrong:** Blocks HTTP response threads on the API server. Database-level timing logic is difficult to cancel, scale, or inspect, and it leaks transport layer concerns into the persistence tier.

**Do this instead:** Keep the 30s timer on the client side (the Hermes Agent VPS) using Python's asyncio task scheduling or a lightweight Cron scheduler. The backend database only records finalized or expired states.

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **Hermes Agent** | Streamable MCP HTTP Client | Remote client communicating with our hosted `puzzlessbox-mcp` endpoint over HTTPS. |
| **Google Calendar** | Google OAuth 2.0 Web Flow | WebApp redirects to Google Consent screen; API stores refresh token, dynamically issuing API writes. |
| **Metadata Scraper** | HTTP GET Parser | `puzzlessbox-api` performs parsing on incoming URLs using standard DOM selectors. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `WebApp ↔ Backend-API` | REST JSON (HTTPS) | Standard JSON payloads for dashboard layout operations. Guarded by Better Auth session cookie. |
| `MCP-Server ↔ Backend-API` | Internal REST Client | `puzzlessbox-mcp` parses MCP tool parameters and dispatches formatted requests to FastAPI internal loop. |
| `FastAPI ↔ PostgreSQL` | SQLAlchemy ORM / SQLModel | Uses connection pool; strictly appends `owner_id` context onto every active database cursor session. |

---

## Coolify Multi-App Deployment Topology

All services are hosted on the single Coolify server, utilizing independent Docker containers linked under a shared private network, exposed securely via the Traefik proxy.

```
                  [ Public Internet HTTPS Traffic ]
                                │
                                ▼
                       ┌─────────────────┐
                       │  Traefik Proxy  │
                       └─┬───┬────────┬──┘
                         │   │        │
      ┌──────────────────┘   │        └────────────────────┐
      │ (app.*)              │ (api.*)                     │ (mcp.*)
      ▼                      ▼                             ▼
┌─────────────┐        ┌─────────────┐               ┌─────────────┐
│   webapp    │        │     api     │               │ mcp-server  │
│ Container A │◀──────▶│ Container B │◀──────────────│ Container C │
└─────────────┘  REST  └─────────────┘ Internal REST └─────────────┘
                             │
                             ▼ Private Network
                       ┌─────────────┐
                       │  Postgres   │
                       │ Container D │
                       └─────────────┘
```

### GitHub Actions Build & Push Strategy
1. **GitHub Actions Workflow:** Triggered on merge to `main`. Builds separate images for `api`, `mcp-server`, and `webapp`.
2. **GHCR Registry:** Pushes images with two tags: `:latest` and `:sha-<git-commit-hash>`.
3. **Webhook Trigger:** Actions issues a POST request to Coolify's deployment webhook. Coolify pulls the updated image from GHCR and performs zero-downtime rolling updates.

### Suggested Build Order
1. **Phase 0 (Branding):** Create brand assets and design system tokens to prevent double-styling.
2. **Phase 1 (Database & Backend-API):** Build the FastAPI endpoints and Postgres schema with the core multi-tenant `owner_id` filters.
3. **Phase 2 (MCP-Server):** Implement FastMCP. Hook up the local backend API client.
4. **Phase 3 (Hermes Plugin):** Set up the Hermes-side plugin. Run the spike to verify 30s scheduling and HTTP communication.
5. **Phase 4 (WebApp):** Build the Next.js interface with Better Auth and Google OAuth integration, referencing the design tokens.
6. **Phase 5 (Coolify Operations):** Create the multi-app stack in Coolify, configure environment secrets, map domains, and configure Postgres database backups.

---
*Architecture research for: Hermes-MCP-Bridged Capture Systems*
*Researched: 2026-07-28*
