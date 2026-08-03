---
status: testing
phase: 04-webapp
source: [04-VERIFICATION.md, 04-05-SUMMARY.md]
started: 2026-08-02T23:51:00Z
updated: 2026-08-03T00:12:00Z
environment: production (https://pbox.puzzlesstool.online)
tester: pending (prod re-run after 04-05)
uat_login: uat@puzzless.local / UatTestPass1!
account_reset: true
dbhub_wipe: user bb876133-c907-4e20-bcfb-192a6e5898d0 (prod-uat@puzzlessbox.local) cascade-deleted 2026-08-02T23:52Z
fresh_user: 7c5b1142-53fc-4b1d-b402-95123dbed78f (uat@puzzless.local)
re_verification: after-04-05-gap-closure
---

## Current Test

number: 1
name: Prod UAT #7 Board Desktop — 5 Kategorien, kein Offline-Banner
expected: |
  5 Default-Spalten rendern; Karten laden; kein 'Keine Verbindung' Banner
awaiting: user response

## Re-Verification Queue (after 04-05)

### RV-1. Prod UAT #7 Board Desktop
expected: 5 Default-Spalten rendern; Karten laden; kein Offline-Banner
result: [pending]

### RV-2. Prod UAT #15 Calendar Wizard
expected: 'Mit Google verbinden' Button; kein Endlos-'Kalender wird geladen…'
result: [pending]

### RV-3. Prod UAT #6 SIGNUP_LOCKED UI
expected: Register-Tab bleibt; VOICE copy 'Registrierung ist geschlossen…' via sessionStorage
result: [pending]

### RV-4. Prod UAT #8–11 Mobile/Modal/DnD/Bulk
expected: Mobile tabs + modal autosave + DnD + bulk move
result: [pending]

### RV-5. Prod UAT #16 Poll + New-Item Feedback
expected: Poll ~10s; Toast + pulse; Offline → Banner
result: [pending]

### RV-6. Prod UAT #17 Cross-Origin Session → API
expected: pbox JWT von api akzeptiert; /categories + /board-items 200
result: [pending]

### RV-7. Prod UAT #18 apollo-onboard.png auf Welcome
expected: Bild lädt auf /welcome nach Login
result: [pending]

## Prior Suite (2026-08-02)

## Tests

### 1. HTTPS Web Root + Login Brand-Hero (D-24)
expected: https://pbox.puzzlesstool.online/login over TLS; Apollo splash + Instrument Serif Wortmarke; Tabs Anmelden|Registrieren
result: pass
tested_by: gsd-browser + curl
notes: |
  LE cert CN=pbox.puzzlesstool.online (valid Aug–Oct 2026). HTTP→HTTPS 302.
  evaluate: hasApollo=true (apollo-splash.png), fonts=Instrument Serif, tabs=[Anmelden,Registrieren].

### 2. First-User Register (AUTH-01)
expected: Empty users → Registrieren → session → /welcome
result: pass
tested_by: gsd-browser
notes: |
  DB users=0 after wipe. Register uat@puzzless.local → wait url_contains /welcome (791ms).
  DB: user 7c5b1142… created.

### 3. First-Login Welcome → Board (D-31)
expected: /welcome → Los geht's → /board; pb.welcome.seen=true
result: pass
tested_by: gsd-browser
notes: |
  Click Los geht's → /board. localStorage pb.welcome.seen=true.

### 4. Session Persist + Offline Banner (AUTH-02 / CAP-05 partial)
expected: F5/reload keeps session on /board; no bounce to /login
result: pass
tested_by: gsd-browser
notes: |
  Re-navigate /board stays authenticated. After API failures settle: offline banner
  "Keine Verbindung. Apollo sucht nach dem Signal… Erneut versuchen" (VOICE OK).
  Board never loads columns (blocked by G-04-1/G-04-2) but session cookie holds.

### 5. Unauth Guard Middleware
expected: cookie-less /board|/settings → /login?next=…
result: pass
tested_by: curl
notes: |
  curl -D- /board → 307 Location: /login?next=%2Fboard
  curl -D- /settings → 307 Location: /login?next=%2Fsettings

### 6. Signup Lock after First User (AUTH-03 / D-25)
expected: Second register rejected; Register tab visible; VOICE SIGNUP_LOCKED copy
result: issue
reported: "API returns 409 SIGNUP_LOCKED (pass). UI VOICE copy not observed after second register — page remounted to /login?next=/welcome without inline locked message."
severity: major
tested_by: gsd-browser + curl
notes: |
  curl POST /api/auth/sign-up/email → 409 {"message":"SIGNUP_LOCKED"}.
  users still=1. Register tab remains visible. UI copy gap = G-04-4.

### 7. Board Desktop Layout (BOARD-01)
expected: 5 columns Inbox|Notizen|Links|Tasks|Termine; no H-scroll
result: issue
reported: "Board stuck loading then offline banner; zero category columns rendered. Root: client calls localhost:8000 + CORS rejects pbox origin."
severity: blocker
tested_by: gsd-browser
notes: |
  Chunk 1tfoa-oq-33e6.js contains baked `localhost:8000`.
  OPTIONS Origin:pbox → 400 "Disallowed CORS origin".
  CORS allows app.puzzlesstool.online + localhost:3000 only.

### 8. Board Mobile Layout (D-02)
expected: <768px tabs + single column; long-press Sheet
result: blocked
blocked_by: prior-phase
reason: "Board data layer never loads on prod — cannot exercise mobile columns/DnD Sheet"

### 9. Item Modal + Autosave (D-09/D-15 / BOARD-04)
expected: Card click → centered Dialog ≤560px; overlay-click no-close; Escape flush
result: blocked
blocked_by: prior-phase
reason: "No board cards without API"

### 10. DnD Handle vs Body + Reorder (BOARD-03 / D-16..D-23)
expected: Handle drag moves; body-click opens modal; fail revert toast
result: blocked
blocked_by: prior-phase
reason: "No board cards without API"

### 11. Bulk Multi-Select Move
expected: Checkbox ≥2 → bulk bar → sequential PATCH
result: blocked
blocked_by: prior-phase
reason: "No board cards without API"

### 12. Kategorien Verwalten (BOARD-02)
expected: Panel create/rename/reorder/color; cannot delete last
result: blocked
blocked_by: prior-phase
reason: "CategoriesPanel present but API unreachable; panel cannot load cats"

### 13. Theme Toggle (D-07)
expected: System/Light/Dark live; persists pb.theme
result: pass
tested_by: gsd-browser
notes: |
  Header toggle → pb.theme=light. Settings Dunkel → dark=true, pb.theme=dark.
  Persist across /board re-nav.

### 14. Settings Hub UI (D-26)
expected: Account + Appearance + Calendar sections
result: pass
tested_by: gsd-browser
notes: |
  /settings headings: Einstellungen, Account (uat@puzzless.local), Google Calendar,
  Darstellung (System/Hell/Dunkel), Sound toggle. Password change + Abmelden present.

### 15. Calendar OAuth Wizard UI (CAL-01)
expected: Step1 Mit Google verbinden visible; disconnect present
result: issue
reported: "Calendar section stuck on 'Kalender wird geladen…' — same API connectivity failure as board; cannot reach connect CTA."
severity: blocker
tested_by: gsd-browser
notes: |
  Google CLIENT_ID present on API Coolify env; UI wizard unreachable until CORS+API URL fixed.
  Full Google consent roundtrip still third-party dependent after fix.

### 16. Board Poll + New-Item Feedback (CAP-05)
expected: ~10s poll; toast+terracotta pulse; offline banner
result: issue
reported: "Offline banner + Erneut versuchen works (pass partial). Poll merge/toast/pulse cannot run — no successful API poll."
severity: blocker
tested_by: gsd-browser

### 17. Cross-Origin Session → API (AUTH-02 prod)
expected: pbox JWT accepted by api.puzzlesstool.online; categories/board-items 200
result: issue
reported: "CORS blocks pbox→api. Also BETTER_AUTH_JWKS_URL points to /.well-known/jwks.json (404); real JWKS at /api/auth/jwks. Even with CORS fix JWT verify may fail."
severity: blocker
tested_by: curl + Coolify env inspect
notes: |
  JWKS right: GET /api/auth/jwks → 200. Wrong: /.well-known/jwks.json → 404.
  API env BETTER_AUTH_JWKS_URL=https://pbox.puzzlesstool.online/.well-known/jwks.json

### 18. apollo-onboard.png Asset
expected: Welcome page onboard image loads
result: issue
reported: "GET /apollo-onboard.png → 404; /_next/image?url=%2Fapollo-onboard.png → 400. Splash/wordmark/avatar OK."
severity: minor
tested_by: curl + network

## Summary

total: 18
passed: 6
issues: 7
pending: 0
skipped: 0
blocked: 5

## Gaps

- gap_id: G-04-1
  truth: "WebApp client calls https://api.puzzlesstool.online (not localhost:8000)"
  status: failed
  reason: "User reported: Board stuck loading then offline. Chunk 1tfoa-oq-33e6.js bakes localhost:8000. Dockerfile builds without NEXT_PUBLIC_API_URL ARG; Coolify runtime env ignored by Next client bundle."
  severity: blocker
  test: 7
  artifacts:
    - path: "webapp/Dockerfile"
      issue: "No ARG/ENV NEXT_PUBLIC_API_URL before pnpm run build"
    - path: "webapp/lib/api-client.ts"
      issue: "Defaults to http://localhost:8000 when unset at build"
    - path: ".github/workflows/deploy-web.yml"
      issue: "Likely no build-args for NEXT_PUBLIC_*"
  missing:
    - "Pass NEXT_PUBLIC_API_URL=https://api.puzzlesstool.online and NEXT_PUBLIC_APP_URL=https://pbox.puzzlesstool.online as Docker build-args / GH Actions build-args"
    - "Rebuild+redeploy puzzlessbox-web image"
  root_cause: "Next.js inlines NEXT_PUBLIC_* at `pnpm run build`. webapp/Dockerfile builder stage has no ARG/ENV for NEXT_PUBLIC_API_URL; GHCR image therefore embeds default http://localhost:8000. Coolify runtime env cannot rewrite client JS."
  debug_session: "prod-uat-2026-08-03"

- gap_id: G-04-2
  truth: "API CORS allows Origin https://pbox.puzzlesstool.online"
  status: failed
  reason: "User reported: OPTIONS Origin:pbox → 400 Disallowed CORS origin. Default CORS_ORIGINS=localhost:3000,https://app.puzzlesstool.online — pbox missing; CORS_ORIGINS not set on Coolify API app."
  severity: blocker
  test: 7
  artifacts:
    - path: "api/app/core/config.py"
      issue: "CORS_ORIGINS default omits pbox.puzzlesstool.online"
  missing:
    - "Set Coolify API env CORS_ORIGINS=https://pbox.puzzlesstool.online (and localhost for local)"
    - "Or update default + redeploy API"
  root_cause: "D-01 chose pbox.puzzlesstool.online but CORS default + Coolify API env still list legacy app. subdomain. Starlette CORSMiddleware rejects unknown Origin with 400 Disallowed CORS origin."
  debug_session: "prod-uat-2026-08-03"

- gap_id: G-04-3
  truth: "API verifies JWTs via https://pbox.puzzlesstool.online/api/auth/jwks"
  status: resolved
  resolved_by: seed-agent Coolify env patch + API restart
  resolved_at: 2026-08-03
  reason: "User reported: BETTER_AUTH_JWKS_URL=https://pbox.puzzlesstool.online/.well-known/jwks.json returns 404; working path is /api/auth/jwks."
  severity: blocker
  test: 17
  artifacts:
    - path: "Coolify API app pasmduuzitoh21qipyq3ay1l env BETTER_AUTH_JWKS_URL"
      issue: "Wrong JWKS path — fixed to /api/auth/jwks"
  missing: []
  root_cause: "Better Auth exposes JWKS at /api/auth/jwks (confirmed 200). Cutover copied wrong well-known path into Coolify API env."
  debug_session: "prod-uat-2026-08-03"

- gap_id: G-04-4
  truth: "Second register shows VOICE copy 'Registrierung ist geschlossen. Apollo lässt nur den ersten Nutzer rein.'"
  status: failed
  reason: "User reported: API 409 SIGNUP_LOCKED OK, but UI did not show locked copy after submit (remounted to /login?next=/welcome)."
  severity: major
  test: 6
  artifacts:
    - path: "webapp/app/login/login-form.tsx"
      issue: "signupLocked state lost on remount / unexpected navigation after failed signup"
  missing:
    - "Keep register tab + SIGNUP_LOCKED_COPY visible without full navigation on 409"
  root_cause: "Server lock works. Client either navigates away after 409 (state remount clears signupLocked) or error shape not matched by isSignupLocked helper — needs repro after connectivity fixes."
  debug_session: "prod-uat-2026-08-03"

- gap_id: G-04-5
  truth: "Welcome page apollo-onboard.png loads"
  status: failed
  reason: "User reported: /apollo-onboard.png 404; image optimizer 400"
  severity: minor
  test: 18
  artifacts:
    - path: "webapp/public/"
      issue: "apollo-onboard.png missing from shipped image/public"
  missing:
    - "Add apollo-onboard.png to webapp/public (or fix welcome img src)"
  root_cause: "Welcome references /apollo-onboard.png but asset not in deployed public/ (splash/wordmark/avatar present)."
  debug_session: "prod-uat-2026-08-03"

## Account Reset Log

- Deleted prior user bb876133-c907-4e20-bcfb-192a6e5898d0 (prod-uat@puzzlessbox.local) + 4 sessions + 1 account via dbhub.
- Kept 5 NULL-owner seed categories.
- Registered fresh uat@puzzless.local (user 7c5b1142-53fc-4b1d-b402-95123dbed78f).
- Second signup rejected server-side (SIGNUP_LOCKED); users remain 1.

## Seeded Board Items (post-JWKS fix)

Auth: Better Auth JWT (after JWKS path patch). Ready for DnD/modal UAT once CORS + NEXT_PUBLIC_API_URL fixed.

| id | title | category |
|----|-------|----------|
| 8718bbe5-9248-475b-a5b8-81a4f31ad3b1 | UAT Inbox Card | Inbox |
| 9a529d2f-e2b8-4130-b078-7a3c9f62567e | UAT Modal Note | Notizen |
| ff312897-3ae3-423c-a2a0-836cc6728930 | UAT DnD Note A | Notizen |
| 97412f63-c7f2-4260-a0d0-8d920a8e16a0 | UAT DnD Note B | Notizen |
| 1d06ad30-b788-4fef-a358-b5b8075c8950 | UAT Link Card | Links |
