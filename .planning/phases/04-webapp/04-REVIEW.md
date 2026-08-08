---
phase: 04-webapp
reviewed: 2026-08-05T13:44:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - webapp/app/login/login-form.tsx
  - webapp/tests/auth.test.tsx
findings:
  critical: 0
  warning: 2
  info: 2
  total: 4
status: issues_found
focus: 04-07 gap closure (isSignupLockedError harden, envelope tests)
---

# Phase 04: Code Review Report

**Reviewed:** 2026-08-05T13:44:00Z  
**Depth:** standard  
**Files Reviewed:** 2  
**Status:** issues_found  
**Focus:** Plan 04-07 SIGNUP_LOCKED detector hardening (`login-form.tsx`, `auth.test.tsx`)

## Summary

04-07 delta is small and achieves gap goal: exported `isSignupLockedError` walks flat `message`/`code`, nested `body`/`response.body`/`json`, string errors, and circular-ref-safe `JSON.stringify` fallback; envelope-shape vitest block covers enumerated shapes; prod UAT #6 r4 passed per SUMMARY. All 23 `auth.test.tsx` tests green locally. No auth bypass or security regression — backend lock unchanged; detector only gates VOICE copy + `sessionStorage` stickiness.

Remaining defects are **false-positive UX** from substring/`JSON.stringify` matching, not missed prod envelopes. Advisory: ship OK for G-04-4; tighten matcher if future errors embed `SIGNUP_LOCKED` as incidental substring.

## Warnings

### WR-01: Substring `includes("SIGNUP_LOCKED")` false-positives on message field

**File:** `webapp/app/login/login-form.tsx:41-42,56-57`  
**Issue:** `messageMatchesSignupLocked` returns true when `value.includes("SIGNUP_LOCKED")`. `"NOT_SIGNUP_LOCKED".includes("SIGNUP_LOCKED")` is `true` in JS — any message containing that substring as non-exact token triggers `lockSignupUi` and hides the real error. Unlikely from Better Auth today (`auth.config.ts` throws exact `"SIGNUP_LOCKED"`), but matcher is logically wrong and untested.  
**Fix:** Prefer exact match on known fields; drop bare `includes` on `message` or gate with word boundary:

```tsx
function messageMatchesSignupLocked(value: string): boolean {
  return value === "SIGNUP_LOCKED";
}
// keep includes only inside JSON.stringify deep fallback if needed
```

Add negative test: `expect(isSignupLockedError({ message: "NOT_SIGNUP_LOCKED" })).toBe(false)`.

### WR-02: `JSON.stringify` fallback matches incidental substring anywhere in envelope

**File:** `webapp/app/login/login-form.tsx:63-64`  
**Issue:** Deep fallback returns true when serialized JSON contains `"SIGNUP_LOCKED"` anywhere — e.g. `{ message: "INVALID_PASSWORD", meta: { ref: "SIGNUP_LOCKED" } }` or `{ status: 500, debug: "SIGNUP_LOCKED in trace" }` both match (verified). User sees locked-signup VOICE copy + sticky flag for unrelated failures. Plan explicitly wanted broad fallback; tradeoff accepted for prod envelope unknowns but creates silent misclassification.  
**Fix:** Restrict fallback to known paths only (drop stringify), or scan parsed JSON for `{ message|code: "SIGNUP_LOCKED" }` at depth ≤2 instead of raw substring on full serialize. Add false-positive regression tests for INVALID_PASSWORD + incidental meta field.

## Info

### IN-01: Integration test still mocks only flat Better Auth envelope

**File:** `webapp/tests/auth.test.tsx:153-157`  
**Issue:** `LoginPage` SIGNUP_LOCKED UI test mocks `{ message: "SIGNUP_LOCKED", status: 409 }` — same shape 04-05 already covered. New nested/Response-wrapped shapes tested only via direct `isSignupLockedError()` calls, not through `handleRegister` + `authClient.signUp.email` mock. Gap between unit detector and form wiring is thin but untested end-to-end for non-flat envelopes.  
**Fix:** Duplicate integration test with `{ status: 409, body: { message: "SIGNUP_LOCKED" } }` mock once.

### IN-02: Prod diagnostic `console.warn` accepted info disclosure

**File:** `webapp/app/login/login-form.tsx:152,163`  
**Issue:** Unrecognized register errors log full object to browser console. Plan threat model T-04-07-02 accepts this (status/message/code only). No PII in current Better Auth 409 envelopes. Gate behind `process.env.NODE_ENV !== "production"` if console noise becomes concern.  
**Fix:** Optional — no change required for gap closure.

---

_Reviewed: 2026-08-05T13:44:00Z_  
_Reviewer: Claude (gsd-code-reviewer)_  
_Depth: standard_  
_Focus: 04-07 isSignupLockedError harden_
