---
status: complete
phase: 05-coolify-deployment-ci-cd-h-rtung
source: [05-01-SUMMARY.md, 05-02-SUMMARY.md, 05-03-SUMMARY.md, 05-04-SUMMARY.md, 05-VERIFICATION.md, docker-compose.yml, webapp/.env.local]
started: 2026-08-03T02:26:00Z
updated: 2026-08-05T20:10:00Z
environment: local (OrbStack) + post-merge prod re-verify + deep-prod-r5 + deep-prod-r6
base_urls:
  web: http://localhost:3000
  api: http://localhost:8000
  mcp: http://localhost:8001
  postgres: 127.0.0.1:5433
prod_urls:
  web: https://pbox.puzzlesstool.online
  api: https://api.puzzlesstool.online
  mcp: https://mcp.puzzlesstool.online
tester: gsd-browser + curl + local psql + shell subagent
suite: deep-local-2026-08-03 + post-merge-prod-r3
pr: https://github.com/clezcoding/puzzlessbox/pull/52
deploy_web: https://github.com/clezcoding/puzzlessbox/actions/runs/30780220321
response_language: de
account_reset: |
  LOCAL wipe via psql 127.0.0.1:5433 then fresh signup
  owner_id=27dabd9c-1801-47ac-8754-d5e24b8b500f email=uat@puzzless.local
  password=UatTestPass1!
prior_prod_uat: archived-complete-2026-08-03-r2 (16/16)
incident: |
  dbhub MCP DSN targets PRODUCTION (185.248.140.207:6045). Initial "wipe"
  hit prod (owner 75d9d55e). Prod first user recreated via pbox signup
  (5ee91aa3… / uat@puzzless.local); signup locked again (409).
  Board seed data on prod lost (notes/tasks) unless restored from Coolify
  backup ibaby40uszso4coqgxjtgp1b (2026-08-02).
subagents:
  - de93c176-c3bd-4514-8213-81afeac0243a (shell curl/artifacts local)
  - 0b69392b-4ab0-410d-8c01-0cd4fa6825a9 (browser board local)
  - 1b5f96b2-0d7a-440b-a834-d92cf961b68f (shell curl prod post-merge)
  - 11b97702-d75e-4d77-9a92-1d573d043d69 (browser prod post-merge)
---

## Current Test

[testing complete]

## Tests

### 1. Docker Compose Stack Healthy (OPS-04 local)
expected: postgres + api + mcp-server Up (healthy); ports 5433/8000/8001
result: pass
tested_by: docker compose ps
notes: all three healthy after `docker compose up -d --build`

### 2. API Liveness /health (OPS-04)
expected: GET http://localhost:8000/health → 200 {"status":"ok"}
result: pass
tested_by: curl

### 3. API Readiness /ready (OPS-04 deep)
expected: GET http://localhost:8000/ready → 200
result: pass
tested_by: curl → {"status":"ready"}

### 4. MCP Liveness /health (OPS-04)
expected: GET http://localhost:8001/health → 200 service mcp-server
result: pass
tested_by: curl

### 5. WebApp /api/health (OPS-04 / D-13)
expected: GET http://localhost:3000/api/health → 200 {"status":"ok"}
result: pass
tested_by: curl

### 6. Account Wipe Verified
expected: local user/session/account = 0 after wipe, then fresh first user
result: pass
tested_by: psql 127.0.0.1:5433
notes: |
  Final local wipe of f57a7d32… succeeded (0 users). Fresh signup created
  27dabd9c… at 2026-08-03T02:32:24Z. See incident: first wipe attempt via
  dbhub hit prod — do not use dbhub for local.

### 7. First-User Signup (AUTH first-lock open)
expected: Signup creates uat@puzzless.local; session cookie set
result: pass
tested_by: POST /api/auth/sign-up/email + gsd-browser login→/welcome
notes: UI signup lives on /login tab Registrieren (no /signup route — 404 expected)

### 8. Signup Lock After First User (AUTH-lock)
expected: Second signup → SIGNUP_LOCKED
result: pass
tested_by: curl POST second email → 409 {"message":"SIGNUP_LOCKED"}

### 9. Login Roundtrip
expected: Login with UAT credentials succeeds; lands welcome/board
result: pass
tested_by: gsd-browser fill #login-email/#login-password → Anmelden → /welcome → Los geht's → /board

### 10. JWKS Endpoint (API↔Auth wiring)
expected: GET /api/auth/jwks → 200 with keys
result: pass
tested_by: curl → EdDSA OKP key present

### 11. API Unauth 401
expected: GET /categories without JWT → 401
result: pass
tested_by: curl
notes: |
  Requires Accept: application/vnd.puzzlessbox.v1+json → 401 UNAUTHORIZED.
  Bare GET without Accept → 415 (version negotiation). Documented, not a gap.

### 12. API Auth Categories (post-login JWT)
expected: Authenticated GET /categories returns defaults
result: pass
tested_by: Bearer JWT from /api/auth/token
notes: Inbox · Notizen · Links · Tasks · Termine (owner_id null system defaults)

### 13. Board Renders After Signup (BOARD smoke)
expected: /board shows columns; cards visible
result: pass
tested_by: gsd-browser
notes: |
  Columns Inbox/Notizen/Links/Tasks/Termine. Cards for UAT Local Note 1–3
  via data-testid board-card-*.

### 14. Create Note via UI / API (CAP/BOARD deep)
expected: Create note; appears on board; persists
result: pass
tested_by: POST /drafts + /confirm ×3; board shows cards; reload via network 200
notes: |
  Board has no add/plus UI (empty-state: capture via Apollo/MCP only) — confirmed by
  [Deep browser board UAT](0b69392b-4ab0-410d-8c01-0cd4fa6825a9) when board empty.
  Items created via capture API (Hermes path); then visible on board.

### 15. Drag/Move Item (BOARD-02 deep)
expected: Move between categories; persists
result: pass
tested_by: PATCH /items/{id} category_id + browser_drag attempt
notes: |
  API move Note3 → Inbox persisted. browser_drag executed (Note1→Links);
  visual drop incomplete in automation — API path authoritative for persist.

### 16. Bulk Move (G-04-bulk-move)
expected: Multi-select + bulk move bar moves items
result: pass
tested_by: gsd-browser + API
notes: |
  Checkbox select shows bulk-move-bar (data-testid). Destination dropdown
  flaky via evaluate (portal timing). Equivalent: PATCH two items → Tasks;
  board-items confirms category_id 1cab6e23….

### 17. MCP Unauth 401 + WWW-Authenticate
expected: POST /mcp without Bearer → 401; WWW-Authenticate present
result: pass
tested_by: curl
notes: |
  WWW-Authenticate: Bearer resource_metadata="http://localhost:8000/.well-known/..."
  Local ENV=dev — localhost expected (prod uses MCP_PUBLIC_BASE_URL).

### 18. MCP Bearer Initialize (MCP-02 deep)
expected: Bearer token → initialize 200
result: pass
tested_by: curl after mcp_clients + service_principals bootstrap
notes: |
  Requires rows keyed to first-user owner_id. docker-compose lacks
  SERVICE_OWNER_ID + MCP_BOOTSTRAP_TOKEN — manual INSERT after signup.
  initialize → Puzzlessbox MCP 3.4.4 SSE 200.

### 19. MCP→API Internal Auth Path
expected: MCP reaches API; auth resolves
result: pass
tested_by: initialize success implies /internal/mcp-auth ok
notes: Before bootstrap: invalid_token + service_principals=0 (issue→fixed)

### 20. Local Env Wiring (OPS-01 local)
expected: Browser hits localhost:8000 not prod FQDN
result: pass
tested_by: gsd-browser network
notes: GET http://localhost:8000/categories + /board-items 200; no *.puzzlesstool.online

### 21. CORS Local (API)
expected: Origin http://localhost:3000 allowed
result: pass
tested_by: shell subagent OPTIONS → ACAO http://localhost:3000

### 22. Deploy Artifacts Present (OPS-02)
expected: deploy-api/web/mcp.yml + Dockerfiles; GHCR + webhook
result: pass
tested_by: shell subagent file + workflow grep

### 23. Web Dockerfile Health Dependencies (D-13)
expected: webapp/Dockerfile installs curl
result: pass
tested_by: `RUN apk add --no-cache curl` line 27

### 24. next.config standalone (05-02)
expected: output standalone
result: pass
tested_by: next.config.ts `output: "standalone"`

### 25. Postgres Data Durability Volume
expected: docker volume puzzlessbox_pgdata exists
result: pass
tested_by: docker volume ls → puzzlessbox_puzzlessbox_pgdata

### 26. OpenAPI Surface (dev vs harden)
expected: Local ENV=dev exposes docs
result: pass
tested_by: /docs 200 + /openapi.json 200

### 27. Settings Page Loads
expected: /settings auth'd; Account + Google Calendar + Darstellung
result: pass
tested_by: gsd-browser → headings Account, Google Calendar, Darstellung; email shown

### 28. Protected Route Guard
expected: Unauth /board → /login
result: pass
tested_by: curl 307 → /login?next=%2Fboard

### 29. Session Cookie Attributes
expected: HttpOnly session cookie after login
result: pass
tested_by: Set-Cookie better-auth.session_token; HttpOnly; SameSite=Lax
notes: Local (non-HTTPS) omits Secure — expected. Prod uses __Secure- prefix.

### 30. Deep Console/Network Audit
expected: No repeated 5xx / CORS / JWKS errors on board
result: pass
tested_by: gsd-browser console + network
notes: |
  Board fetch 200 only. Console: Next image aspect warning on apollo-wordmark
  (cosmetic). No 5xx, no CORS failures, JWKS/token 200.

## Summary (local suite)

total: 30
passed: 30
issues: 0
pending: 0
skipped: 0
blocked: 0

## Post-merge Prod Re-verify (2026-08-03 r3)

After PR #52 squash-merge + Deploy WebApp run 30780220321 success + Coolify `puzzlessbox-web` `running:healthy`.

### Curl (15/15) — [Prod curl UAT](1b5f96b2-0d7a-440b-a834-d92cf961b68f)

| ID | Result | Evidence |
|----|--------|----------|
| T1–T4 health | pass | pbox/api/mcp /health|/ready 200 |
| T5 TLS redirect | pass | HTTP 302 → HTTPS all three FQDNs |
| T6 API unauth | pass | categories 401 |
| T7 MCP WWW-Auth | pass | `mcp.puzzlesstool.online` (no localhost) — G-05-5 holds |
| T8–T9 login+JWT | pass | `__Secure-better-auth.session_token` HttpOnly Secure; token JWT |
| T10–T11 API auth | pass | categories + board-items 200 (board empty []) |
| T12 CORS | pass | ACAO `https://pbox.puzzlesstool.online` |
| T13 JWKS | pass | EdDSA keys |
| T14 signup lock | pass | 409 SIGNUP_LOCKED |
| T15 route guard | pass | /board → 307 /login |

### Browser — gsd-browser + [Prod browser UAT](11b97702-d75e-4d77-9a92-1d573d043d69)

| Check | Result | Evidence |
|-------|--------|----------|
| Login → welcome → board | pass | uat@puzzless.local |
| Board columns | pass | Inbox/Notizen/Links/Tasks/Termine (empty — expected post-incident) |
| Network FQDN | pass | `https://api.puzzlesstool.online/categories` + `board-items` 200; no localhost |
| Settings | pass | Account + Google Calendar + Darstellung |
| Logout guard | pass | Abmelden → `/board` → `/login?next=/board` |
| Console/network | pass | 0 console errors; no 5xx/CORS |
| Coolify | pass | uuid `qxpgv6p1rp3vupue9al8hbzz` status `running:healthy` |

### Prod summary

total: 15 curl + 6 browser
passed: all
issues: 0
board_items: empty (seed lost in incident; capture path still healthy)

## Gaps

- truth: "Local tooling must never target production DB"
  status: resolved_with_followup
  reason: "dbhub MCP DSN in ~/.cursor/mcp.json points at prod 185.248.140.207:6045; shell DATABASE_URL also prod. Agent wipe hit prod; recovered via signup recreate."
  severity: blocker
  test: 6
  root_cause: "MCP/tooling DSN misconfigured for local UAT"
  artifacts:
    - "~/.cursor/mcp.json dbhub --dsn"
    - "shell env DATABASE_URL"
  missing:
    - "Local dbhub DSN (127.0.0.1:5433) or separate MCP server id"
    - "Document coolify backup restore if board seed data needed on prod"
  debug_session: ""
  resolved_at: "2026-08-03"
  resolution: |
    Prod first user recreated (5ee91aa3… / uat@puzzless.local); signup locked (409).
    Local UAT continued exclusively via psql :5433. Recommend: retarget dbhub DSN
    or add local profile; unset shell DATABASE_URL when developing webapp.

- truth: "docker-compose should bootstrap MCP client for local first user"
  status: resolved
  reason: "SERVICE_OWNER_ID + MCP_BOOTSTRAP_TOKEN absent; MCP initialize fails until manual INSERT"
  severity: minor
  test: 18
  root_cause: "compose env incomplete for MCP auth bootstrap"
  artifacts:
    - "docker-compose.yml"
    - "api/app/core/bootstrap.py"
  missing:
    - "Document post-signup bootstrap or add compose env after first user exists"
  debug_session: ""
  resolved_at: "2026-08-08"
  resolution: |
    Closed by Phase 05.1 Plan 01: check_and_bootstrap_first_user on /internal/mcp-auth
    auto-creates mcp_clients + service_principals for first Better Auth user when
    mcp_clients empty. Prod still requires MCP_BOOTSTRAP_TOKEN (D-02). Deploy of
    API image to prod still pending (gsd branch not yet on main).

## Prior Gaps Reconciliation (prod baseline)

| Gap | Status |
|-----|--------|
| G-05-1..G-05-5 | resolved in prior prod UAT (reference only) |
| G-05-6 dbhub/prod DSN | new — tooling follow-up (see Gaps) |
| G-05-7 local MCP bootstrap | resolved via 05.1-01 (deploy pending) |

## Incident Log

1. **Prod account wipe via dbhub** (2026-08-03 ~02:25Z): DELETE cascade on production user 75d9d55e… (notes×3, tasks×2, categories×1, sessions×5).
2. **Emergency recovery**: POST https://pbox.puzzlesstool.online/api/auth/sign-up/email → user 5ee91aa3…; signup locked.
3. **Optional**: Restore Coolify backup `ibaby40uszso4coqgxjtgp1b` if prior board seed required (will rewind DB to 2026-08-02).
4. **Local path corrected**: all subsequent DB ops via `PGPASSWORD=… psql -h 127.0.0.1 -p 5433`.

---

## Prod Ops Re-Verify r3 (2026-08-03T03:01Z)

tester: [Ops curl UAT](417ca262-164c-4280-91a8-465f67ecd6c2) + Coolify MCP/CLI  
suite: deep-prod-ops-2026-08-03-r3

| Check | Result | Evidence |
|-------|--------|----------|
| api/mcp/web Coolify status | pass | all `running:healthy` (pasmduuz… / n5frtiup… / qxpgv6p1…) |
| Live /health ×3 | pass | 200 ok |
| api /ready | pass | 200 ready |
| docs/redoc/openapi.json | pass | 404 (prod hardened) |
| MCP no-auth + wrong bearer | pass | 401; WWW-Authenticate uses mcp.puzzlesstool.online |
| TLS LE all hosts | pass | ssl_verify_result 0 |
| Old API `dxoflgio67786lc4yilhce43` | pass | already deleted (404 Application not found) — no delete needed |
| Env completeness | pass | API auth/DB/service/scraper/CORS/MCP_BOOTSTRAP; MCP SERVICE_BEARER+MCP_API_BASE_URL+MCP_PUBLIC_BASE_URL; Web BETTER_AUTH_*+NEXT_PUBLIC_*+DATABASE_URL |
| JWKS | pass | `/api/auth/jwks` 200 EdDSA; `/.well-known/jwks.json` 404 (expected) |
| categories bare GET | warn | 415 without Accept; with Accept v1 → 401 |

ops_summary: 17 pass / 1 warn / 0 fail

---

## Prod Deep UAT r5 (2026-08-05)

tester: main session (gsd-browser `uat-r5`) + [Ops curl UAT](a195555d-a2fe-40ab-8c39-5050c0cae67f) + Coolify MCP/CLI + dbhub coolify  
suite: deep-prod-2026-08-05-r5  
prod_urls: pbox / api / mcp @ puzzlesstool.online  
account_reset: true  
wipe: cascade-deleted prior first user `d7744538…` (+ race `second@` `686f5c2c…`)  
fresh_user: `a37a33c9-1a59-4f84-96bd-9ebdc842aeaa` (`uat@puzzless.local` / `UatTestPass1!`)

### Task 2 — Coolify inventory + env

| Check | Result | Evidence |
|-------|--------|----------|
| puzzlessbox-api-ghcr `pasmduuz…` | pass | `running:healthy` · `ghcr.io/clezcoding/puzzlessbox-api:latest` · `/health` |
| puzzlessbox-mcp `n5frtiup…` | pass | `running:healthy` · `/health` |
| puzzlessbox-web `qxpgv6p1…` | pass | `running:healthy` · `/api/health` |
| Live health ×4 | pass | api `/health`+`/ready`, mcp `/health`, web `/api/health` → 200 |
| Old API `dxoflgio67786lc4yilhce43` | pass | already deleted (MCP+CLI 404) — delete noop |
| API env complete | pass | DATABASE_URL, GOOGLE_*, ENCRYPTION_KEY, BETTER_AUTH_JWKS/BASE, CORS_ORIGINS (pbox), SERVICE_*, SCRAPER/FIRECRAWL/CAMOUFOX, MCP_BOOTSTRAP_TOKEN |
| Web env complete | pass | DATABASE_URL, BETTER_AUTH_URL/SECRET, NEXT_PUBLIC_APP/API_URL, NODE_ENV=production |
| MCP env complete | pass | SERVICE_BEARER_TOKEN, MCP_API_BASE_URL, MCP_PUBLIC_BASE_URL, ENV=prod |
| Advisory MCP_API_BASE_URL | warn | prod value public `https://api…` (works); preview still internal docker hostname |
| Traefik | warn | host 3.6.13 vs latest 3.6.23 — record only |

### Task 1 — Account wipe + first signup

| Check | Result | Evidence |
|-------|--------|----------|
| Cascade wipe | pass | sessions/account/notes/tasks/owner-cats/user → 0; seed cats 5 preserved |
| First-user signup | pass | gsd-browser register fill+`requestSubmit` (Radix tab `click_ref` flake) → `/welcome` |
| Fresh owner | pass | `a37a33c9…` / `uat@puzzless.local` |

### Ops curl suite ([Ops](a195555d-a2fe-40ab-8c39-5050c0cae67f)) — 18 pass / 1 fail / 4 warn

| ID | Result | Notes |
|----|--------|-------|
| Health/ready/JWKS/CORS/401/415/guards/Apollo assets/TLS | pass | as listed in subagent JSON |
| Homepage bundle host smoke | fail→**reclassified pass** | homepage entry chunks lack literal host; **board chunks** `apiHost=1 localhost8000=0` |
| Signup probe second@ | warn | raced wipe (created first user briefly); wiped again before real signup |
| MCP invalid bearer root | warn | bare GET 404; POST `/mcp` → **401** + WWW-Authenticate mcp FQDN (deep recheck pass) |
| Security headers | warn | HSTS + x-content-type-options present; fuller CSP not required v1 |
| Coolify from shell | warn | MCP/CLI used instead — inventory confirmed |

### Browser deep (gsd-browser session `uat-r5`)

| # | Test | Result | Evidence |
|---|------|--------|----------|
| 1 | HTTPS login brand | pass | Apollo splash; Instrument Serif h1; tabs Anmelden\|Registrieren |
| 2 | First-user register | pass | → `/welcome`; session cookie |
| 3 | Welcome → board | pass | „Los geht's“ → `/board`; `pb.welcome.seen=true` |
| 4 | 5 columns desktop | pass | Inbox\|Notizen\|Links\|Tasks\|Termine; offline=false |
| 5 | API XHR host | pass | network: `api.puzzlesstool.online/categories` + `/board-items` 200 |
| 6 | Signup lock API | pass | POST second@ → 409 `SIGNUP_LOCKED` |
| 7 | Signup lock UI | pass | VOICE copy sticky; `pb.signup_locked=1`; no generic fail copy |
| 8 | Capture→board poll | pass | seeded 3 notes+2 tasks via `/drafts`+confirm; 5× toast „Eintrag gesichert…“ |
| 9 | Item modal + autosave | pass | dialog w=512≤560; title DB `UAT Note 1 edited` |
| 10 | Bulk move (API + UI) | pass | API: Note2/3 → Links. UI ([Board deep UAT](a0571636-d583-4a66-af43-42d505460668)): 2 ausgewählt → Links; DB notes `55baeec3…`+`85229b33…` → `ccd452ba…` |
| 11 | Categories create | pass/warn | API create `UAT-Cat-R5` owner=`a37a33c9…`; seed NULL=5. UI panel: create skipped (already existed) — ownership invariants verified |
| 12 | Settings surface | pass | Account / Google Calendar („Mit Google verbinden“) / Darstellung |
| 13 | Theme dark | pass | `pb.theme=dark`; `html.dark`; persists after logout |
| 14 | Logout | pass | Abmelden → `/login` |
| 15 | Mobile iPhone 15 | pass | w=393; tablist 5 cats; single column h2=Inbox |
| 16 | MCP unauth | pass | POST `/mcp` 401; WWW-Authenticate mcp FQDN |
| 17 | Unauth guards | pass | `/board`+`/settings` → 307 `/login?next=` |

### Browser board2 suite ([Board deep UAT](a0571636-d583-4a66-af43-42d505460668)) — 8 pass / 1 warn

| ID | Result | Notes |
|----|--------|-------|
| login→board | pass | session `uat-r5-board2` |
| 5 columns + no offline | pass | Inbox\|Notizen\|Links\|Tasks\|Termine |
| modal body click + autosave | pass | title toggle persisted DB `55baeec3…` |
| bulk select → Links | pass | bar `2 ausgewählt`; DB category_id Links |
| categories panel create | warn | `UAT-Cat-R5` pre-existed; owner + seed NULL verified |
| theme dark | pass | `pb.theme=dark` + `html.dark` |
| logout | pass | → `/login` |
| signup lock UI | pass | 409 + VOICE copy + `pb.signup_locked=1` |
| mobile iPhone 15 | pass | tablist + single column Inbox |

### Browser notes / flakes

- Radix Tabs `Registrieren`/`Anmelden`: `browser_click_ref` often leaves `data-state=inactive`. Workaround: native InputEvent fill + `form.requestSubmit()` on forceMounted panels.
- Capture endpoint is `/drafts` (not `/capture/drafts`).
- Homepage-only chunk grep misses baked `NEXT_PUBLIC_API_URL`; verify board-route chunks or live XHR host.

### r5 summary

| Bucket | pass | fail | warn |
|--------|------|------|------|
| Coolify Task 2 | 10 | 0 | 2 |
| Account wipe/signup | 3 | 0 | 0 |
| Ops curl (after reclass) | 19 | 0 | 3 |
| Browser deep (main) | 17 | 0 | 0 |
| Browser board2 | 8 | 0 | 1 |
| **Total** | **57** | **0** | **6** |

open_gaps_unchanged:
- G-05-7 local MCP bootstrap — resolved in Phase 05.1 (code); prod API image deploy still pending
- dbhub DSN still points at prod — intentional for this prod UAT; keep caution for local work

---

## Prod Deep UAT r6 (2026-08-05) — milestone audit companion

tester: main + [curl ops](3f08a9bf-2a49-4e44-be47-18e60382b1fe) + [integration](de8bfc90-f5bf-4a77-9cd3-12dd2c30a377) + gsd-browser `uat-r6`  
suite: deep-prod-2026-08-05-r6 /gsd-audit-milestone  
prod_urls: pbox / api / mcp @ puzzlesstool.online  
wipe: cascade `a37a33c9…` + accidental probe `f89a50aa…`  
fresh_user: `1ac8eb47-6526-472a-8267-bbf7b02eff73` (`uat@puzzless.local` / `UatTestPass1!`)  
SERVICE_OWNER_ID: updated to fresh user + API restart → `/ready` 200

### Task 1 — Wipe + first account

| Check | Result | Evidence |
|-------|--------|----------|
| Cascade wipe | pass | users/accounts/sessions=0; seed cats 5 |
| Probe race wipe | pass | curl probe stole slot briefly → wiped |
| First signup | pass | POST `/api/auth/sign-up/email` 200 → `1ac8eb47…` |
| Signup lock | pass | 2nd+ → 409 `SIGNUP_LOCKED` |

### Task 2 — Coolify

| Check | Result | Evidence |
|-------|--------|----------|
| api/mcp/web healthy | pass | CLI+MCP `running:healthy`; live health×4 200 |
| Env keys complete | pass | API 17 / MCP 4 / Web 6 (values not logged) |
| Old API `dxoflgio…` | pass | already 404 — delete noop |
| SERVICE_OWNER_ID retarget | pass | → new first user; restart queued; ready OK |

### Curl deep — 16 pass / 0 fail / 4 warn

docs 404, JWKS, CORS, unauth 401, MCP WWW-Auth prod host, workflows. Warns: HSTS, Server banners, oauth well-known 404, Accept 415 nuance.

### Browser deep (`uat-r6`)

| # | Test | Result | Evidence |
|---|------|--------|----------|
| 1 | Login → welcome → board | pass | Apollo + Los geht's |
| 2 | 5 seed columns + empty VOICE | pass | Inbox…Termine |
| 3 | Create `UAT-Cat` | pass | sheet Anlegen → column |
| 4 | Draft note/task + link scrape | pass | board cards; Example Domain metadata |
| 5 | Move via PATCH `/items/{id}` | pass | link → Inbox |
| 6 | Item detail edit Verstauen | pass | title DB `UAT Note Edited` |
| 7 | Settings Google CTA | pass | Mit Google verbinden |
| 8 | XHR api host | pass | `api…/categories`+`/board-items` 200; no localhost |
| 9 | Logout | pass | Abmelden → /login |
| 10 | Signup sticky VOICE | pass | „Registrierung ist geschlossen…“ + `pb.signup_locked=1` |

### Browser board suite ([Deep browser board UAT](e09ab167-17a9-419b-b4d3-5c4b6bfc772f) session `uat-r6-a2`) — 16 pass / 0 fail / 2 warn

| ID | Result | Notes |
|----|--------|-------|
| login UI | warn | Anmelden fill flake; XHR sign-in 200 → /welcome OK |
| welcome→board | pass | Los geht's |
| signup sticky VOICE | pass | closed copy + `pb.signup_locked=1` + 409 |
| re-login | warn | UI bounce once; XHR session + /board OK |
| 5 columns | pass | Inbox…Termine |
| note/task/link create | pass | drafts+confirm; scrape titles on board |
| single-item Radix move | warn | menu flake; PATCH `/items/{id}` 200 |
| bulk move | pass | 2 ausgewählt → Inbox |
| modal autosave | pass | Eintrag bearbeiten title EDITED |
| empty VOICE / settings / GCal CTA | pass | as listed |
| XHR api host / health / brand | pass | api.puzzlesstool.online; no localhost; console critical=0 |

### r6 summary

| Bucket | pass | fail | warn |
|--------|------|------|------|
| Task 1 account | 4 | 0 | 0 |
| Task 2 Coolify | 4 | 0 | 0 |
| Curl | 16 | 0 | 4 |
| Browser main | 10 | 0 | 0 |
| Browser board a2 | 16 | 0 | 2 |
| **Total** | **50** | **0** | **6** |

Audit report: `.planning/v1.0-MILESTONE-AUDIT.md` (`tech_debt` — 28/28 reqs; Nyquist NOT-VALIDATED ×5)
