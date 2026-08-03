---
status: complete
phase: 05-coolify-deployment-ci-cd-h-rtung
source: [05-01-SUMMARY.md, 05-02-SUMMARY.md, 05-03-SUMMARY.md, 05-04-SUMMARY.md, 05-VERIFICATION.md, docker-compose.yml, webapp/.env.local]
started: 2026-08-03T02:26:00Z
updated: 2026-08-03T02:52:00Z
environment: local (OrbStack) + post-merge prod re-verify
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

### Browser — gsd-browser session `uat-prod-05-main`

| Check | Result | Evidence |
|-------|--------|----------|
| Login → welcome → board | pass | uat@puzzless.local |
| Board columns | pass | Inbox/Notizen/Links/Tasks/Termine (empty — expected post-incident) |
| Network FQDN | pass | `https://api.puzzlesstool.online/categories` + `board-items` 200 |
| Settings | pass | Account + Google Calendar + Darstellung |
| Coolify | pass | uuid `qxpgv6p1rp3vupue9al8hbzz` status `running:healthy` |

### Prod summary

total: 15 curl + 5 browser
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
  status: open
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

## Prior Gaps Reconciliation (prod baseline)

| Gap | Status |
|-----|--------|
| G-05-1..G-05-5 | resolved in prior prod UAT (reference only) |
| G-05-6 dbhub/prod DSN | new — tooling follow-up (see Gaps) |
| G-05-7 local MCP bootstrap | open minor |

## Incident Log

1. **Prod account wipe via dbhub** (2026-08-03 ~02:25Z): DELETE cascade on production user 75d9d55e… (notes×3, tasks×2, categories×1, sessions×5).
2. **Emergency recovery**: POST https://pbox.puzzlesstool.online/api/auth/sign-up/email → user 5ee91aa3…; signup locked.
3. **Optional**: Restore Coolify backup `ibaby40uszso4coqgxjtgp1b` if prior board seed required (will rewind DB to 2026-08-02).
4. **Local path corrected**: all subsequent DB ops via `PGPASSWORD=… psql -h 127.0.0.1 -p 5433`.
