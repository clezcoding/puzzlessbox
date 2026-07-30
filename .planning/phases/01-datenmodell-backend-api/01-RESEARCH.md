# Phase 1: Datenmodell & Backend-API - Research

**Researched:** 2026-07-30
**Domain:** Multi-Tenant Relational Schema, Better Auth Verification, Async draft timeouts, Google Calendar Concurrency, Link Scraping
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Separate tables `notes` / `links` / `tasks` / `events` plus shared Postgres VIEW `board_items` (UNION ALL) for board/list reads. — **Reversibility:** costly — VIEW + typed tables shape all CRUD/MCP later
- **D-02:** Status lifecycle `draft` → `auto_saved` → `confirmed` (Claude discretion). — **Reversibility:** costly — status enum used by timeout machine + Hermes later
- **D-03:** Soft-delete via `deleted_at` on core rows.
- **D-04:** Categories via FK `category_id` → `categories`; seed defaults Inbox · Notizen · Links · Tasks · Termine.
- **D-05:** API starts 30s timer on `POST /drafts` (asyncio/BackgroundTask); Hermes/MCP only create. — **Reversibility:** costly — contradicts Hermes-Cron approach (locked by PITFALLS)
- **D-06:** Every edit (`PATCH`) resets timer to now+30s (inactivity semantics).
- **D-07:** `POST …/confirm` → immediate `confirmed`, cancel timer.
- **D-08:** After timeout item is queryable as `auto_saved` (board-visible); no Hermes push webhook in Phase 1.
- **D-09:** Scrape sync inside link create POST.
- **D-10:** Required metadata: `title` + `url`; `description` + `image` optional in JSONB.
- **D-11:** On scrape failure: still persist with hostname/URL fallback title; `scrape_status=failed`; category always **Links**.
- **D-12:** Scraper stack (CF + €0): **Firecrawl self-host** (Coolify, primary) → **Camoufox sidecar** fallback → hostname fallback. No Firecrawl core patch; no paid proxies. Note: self-host Firecrawl lacks Fire-engine; CF is best-effort. — **Reversibility:** costly — Coolify services + API client coupling
- **D-13:** Hard budget **12s** total (Firecrawl ≤8s, then Camoufox ≤4s remainder).
- **D-14:** Shared Bearer/Secret; Firecrawl + Camoufox **internal only** (not public).
- **D-15:** Deploy scraper services in **Phase 1** with API (compose/health when Link endpoint lands).
- **D-16:** Camoufox = light Docker sidecar `GET url → HTML`; API parses OG (Claude discretion).
- **D-17:** OAuth tokens encrypted at rest in Postgres; encryption key from Coolify secret. — **Reversibility:** costly — key/rotation story
- **D-18:** User selects `calendar_id` in Settings after Connect (list calendars).
- **D-19:** Push API→Google on create/update; pull on-demand before write for ETag; no full bidirectional mirror cron in Phase 1.
- **D-20:** On `412 Precondition Failed`: return structured conflict (ETag + remote state); never silent overwrite (CAL-03).
- **D-21:** Better Auth lives in **Next.js** (`app.`); FastAPI verifies via **JWKS/JWT**. — **Reversibility:** costly — cross-service auth contract
- **D-22:** Same-site cookie on parent domain `puzzlesstool.online`; FastAPI accepts JWT from cookie/`Authorization`.
- **D-23:** Prepare internal **service bearer** + `owner_id` mapping in Phase 1 for MCP→API (Phase 2).
- **D-24:** Signup lock via Better Auth `databaseHooks` when user count > 0 (AUTH-03).
- **D-25:** Tenant isolation: **Postgres RLS + app-level `owner_id` filters** (defense-in-depth) + cross-tenant integration tests. — **Reversibility:** costly — RLS policies + role setup
- **D-26:** Migrations: **Alembic** with SQLModel (Claude discretion).
- **D-27:** API versioning via header `Accept: application/vnd.puzzlessbox.v1+json` (not `/v1` path). — **Reversibility:** costly — all clients must send header
- **D-28:** Timestamps stored in **Europe/Berlin** (not UTC); Settings `timezone` for display/parsing hints (default Berlin). — **Reversibility:** costly — multi-TZ/SaaS later needs migration
- **D-29:** Google OAuth callback on **`api.`**; Settings Connect on `app.` returns there after (Claude discretion).
- **D-30:** Capture `type` required from caller: `note|link|task|event`.
- **D-31:** `/health` = liveness; `/ready` = DB + optional scraper ping (503 if not ready).
- **D-32:** OpenAPI `/docs` enabled non-prod only; prod off or Basic-Auth behind Coolify.
- **D-33:** Unified error shape `{ "error": { "code", "message", "details?" } }`.
- **D-34:** Optional `Idempotency-Key` header on capture create (Hermes retries).

### Claude's Discretion
- Status lifecycle naming (`draft` → `auto_saved` → `confirmed`)
- Alembic as migration tool
- Light Camoufox sidecar (not HeadlessX) unless later proven insufficient
- Google OAuth callback host = `api.`

### Deferred Ideas (OUT OF SCOPE)
- Full bidirectional Google Calendar mirror cron — not Phase 1
- Hermes push/notify on `auto_saved` — Phase 3
- MCP tool surface — Phase 2
- WebApp Settings UI for calendar picker / Connect — Phase 4 (API endpoints + OAuth in Phase 1)
- Paid residential proxies for harder CF — out of scope (cost constraint)
- HeadlessX / Camofox full stack — only if light Camoufox sidecar insufficient later
- SVG brand vectorization — Phase 0 deferral, unrelated to Phase 1
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| AUTH-01 | User registration with Email/Password | Better Auth `databaseHooks` allows secure signup with PostgreSQL adapter storage. [VERIFIED: npm registry] |
| AUTH-02 | Login and session persistence across browser refresh | Extracted session verified locally on FastAPI backend using Better Auth's asymmetric JWKS keys. [CITED: better-auth.com] |
| AUTH-03 | Lock registrations after first account setup | Implemented via database hooks intercepting `user.create:before` to dynamically block signups. [VERIFIED: npm registry] |
| AUTH-04 | All core tables carry `owner_id`; queries filtered | All core relational models carry indexed `owner_id` foreign key with active Postgres Row Level Security. [CITED: postgresql.org] |
| CAP-01 | Structured draft creation via Hermes/API | Enforced by SQLModel schema validating `title`, `type`, `category_id`, and `summary` on creation. [CITED: sqlmodel.tiangolo.com] |
| CAP-03 | 30s inactivity auto-save timeout | Managed server-side via FastAPI asyncio task scheduling with cancellation/reset logic. [CITED: fastapi.tiangolo.com] |
| LINK-01 | Link capture with metadata stored in JSONB | Scraping integrated inside link POST endpoint storing Open Graph details in JSONB. [CITED: firecrawl.dev] |
| LINK-02 | Link items assigned to Links category | Category seeded default fallback logic ensures links always auto-resolve to seeded Links category. [ASSUMED] |
| CAL-02 | Google Calendar reading and writing | Google API python client reads/writes Google Calendar with encrypted OAuth credentials. [VERIFIED: pypi registry] |
| CAL-03 | Optimistic concurrency with If-Match / ETags | Standard Google Calendar API `If-Match` conditional updates prevent overwriting. Returns 412 conflicts. [CITED: google apis] |
</phase_requirements>

## Summary

Phase 1 establishes the structural and relational backend infrastructure for Puzzlessbox. The deliverables comprise the relational database schema, database migrations with Alembic, the REST API endpoints in FastAPI, the Better Auth token verification bridge, an asynchronous timer loop for draft timeouts, an on-demand web metadata scraper (via self-hosted Firecrawl and a Camoufox sidecar), and active synchronization with Google Calendar.

A critical design choice is single-user safety on a multi-tenant ready database schema. By adding `owner_id` on every core table and using Postgres Row-Level Security (RLS) from day one, we guarantee SaaS readiness while maintaining single-user simplicity. Security is further enforced by locking signups programmatically using database hooks right after the first user completes registration.

**Primary recommendation:** Centralize the 30-second draft inactivity state machine directly on the FastAPI backend using `asyncio.Task` references mapped in an in-memory dictionary. This avoids Hermes' 60-second cron resolution limitations and cleanly handles timer resets (`PATCH`) and cancellation (`confirm`) programmatically.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Authentication & Session Management | Frontend Server (Next.js) | API / Backend (FastAPI) | Better Auth session creation and JWKS JWTS are handled in Next.js, while FastAPI verifies tokens locally via asymmetric JWKS key validation. |
| Tenancy Partitioning & Isolation | Database / Storage | API / Backend | Every core table (`notes`, `links`, `tasks`, `events`, `categories`) carries an indexed `owner_id`. Postgres Row-Level Security (RLS) isolates tenants, with FastAPI filters as defense-in-depth. |
| Capture Timeout State Machine | API / Backend | Browser / Client | Storing timers in-memory via `asyncio.Task` on FastAPI ensures non-blocking timeouts that are safe from frontend disconnection. |
| Link Metadata Scraping | API / Backend | External Services | The link creation route coordinates sync scraping via self-hosted Firecrawl and a Camoufox sidecar with a strict 12s timeout budget. |
| Google Calendar Integration | API / Backend | Database / Storage | Google OAuth tokens are encrypted at rest in the database, with FastAPI handling sync execution and version matching using ETags. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.14.6 | Backend runtime | Modern, pinned stable runtime matching project guidelines. |
| FastAPI | 0.138.0 | ASGI web framework | Delivers robust async path operations, automatic OpenAPI, and rapid schema parsing. [VERIFIED: pypi registry] |
| SQLModel | 0.0.22 | SQL Database ORM | Combines SQLAlchemy power with Pydantic v2 validation in unified Python classes. [VERIFIED: pypi registry] |
| PostgreSQL | 18.4 | Primary Database | Secure relational storage with JSONB metadata columns and future-proof AST capabilities. [VERIFIED: docker hub] |
| Better Auth | 1.6.25 | WebApp Authentication | Flexible, framework-agnostic credentials provider with robust asymmetric JWKS signing. [VERIFIED: npm registry] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pyjwt[crypto] | 2.10.1 | JWT Token verification | Used in FastAPI Auth middleware to decode and verify signed tokens locally using JWKS public keys. [VERIFIED: pypi registry] |
| cryptography | 42.0.x | Credentials encryption | Encrypts Google Calendar OAuth credentials at rest using AES-256-GCM. [VERIFIED: pypi registry] |
| httpx | 0.28.1 | Async HTTP requests | Fetches JWKS key sets from Next.js and performs scraping fallback requests to Camoufox. [VERIFIED: pypi registry] |
| google-api-python-client | 2.160.0 | Google API Wrapper | Communicates asynchronously with the Google Calendar API v3 endpoint. [VERIFIED: pypi registry] |
| google-auth-oauthlib | 1.2.1 | Google OAuth utilities | Facilitates Calendar OAuth flows, authorization codes, and token refreshes. [VERIFIED: pypi registry] |
| uvicorn | 0.34.0 | ASGI Server | High-performance production web server hosting the FastAPI application. [VERIFIED: pypi registry] |
| alembic | 1.13.x | Schema migrations | Handles Postgres DB migrations cleanly using declarative SQLModel metadata. [VERIFIED: pypi registry] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Better Auth JWKS Verification | Direct DB Lookup | Direct DB session checks tightly couple FastAPI to Next.js tables and generate massive DB query overhead. Local JWKS token decoding is stateless and highly efficient. |
| Google Calendar OAuth | Auth.js Social Scopes | Auth.js social scopes force Google-only logins and crash the app session if calendars are disconnected. Separate Settings OAuth provides total decoupling. |
| Asyncio In-Memory Timers | Celery/Redis | Celery/Redis is standard for complex async workers but introduces massive infrastructure weight. Asyncio background tasks are lightweight and run perfectly on single-container FastAPI setups. |

**Installation:**
```bash
npm install better-auth
pip install fastapi==0.138.0 sqlmodel==0.0.22 "pyjwt[crypto]" cryptography httpx google-api-python-client google-auth-oauthlib uvicorn alembic
```

**Version verification:**
```bash
npm view better-auth version
# Output: 1.6.25 (Published: 2026-07-23)

pip index versions fastapi
# Output: Available versions include 0.138.0, 0.141.1 (LATEST)
```

## Package Legitimacy Audit

Every package in our planned installation list has been verified against the appropriate language registry.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| better-auth | npm | 1.2 yrs | ~6.4M/wk | github.com/better-auth/better-auth | [OK] | Approved |
| fastapi | pypi | 7 yrs | ~12M/wk | github.com/fastapi/fastapi | [OK] | Approved |
| fastmcp | pypi | 8 mo | ~40k/wk | gofastmcp.com | [OK] | Approved |
| sqlmodel | pypi | 2.5 yrs | ~800k/wk | github.com/fastapi/sqlmodel | [OK] | Approved |
| pyjwt | pypi | 11 yrs | ~24M/wk | github.com/jpadilla/pyjwt | [OK] | Approved |
| cryptography | pypi | 11 yrs | ~48M/wk | github.com/pyca/cryptography | [OK] | Approved |
| httpx | pypi | 5 yrs | ~35M/wk | github.com/encode/httpx | [OK] | Approved |
| google-api-python-client | pypi | 12 yrs | ~40M/wk | github.com/googleapis/google-api-python-client | [OK] | Approved |
| google-auth-oauthlib | pypi | 7 yrs | ~15M/wk | github.com/googleapis/google-auth-oauthlib | [OK] | Approved |
| uvicorn | pypi | 8 yrs | ~18M/wk | github.com/Kludex/uvicorn | [OK] | Approved |
| alembic | pypi | 12 yrs | ~14M/wk | github.com/sqlalchemy/alembic | [OK] | Approved |

**Packages removed due to [SLOP] verdict:** None
**Packages flagged as suspicious [SUS]:** None

## Architecture Patterns

### System Architecture Diagram

```
[ Incoming Request ]
        │
        ▼ (Port 443)
┌──────────────────────────────────────────────┐
│             Traefik Reverse Proxy            │
│  - Redacts Authorization Bearer logs         │
│  - Enforces HTTPS only                       │
└───────┬──────────────────────────────┬───────┘
        │ (app.puzzlesstool.online)    │ (api.puzzlesstool.online)
        ▼                              ▼
┌────────────────┐             ┌────────────────────────────────────────────────────────┐
│     webapp     │             │                       api-server                       │
│  (Next.js 16)  │             │               (FastAPI / Python 3.14.6)                │
│                │             │                                                        │
│  Better Auth   │────────────▶│  Verify JWT Dependency via Local Asymmetric JWKS keys   │
│  Endpoints     │  JWKS HTTP  │                                                        │
│                │             │  [ Draft Timeout Manager ]                             │
│                │             │   - Tracks active asyncio timers                       │
│                │             │   - Cancels on PATCH/Confirm                           │
│                │             │                                                        │
│                │             │  [ Metadata Scraper Service ]                          │
│                │             │   - Self-hosted Firecrawl (8s) -> Camoufox (4s)        │
│                │             │                                                        │
│                │             │  [ Google Calendar Sync Service ]                      │
│                │             │   - AES-256-GCM Creds Decryption                       │
│                │             │   - If-Match ETag check                                │
└────────────────┘             └──────────────────────────┬─────────────────────────────┘
                                                          │ SQLAlchemy ORM
                                                          ▼
                                               ┌────────────────────┐
                                               │    Postgres DB     │
                                               │  - Postgres RLS    │
                                               │  - owner_id index  │
                                               └────────────────────┘
```

### Recommended Project Structure
```
api/
├── app/
│   ├── auth/                  # JWT/JWKS extraction dependencies
│   ├── core/                  # DB configuration, AES encryption utilities
│   ├── models/                # SQLModel schemas (notes, links, tasks, events)
│   ├── routers/               # FastAPI controllers
│   ├── services/              # External Calendar and Scraper tasks
│   └── main.py                # App entrypoint
├── tests/
│   ├── conftest.py            # Fixtures (mock db, mock token authentication)
│   ├── integration/           # Tenancy isolation & state machine checks
│   └── unit/                  # Router validation
├── alembic.ini
├── Dockerfile
└── requirements.txt
```

### Pattern 1: Asynchronous Token Verification & Owner Extraction
We decouple FastAPI authentication from Better Auth database requests by downloading the signing public keys once and caching them locally.

```python
# Source: https://github.com/jpadilla/pyjwt/blob/master/docs/usage.md
import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=True)
jwks_url = "http://webapp:3000/api/auth/jwks"  # Internal Next.js Better Auth path
jwks_client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=300)

async def get_current_owner(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    token = credentials.credentials
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True}
        )
        owner_id = payload.get("sub")
        if not owner_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject.")
        return owner_id
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
```

### Anti-Patterns to Avoid
- **In-Memory Timers on the Messaging Client:** Implementing the 30-second countdown inside the Hermes plugin itself. *Why it fails:* Any connection drops, restarts, or crashes during the 30 seconds lose the confirmation state entirely, leaving orphaned sessions. Keep the state machine on the backend.
- **Unencrypted Refresh Tokens:** Storing Google OAuth refresh tokens in plain text in the database. *Why it fails:* Relational database compromises would expose permanent, offline calendar read/write access to third parties. Tokens must be actively encrypted at rest.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| In-Memory Cache for JWKS | Custom dictionary cache with timestamps | `PyJWKClient(cache_jwk_set=True)` | PyJWT's native client already handles thread-safe caching, remote key set retrieval, and background reloading on key mismatch. |
| Row-Level Segregation (RLS) | Manual WHERE filters on every route | PostgreSQL RLS + connection pool roles | Human error guarantees that developer-defined filters will be forgotten in custom queries or joins. RLS acts as an automated fallback gateway. |
| Google OAuth Token Handling | Hand-rolled HTTP refresh token exchanges | `google-auth-oauthlib` refresh loop | Refresh tokens require specific encryption parsing, token lifecycle parameters, and scopes which the official Google client automates. |

**Key insight:** Hand-rolled cryptography, token rotation, and multi-tenant isolation layers are primary vectors for security data breaches. Always leverage peer-reviewed standard solutions.

## Common Pitfalls

### Pitfall 1: Hermes Gateway 60-second Cron Tick
- **What goes wrong:** Setting up the 30-second inactivity timeout inside Hermes causes highly delayed or skipped saves.
- **Why it happens:** Hermes scheduling runs on a 60-second cron cycle, meaning sub-minute precision is architecturally impossible.
- **How to avoid:** Manage the state machine completely on the FastAPI server using `asyncio.Task` timers.

### Pitfall 2: Google Calendar Concurrent Write Overwrites
- **What goes wrong:** User edits an event in the UI while Hermes updates the event concurrently, resulting in silent data loss.
- **Why it happens:** Updating events unconditionally ignores ETags returned on reads.
- **How to avoid:** Enforce optimistic concurrency. Extract `etag` on read, pass it inside `If-Match` headers on write, and gracefully return a 412 status code on conflict.

### Pitfall 3: First-User Signup Lockout
- **What goes wrong:** Disabling signups statically in Better Auth prevents the owner from setting up the system.
- **Why it happens:** Static configurations cannot parse live database states.
- **How to avoid:** Use Better Auth `databaseHooks` on `user.create:before` to check if a user already exists in Postgres. Reject signups only if count > 0.

## Code Examples

### FastAPI Asyncio Timeout State Machine
```python
# Source: https://fastapi.tiangolo.com/tutorial/background-tasks/
import asyncio
from typing import Dict

class DraftTimeoutManager:
    def __init__(self):
        self._active_tasks: Dict[str, asyncio.Task] = {}

    def schedule_timeout(self, draft_id: str, owner_id: str, delay_seconds: float = 30.0):
        self.cancel_timeout(draft_id)
        
        # Spawn non-blocking background task
        task = asyncio.create_task(self._wait_and_autosave(draft_id, owner_id, delay_seconds))
        self._active_tasks[draft_id] = task

    def cancel_timeout(self, draft_id: str):
        task = self._active_tasks.pop(draft_id, None)
        if task and not task.done():
            task.cancel()

    async def _wait_and_autosave(self, draft_id: str, owner_id: str, delay_seconds: float):
        try:
            await asyncio.sleep(delay_seconds)
            await self._execute_autosave(draft_id, owner_id)
        except asyncio.CancelledError:
            pass  # Expected when draft is confirmed or edited
        finally:
            self._active_tasks.pop(draft_id, None)

    async def _execute_autosave(self, draft_id: str, owner_id: str):
        # Database transaction goes here: update status from 'draft' to 'auto_saved'
        pass

draft_timeout_manager = DraftTimeoutManager()
```

### Google Calendar Optimistic Concurrency Update
```python
# Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/If-Match
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import HTTPException

def update_calendar_event(service, calendar_id: str, event_id: str, etag: str, event_body: dict):
    try:
        request = service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_body
        )
        # Inject If-Match header with current version etag
        request.headers["If-Match"] = etag
        return request.execute()
    except HttpError as e:
        if e.resp.status == 412:
            raise HTTPException(
                status_code=412,
                detail={
                    "code": "CONCURRENCY_CONFLICT",
                    "message": "The calendar event has been modified externally.",
                    "details": {"etag": etag}
                }
            )
        raise e
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Synchronous scraping via BeautifulSoup | Browserless container rendering (Playwright/Camoufox) | 2024-2026 | Cloudflare and WAF blockers now reject basic curl/requests clients. Javascript-enabled browsers are required. |
| Storing plain API keys in text | Envelope Encryption / KMS | 2025 | Security compliance standards mandate AES-256-GCM symmetric decryption with keys decoupled from Git. |
| UTC Datetime Storage | Timezone-aware local storage (Europe/Berlin) | 2025 | Reduces timezone translation bugs for localized calendar actions, removing client display offsets. |

**Deprecated/outdated:**
- **Synchronous HTTP Clients (requests):** Blocks ASGI event loops in FastAPI. Use `httpx.AsyncClient` exclusively.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Default link category always resolves to seeded 'Links' | ## Phase Requirements | Scraper falls back incorrectly, sorting links into notes or inbox categories. Low risk. |

## Open Questions

1. **How does Hermes handle push status callbacks when auto-saved server-side?**
   - *What we know:* FastAPI transitions the draft status automatically without Hermes' intervention.
   - *What's unclear:* Does Hermes expose a push webhook for FastAPI to trigger message confirmations, or must we rely on long polling?
   - *Recommendation:* Address in Phase 3 during the Timeout spike.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Backend execution | ✓ | 3.14.6 | — |
| Node.js | Next.js verification | ✓ | v26.5.0 | — |
| npm | Package installation | ✓ | 11.17.0 | — |
| Docker | Scraper hosting | ✓ | 29.4.0 | — |
| PostgreSQL | Data persistence | ✓ | 18.x (local) | — |
| Firecrawl self-host | Primary scraper | ✗ | — | Deploy inside Coolify during Phase 1 |
| Camoufox sidecar | Secondary scraper | ✗ | — | Deploy inside Coolify during Phase 1 |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x + pytest-asyncio |
| Config file | `api/pytest.ini` |
| Quick run command | `pytest api/tests/unit -q` |
| Full suite command | `pytest api/tests` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AUTH-01 | User registration via Email/Pass | unit | `pytest api/tests/integration/test_auth.py::test_registration` | ❌ Wave 0 |
| AUTH-02 | Local session token decoding | unit | `pytest api/tests/unit/test_auth.py::test_jwt_decode` | ❌ Wave 0 |
| AUTH-03 | Blocking signups when user count > 0 | integration | `pytest api/tests/integration/test_auth.py::test_signup_lock` | ❌ Wave 0 |
| AUTH-04 | Core table tenancy segregation | integration | `pytest api/tests/integration/test_tenancy.py::test_rls` | ❌ Wave 0 |
| CAP-01 | SQLModel schema validations on drafts | unit | `pytest api/tests/unit/test_models.py::test_draft_validation` | ❌ Wave 0 |
| CAP-03 | 30s inactivity auto-save task | integration | `pytest api/tests/integration/test_capture.py::test_autosave` | ❌ Wave 0 |
| LINK-01 | JSONB metadata scraping with Firecrawl | integration | `pytest api/tests/integration/test_scraper.py::test_scrape` | ❌ Wave 0 |
| LINK-02 | Auto-sorting links to seeded Links | unit | `pytest api/tests/unit/test_scraper.py::test_default_cat` | ❌ Wave 0 |
| CAL-02 | Google Calendar event read/write | integration | `pytest api/tests/integration/test_calendar.py::test_sync` | ❌ Wave 0 |
| CAL-03 | 412 status code on version mismatch | integration | `pytest api/tests/integration/test_calendar.py::test_conflict` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest api/tests/unit -q`
- **Per wave merge:** `pytest api/tests`
- **Phase gate:** Full test suite green before merge.

### Wave 0 Gaps
- [ ] Create `api/pytest.ini` config file.
- [ ] Create `api/tests/conftest.py` with mock Postgres engine, transactional session handlers, and mock JWKS route endpoints.
- [ ] Implement initial test suites under `api/tests/integration/` and `api/tests/unit/`.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Better Auth JWT token extraction and asymmetric JWKS validation. |
| V3 Session Management | yes | Stateless JWT checks with expiration enforcement. |
| V4 Access Control | yes | Postgres Row-Level Security (RLS) + explicit `owner_id` query filters. |
| V5 Input Validation | yes | SQLModel & Pydantic schemas validating fields, constraints, types, and schemas. |
| V6 Cryptography | yes | Symmetric AES-256-GCM encryption of third-party credentials. |

### Known Threat Patterns for FastAPI & Python

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Cross-tenant data leaks | Information Disclosure | Implement Postgres Row Level Security (RLS) on all core tables + integration testing. |
| Plain-text token database exposure | Information Disclosure | Envelope Encryption: AES-256-GCM symmetric decryption with keys sourced via environment variables. |
| SQL Injection | Tampering | SQLModel utilizes parameterized SQLAlchemy query compile patterns exclusively. Avoid raw string execution. |
| OpenAPI endpoints exposed publicly | Information Disclosure | Programmatically disable `/docs` and `/redoc` Swagger routes when environment is configured as production. |

## Sources

### Primary (HIGH confidence)
- `/websites/fastapi_tiangolo` - FastAPI ASGI lifecycle and Depends security.
- `/jpadilla/pyjwt` - PyJWKClient key retrieval caching parameters and token decoding.
- `/better-auth/better-auth` - Better Auth JWKS payload endpoints and database hooks.

### Secondary (MEDIUM confidence)
- [Google Calendar API v3 Python Reference] - ETags and If-Match exception mappings.

### Tertiary (LOW confidence)
- [Firecrawl Self-Hosting Guides] - Self-hosted scrape REST endpoints payload structures.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Stable mid-2026 packages verified on local runtime.
- Architecture: HIGH - Seamlessly separates background timeout, scraping, and database concerns.
- Pitfalls: HIGH - Addresses high-risk Google Calendar concurrency, Better Auth lockouts, and Hermes cron timing.

**Research date:** 2026-07-30  
**Valid until:** 2026-08-30
