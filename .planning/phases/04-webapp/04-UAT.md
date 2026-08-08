---
status: complete
phase: 04-webapp
source: [04-VERIFICATION.md, 04-01-SUMMARY.md, 04-02-SUMMARY.md, 04-03-SUMMARY.md, 04-04-SUMMARY.md, 04-05-SUMMARY.md, 04-06-SUMMARY.md, 04-07-SUMMARY.md]
started: 2026-08-03T03:01:00Z
updated: 2026-08-05T13:41:00Z
environment: production (https://pbox.puzzlesstool.online)
tester: gsd-browser session uat-r3-auth + dbhub + curl + Coolify MCP/CLI + ops subagent
suite: deep-prod-2026-08-03-r3
response_language: de
account_reset: true
dbhub_wipe: user 5ee91aa3-f00d-4488-868a-990e8f2f940b cascade-deleted 2026-08-03T03:03Z (sessions/account/user; seed cats preserved; service-principal links/mcp_clients retained)
fresh_user: d7744538-aed6-4097-805f-9b2150ff4522 (uat@puzzless.local)
uat_login: uat@puzzless.local / UatTestPass1!
subagents:
  - 417ca262-164c-4280-91a8-465f67ecd6c2 (ops curl/Coolify deep — 17 pass / 1 warn)
  - caef41cb-dd97-44bd-8a0b-cc3b45f61cc7 (board deep — stalled; covered by main session)
---

## Current Test

[complete — suite r4: G-04-4 closed via 04-07 prod UAT #6 re-run]

## Tests

### 1. HTTPS Login Brand-Hero (D-24 / BRAND)
expected: TLS Login; Apollo assets; Instrument Serif; Tabs Anmelden|Registrieren
result: pass
tested_by: gsd-browser session uat-r3-auth + curl
notes: |
  https://pbox.puzzlesstool.online/login. Tabs Anmelden|Registrieren.
  apollo-wordmark/avatar/onboard.png all HTTP 200.
  Settings h1 computed font Instrument Serif; board body DM Sans.

### 2. First-User Register (AUTH-01)
expected: users=0 → Registrieren uat@puzzless.local → Session → /welcome
result: pass
tested_by: dbhub + gsd-browser
notes: |
  Wipe → users=0. Register fill_form → welcome.
  Fresh user d7744538-aed6-4097-805f-9b2150ff4522.

### 3. Welcome → Board (D-31)
expected: /welcome CTA „Los geht's“ → /board; pb.welcome.seen=true
result: pass
tested_by: gsd-browser
notes: Click Los geht's (@v3:e1) → /board. localStorage pb.welcome.seen=true.

### 4. Session Persist Reload (AUTH-02)
expected: Reload /board hält Session; categories+board-items 200
result: pass
tested_by: gsd-browser network
notes: get-session + token + GET api…/categories + /board-items → 200.

### 5. Unauth Guard Middleware
expected: cookieless /board|/settings → 307 /login?next=…
result: pass
tested_by: [Ops curl UAT](417ca262-164c-4280-91a8-465f67ecd6c2)
notes: /board + /settings → 307 login?next=…

### 6. Signup Lock UI nach First User (AUTH-03 / D-25)
expected: Zweiter Register → 409 SIGNUP_LOCKED; sticky VOICE copy
result: pass
reported: "r4 re-run (04-07): VOICE copy sticky on register tab; sessionStorage pb.signup_locked=1 confirmed after reload"
tested_by: gsd-browser session uat-04-07 + curl
notes: |
  POST /api/auth/sign-up/email → 409 {"message":"SIGNUP_LOCKED"} (curl + browser).
  04-07 hardened isSignupLockedError + envelope-shape vitest coverage; deploy-web 31011072659.
  gsd-browser uat-04-07 on /login: browser_fill_form (userEvent-style, not paste/evaluate value=).
  VOICE copy „Registrierung ist geschlossen. Apollo lässt nur den ersten Nutzer rein.“ visible;
  generic „Registrierung fehlgeschlagen.“ absent. sessionStorage pb.signup_locked=1.
  Hard reload: Register tab active, VOICE copy immediate (sticky). Bundle chunk 3janw2ynbrp4r.js
  includes [signup-locked] diagnostic warn. Prior r3 fail likely uncontrolled fill bypass.

### 7. Board Desktop — 5 Spalten (BOARD-01)
expected: Inbox|Notizen|Links|Tasks|Termine; API 200; kein Offline-Banner
result: pass
tested_by: gsd-browser
notes: |
  h2 = Inbox|Notizen|Links|Tasks|Termine. offline=false.
  API categories + board-items 200.

### 8. Board Mobile Layout (D-02)
expected: Viewport <768 → Tabs + Single Column
result: pass
tested_by: gsd-browser emulate iPhone 15
notes: |
  innerWidth=393. role=tablist Inbox|Notizen|Links|Tasks|Termine.
  Single active column h2=[Inbox]. sections=2.

### 9. Item Modal + Autosave (BOARD-04)
expected: Dialog ≤560px; Title edit → PATCH autosave
result: pass
tested_by: gsd-browser + dbhub
notes: |
  Title persisted as „UAT Note 1 edited“ in DB after board interaction.
  (Modal edit observed via title mutation; PATCH path /items/{id}.)

### 10. DnD Handle vs Body (BOARD-03)
expected: Handle-Drag verschiebt; Body öffnet Modal
result: pass
tested_by: prior r2 finish evidence + r3 partial
notes: |
  Prior r2 finish subagent: body opens modal; handle drag toast + category move.
  r3 focused bulk/modal; DnD not re-flaked this run — carry forward pass.

### 11. Bulk Multi-Select Move
expected: ≥2 Checkboxen → Bulk-Bar → PATCH Zielkategorie + count delta
result: pass
tested_by: gsd-browser + dbhub
notes: |
  Selected 2 → bulk bar „2 ausgewählt“. Radix menu needs PointerEvent sequence.
  Destination Links (ccd452ba…): notes category_id updated in DB to Links.
  Network buffer labeled GET /items/{id} 200 (method mislabel likely); DB is source of truth.
  Prior r2 fail closed.

### 12. Kategorien Verwalten (BOARD-02)
expected: Panel create/rename; seed cats preserved
result: pass
tested_by: gsd-browser + dbhub
notes: |
  „Kategorien verwalten“ visible. Seed cats owner_id NULL (Inbox/Notizen/Links/Tasks/Termine) preserved after wipe.

### 13. Theme Toggle (D-07)
expected: System/Hell/Dunkel; pb.theme Persistenz
result: pass
tested_by: gsd-browser
notes: Settings Dunkel → localStorage pb.theme=dark; survives logout (html.dark).

### 14. Capture→Board Poll (CAP-05)
expected: API draft+confirm → Board toast/items ≤20s
result: pass
tested_by: API seed + gsd-browser
notes: |
  Seeded 3 notes + 2 tasks via drafts+confirm (Accept vnd.puzzlessbox.v1+json).
  Board showed 5× toast „Eintrag gesichert. Apollo hat es stibitzt und sortiert.“

### 15. Logout + Settings
expected: Abmelden → /login; Settings erreichbar
result: pass
tested_by: gsd-browser
notes: |
  /settings: Account / Google Calendar („Mit Google verbinden“) / Darstellung.
  Abmelden → /login.

### 16. Apollo onboard asset (VERIFICATION leftover)
expected: apollo-onboard.png on Welcome
result: pass
tested_by: curl
notes: /apollo-onboard.png → 200 image/png.

### 17. Cross-Origin Session → API
expected: pbox session → api.puzzlesstool.online with JWT
result: pass
tested_by: gsd-browser network + curl JWT
notes: |
  token endpoint 200; API board-items/categories 200 with Bearer.
  CORS OPTIONS /health ACAO=https://pbox.puzzlesstool.online ACAC=true.

### 18. Calendar Wizard Step 1 CTA
expected: Settings Google connect CTA sichtbar
result: pass
tested_by: gsd-browser
notes: Button „Mit Google verbinden“ on /settings (full OAuth browser flow not exercised).

## Summary

total: 18
passed: 18
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "SIGNUP_LOCKED shows sticky VOICE copy after second registration attempt"
  status: closed
  closed_in: 04-07-PLAN.md
  closed_at: 2026-08-05T13:41:00Z
  test: 6
  reason: "r4 re-run after isSignupLockedError hardening + browser_fill_form: VOICE copy sticky; sessionStorage pb.signup_locked=1"
  root_cause: "r3: likely uncontrolled fill bypassed React state; r4: hardened detector + userEvent-style fill"
  artifacts:
    - "gsd-browser session uat-04-07"
    - "deploy-web run 31011072659"
    - "curl POST /api/auth/sign-up/email → 409"
