---
status: complete
quick: true
id: 260803-3gu
slug: fix-open-uat-gaps-g-04-4-sticky-signup-l
completed: 2026-08-03T00:32:00Z
---

# Summary — Fix open UAT gaps

## Done

- **G-04-4:** `login-form.tsx` now checks Better Auth `{ error }` (client does not throw). No more false `router.push("/")` on SIGNUP_LOCKED 409. Sticky `pb.signup_locked` until user switches to Anmelden. Init tab/locked from sessionStorage. Tests updated + remount sticky case.
- **G-04-6:** Bulk bar already correct; hardened Checkbox `onPointerDown` stopPropagation. Prior UAT fail was automation/viewport flake.
- **G-05-4:** `openapi_url=None` in prod; test asserts `/docs`, `/redoc`, `/openapi.json` → 404.

## Verification

- `pnpm exec vitest run tests/auth.test.tsx tests/dnd.test.tsx` → 18 passed
- `uv run pytest tests/unit/test_health.py::test_docs_disabled_prod` → passed

## Files

- `webapp/app/login/login-form.tsx`
- `webapp/tests/auth.test.tsx`
- `webapp/components/board/board-card.tsx`
- `api/app/main.py`
- `api/tests/unit/test_health.py`
