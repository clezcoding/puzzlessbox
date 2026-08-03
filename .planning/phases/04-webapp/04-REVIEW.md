---
phase: 04-webapp
reviewed: 2026-08-03T00:08:00Z
depth: quick
files_reviewed: 4
files_reviewed_list:
  - api/app/core/config.py
  - webapp/Dockerfile
  - .github/workflows/deploy-web.yml
  - webapp/app/login/login-form.tsx
findings:
  critical: 0
  warning: 2
  info: 2
  total: 4
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-08-03T00:08:00Z  
**Depth:** quick  
**Files Reviewed:** 4 (+ `webapp/public/apollo-onboard.png` binary — presence verified, content skipped)  
**Status:** issues_found

## Summary

Quick-pattern + targeted read of gap-closure plan 04-05 files (CORS default, Docker build-args, deploy-web workflow, SIGNUP_LOCKED UI, onboard asset). Gap infra changes align with plan intent: `CORS_ORIGINS` includes pbox, `NEXT_PUBLIC_*` baked at image build, workflow passes matching build-args, onboard PNG present and byte-identical to brand source. No critical/blocker defects in reviewed delta. Two warnings on deployment robustness and untested remount path; two info notes on asset verification and local Docker ergonomics.

## Warnings

### WR-01: JWKS code default still localhost — prod footgun

**File:** `api/app/core/config.py:12`  
**Issue:** `BETTER_AUTH_JWKS_URL` default remains `http://localhost:3000/api/auth/jwks` while plan 04-05 closes G-04-3/G-05-3 via Coolify env (`https://pbox.puzzlesstool.online/api/auth/jwks`). Task 2 only updated `CORS_ORIGINS`. Any API deploy/restart with missing or drifted `BETTER_AUTH_JWKS_URL` env silently breaks JWT verification (`jwt.py` caches JWKS client from settings).  
**Fix:** Mirror CORS pattern — set code default to prod canonical URL (or empty string with startup validation when `ENV=prod`):

```python
BETTER_AUTH_JWKS_URL: str = "https://pbox.puzzlesstool.online/api/auth/jwks"
```

Keep docker-compose / `.env.example` overrides for local dev.

### WR-02: SIGNUP_LOCKED sessionStorage remount path untested

**File:** `webapp/app/login/login-form.tsx:45-51,84-87`  
**Issue:** G-04-4 fix persists lock flag via `sessionStorage` for post-navigation remount, but `webapp/tests/auth.test.tsx` only covers inline `mockRejectedValue({ message: "SIGNUP_LOCKED" })` — no test seeds `sessionStorage` before render. Regressions in remount UX (the original prod repro) would not fail CI.  
**Fix:** Add test case:

```tsx
it("restores SIGNUP_LOCKED copy from sessionStorage after remount", () => {
  sessionStorage.setItem("pb.signup_locked", "1");
  render(<LoginForm />);
  expect(screen.getByText(/Registrierung ist geschlossen/)).toBeInTheDocument();
  expect(screen.getByRole("tab", { name: "Registrieren" })).toHaveAttribute("data-state", "active");
});
```

## Info

### IN-01: Onboard asset verified

**File:** `webapp/public/apollo-onboard.png`  
**Issue:** Binary not content-reviewed (per scope). File exists; `cmp` confirms byte-identical to `brand/assets/apollo-onboard.png`. Referenced by `webapp/app/welcome/page.tsx:38`. Dockerfile copies `webapp/public` into runner image — G-04-5 satisfied after deploy.  
**Fix:** None required.

### IN-02: Dockerfile ARG defaults target prod only

**File:** `webapp/Dockerfile:12-15`  
**Issue:** `ARG NEXT_PUBLIC_API_URL` / `NEXT_PUBLIC_APP_URL` default to production hosts. Local `docker build` without `--build-arg` bakes prod URLs (same as GHCR intent). Dev surprise, not prod bug.  
**Fix:** Document in README or add commented dev override example in Dockerfile if local image builds are common.

---

_Reviewed: 2026-08-03T00:08:00Z_  
_Reviewer: Claude (gsd-code-reviewer)_  
_Depth: quick_
