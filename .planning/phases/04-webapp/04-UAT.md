---
status: partial
phase: 04-webapp
source: [04-VERIFICATION.md, 04-01-SUMMARY.md, 04-02-SUMMARY.md, 04-03-SUMMARY.md, 04-04-SUMMARY.md, 04-05-SUMMARY.md]
started: 2026-08-03T01:36:00Z
updated: 2026-08-03T02:14:00Z
environment: production (https://pbox.puzzlesstool.online)
tester: gsd-browser (agent-driven deep UAT) + dbhub + curl + Coolify
suite: deep-prod-2026-08-03-r2
response_language: de
account_reset: true
dbhub_wipe: user 01557773-532f-4606-aec3-a7a3613231be cascade-deleted 2026-08-03T01:38Z
fresh_user: 75d9d55e-78ca-45c4-9270-3bf08f0a99d3 (uat@puzzless.local)
uat_login: uat@puzzless.local / UatTestPass1!
subagents:
  - c8570ed9-cae5-4e60-8648-ffe2ce67c5c3 (Phase 5 ops)
  - 2dab9a70-ec2c-4885-8be2-088006e36a1b (Phase 4 deep — DnD/bulk flaky)
  - 310b1fc3-ef29-4c8a-be83-0de14b0080e8 (Phase 4 finish — 9 pass / 1 issue bulk)
---

## Current Test

[partial — UAT #11 bulk destination: code closed via 04-06; await web deploy + re-verify]

## Tests

### 1. HTTPS Login Brand-Hero (D-24 / BRAND)
expected: TLS Login; Apollo assets; Instrument Serif; Tabs Anmelden|Registrieren
result: pass
tested_by: gsd-browser session uat-04-05
notes: |
  https://pbox.puzzlesstool.online/login. fonts include Instrument Serif + DM Sans.
  Tabs Anmelden|Registrieren. apollo-wordmark + avatar assets load.

### 2. First-User Register (AUTH-01)
expected: users=0 → Registrieren uat@puzzless.local → Session → /welcome
result: pass
tested_by: gsd-browser + dbhub
notes: |
  dbhub wipe → users=0. Register via DOM force on Registrieren tab (radix pointer events).
  Fresh user 75d9d55e-78ca-45c4-9270-3bf08f0a99d3. Redirect /welcome.

### 3. Welcome → Board (D-31)
expected: /welcome CTA „Los geht's“ → /board; pb.welcome.seen=true
result: pass
tested_by: gsd-browser
notes: Click Los geht's (@v3:e1) → /board. localStorage pb.welcome.seen=true.

### 4. Session Persist Reload (AUTH-02)
expected: Reload /board hält Session; categories+board-items 200
result: pass
tested_by: gsd-browser network
notes: Re-navigate /board while cookied; get-session + token + API 200.

### 5. Unauth Guard Middleware
expected: cookieless /board|/settings → 307 /login?next=…
result: pass
tested_by: curl
notes: |
  /board → 307 login?next=%2Fboard
  /settings → 307 login?next=%2Fsettings

### 6. Signup Lock UI nach First User (AUTH-03 / D-25)
expected: Zweiter Register → 409 SIGNUP_LOCKED; sticky copy
result: pass
tested_by: curl + [Deep Phase4 board UAT](2dab9a70-ec2c-4885-8be2-088006e36a1b)
notes: |
  POST /api/auth/sign-up/email second@… → 409 {"message":"SIGNUP_LOCKED"}.
  UI copy: „Registrierung ist geschlossen. Apollo lässt nur den ersten Nutzer rein.“

### 7. Board Desktop — 5 Spalten (BOARD-01)
expected: Inbox|Notizen|Links|Tasks|Termine; API 200; kein Offline-Banner
result: pass
tested_by: gsd-browser
notes: |
  5 h2 headings. GET api.puzzlesstool.online/categories + /board-items → 200.
  offlineBanner=false. Empty-state Apollo art per column when empty.

### 8. Board Mobile Layout (D-02)
expected: Viewport <768 → Tabs + Single Column
result: pass
tested_by: gsd-browser emulate iPhone 15
notes: |
  innerWidth=393. role=tablist Inbox|Notizen|Links|Tasks|Termine.
  Single active column (Inbox heading). sections≈2.

### 9. Item Modal + Autosave (BOARD-04)
expected: Dialog ≤560px; Title edit → PATCH autosave
result: pass
tested_by: gsd-browser + API logs
notes: |
  Dialog „Eintrag bearbeiten“ width=512. Title → …RENAMED.
  API PATCH /items/2549b528-… → 200. Title persists on board.

### 10. DnD Handle vs Body (BOARD-03)
expected: Handle-Drag verschiebt; Body öffnet Modal
result: pass
tested_by: [Finish Phase4 UI UAT](310b1fc3-ef29-4c8a-be83-0de14b0080e8) (+ prior deep flaky)
notes: |
  Body click opens modal. Finish-subagent: browser_drag → toast „You have dropped the item“;
  moved list 9823… → ccd452… (Tasks→Links). Prior deep session flaky — overruled by finish evidence.

### 11. Bulk Multi-Select Move
expected: ≥2 Checkboxen → Bulk-Bar → PATCH Zielkategorie
result: issue
severity: major
reported: "2 cards selected; bulk bar showed '2 ausgewählt'; no PATCH captured, counts not verified"
tested_by: [Finish Phase4 UI UAT](310b1fc3-ef29-4c8a-be83-0de14b0080e8) + [Deep Phase4 board UAT](2dab9a70-ec2c-4885-8be2-088006e36a1b)
notes: |
  Multi-select + bulk bar works. Destination commit / PATCH + count-delta still not verified
  across both corroborators.

### 12. Kategorien Verwalten (BOARD-02)
expected: Panel create/rename; seed cats preserved
result: pass
tested_by: gsd-browser + [Finish Phase4 UI UAT](310b1fc3-ef29-4c8a-be83-0de14b0080e8)
notes: |
  Panel Anlegen + Inbox|Notizen|Links|Tasks|Termine. Finish created category „UAT Extra“.
  Seed cats owner_id NULL preserved after wipe.

### 13. Theme Toggle (D-07)
expected: System/Hell/Dunkel; pb.theme Persistenz
result: pass
tested_by: gsd-browser + [Finish Phase4 UI UAT](310b1fc3-ef29-4c8a-be83-0de14b0080e8)
notes: |
  Settings System|Hell|Dunkel. pb.theme persists (dark/system observed across sessions).

### 14. Capture→Board Poll (CAP-05)
expected: API draft+confirm → Board toast/items ≤20s
result: pass
tested_by: curl JWT + gsd-browser
notes: |
  POST /drafts + /confirm ×5 (notes/tasks). Board shows items + toast
  „Eintrag gesichert. Apollo hat es stibitzt und sortiert.“

### 15. Logout + Settings
expected: Abmelden → /login; Settings erreichbar
result: pass
tested_by: [Finish Phase4 UI UAT](310b1fc3-ef29-4c8a-be83-0de14b0080e8) + [Deep Phase4 board UAT](2dab9a70-ec2c-4885-8be2-088006e36a1b)
notes: |
  /settings: Account/Google Calendar/Darstellung. Abmelden → /login.
  Logged-out /board → /login?next=%2Fboard. Session reload on /board stays authed.

## Summary

total: 15
passed: 14
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "Bulk multi-select moves ≥2 items into chosen category"
  status: failed
  reason: "2 cards selected; bulk bar showed '2 ausgewählt'; no PATCH captured, counts not verified"
  severity: major
  test: 11
  root_cause: ""
  artifacts:
    - "session uat-04-finish ([Finish Phase4 UI UAT](310b1fc3-ef29-4c8a-be83-0de14b0080e8))"
    - "session uat-04-deep ([Deep Phase4 board UAT](2dab9a70-ec2c-4885-8be2-088006e36a1b))"
  missing: ["destination picker commit", "sequential PATCH evidence", "count delta"]
  debug_session: ""
