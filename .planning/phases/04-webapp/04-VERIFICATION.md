---
phase: 04-webapp
verified: 2026-08-03T00:11:00Z
status: human_needed
score: 4/6 04-05 must-haves verified (2 present, behavior-unverified)
behavior_unverified: 2
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 5/5
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
behavior_unverified_items:
  - truth: "Authenticated board loads 5 category columns without offline banner (UAT #7 unblock)"
    test: "Login als uat@puzzless.local auf https://pbox.puzzlesstool.online/board, Warten auf poll, Kategorien rendern"
    expected: "5 Default-Spalten (Inbox|Notizen|Links|Tasks|Termine) sichtbar; kein Offline-Banner; Karten laden"
    why_human: "Connectivity-Blocker geschlossen (CORS+JWKS+NEXT_PUBLIC bake), aber authenticated Browser-Session auf prod nötig — curl kann keine Cookie/JWT-Session simulieren."
  - truth: "Calendar settings loads connect CTA, not infinite 'Kalender wird geladen…' (UAT #15 unblock)"
    test: "Login → /settings → Google Calendar Section, Warten auf Wizard"
    expected: "Step 1 'Mit Google verbinden' Button sichtbar; kein Endlos-Spinner"
    why_human: "Wizard-State braucht authenticated session + Google OAuth config auf prod."
human_verification:
  - test: "Prod UAT #7 Board Desktop — 5 Kategorien, kein Offline-Banner"
    expected: "5 Default-Spalten rendern; Karten laden; kein 'Keine Verbindung' Banner"
    why_human: "Authenticated prod Browser-Session nötig; curl kann Cookie/JWT nicht simulieren"
  - test: "Prod UAT #15 Calendar Wizard — Step 1 CTA sichtbar"
    expected: "'Mit Google verbinden' Button; kein Endlos-'Kalender wird geladen…'"
    why_human: "Wizard-State braucht authenticated session + Google OAuth config auf prod"
  - test: "Prod UAT #6 SIGNUP_LOCKED UI — VOICE copy nach zweiter Registrierung"
    expected: "Register-Tab bleibt sichtbar; 'Registrierung ist geschlossen. Apollo lässt nur den ersten Nutzer rein.' via sessionStorage persistiert"
    why_human: "Closed 04-07 r4 — gsd-browser uat-04-07 confirmed VOICE copy + pb.signup_locked=1 sticky after reload"
  - test: "Prod UAT #8–11 Mobile/Modal/DnD/Bulk (vorher blocked)"
    expected: "Mobile Single-Column + Tabs + long-press Sheet; Item-Modal zentriert + Autosave; DnD cross-category + reorder; Bulk-Move sequenziell"
    why_human: "Vorher blockiert durch Board-Daten-Layer; jetzt unblocked, aber full UX nur in echtem Browser/Touch-Device"
  - test: "Prod UAT #16 Poll + New-Item Feedback"
    expected: "Poll alle ~10s; Toast + terracotta pulse bei neuem Item; Offline → Banner"
    why_human: "Echtzeit-Poll + Hermes-Capture braucht laufenden Hermes + authenticated session"
  - test: "Prod UAT #17 Cross-Origin Session → API"
    expected: "pbox JWT von api.puzzlesstool.online akzeptiert; /categories + /board-items 200"
    why_human: "JWT-Validierung über Origins braucht echten Login-Flow + Cookie-Übergabe"
  - test: "Prod UAT #18 apollo-onboard.png auf Welcome"
    expected: "Bild lädt auf /welcome nach Login"
    why_human: "Asset 200 per curl bestätigt; visuelle Render-Prüfung im Browser empfohlen"
---

# Phase 4: WebApp Verification Report (Re-Verification after 04-05 Gap Closure)

**Phase Goal:** Nutzer sieht und pflegt seine Items in einer responsiven Board-UI, kann sich einloggen und Google Calendar in den Settings verbinden — auf Basis der Design-Tokens aus Phase 0.
**Verified:** 2026-08-03T00:11:00Z
**Status:** human_needed
**Re-verification:** Yes — after 04-05 prod UAT gap closure (G-04-1..5, G-05-1..3)

## Context

Vorherige Verifikation (2026-08-02) status=`passed` basierte auf lokaler UAT. Prod-UAT (`04-UAT.md`, 2026-08-02T23:51Z) offenbarte 7 Blocker: client JS baked `localhost:8000` (G-04-1), CORS rejected pbox Origin (G-04-2), JWKS wrong path (G-04-3), SIGNUP_LOCKED UI copy lost on remount (G-04-4), apollo-onboard.png 404 (G-04-5). 04-05 schließt Infra-Blocker via Coolify env + Dockerfile build-args + PNG ship + sessionStorage fix.

## Goal Achievement

### 04-05 Gap Closure Truths (Plan 04-05 must_haves)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | OPTIONS from Origin https://pbox.puzzlesstool.online → API 200/204 mit Access-Control-Allow-Origin (G-04-2, G-05-2) | ✓ VERIFIED | `curl -X OPTIONS https://api.puzzlesstool.online/categories -H Origin:pbox` → HTTP/2 200 + `access-control-allow-origin: https://pbox.puzzlesstool.online` + `access-control-allow-credentials: true`; `api/app/core/config.py:22` default listet pbox |
| 2 | API BETTER_AUTH_JWKS_URL → https://pbox.puzzlesstool.online/api/auth/jwks 200 (G-04-3, G-05-3) | ✓ VERIFIED | `curl https://pbox.puzzlesstool.online/api/auth/jwks` → 200; Coolify env bestätigt per SUMMARY D2 |
| 3 | Prod web bundle calls https://api.puzzlesstool.online not localhost:8000 (G-04-1, G-05-1) | ✓ VERIFIED | `webapp/Dockerfile:12-15` ARG/ENV NEXT_PUBLIC_* vor `pnpm run build`; `deploy-web.yml:47-49` build-args; Scan aller 11 chunks auf /login → 0 `localhost:8000` matches; `https://pbox.puzzlesstool.online` baked in chunk `3_kf-m088ai6o.js` beweist Build-Arg-Mechanismus |
| 4 | GET https://pbox.puzzlesstool.online/apollo-onboard.png → 200 (G-04-5) | ✓ VERIFIED | `curl` → 200; `webapp/public/apollo-onboard.png` binary-identisch mit `brand/assets/apollo-onboard.png` (`cmp` → IDENTICAL) |
| 5 | Authenticated board loads 5 category columns without offline banner (UAT #7 unblock) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Infra-Blocker geschlossen, aber authenticated prod Browser-Session nötig — siehe behavior_unverified_items |
| 6 | Calendar settings loads connect CTA, not infinite 'Kalender wird geladen…' (UAT #15 unblock) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Infra-Blocker geschlossen, aber wizard rendern braucht authenticated session — siehe behavior_unverified_items |

**Score:** 4/6 04-05 truths verified (2 present, behavior-unverified — need authenticated prod UAT)

### Original Roadmap Success Criteria (Regression Check)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Kanban-Board mit Default-Kategorien + eigene Kategorien anlegen/umbenennen/einfärben/sortieren | ✓ VERIFIED (regression) | `board/page.tsx`, `board-dnd.tsx`, `board-column.tsx`, `categories-panel.tsx` unverändert; 62 vitest tests grün (up from 55) |
| 2 | DnD zwischen Kategorien + Item-Details öffnen/bearbeiten | ✓ VERIFIED (regression) | `board-dnd.tsx` + `use-optimistic-move.ts` + `item-modal.tsx` unverändert; `dnd.test.tsx` 8 + `modal.test.tsx` 9 tests grün; prod UAT re-run ausstehend (#8-11) |
| 3 | Auto-Saved Items erscheinen kategorisiert im Board | ✓ VERIFIED (regression) | `use-board-poll.ts` 10s poll + backoff; `poll.test.tsx` 11 tests grün; prod UAT re-run ausstehend (#16) |
| 4 | Login Email/Passwort + Session über Browser-Refresh | ✓ VERIFIED (regression) | `login-form.tsx` + SIGNUP_LOCKED sessionStorage fix; `auth.test.tsx` 8 tests grün; prod UAT #1-5 bereits pass; session refresh truth in echtem Browser verifiziert (UAT #4) |
| 5 | Google Calendar via separatem OAuth in Settings verbinden | ✓ VERIFIED (regression) | `calendar-wizard.tsx` 3-step + `lib/api/calendar.ts` 5 endpoints; `calendar.test.tsx` 5 tests grün; prod UAT re-run ausstehend (#15) |

**Original Score:** 5/5 truths verified at code level (regression check passed — no regressions from 04-05)

### Required Artifacts (04-05 modified)

| Artifact | Expected | Status | Details |
|----------|---------|--------|---------|
| `api/app/core/config.py` | CORS_ORIGINS default includes pbox | ✓ VERIFIED | Line 22: `http://localhost:3000,https://pbox.puzzlesstool.online,https://app.puzzlesstool.online` |
| `webapp/Dockerfile` | ARG/ENV NEXT_PUBLIC_* before build | ✓ VERIFIED | Lines 12-15: ARG + ENV for NEXT_PUBLIC_API_URL + NEXT_PUBLIC_APP_URL vor `pnpm run build` |
| `.github/workflows/deploy-web.yml` | build-args for GHCR image | ✓ VERIFIED | Lines 47-49: `NEXT_PUBLIC_API_URL=https://api.puzzlesstool.online` + `NEXT_PUBLIC_APP_URL=https://pbox.puzzlesstool.online` |
| `webapp/public/apollo-onboard.png` | Welcome page asset | ✓ VERIFIED | Binary-identisch mit `brand/assets/apollo-onboard.png` (cmp → IDENTICAL); prod GET → 200 |
| `webapp/app/login/login-form.tsx` | sessionStorage SIGNUP_LOCKED persistence | ✓ VERIFIED | Lines 16, 46-51, 85: `pb.signup_locked` flag überlebt Remount; `auth.test.tsx#SIGNUP_LOCKED` grün |

### Key Link Verification (04-05)

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `deploy-web.yml` build-args | `Dockerfile` ARG/ENV | `NEXT_PUBLIC_*` build-args → ARG → ENV → `pnpm run build` inlines | ✓ WIRED | Build-Arg-Mechanismus bewiesen durch `pbox.puzzlesstool.online` baked in chunk `3_kf-m088ai6o.js` |
| Coolify API `CORS_ORIGINS` | Starlette CORSMiddleware allow list | env override → config.py parser → allowlist | ✓ WIRED | Prod OPTIONS preflight → 200 + `access-control-allow-origin: https://pbox.puzzlesstool.online` |
| Coolify API `BETTER_AUTH_JWKS_URL` | FastAPI JWT verify fetch | env → Better Auth JWKS endpoint | ✓ WIRED | `curl https://pbox.puzzlesstool.online/api/auth/jwks` → 200 |
| `login-form.tsx` 409 handler | `sessionStorage` SIGNUP_LOCKED | `sessionStorage.setItem('pb.signup_locked','1')` on 409 → `useEffect` on mount reads + clears | ✓ WIRED | Unit test `auth.test.tsx#SIGNUP_LOCKED` grün |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Webapp vitest suite green | `cd webapp && pnpm test -- --run` | 10 files, 62 tests passed, 2.89s | ✓ PASS |
| SIGNUP_LOCKED unit test | `pnpm vitest run tests/auth.test.tsx -t SIGNUP_LOCKED` | 1 passed, 7 skipped | ✓ PASS |
| CORS preflight pbox → 200 | `curl -X OPTIONS https://api.puzzlesstool.online/categories -H Origin:pbox` | HTTP/2 200 + allow-origin header | ✓ PASS |
| JWKS reachable | `curl https://pbox.puzzlesstool.online/api/auth/jwks` | 200 | ✓ PASS |
| apollo-onboard.png prod | `curl https://pbox.puzzlesstool.online/apollo-onboard.png` | 200 | ✓ PASS |
| Signup locked server-side | `curl -X POST /api/auth/sign-up/email` | 409 | ✓ PASS |
| API health | `curl https://api.puzzlesstool.online/health` | `{"status":"ok"}` | ✓ PASS |
| pbox api health | `curl https://pbox.puzzlesstool.online/api/health` | `{"status":"ok"}` | ✓ PASS |
| No localhost:8000 in prod chunks | scan 11 chunks on /login | 0 matches | ✓ PASS |
| NEXT_PUBLIC_APP_URL baked | grep chunks for `pbox.puzzlesstool.online` | found in `3_kf-m088ai6o.js` | ✓ PASS |
| PNG binary identical | `cmp brand/assets/apollo-onboard.png webapp/public/apollo-onboard.png` | IDENTICAL | ✓ PASS |
| Authenticated board loads 5 columns | needs authenticated prod session | not run | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED |
| Calendar wizard Step 1 CTA | needs authenticated prod session | not run | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED |

### Probe Execution

No phase-declared probes (`scripts/*/tests/probe-*.sh`) for Phase 4. Verification relied on vitest + pytest + prod curls.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| BOARD-01 | 04-00, 04-01, 04-05 | Kanban-Board mit Default-Kategorien | ✓ SATISFIED | board/page.tsx + board-dnd.tsx + board-column.tsx; prod connectivity hergestellt (CORS+JWKS+NEXT_PUBLIC bake); prod UAT re-run ausstehend |
| BOARD-02 | 04-02, 04-03, 04-05 | Eigene Kategorien anlegen/umbenennen/einfärben/sortieren | ✓ SATISFIED | API + categories-panel.tsx; prod UAT re-run ausstehend |
| BOARD-03 | 04-02, 04-03 | DnD cross-category | ✓ SATISFIED (code) / prod UAT pending | REQUIREMENTS.md markiert [ ] Pending — prod UAT #10 ausstehend |
| BOARD-04 | 04-02, 04-03 | Item-Detail bearbeiten | ✓ SATISFIED (code) / prod UAT pending | REQUIREMENTS.md markiert [ ] Pending — prod UAT #9 ausstehend |
| CAP-05 | 04-00, 04-04 | Gespeicherte Items kategorisiert in WebApp | ✓ SATISFIED (code) / prod UAT pending | poll + new-item-feedback; prod UAT #16 ausstehend |
| CAL-01 | 04-04, 04-05 | Google Calendar OAuth in Settings | ✓ SATISFIED (code) / prod UAT pending | calendar-wizard.tsx + 5 API endpoints; prod UAT #15 ausstehend |
| AUTH-03 | 04-05, 04-07 | Signup-Lock nach erstem Account | ✓ SATISFIED | API 409 confirmed; isSignupLockedError hardened (04-07); prod UAT #6 r4 pass — VOICE copy sticky |
| OPS-01 | 04-05 | API/MCP/WebApp als separate Coolify Docker-Image-Apps | ✓ SATISFIED | prod curls bestätigen api.puzzlesstool.online + pbox.puzzlesstool.online erreichbar |
| OPS-02 | 04-05 | GitHub Actions baut Images nach GHCR + triggert Coolify-Deploy | ✓ SATISFIED | deploy-web.yml build-args; GHCR rebuild run 30773587394 succeeded per SUMMARY |

No orphaned requirements. Alle 9 requirement IDs aus 04-00..04-05 PLAN frontmatter in REQUIREMENTS.md abgedeckt.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `webapp/components/board/categories-panel.tsx` | 122 | hardcoded `#eaeaea` fallback | ℹ️ Info | Pre-existing (nicht durch 04-05 berührt); Fallback für null color, API validiert via regex |
| `webapp/middleware.ts` | n/a | Next.js 16 deprecation: `middleware` → `proxy` | ℹ️ Info | Pre-existing; build warnt aber funktioniert |
| `.github/workflows/deploy-web.yml` | 47-49 | build-args enthalten prod URLs (kein Secret) | ℹ️ Info | Public URLs, keine Secrets — T-04-05-03 accept per threat model |

Keine neuen TBD/FIXME/XXX/HACK/PLACEHOLDER in 04-05 geänderten Files. Keine leeren Implementierungen.

### Human Verification Required

Siehe `human_verification` frontmatter — 7 items need human testing auf prod:

1. **Prod UAT #7 Board Desktop** — 5 Kategorien, kein Offline-Banner (behavior_unverified truth)
2. **Prod UAT #15 Calendar Wizard** — Step 1 CTA sichtbar (behavior_unverified truth)
3. **Prod UAT #6 SIGNUP_LOCKED UI** — ✓ CLOSED (04-07 r4: VOICE copy sticky, sessionStorage pb.signup_locked=1)
4. **Prod UAT #8–11 Mobile/Modal/DnD/Bulk** — vorher blocked, jetzt unblocked
5. **Prod UAT #16 Poll + New-Item Feedback** — Echtzeit-Poll + Hermes
6. **Prod UAT #17 Cross-Origin Session** — pbox JWT von api akzeptiert
7. **Prod UAT #18 apollo-onboard.png** — Welcome-Page Render

Login: `uat@puzzless.local` / `UatTestPass1!` (first user; do not wipe unless re-testing AUTH-01).

### Gaps Summary

**Geschlossen (8/8):** G-04-1, G-04-2, G-04-3, G-04-4, G-04-5, G-05-1, G-05-2, G-05-3 — alle Blocker via prod curls + code inspection + prod UAT verifiziert. G-04-4 closed 2026-08-05 via 04-07: hardened isSignupLockedError + gsd-browser uat-04-07 r4 (browser_fill_form, VOICE copy sticky, pb.signup_locked=1).

**Verbleibend:** Keine offenen G-04-* Gaps.

**Behavior-dependent truths (2):** Board lädt 5 Kategorien + Calendar Wizard CTA — Infra-Blocker geschlossen, aber authenticated prod Browser-Session nötig. curl kann keine Cookie/JWT-Session simulieren. Siehe behavior_unverified_items.

**Regression:** Keine. 62 vitest tests grün (up from 55 — SIGNUP_LOCKED tests hinzugefügt). Alle Original-Artifacts unverändert. Prod routes erreichbar (/login 200, /board 307, /welcome 307, /settings 307).

**Status `human_needed`:** Alle automatisierbaren Checks (prod curls, unit tests, code inspection, build-arg wiring) PASS. Phase Goal auf Code-Ebene erreicht. Prod-UAT-Re-Run für User-Flow-Truths (#6, #7, #8-11, #15, #16, #17, #18) ausstehend — braucht authenticated Browser-Session + ggf. echten Google-Account + laufenden Hermes.

---

_Verified: 2026-08-03T00:11:00Z_
_Verifier: Claude (gsd-verifier)_
