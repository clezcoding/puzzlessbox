---
phase: 04-webapp
verified: 2026-08-05T13:44:00Z
status: passed
score: 6/6 04-05 must-haves verified (0 present, behavior-unverified)
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 4/6
  gaps_closed:
    - "G-04-1: NEXT_PUBLIC_API_URL baked into GHCR web image (no localhost:8000 in prod chunks)"
    - "G-04-2: CORS allows pbox Origin preflight (200 + allow-origin)"
    - "G-04-3: BETTER_AUTH_JWKS_URL → /api/auth/jwks returns 200"
    - "G-04-4: SIGNUP_LOCKED sticky VOICE copy on prod after second register — closed via 04-07 prod UAT #6 r4"
    - "G-04-5: apollo-onboard.png served from prod (200)"
    - "G-05-1: same as G-04-1 (phase 5 connectivity)"
    - "G-05-2: same as G-04-2 (phase 5 connectivity)"
    - "G-05-3: same as G-04-3 (phase 5 connectivity)"
  gaps_remaining: []
  regressions: []
---

# Phase 4: WebApp Verification Report (Re-Verification after 04-07 Gap Closure)

**Phase Goal:** Nutzer sieht und pflegt seine Items in einer responsiven Board-UI, kann sich einloggen und Google Calendar in den Settings verbinden — auf Basis der Design-Tokens aus Phase 0.
**Verified:** 2026-08-05T13:44:00Z
**Status:** passed
**Re-verification:** Yes — after 04-07 prod UAT #6 gap closure (G-04-4)

## Context

Vorherige Verifikation (2026-08-03) status=`human_needed` mit 2 behavior-unverified truths (Board lädt 5 Kategorien, Calendar Wizard CTA). 04-07 schließt den letzten offenen Gap G-04-4 (SIGNUP_LOCKED sticky VOICE copy) via hardened `isSignupLockedError` + envelope-shape vitest coverage + prod UAT #6 r4 re-run mit `browser_fill_form` (userEvent-style). Prod-UAT-Suite r4 (2026-08-05): 18/18 pass — alle behavior-unverified truths via echtes gsd-browser auf prod bestätigt.

## Goal Achievement

### 04-05 Gap Closure Truths (Plan 04-05 must_haves)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | OPTIONS from Origin pbox → API 200/204 mit Access-Control-Allow-Origin (G-04-2, G-05-2) | ✓ VERIFIED | `curl -X OPTIONS` → HTTP/2 200 + `access-control-allow-origin: https://pbox.puzzlesstool.online`; `api/app/core/config.py:22` |
| 2 | API BETTER_AUTH_JWKS_URL → /api/auth/jwks 200 (G-04-3, G-05-3) | ✓ VERIFIED | `curl https://pbox.puzzlesstool.online/api/auth/jwks` → 200 |
| 3 | Prod web bundle calls api.puzzlesstool.online not localhost:8000 (G-04-1, G-05-1) | ✓ VERIFIED | `webapp/Dockerfile:12-15` ARG/ENV vor build; `deploy-web.yml:47-49` build-args; 0 `localhost:8000` in prod chunks |
| 4 | GET /apollo-onboard.png → 200 (G-04-5) | ✓ VERIFIED | `curl` → 200; binary-identisch mit `brand/assets/apollo-onboard.png` |
| 5 | Authenticated board loads 5 category columns without offline banner (UAT #7) | ✓ VERIFIED | `04-UAT.md` Test #7 `result: pass`: gsd-browser auf /board → 5 Spalten (Inbox/Notizen/Links/Tasks/Termine); offline=false; API 200 |
| 6 | Calendar settings loads connect CTA, not infinite 'Kalender wird geladen…' (UAT #15) | ✓ VERIFIED | `04-UAT.md` Test #15 `result: pass`: „Mit Google verbinden" Button sichtbar |

**Score:** 6/6 04-05 truths verified (0 behavior-unverified — prod UAT r4 hat beide behavior-dependent truths via echte Browser-Session bestätigt)

### 04-07 Gap Closure Truths (Plan 04-07 must_haves)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Second registration on prod shows sticky VOICE copy on Register tab (G-04-4 / UAT #6) | ✓ VERIFIED | `04-UAT.md` Test #6 `result: pass` (r4): gsd-browser uat-04-07, `browser_fill_form`, VOICE copy visible, sticky nach reload; `login-form.tsx:251-253` |
| 2 | sessionStorage 'pb.signup_locked'='1' after 409 on prod | ✓ VERIFIED | `login-form.tsx:74` setItem; UAT #6 notes confirm `pb.signup_locked === "1"` nach reload; `auth.test.tsx:181` |
| 3 | isSignupLockedError detects SIGNUP_LOCKED across all better-auth client envelope shapes | ✓ VERIFIED | `login-form.tsx:45-68` hardened detector; `auth.test.tsx:73-143` 13 envelope-shape tests grün; 23/23 pass |
| 4 | VOICE copy survives remount via sessionStorage (sticky) | ✓ VERIFIED | `login-form.tsx:94-104` useState(readSignupLockedFlag) + useEffect; `auth.test.tsx:184-199` sticky-remount test grün; UAT #6 r4 sticky nach hard refresh |
| 5 | Vitest suite stays green with new envelope-shape tests | ✓ VERIFIED | `pnpm test -- --run` → 10 files, 77 tests passed (up from 62); RED→GREEN commits `f702ff2` + `ffd9dbd` |

**Score:** 5/5 04-07 truths verified

### Original Roadmap Success Criteria (Regression Check)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Kanban-Board mit Default-Kategorien + eigene Kategorien verwalten | ✓ VERIFIED | board files unverändert; 77 vitest tests grün; UAT #7 + #12 pass |
| 2 | DnD zwischen Kategorien + Item-Details bearbeiten | ✓ VERIFIED | UAT #9 + #10 pass auf prod |
| 3 | Auto-Saved Items erscheinen kategorisiert im Board | ✓ VERIFIED | `use-board-poll.ts` 10s poll; UAT #14 + #16 pass |
| 4 | Login Email/Passwort + Session über Browser-Refresh | ✓ VERIFIED | `login-form.tsx` + hardened SIGNUP_LOCKED detection; UAT #1-6 pass |
| 5 | Google Calendar via separatem OAuth in Settings | ✓ VERIFIED | `calendar-wizard.tsx` 3-step + 5 endpoints; UAT #15 + #18 pass |

**Original Score:** 5/5 truths verified (no regressions from 04-05/04-07)

### Required Artifacts (04-05 + 04-07 modified)

| Artifact | Expected | Status | Details |
|----------|---------|--------|---------|
| `api/app/core/config.py` | CORS_ORIGINS includes pbox | ✓ VERIFIED | Line 22 lists pbox |
| `webapp/Dockerfile` | ARG/ENV NEXT_PUBLIC_* before build | ✓ VERIFIED | Lines 12-15 |
| `.github/workflows/deploy-web.yml` | build-args for GHCR image | ✓ VERIFIED | Lines 47-49 |
| `webapp/public/apollo-onboard.png` | Welcome page asset | ✓ VERIFIED | Binary-identisch; prod GET → 200 |
| `webapp/app/login/login-form.tsx` | sessionStorage persistence + hardened detector | ✓ VERIFIED | Lines 16, 23-68 (detector + helpers), 70-77 (lockSignupUi), 94-104 (sticky useEffect), 149-168 (handleRegister with diagnostic `console.warn` at 152, 163), 251-253 (VOICE copy render) |
| `webapp/tests/auth.test.tsx` | envelope-shape unit tests | ✓ VERIFIED | Lines 5 (named import), 73-143 (13 envelope-shape tests), 153-199 (existing SIGNUP_LOCKED + sticky-remount tests) |

### Key Link Verification (04-05 + 04-07)

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `deploy-web.yml` build-args | `Dockerfile` ARG/ENV | NEXT_PUBLIC_* build-args → ARG → ENV → build inlines | ✓ WIRED | pbox URL baked in prod chunk |
| Coolify API CORS_ORIGINS | Starlette CORSMiddleware | env override → config.py allowlist | ✓ WIRED | Prod OPTIONS preflight → 200 + allow-origin |
| Coolify API BETTER_AUTH_JWKS_URL | FastAPI JWT verify | env → JWKS endpoint | ✓ WIRED | curl → 200 |
| `login-form.tsx` 409 handler | sessionStorage SIGNUP_LOCKED | setItem on 409 → useEffect reads on mount | ✓ WIRED | Unit test grün; UAT #6 r4 sticky |
| `authClient.signUp.email` 409 envelope | `isSignupLockedError` detector | error → flat/nested/string/stringify check → lockSignupUi | ✓ WIRED | 13 envelope-shape tests grün; UAT #6 r4 |
| `lockSignupUi` → render | VOICE copy + activeTab=register | setSignupLocked + setActiveTab → JSX | ✓ WIRED | `login-form.tsx:70-77` + 251-253; UAT #6 r4 sticky |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Webapp vitest suite green | `cd webapp && pnpm test -- --run` | 10 files, 77 tests passed, 2.68s | ✓ PASS |
| Envelope-shape tests green | `pnpm vitest run tests/auth.test.tsx --reporter=verbose` | 23/23 passed (13 envelope + 10 existing) | ✓ PASS |
| CORS preflight pbox → 200 | `curl -X OPTIONS` | HTTP/2 200 + allow-origin header | ✓ PASS |
| JWKS reachable | `curl /api/auth/jwks` | 200 | ✓ PASS |
| apollo-onboard.png prod | `curl /apollo-onboard.png` | 200 | ✓ PASS |
| Signup locked server-side | `curl -X POST /api/auth/sign-up/email` | 409 | ✓ PASS |
| No localhost:8000 in prod chunks | scan 11 chunks on /login | 0 matches | ✓ PASS |
| Commits exist | `git log --oneline -5` | `f702ff2` (RED) + `ffd9dbd` (GREEN) + `9291873` (docs) + `b17337e` (plan) | ✓ PASS |

### Probe Execution

No phase-declared probes (`scripts/*/tests/probe-*.sh`) for Phase 4. Verification relied on vitest + prod curls + gsd-browser prod UAT.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| BOARD-01 | 04-00, 04-01, 04-05 | Kanban-Board mit Default-Kategorien | ✓ SATISFIED | board files; UAT #7 pass |
| BOARD-02 | 04-02, 04-03, 04-05 | Eigene Kategorien verwalten | ✓ SATISFIED | categories-panel.tsx; UAT #12 pass |
| BOARD-03 | 04-02, 04-03, 04-06 | DnD cross-category | ✓ SATISFIED | dnd.test.tsx bulk-destination strengthened; UAT #10 pass |
| BOARD-04 | 04-02, 04-03 | Item-Detail bearbeiten | ✓ SATISFIED | item-modal.tsx autosave; UAT #9 pass |
| CAP-05 | 04-00, 04-04 | Gespeicherte Items kategorisiert | ✓ SATISFIED | poll + new-item-feedback; UAT #14 + #16 pass |
| CAL-01 | 04-04, 04-05 | Google Calendar OAuth in Settings | ✓ SATISFIED | calendar-wizard.tsx + 5 endpoints; UAT #15 + #18 pass |
| AUTH-03 | 04-05, 04-07 | Signup-Lock nach erstem Account | ✓ SATISFIED | API 409; hardened detector; UAT #6 r4 pass — VOICE copy sticky |
| OPS-01 | 04-05 | Separate Coolify Docker-Image-Apps | ✓ SATISFIED | prod curls bestätigen api + pbox erreichbar |
| OPS-02 | 04-05 | GitHub Actions → GHCR → Coolify webhook | ✓ SATISFIED | deploy-web.yml build-args; GHCR rebuild succeeded |

No orphaned requirements. Alle requirement IDs aus 04-00..04-07 PLAN frontmatter in REQUIREMENTS.md abgedeckt.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `webapp/components/board/categories-panel.tsx` | 122 | hardcoded `#eaeaea` fallback | ℹ️ Info | Pre-existing; Fallback für null color, API validiert |
| `webapp/middleware.ts` | n/a | Next.js 16 deprecation: `middleware` → `proxy` | ℹ️ Info | Pre-existing; build warnt aber funktioniert |
| `.github/workflows/deploy-web.yml` | 47-49 | build-args enthalten prod URLs (kein Secret) | ℹ️ Info | Public URLs, keine Secrets — T-04-05-03 accept |

Keine neuen TBD/FIXME/XXX/HACK/PLACEHOLDER in 04-05/04-07 geänderten Files. `console.warn` in `login-form.tsx:152,163` ist gewolltes Diagnose-Log per 04-07 PLAN (T-04-07-02 accept).

### Human Verification Required

Keine. Alle 18 UAT-Tests in `04-UAT.md` `result: pass` (Suite r4, 2026-08-05). Beide behavior-unverified truths (Board lädt 5 Kategorien, Calendar Wizard CTA) via gsd-browser prod UAT #7 + #15 bestätigt. UAT #6 (SIGNUP_LOCKED sticky VOICE copy) via 04-07 r4 closed.

### Gaps Summary

**Geschlossen (8/8):** G-04-1, G-04-2, G-04-3, G-04-4, G-04-5, G-05-1, G-05-2, G-05-3 — alle Blocker via prod curls + code inspection + prod UAT verifiziert. G-04-4 closed 2026-08-05 via 04-07: hardened `isSignupLockedError` (flat/code/nested body/Response-wrapped/json/string/deep stringify/circular-safe) + gsd-browser uat-04-07 r4 (`browser_fill_form`, VOICE copy sticky, `pb.signup_locked=1`).

**Verbleibend:** Keine offenen G-04-* oder G-05-* Gaps.

**Regression:** Keine. 77 vitest tests grün (up from 62 — 13 envelope-shape tests + circular-ref test hinzugefügt). Alle Original-Artifacts unverändert. Prod routes erreichbar.

**Status `passed`:** Alle automatisierbaren Checks (prod curls, unit tests, code inspection, build-arg wiring, envelope-shape coverage) PASS. Phase Goal auf Code- und Prod-Ebene erreicht. Prod-UAT-Suite r4: 18/18 pass — alle behavior-dependent truths via echte gsd-browser Browser-Session auf prod bestätigt. Phase 4 vollständig verifiziert.

---

_Verified: 2026-08-05T13:44:00Z_
_Verifier: Claude (gsd-verifier)_
