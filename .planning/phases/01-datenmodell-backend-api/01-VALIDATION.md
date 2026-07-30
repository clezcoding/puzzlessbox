---
phase: 1
slug: datenmodell-backend-api
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-30
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio |
| **Config file** | `api/pytest.ini` (Wave 0) |
| **Quick run command** | `pytest api/tests/unit -q` |
| **Full suite command** | `pytest api/tests` |
| **Estimated runtime** | ~60 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest api/tests/unit -q`
- **After every plan wave:** Run `pytest api/tests`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-W0 | 01 | 0 | — | — | N/A | infra | `pytest api/tests/unit -q` | ❌ W0 | ⬜ pending |
| AUTH-reg | TBD | TBD | AUTH-01 | T-01-auth | Only email/password signup creates user | integration | `pytest api/tests/integration/test_auth.py::test_registration` | ❌ W0 | ⬜ pending |
| AUTH-jwt | TBD | TBD | AUTH-02 | T-01-auth | JWT verified via JWKS; invalid → 401 | unit | `pytest api/tests/unit/test_auth.py::test_jwt_decode` | ❌ W0 | ⬜ pending |
| AUTH-lock | TBD | TBD | AUTH-03 | T-01-auth | Signup blocked when user_count > 0 | integration | `pytest api/tests/integration/test_auth.py::test_signup_lock` | ❌ W0 | ⬜ pending |
| AUTH-tenant | TBD | TBD | AUTH-04 | T-01-tenant | Cross-owner reads return empty/403 | integration | `pytest api/tests/integration/test_tenancy.py::test_rls` | ❌ W0 | ⬜ pending |
| CAP-draft | TBD | TBD | CAP-01 | — | Draft schema validation | unit | `pytest api/tests/unit/test_models.py::test_draft_validation` | ❌ W0 | ⬜ pending |
| CAP-timeout | TBD | TBD | CAP-03 | — | 30s inactivity → auto_saved | integration | `pytest api/tests/integration/test_capture.py::test_autosave` | ❌ W0 | ⬜ pending |
| LINK-scrape | TBD | TBD | LINK-01 | T-01-ssrf | JSONB metadata; scrape budget | integration | `pytest api/tests/integration/test_scraper.py::test_scrape` | ❌ W0 | ⬜ pending |
| LINK-cat | TBD | TBD | LINK-02 | — | Default Links category | unit | `pytest api/tests/unit/test_scraper.py::test_default_cat` | ❌ W0 | ⬜ pending |
| CAL-sync | TBD | TBD | CAL-02 | T-01-oauth | Encrypted tokens; calendar R/W | integration | `pytest api/tests/integration/test_calendar.py::test_sync` | ❌ W0 | ⬜ pending |
| CAL-etag | TBD | TBD | CAL-03 | — | If-Match mismatch → 412 | integration | `pytest api/tests/integration/test_calendar.py::test_conflict` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `api/pytest.ini` — pytest config
- [ ] `api/tests/conftest.py` — mock Postgres engine, transactional session, mock JWKS
- [ ] `api/tests/unit/` + `api/tests/integration/` — initial suites (RED scaffolds OK)
- [ ] Install pytest + pytest-asyncio in API deps

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Better Auth signup UI cookie round-trip in browser | AUTH-02 | Browser session cookie jar | Register → refresh → still authenticated in Next.js |
| Firecrawl + Camoufox Coolify internal-only networking | LINK-01 | Infra / network topology | Confirm services not publicly routed; API can reach them |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
