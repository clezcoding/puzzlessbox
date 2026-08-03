---
quick: true
id: 260803-3gu
slug: fix-open-uat-gaps-g-04-4-sticky-signup-l
status: active
created: 2026-08-03T00:30:00Z
---

# Quick: Fix open UAT gaps (G-04-4, G-04-6, G-05-4)

## Goal

Close remaining prod UAT gaps from Phase 4/5 deep verify.

## Tasks

1. **G-04-4** — `login-form.tsx`: Better Auth client returns `{ data, error }` (does not throw). Check `error` before `router.push`. Keep `pb.signup_locked` sticky until user switches to Anmelden tab. Init tab/locked from sessionStorage synchronously.
2. **G-04-6** — Bulk bar code path OK; harden Checkbox `onPointerDown` stopPropagation so selection clicks never hit card. Confirm unit test coverage for bulk bar.
3. **G-05-4** — `api/app/main.py`: set `openapi_url=None` when `is_prod`. Extend `test_docs_disabled_prod` to assert `/openapi.json` 404.

## Done when

- Auth tests cover SIGNUP_LOCKED without throw (return `{ error }`)
- Prod create_app has no openapi URL
- PLAN executed + SUMMARY written
