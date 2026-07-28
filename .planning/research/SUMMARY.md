# Project Research Summary

**Project:** Puzzlessbox
**Domain:** Personal Capture / Second Brain / Voice-to-Structured-Note
**Researched:** July 28, 2026
**Confidence:** HIGH

## Executive Summary

Puzzlessbox is a modern successor to the traditional handheld voice recorder, designed as a frictionless personal capture inbox. Users can ingest thoughts, notes, links, tasks, and calendar events via a messaging gateway (like Telegram or WhatsApp) hosted on an external Hermes Agent. The core user experience centers around "Capture without friction, organization in the background." To achieve this, when a user sends voice or text messages to Hermes, the system processes it, presents a structured confirmation draft (Title, Type, Category, Summary), and initiates a 30-second timeout window. If the user does not edit or manually confirm, it automatically saves. The captured item is then viewable on a responsive web-based Kanban board.

To build this system reliably, the backend API runs on FastAPI (Python 3.14.6) with PostgreSQL 18.4, and the frontend WebApp runs on Next.js 16.2.7. Programmatic tool access is enabled via a dedicated, remote FastMCP server (FastMCP 3.4.4). A key architectural requirement is multi-tenant capability: from Day 1, all core tables must include an `owner_id` to partition data securely. To protect single-user self-hosted environments while remaining SaaS-ready, registration is dynamically closed using a database hook after the first user signs up.

The primary technical risks lie in the synchronization timing and concurrency layers. Specifically, Hermes' native cron scheduler ticks at 60-second intervals, making sub-minute real-time timers impossible on the client side alone. To resolve this, a robust API-side timeout state machine is recommended. Furthermore, Google Calendar integration requires optimistic concurrency controls (version-matching via ETags and If-Match headers) to avoid dual-write race conditions when a user and an agent modify events concurrently.

## Key Findings

### Recommended Stack

The recommended stack is modern, stable, and selected to minimize compilation overhead on the self-hosted VPS by building Docker images in GitHub Actions, pushing them to GHCR, and pulling them into Coolify via webhooks.

**Core technologies:**
- **Python**: 3.14.6 — backend runtime, pinned stable bugfix release for FastAPI and FastMCP.
- **FastAPI**: 0.136.1 — backend REST API and internal client interface, leveraging asynchronous handlers and Pydantic v2 validation.
- **FastMCP**: 3.4.4 — remote MCP server framework to expose backend tools to Hermes Agent over HTTP/SSE. Deployed as a separate, independent Coolify app (Docker-image deploy) to isolate programmatic access from the main API.
- **PostgreSQL**: 18.4 — primary relational database, providing robust ACID compliance, JSONB columns for link metadata, and native pgvector support for future AI searches.
- **Next.js**: 16.2.7 — WebApp frontend framework running on React 19.2 with Turbopack for high-performance interactive boards.
- **Better Auth**: 1.6.14 — WebApp authentication supporting Email/Password credentials with a custom Postgres adapter and dynamic signup locks.
- **Google Calendar API**: v3 — official Google API for reading and writing calendar events, integrated via separate OAuth 2.0 flow in WebApp Settings.
- **Coolify**: 4.1.2 — self-hosted PaaS managing PostgreSQL, Docker-image deployments, environments, secrets, and local backups.

### Expected Features

Detailed feature definitions can be found in `FEATURES.md`.

**Must have (table stakes):**
- **High-Accuracy Voice Transcription** — spoken notes converted to text with high fidelity using Hermes' built-in voice mode.
- **Automated Structured Formatting** — raw text cleaned and formatted into markdown summaries, categories, and action items via LLM.
- **Multi-Channel Ingestion** — message capture via Telegram, WhatsApp, Discord, Slack, Signal, Email, Web, or direct Voice.
- **Categorization & Board UI** — drag-and-drop Kanban board layout representing categories (Inbox, Notes, Links, Tasks, Calendar).
- **Secure WebApp Authentication** — secure login/signup with PostgreSQL storage.

**Should have (competitive):**
- **Capture Confirmation UX & Auto-save** — interactive confirmation flow where Hermes presents a draft and auto-saves it after a 30-second timeout.
- **Link Bookmarking with Rich Previews** — automatic scraping of links sent via chat to extract Open Graph metadata, saving previews in JSONB.
- **Google Calendar Sync** — direct read/write event syncing via separate Google OAuth in Settings.
- **Better Auth First-User Lock** — dynamic database hook that closes signup automatically after the first user registers to secure private VPS instances.
- **MCP Tool Surface** — FastMCP server exposing tools (`create_item`, `list_categories`, `move_item`, `confirm_item`, `update_item`) for programmatic interaction.

**Defer (v2+):**
- **Multi-User SaaS UI** — full team collaboration dashboard, public signups, tenant isolation screens, and billing integrations.
- **"Ask AI" Knowledge Retrieval** — semantic search and interactive chat over historical notes.
- **Google Tasks Sync** — synchronizing tasks with Google Tasks (retained locally in v1 to reduce OAuth scope complexity).

### Architecture Approach

Puzzlessbox utilizes a multi-app monorepo structure. Each component is compiled into its own Docker container and deployed via Coolify, sharing a private network with Traefik handling ingress and routing.

**Major components:**
1. **puzzlessbox-webapp (Next.js 16)** — single-user dashboard representing items on a drag-and-drop board, including Settings and separate Google OAuth consent.
2. **puzzlessbox-api (FastAPI / Python 3.14.6)** — core REST API, business logic, asynchronous services (metadata scraper, Google Calendar sync), and Better Auth integration. Enforces `owner_id` tenancy filters on all database sessions.
3. **puzzlessbox-mcp (FastMCP 3.4.4)** — a dedicated, independent Coolify service exposing the programmatic tool surface to Hermes over HTTPS with Bearer token authentication.
4. **puzzlessbox-db (PostgreSQL 18.4)** — central relational database.
5. **hermes-plugin-puzzlessbox** — lightweight python package deployed on the external Hermes Agent VPS to intercept incoming user messages and orchestrate confirmations.

### Critical Pitfalls

Detailed analysis is available in `PITFALLS.md`.

1. **Hermes Cron 30s Timeout Incompatibility** — Hermes gateway ticks its scheduler at 60s intervals, making 30s client-side timing highly irregular. *Avoid by centralizing the timeout state machine on the FastAPI Backend-API, saving the item as `pending_confirmation` with an expiration timestamp and scheduling a non-blocking background task.*
2. **Google Calendar Dual-Write Race Condition** — Concurrent agent and user edits overwrite each other. *Avoid by implementing optimistic concurrency control: return ETags on read, enforce `If-Match` preconditions on write tools, and handle `412 Precondition Failed` gracefully by letting the agent re-plan.*
3. **First-User Signup Lockout** — Static `disableSignUp: true` blocks the owner. *Avoid by using Better Auth's dynamic `databaseHooks` on user create to check if user count > 0, dynamically rejecting registrations after the first user.*
4. **MCP Bearer Token Exposure** — Token leak over HTTP allows raw database access. *Avoid by enforcing HTTPS/TLS on Coolify for the MCP subdomain. (Note: IP-allowlisting on Traefik is deferred as an optional hardening step).*
5. **Multi-Tenant owner_id Leakage** — Information exposure between tenants when transitioning to SaaS. *Avoid by enforcing `owner_id` filters globally at the database/ORM layer, passing session context through FastAPI dependencies, and writing robust multi-tenant integration tests.*

## Implications for Roadmap

Based on research, the suggested phase structure enforces strict dependency management, de-risks critical integration paths early, and establishes branding tokens before frontend implementation.

### Phase 1: Branding & Design DNA
**Rationale:** Establishing Hallmark branding and design tokens first prevents double-styling and ensures the WebApp uses professional, non-AI-slop visuals from the start.
**Delivers:** Logo, icon assets, visual guidelines, and CSS custom properties (Tailwind tokens).

### Phase 2: Database & Backend API (FastAPI)
**Rationale:** The foundation of the system. All schemas, ORM logic, and multi-tenant filters must be built from Day 1 to avoid massive future refactoring. It also houses the Google OAuth sync and metadata scraping.
**Delivers:** PostgreSQL 18.4 instance, FastAPI REST API, SQLModel schemas with `owner_id` partition, Better Auth dynamic registration lock, link scraper service, and Google Calendar sync with optimistic concurrency.
**Addresses:** Secure WebApp Authentication, First-User Lock, Automated Structured Formatting, Link Bookmarking, and Google Calendar Sync.
**Avoids:** First-User Signup Lockout, Google Calendar Dual-Write Race, and Multi-Tenant owner_id Leakage.

### Phase 3: MCP Server
**Rationale:** With the central database and API in place, we build the remote programmatic tool interface, keeping it as a separate Coolify app to insulate it from main API crashes.
**Delivers:** FastMCP 3.4.4 server running in its own Docker container, integrated with Bearer token validation, exposing core item creation and management tools.
**Addresses:** MCP Tool Surface.
**Avoids:** MCP Bearer Token Exposure.

### Phase 4: Hermes Plugin & Timeout Spike
**Rationale:** The most technically uncertain integration. A dedicated spike is required to verify messaging intercepts and the 30-second API-side timeout flow before building the WebApp.
**Delivers:** Python plugin module for Hermes, integration hooks, and the end-to-end 30s auto-save timeout state machine.
**Addresses:** Capture Confirmation UX & Auto-save.
**Avoids:** Hermes Cron 30s Timeout Incompatibility.

### Phase 5: WebApp Frontend (Next.js)
**Rationale:** Built once the back-end, MCP, and ingestion pipelines are fully operational. Consumes Hallmark design tokens and connects to the API REST endpoints.
**Delivers:** Next.js 16.2.7 Kanban board UI, Drag-and-Drop categories layout, responsive boards, login/register UI, and separate Google OAuth toggle in Settings.
**Addresses:** Categorization & Board UI.

### Phase 6: Coolify Operations & Infrastructure
**Rationale:** Operationalizing the monorepo for production. Set up automated container builds in GHCR via GitHub Actions, configure environment secrets, map subdomains, and automate local backups.
**Delivers:** Traefik configurations, GitHub Actions workflows, Coolify multi-app orchestration, and automated Postgres cron.

### Phase Ordering Rationale

- **Branding-First (Phase 1)**: Ensures Next.js styling is semantic and unified from the start, avoiding retrofitted theme overhauls.
- **API and DB before MCP/Plugin (Phases 2 & 3)**: Core logic, models, and security must be solidified so that the MCP server has a reliable internal REST client to interact with.
- **Plugin Spike (Phase 4) before WebApp (Phase 5)**: De-risks the high-uncertainty capture flow early. If the 30-second API-side timer or Hermes hooks require API modifications, they can be made before frontend interfaces are hardcoded.
- **Decoupled Apps (Phases 2, 3, 5)**: Splitting the WebApp, central API, and MCP into separate Coolify docker-image deploys protects each service's availability and conforms with the production topology guidelines.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 4 (Hermes Plugin & Timeout Spike):** High risk due to Hermes' internal message hooks and cron constraints. Requires hands-on testing to ensure non-blocking `httpx` requests do not choke Hermes' main thread.
- **Phase 2 (Google Calendar Concurrency):** Optimistic locking with ETags needs precise mapping of Google Calendar API error structures and mock testing.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Branding):** Well-established design patterns using standard toolsets.
- **Phase 5 (WebApp Frontend):** Standard Next.js 16 drag-and-drop and state management.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Core technologies are fully documented, stable mid-2026 releases. Decoupled Coolify apps for API, MCP, and WebApp ensure independent horizontal scalability. |
| Features | HIGH | Detailed landscape in FEATURES.md. High clarity on MVP boundaries vs post-MVP enhancements. |
| Architecture | HIGH | Clear components and monorepo structure. Decoupled FastMCP and FastAPI services protect system availability. |
| Pitfalls | HIGH | Deep understanding of major risks (Hermes 60s cron, Google Calendar races, Better Auth lockout, token exposure, multi-tenant leaks) with robust prevention plans. |

**Overall confidence:** HIGH

### Gaps to Address

- **Hermes Message Status Callbacks** — If an item is auto-saved on the FastAPI side, we need a clean mechanism to push a "Saved" message back to the user via Hermes. This requires confirming whether Hermes exposes a push-webhook endpoint or if we need to call its direct gateway client.
- **Bearer Token Rotation** — There is currently no active token rotation strategy. For v1, tokens must be rotated manually via Coolify secrets.

## Sources

### Primary (HIGH confidence)
- `/better-auth/better-auth` — Dynamic registration database hooks and lifecycle events.
- `/prefecthq/fastmcp` — Remote MCP server configuration and ASGI compatibility.
- `/websites/postgresql_18` — Postgres 18.4 capabilities and pgvector integration.
- `/vercel/next.js` — Next.js 16 App Router standard structures.

### Secondary (MEDIUM confidence)
- [Nous Research Hermes Agent Documentation] — Details on cron limits (60s tick) and message event registration.
- [Google Calendar API Reference] — Specifications for ETags and `If-Match` conditional operations.

---
*Research completed: July 28, 2026*
*Ready for roadmap: yes*
