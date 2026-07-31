---
phase: 1
slug: datenmodell-backend-api
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-30
validated: 2026-07-31
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Nyquist audit 2026-07-31: SUMMARY coverage cross-checked against live pytest.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x + pytest-asyncio |
| **Config file** | `api/pytest.ini` |
| **Quick run command** | `cd api && DATABASE_URL=postgresql+psycopg2://puzzless@localhost:5432/puzzlessbox PATH=.venv/bin:$PATH .venv/bin/pytest tests/unit -q` |
| **Full suite command** | `cd api && DATABASE_URL=postgresql+psycopg2://puzzless@localhost:5432/puzzlessbox PATH=.venv/bin:$PATH .venv/bin/pytest tests/ -q` |
| **Estimated runtime** | ~22 seconds |
| **Last full run** | 2026-07-31 — **46 passed** |

---

## Sampling Rate

- **After every task commit:** Run quick unit suite
- **After every plan wave:** Run full suite (requires local Postgres + `alembic` on PATH via `.venv/bin`)
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Requirement Coverage Matrix

Phase requirements from ROADMAP: AUTH-01..04, CAP-01, CAP-03, LINK-01..02, CAL-02..03.

| Req | Behavior | Primary Test(s) | Type | Status |
|-----|----------|-----------------|------|--------|
| AUTH-01 | Email/password registration via Better Auth proxy | `test_auth.py::test_registration` | integration | ✅ green |
| AUTH-02 | JWT JWKS verify + login sets session cookie + cookie alone authenticates | `test_jwt_decode`, `test_jwt_decode_expired`, `test_login_persists_session`, `test_cookie_session_replays_on_verify` | unit + integration | ✅ green |
| AUTH-03 | Signup locked when user_count > 0 | `test_auth.py::test_signup_lock` | integration | ✅ green |
| AUTH-04 | owner_id RLS + cross-tenant empty board | `test_tenancy.py::test_rls`, `test_capture.py::test_cross_tenant_board_items_empty` | integration | ✅ green |
| CAP-01 | Structured draft create (polymorphic types) | `test_models.py::test_draft_validation`, `test_capture.py::test_draft_roundtrip[*]`, `test_idempotency` | unit + integration | ✅ green |
| CAP-03 | 30s inactivity → auto_saved (1s override in tests) | `test_autosave`, `test_autosave_task_type`, `test_patch_resets`, `test_confirm_cancels`, `test_parallel_edits`, `test_no_orphan_autosave`, `test_patch_task_type_resets` | integration | ✅ green |
| LINK-01 | Link JSONB metadata + scrape budget/SSRF/fallback | `test_scrape`, `test_camoufox_fallback`, `test_scrape_fail_fallback`, `test_12s_budget`, `test_ready_scraper_ping`, `test_ssrf_blocked[*]` | integration | ✅ green |
| LINK-02 | Default Links category | `test_scraper.py::test_default_cat` (unit + integration) | unit + integration | ✅ green |
| CAL-02 | Calendar R/W sync + encrypted tokens | `test_calendar.py::test_sync` | integration | ✅ green |
| CAL-03 | If-Match mismatch → 412, no silent overwrite | `test_conflict`, `test_patch_matching_etag`, `test_pull_before_write`, `test_no_silent_overwrite` | integration | ✅ green |

Supporting (infra / shell — not roadmap reqs): `test_health.py` (6), `test_schema.py` (4), `test_service_bearer`.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-W0 | 01 | 0 | — | — | N/A | infra | `pytest tests/unit -q` | ✅ | ✅ green |
| HEALTH | 01 | 1 | — | T-01-docs / T-01-versioning | /health+/ready; Accept 415; docs off prod | unit | `pytest tests/unit/test_health.py -q` | ✅ | ✅ green |
| CAP-timeout | 02 | 2 | CAP-03 | T-01-orphan-save | 30s inactivity → auto_saved; confirm cancels | integration | `pytest tests/integration/test_capture.py -k autosave -q` | ✅ | ✅ green |
| LINK-scrape | 03 | 2 | LINK-01 | T-01-ssrf | JSONB metadata; SSRF blocked; 12s budget | integration | `pytest tests/integration/test_scraper.py -q` | ✅ | ✅ green |
| LINK-cat | 03 | 2 | LINK-02 | — | Default Links category | unit | `pytest tests/unit/test_scraper.py::test_default_cat -q` | ✅ | ✅ green |
| CAL-sync | 04 | 2 | CAL-02 | T-01-token-exposure | Encrypted tokens; calendar R/W | integration | `pytest tests/integration/test_calendar.py::test_sync -q` | ✅ | ✅ green |
| CAL-etag | 04 | 2 | CAL-03 | T-01-silent-overwrite | If-Match mismatch → 412 | integration | `pytest tests/integration/test_calendar.py::test_conflict -q` | ✅ | ✅ green |
| SCHEMA | 05 | 1 | AUTH-04 / CAP-01 | T-01-tenant | RLS + draft schema validation | unit+int | `pytest tests/unit/test_models.py tests/integration/test_tenancy.py tests/integration/test_schema.py -q` | ✅ | ✅ green |
| AUTH-reg | 06 | 1 | AUTH-01 | T-01-auth | Email/password signup creates user | integration | `pytest tests/integration/test_auth.py::test_registration -q` | ✅ | ✅ green |
| AUTH-jwt | 06 | 1 | AUTH-02 | T-01-auth / T-01-cookie | JWT via JWKS; cookie replay on /auth/verify | unit+int | `pytest tests/unit/test_auth.py tests/integration/test_auth.py -k 'jwt or cookie or login' -q` | ✅ | ✅ green |
| AUTH-lock | 06 | 1 | AUTH-03 | T-01-signup | Signup blocked when locked | integration | `pytest tests/integration/test_auth.py::test_signup_lock -q` | ✅ | ✅ green |
| AUTH-tenant | 06 | 1 | AUTH-04 | T-01-tenant | Cross-owner board empty | integration | `pytest tests/integration/test_capture.py::test_cross_tenant_board_items_empty -q` | ✅ | ✅ green |
| CAP-draft | 06 | 1 | CAP-01 | T-01-idempotency | Draft roundtrip + idempotency | integration | `pytest tests/integration/test_capture.py -k 'draft_roundtrip or idempotency' -q` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `api/pytest.ini` — pytest config (`asyncio_mode=auto`)
- [x] `api/tests/conftest.py` — Postgres engine, transactional session, mock JWKS, owner fixtures
- [x] `api/tests/unit/` + `api/tests/integration/` — suites green
- [x] pytest + pytest-asyncio in API deps

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Better Auth signup UI cookie round-trip in real browser | AUTH-02 | Browser session cookie jar + webapp deploy | Register → refresh → still authenticated in Next.js at `app.puzzlesstool.online` |
| Production Better Auth signup lock (live hook) | AUTH-03 | Hook lives in `webapp/lib/auth.config.ts`; API tests mock Better Auth HTTP | First signup succeeds; second → SIGNUP_LOCKED/409 |
| Firecrawl + Camoufox Coolify internal-only networking | LINK-01 | Infra / network topology | Confirm services not publicly routed; API can reach them |
| Production Google Calendar OAuth round-trip | CAL-02 | Tests mock `googleapiclient` | Connect → Google grant → callback → create/list events |
| Production link scrape (if `SCRAPER_ENABLED`) | LINK-01 | Scraper HTTP mocked | `POST /links` with public URL → metadata or hostname fallback |

---

## Gaps

| Gap | Classification | Resolution |
|-----|----------------|------------|
| AUTH-02 cookie follow-up (Set-Cookie asserted, no replay) | was PARTIAL | **FILLED** — `test_cookie_session_replays_on_verify` (2026-07-31) |
| Live Better Auth / Google / scraper | env-specific | Manual-only (justified) — not blockers for Nyquist automated coverage |

**No MISSING automated gaps for Phase 1 roadmap requirements.**

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s (~22s full suite)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-07-31
**Verdict:** **PASS**

---

## Validation Audit 2026-07-31

| Metric | Count |
|--------|-------|
| Phase requirements | 10 |
| COVERED (automated green) | 10 |
| PARTIAL | 0 |
| MISSING | 0 |
| Gaps found | 1 (AUTH-02 cookie replay) |
| Resolved (new test) | 1 |
| Escalated | 0 |
| Manual-only (justified) | 5 |
| Pytest evidence | 46 passed in ~22s |

### Tests Created This Audit

| # | File | Type | Command |
|---|------|------|---------|
| 1 | `api/tests/integration/test_auth.py::test_cookie_session_replays_on_verify` | integration | `pytest tests/integration/test_auth.py::test_cookie_session_replays_on_verify -q` |

### Evidence Command

```bash
cd api && DATABASE_URL=postgresql+psycopg2://puzzless@localhost:5432/puzzlessbox PATH=.venv/bin:$PATH .venv/bin/pytest tests/ -q
# → 46 passed
```
