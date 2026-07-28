<!-- GSD:project-start source:PROJECT.md -->

## Project

**Puzzlessbox**

Puzzlessbox ist der moderne Nachfolger des klassischen Handheld-Sprachrekorders: Sprach- oder Textnachricht an den Hermes Agent → strukturierte Verarbeitung → formatierte Bestätigung mit Edit-Option → Auto-Save nach 30s Inaktivität → kategorisierte Anzeige in der WebApp. Kernprinzip: **Erfassen ohne Reibung, Ordnung im Hintergrund.** Primär für den Betreiber (Single-User), architektonisch vorbereitet für späteren Public-/SaaS-Ausbau.

**Core Value:** Capture-Flow muss reibungslos sitzen: Nachricht rein → Bestätigung → Auto-Save → Eintrag landet kategorisiert in der WebApp — ohne manuelle Nacharbeit.

### Constraints

- **Stack**: Python 3.14.6 · FastAPI 0.13x · FastMCP 3.4.4 (nicht 4.0-alpha) · PostgreSQL 18.4 · Next.js 16.2.7 · Node 24 LTS · Hermes v0.19.0 · Coolify v4.1.2
- **Auth WebApp**: Better Auth (Email/Password); Postgres-Adapter; nach erstem User Signup sperren
- **Auth Calendar**: Separater Google-OAuth (nicht Better Auth Social) — Connect in Settings
- **Auth MCP**: Statisches Bearer-Token (rotierbar, Coolify Secret); keine IP-Allowlist
- **Tenancy**: Jede Kerntabelle mit `owner_id` von Tag 1; Queries immer filtern
- **Repo**: Privat; AGPL-3.0 + Commercial Dual-Lizenz; Monorepo (`api/`, `mcp-server/`, `webapp/`, `hermes-plugin/`)
- **Domains (dev)**: `app.` / `api.` / `mcp.` unter `puzzlesstool.online`
- **Backups**: Nur lokal auf Coolify-Server (Phase 5)
- **Branding**: Hallmark — kein AI-Slop; Design-Entscheidungen in Discuss Phase 0

<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->

## Technology Stack

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.14.6 | Backend runtime | Pinned stable bugfix release in mid-2026. Provides optimal performance, modern language features, and full compatibility with FastAPI and FastMCP. |
| FastAPI | 0.136.1 | Backend REST API & ASGI host | Latest stable 0.13x release as of April 2026. Delivers high-performance asynchronous endpoints, native Pydantic v2 type-hint validation, and automatic OpenAPI 3.1 documentation. |
| FastMCP | 3.4.4 | Remote MCP server framework | Recommended stable version (avoiding 4.0.0-alpha). Allows exposing backend tools to Hermes Agent over HTTP/SSE. Mounted as an ASGI sub-app inside FastAPI to run on a single port. |
| PostgreSQL | 18.4 | Primary relational database | Stable bugfix release in mid-2026 (Postgres 18.0 released late 2025). Provides robust ACID compliance, JSONB for flexible metadata, and native support for pgvector. |
| Next.js | 16.2.7 | WebApp frontend framework | Recommended stable version in mid-2026, running on React 19.2 with Turbopack. Ideal for the Kanban board UI with server-side rendering and API routes. |
| Node.js | 24 LTS | Frontend runtime & tooling | Active LTS version in mid-2026, ensuring full compatibility with Next.js 16's minimum requirements (>=20.9.0). |
| Better Auth | 1.6.14 | WebApp authentication | Current stable release in mid-2026. Framework-agnostic, secure, and supports Email/Password login, PostgreSQL adapter, and JWT/JWKS plugin for FastAPI session verification. |
| Google Calendar API | v3 | Calendar synchronization | Official Google API for reading and writing calendar events, integrated via separate OAuth 2.0 flow in Settings. |
| Coolify | 4.1.2 | Self-hosted PaaS | Current stable self-hosting platform. Manages PostgreSQL, Docker-image deployments, environment variables, secrets, and local backups. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| SQLModel | 0.0.22 | ORM for FastAPI & Postgres | Used in the FastAPI backend to define database schemas and interact with PostgreSQL using Pydantic models. |
| PyJWT / Cryptography | 2.10.1 | JWT token verification | Used in FastAPI backend to decode and verify Better Auth JWKS-signed JWT tokens locally without hitting the database. |
| httpx | 0.28.1 | Asynchronous HTTP client | Used in FastAPI backend to fetch JWKS public keys from Next.js and communicate with external services (e.g., Google OAuth). |
| google-auth-oauthlib | 1.2.1 | Google OAuth integration | Used in FastAPI backend to handle the Google Calendar OAuth 2.0 flow and token exchange. |
| google-api-python-client | 2.160.0 | Google API client | Used in FastAPI backend to interact with the Google Calendar API. |
| @hello-pangea/dnd | 18.0.1 | Drag and drop board UI | Used in the Next.js frontend to implement the Kanban board categories view. |
| Tailwind CSS | 4.0.0 | Utility-first CSS styling | Used in the Next.js frontend for modern, responsive, and clean UI styling. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| GitHub Actions | CI/CD pipeline & Docker builds | Builds Docker images for API, MCP, and WebApp, pushes them to GHCR, and triggers Coolify deployments via webhooks. Offloads CPU/memory overhead from the Coolify VPS. |
| GHCR (ghcr.io) | Container registry | Securely hosts the built Docker images using GITHUB_TOKEN. |
| Higgsfield CLI | Asset generation | Used in Phase 0 to generate branding assets (logos, icons, illustrations) for the hallmark design. |
| GSD CLI (ctx7) | Spec-driven development & docs | Used to fetch current documentation and manage project milestones. |

## Installation

# Core (Next.js WebApp)

# Dev dependencies (Next.js WebApp)

# Backend (FastAPI - requirements.txt)

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Authentication | Better Auth (Email/Password) | NextAuth.js / Auth.js | NextAuth.js is heavily tied to Next.js and harder to integrate with external non-JS backends like FastAPI. Better Auth is framework-agnostic and provides a clean JWKS endpoint for FastAPI token verification. |
| Database | PostgreSQL 18.4 | SQLite | SQLite is great for local development but lacks robust concurrent write handling, JSONB indexing power, and native pgvector support for future AI search features. Postgres is the standard for production-ready multi-tenant databases. |
| Deployment | Coolify Docker-Image (GHCR) | Coolify Nixpacks / Git Build | Git-based builds on Coolify compile the application directly on the self-hosted VPS, which can easily exhaust CPU and RAM on smaller servers. External builds via GitHub Actions offload this overhead completely. |
| MCP Server | FastMCP (Python) | mcp-python-sdk | mcp-python-sdk is the low-level official SDK but requires significant boilerplate to define tools, resources, and lifespans. FastMCP provides a beautiful, high-level decorator-based API and built-in FastAPI integration. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| FastMCP 4.0.0-alpha | Unstable prerelease version. Introduces breaking API changes and lacks production-tested stability for HTTP/SSE. | FastMCP 3.4.4 |
| Better Auth Social Login for Calendar | Coupling primary login with Google Calendar scopes forces the user to sign in with Google. If Google API is down or scopes change, login breaks. | Email/Password login via Better Auth + separate Google OAuth in Settings |
| Direct Postgres DB checks for FastAPI auth | Querying the `session` table in Postgres from FastAPI on every request couples the backend to Better Auth's internal table structure and adds DB overhead. | Local JWT verification via Better Auth's JWKS endpoint |
| Coolify Git-based builds | Compiling Next.js 16 and FastAPI on a small self-hosted VPS can cause out-of-memory (OOM) crashes and high latency during deploys. | GitHub Actions building to GHCR + Coolify Webhook pull |

## Stack Patterns by Variant

- Use a single shared PostgreSQL database instance on Coolify.
- Because it is extremely cost-effective, simple to back up locally, and has near-zero latency.
- Use PostgreSQL with tenant isolation enforced via row-level security (RLS) or strict `owner_id` WHERE clauses on every query.
- Because it ensures secure data isolation between tenants while keeping infrastructure simple and scalable.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Python@3.14.6 | FastAPI@0.136.1 | FastAPI 0.136.1 fully supports Python 3.14's type-hinting and performance improvements. |
| FastMCP@3.4.4 | FastAPI@0.136.1 | FastMCP 3.4.4's ASGI app can be mounted directly in FastAPI 0.136.1 and shares its lifespan. |
| Next.js@16.2.7 | Node.js@24 LTS | Next.js 16 requires Node >=20.9.0, and Node 24 LTS provides the optimal, stable runtime environment. |
| Better Auth@1.6.14 | PostgreSQL@18.4 | Better Auth's Postgres adapter is fully compatible with Postgres 18.4's schema and indexing. |

## Sources

- `/better-auth/better-auth` — JWT/JWKS plugin documentation and session verification.
- `/prefecthq/fastmcp` — FastAPI ASGI integration and lifespan combining.
- `/vercel/next.js` — Next.js 16 Node requirements and stable release notes.
- `/websites/fastapi_tiangolo` — FastAPI 0.136.1 release notes and Pydantic v2 support.
- `/websites/postgresql_18` — PostgreSQL 18.4 stable release notes and features.

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

| Skill | Description | Path |
|-------|-------------|------|
| hallmark | "Anti-AI-slop design skill for greenfield pages, audits, redesigns, and design extraction from URLs or screenshots. Use when the user asks to build a new app or landing page, wants to redesign something, invokes Hallmark by name, or uses audit/redesign/study." | `.agents/skills/hallmark/SKILL.md` |
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
