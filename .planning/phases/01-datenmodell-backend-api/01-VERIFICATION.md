---
phase: 01-datenmodell-backend-api
verified: 2026-07-31T00:42:00Z
status: human_needed
score: 4/5 must-haves verified
behavior_unverified: 1
overrides_applied: 0
behavior_unverified_items:
  - truth: "Session persists across API calls via puzzlessbox_session cookie (AUTH-02 / roadmap SC1)"
    test: "POST /auth/login on deployed stack, then GET /auth/verify or GET /board-items with only the Set-Cookie session (no Authorization Bearer)"
    expected: "200 with owner_id / board items; cookie accepted by get_current_owner"
    why_human: "test_login_persists_session only asserts Set-Cookie headers; no integration test replays cookie on a follow-up request"
human_verification:
  - test: "Cookie-only session across API calls"
    expected: "After login, subsequent API request with session cookie alone returns 200 (verify or board-items)"
    why_human: "Cookie extraction wired in jwt.py but not exercised end-to-end in pytest"
  - test: "Production Better Auth signup lock"
    expected: "First signup on webapp succeeds; second signup returns SIGNUP_LOCKED/409"
    why_human: "Integration tests mock Better Auth HTTP client; hook lives in webapp auth.config.ts"
  - test: "Production Google Calendar OAuth round-trip"
    expected: "GET /auth/google/connect → callback → GET /calendars lists calendars; POST/PATCH /events syncs"
    why_human: "Calendar tests mock googleapiclient; real OAuth needs live Google credentials"
  - test: "Production link scrape (optional if SCRAPER_ENABLED)"
    expected: "POST /links with public URL returns metadata or hostname fallback with scrape_status set"
    why_human: "Scraper integration tests mock Firecrawl/Camoufox HTTP"
---

# Phase 1: Datenmodell & Backend-API Verification Report

**Phase Goal:** Backend-API und Datenmodell stehen mit Mehrmandantenfähigkeit (`owner_id`) von Tag 1, Auth ist integriert, und Capture/Link/Kalender-Backendlösungen sind end-to-end über die API nutzbar.

**Verified:** 2026-07-31T00:42:00Z  
**Status:** human_needed  
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Email/password register + login; session across API calls; signup locked after first account | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `webapp/lib/auth.config.ts` signup lock hook; `api/app/routers/auth.py` proxy + cookie; `test_registration`, `test_signup_lock` pass; Bearer session via `test_draft_roundtrip` pass; **cookie not replayed on follow-up request** (`test_login_persists_session` stops at Set-Cookie) |
| 2 | Core tables carry `owner_id`; every API query filters — cross-tenant isolation | ✓ VERIFIED | `0001_initial_schema.py` RLS + indexes; `database.py` `apply_tenant_context`; `capture.py` explicit `WHERE owner_id`; `test_rls`, `test_cross_tenant_board_items_empty` pass |
| 3 | API draft persists; 30s timeout state machine auto_saves without intervention | ✓ VERIFIED | `timeout.py` asyncio.Task + polymorphic UPDATE; `capture.py` schedules on POST/PATCH; `test_autosave`, `test_autosave_task_type`, `test_confirm_cancels`, `test_no_orphan_autosave` pass (DRAFT_TIMEOUT_SECONDS=1 in tests; default 30s in code) |
| 4 | Link stored with JSONB metadata + sensible category | ✓ VERIFIED | `links.py` + `scraper.py` Firecrawl→Camoufox→hostname; always `Links` category; `test_scrape`, `test_default_cat`, `test_scrape_fail_fallback` pass |
| 5 | Calendar events read/write Google; If-Match fails on concurrent writes | ✓ VERIFIED | `calendar.py` `update_event_with_etag` pulls remote etag, sets If-Match, `concurrency_conflict` on 412; AES-GCM `security.py`; `test_sync`, `test_conflict`, `test_no_silent_overwrite` pass (Google API mocked) |

**Score:** 4/5 truths verified (1 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `api/app/main.py` | FastAPI shell, routers, versioning | ✓ VERIFIED | Title "Puzzlessbox API"; Accept middleware; auth/capture/links/calendar/events registered |
| `api/app/routers/health.py` | /health + /ready | ✓ VERIFIED | Prod `https://api.puzzlesstool.online/health` → 200; `/ready` → `{"status":"ready"}` |
| `api/alembic/versions/0001_initial_schema.py` | Schema, RLS, VIEW, seeds | ✓ VERIFIED | notes/links/tasks/events/categories + board_items VIEW; 5 default categories; no `users` table |
| `api/alembic/versions/0002_idempotency.py` | Idempotency keys | ✓ VERIFIED | Migration exists; `test_idempotency` pass |
| `api/alembic/versions/0003_calendar_tokens.py` | Encrypted OAuth tokens | ✓ VERIFIED | encrypted_access/refresh columns; calendar tests pass |
| `api/app/services/timeout.py` | 30s draft timer | ✓ VERIFIED | Polymorphic autosave; cancel on confirm |
| `api/app/routers/capture.py` | Draft CRUD + board-items | ✓ VERIFIED | POST/PATCH/confirm + idempotency wired |
| `api/app/services/scraper.py` | Link scrape pipeline | ✓ VERIFIED | 12s budget, SSRF guards, fallback |
| `api/app/routers/links.py` | POST /links | ✓ VERIFIED | JSONB metadata + Links category |
| `api/app/services/calendar.py` | Google sync + etag | ✓ VERIFIED | OAuth, encrypt at rest, If-Match conflict |
| `webapp/lib/auth.config.ts` | Better Auth + signup lock | ✓ VERIFIED | databaseHooks user.create:before count check |
| `webapp/app/api/auth/[...all]/route.ts` | JWKS handler | ✓ VERIFIED | toNextJsHandler(auth) |
| `docker-compose.scraper.yml` | Internal scraper stack | ✓ VERIFIED | File present (Firecrawl + Camoufox) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `capture.py` POST /drafts | `timeout.py` | `schedule_timeout` after commit | ✓ WIRED | Line 169 |
| `timeout.py` | Postgres | `_execute_autosave` UPDATE by item_type | ✓ WIRED | Sets `app.owner_id` + RLS role |
| `jwt.py` | Better Auth JWKS | `PyJWKClient` | ✓ WIRED | Bearer + cookie extraction |
| `auth.py` | Better Auth | httpx proxy signup/login | ✓ WIRED | Sets session cookie on login |
| `links.py` | `scraper.py` | `scrape_service.scrape` | ✓ WIRED | Persists Link row |
| `events.py` PATCH | `calendar.py` | `update_event_with_etag` | ✓ WIRED | 412 CONCURRENCY_CONFLICT |
| `calendar.py` callback | `security.py` | `encrypt_token` | ✓ WIRED | Tokens encrypted at rest |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|-------------------|--------|
| `capture.py` GET /board-items | board rows | `board_items` VIEW + `owner_id` filter | DB query | ✓ FLOWING |
| `links.py` POST /links | metadata JSONB | `scrape_service.scrape(url)` | Dynamic scrape/fallback | ✓ FLOWING (mocked in tests) |
| `events.py` POST /events | google_event_id, etag | `calendar_service.create_event` | Google API + local persist | ✓ FLOWING (mocked in tests) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full test suite | `DATABASE_URL=postgresql+psycopg2://puzzless@localhost:5432/puzzlessbox PATH=api/.venv/bin:$PATH pytest tests/ -q` | 45 passed in 17.58s | ✓ PASS |
| RLS isolation | `pytest tests/integration/test_tenancy.py::test_rls` | pass | ✓ PASS |
| Autosave timer | `pytest tests/integration/test_capture.py::test_autosave` | pass | ✓ PASS |
| Signup lock | `pytest tests/integration/test_auth.py::test_signup_lock` | pass | ✓ PASS |
| Calendar conflict | `pytest tests/integration/test_calendar.py::test_conflict` | pass | ✓ PASS |
| Prod liveness | `curl https://api.puzzlesstool.online/health` | 200 | ✓ PASS |
| Prod readiness | `curl https://api.puzzlesstool.online/ready` | `{"status":"ready"}` | ✓ PASS |

**Note:** Integration tests require `alembic` on PATH (`api/.venv/bin`). Without it, `postgres_engine` fixture errors with `FileNotFoundError: alembic` — test harness ergonomics, not a missing implementation.

### Probe Execution

Step 7c: SKIPPED — no phase-declared probes or `scripts/*/tests/probe-*.sh` for this phase.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| AUTH-01 | 01-06 | Email/password register | ✓ SATISFIED | `auth.config.ts`, `test_registration` |
| AUTH-02 | 01-06 | Login + session persistence | ⚠️ PARTIAL | Bearer path verified; cookie follow-up request unverified |
| AUTH-03 | 01-06 | Signup lock after first user | ✓ SATISFIED | databaseHooks + `test_signup_lock` |
| AUTH-04 | 01-05, 01-06 | owner_id + query filter | ✓ SATISFIED | RLS + app filters + `test_rls` |
| CAP-01 | 01-05, 01-06 | Structured draft create | ✓ SATISFIED | POST /drafts polymorphic + `test_draft_roundtrip` |
| CAP-03 | 01-02 | 30s autosave state machine | ✓ SATISFIED | `timeout.py` + 7 capture timer tests |
| LINK-01 | 01-03 | Link metadata JSONB | ✓ SATISFIED | `links.py` + `test_scrape` |
| LINK-02 | 01-03 | Links category default | ✓ SATISFIED | `_links_category_id` + `test_default_cat` |
| CAL-02 | 01-04 | Calendar read/write sync | ✓ SATISFIED | `calendar.py` + `test_sync` (mocked Google) |
| CAL-03 | 01-04 | If-Match concurrency | ✓ SATISFIED | `test_conflict`, `test_no_silent_overwrite` |

No orphaned Phase 1 requirements in REQUIREMENTS.md traceability table.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | None (TBD/FIXME/TODO/placeholder) | — | Clean scan on phase key files |

### Human Verification Required

### 1. Cookie-only session across API calls

**Test:** Login via POST `/auth/login`, then call GET `/auth/verify` or GET `/board-items` sending only `puzzlessbox_session` cookie (strip Authorization header).  
**Expected:** 200 with valid `owner_id` / board data.  
**Why human:** Cookie set on login is tested; cookie replay on subsequent request is not.

### 2. Production Better Auth signup lock

**Test:** Register first account on deployed webapp; attempt second registration.  
**Expected:** Second attempt rejected with SIGNUP_LOCKED / 409.  
**Why human:** API tests mock Better Auth HTTP; lock hook runs in Next.js.

### 3. Production Google Calendar OAuth

**Test:** Complete OAuth connect flow on prod; list calendars; create and PATCH event with stale etag.  
**Expected:** Calendars listed; PATCH with stale etag returns 412 CONCURRENCY_CONFLICT.  
**Why human:** Tests mock googleapiclient.

### 4. Production link scrape (if SCRAPER_ENABLED)

**Test:** POST `/links` with real public URL on prod.  
**Expected:** 201 with metadata or hostname fallback; `scrape_status` explicit.  
**Why human:** Scraper HTTP mocked in tests.

### Gaps Summary

No blocking implementation gaps. Code, wiring, migrations, and 45/45 pytest cases pass against local Postgres. One roadmap sub-behavior (cookie session replay) lacks behavioral test coverage; external-service paths (Better Auth, Google, scraper) need prod smoke checks before treating Phase 1 fully closed for operators.

---

_Verified: 2026-07-31T00:42:00Z_  
_Verifier: Claude (gsd-verifier)_
