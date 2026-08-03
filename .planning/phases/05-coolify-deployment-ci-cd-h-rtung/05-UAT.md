---
status: diagnosed
phase: 05-coolify-deployment-ci-cd-h-rtung
source: [05-01-SUMMARY.md, 05-02-SUMMARY.md, 05-03-SUMMARY.md, 05-04-SUMMARY.md, 05-VERIFICATION.md]
started: 2026-08-02T23:51:00Z
updated: 2026-08-02T23:58:00Z
environment: production (pbox / api / mcp *.puzzlesstool.online)
tester: gsd-browser + curl + Coolify MCP + dbhub
---

## Current Test

[testing complete — production suite]

## Tests

### 1. Web Health HTTPS (OPS-04)
expected: GET https://pbox.puzzlesstool.online/api/health → 200 {"status":"ok"} unauth
result: pass
tested_by: curl
notes: HTTP 200 {"status":"ok"}

### 2. API Health HTTPS (OPS-04)
expected: GET https://api.puzzlesstool.online/health → 200 {"status":"ok"}
result: pass
tested_by: curl
notes: HTTP 200 {"status":"ok"}

### 3. MCP Health HTTPS (OPS-04)
expected: GET https://mcp.puzzlesstool.online/health → 200 service mcp-server
result: pass
tested_by: curl
notes: HTTP 200 {"status":"ok","service":"mcp-server"}

### 4. Three Separate FQDNs + TLS (OPS-01)
expected: pbox/api/mcp distinct; LE certs; HTTP→HTTPS
result: pass
tested_by: curl + openssl
notes: |
  Cert CN=pbox.puzzlesstool.online LE valid. HTTP pbox → 302 HTTPS.
  Coolify apps: web qxpgv6p1rp3vupue9al8hbzz, api pasmduuzitoh21qipyq3ay1l, mcp n5frtiupale5c2zjm9fyk1qc.

### 5. MCP Unauth 401 (MCP-02)
expected: POST /mcp without Bearer → 401
result: pass
tested_by: curl
notes: POST initialize without auth → HTTP 401

### 6. DB Backup Schedule (OPS-03)
expected: cron 0 3 * * *; retention 14/14 local; ≥1 success baseline
result: pass
tested_by: Coolify MCP get_database_backups
notes: |
  Schedule jl0skzwpd3ot7hgfmohlny9s enabled, save_s3=false, frequency 0 3 * * *,
  retention 14/14. Execution ibaby40uszso4coqgxjtgp1b status=success (local dump).

### 7. Second-Register Rejected Prod (AUTH-03)
expected: After owner exists, signup rejected SIGNUP_LOCKED
result: pass
tested_by: curl
notes: POST /api/auth/sign-up/email → 409 {"message":"SIGNUP_LOCKED"}; users=1

### 8. Web→API Env Wiring (OPS-01/02 runtime)
expected: NEXT_PUBLIC_API_URL baked to api.puzzlesstool.online; CORS allows pbox
result: issue
reported: "Coolify WebApp env has NEXT_PUBLIC_API_URL=https://api.puzzlesstool.online at runtime, but Docker image bakes localhost:8000 (no build-arg). API CORS_ORIGINS omits https://pbox.puzzlesstool.online → Disallowed CORS origin. End-to-end board/API dead."
severity: blocker
tested_by: curl + Coolify envs + JS chunk grep
notes: |
  See Phase 4 gaps G-04-1, G-04-2. Health endpoints pass; authenticated product path fails.

### 9. JWKS Path for API Auth
expected: BETTER_AUTH_JWKS_URL reachable JWKS for JWT verify
result: issue
reported: "API env BETTER_AUTH_JWKS_URL=…/.well-known/jwks.json → 404. Working: /api/auth/jwks → 200."
severity: blocker
tested_by: curl + Coolify get_application_envs
notes: Cross-links G-04-3. Would break JWT even after CORS+URL fix.

### 10. OpenAPI Surface in Prod
expected: /docs off in prod; openapi not publicly useful
result: issue
reported: "/docs → 404 (good). /openapi.json → 200 still publicly readable."
severity: minor
tested_by: curl

### 11. End-to-End Capture→Board (CAP-05 prod / prior UAT #7)
expected: MCP/Hermes create item → appears on pbox board ≤20s
result: blocked
blocked_by: prior-phase
reason: "Board/API path broken (G-04-1/2/3). Cannot verify Hermes→board on prod until connectivity fixed."

### 12. GHCR Deploy Pipeline Smoke (OPS-02)
expected: deploy-web/api workflows + webhook pattern exist; apps healthy
result: pass
tested_by: artifact + live health
notes: |
  Workflows present; apps healthy via health probes. Full webhook re-fire not re-run this session
  (prior 05-VERIFICATION already green). Live health proves deploy state holds.

## Summary

total: 12
passed: 8
issues: 3
pending: 0
skipped: 0
blocked: 1

## Gaps

- gap_id: G-05-1
  truth: "Prod WebApp client bundle uses https://api.puzzlesstool.online"
  status: failed
  reason: "Same as G-04-1 — NEXT_PUBLIC_* must be build-args in deploy-web.yml / Dockerfile"
  severity: blocker
  test: 8
  artifacts:
    - path: "webapp/Dockerfile"
      issue: "No NEXT_PUBLIC build-args"
    - path: ".github/workflows/deploy-web.yml"
      issue: "No docker build-args for public URLs"
  missing:
    - "Add build-args + rebuild GHCR web image + Coolify pull"
  root_cause: ""
  debug_session: ""

- gap_id: G-05-2
  truth: "API CORS_ORIGINS includes https://pbox.puzzlesstool.online"
  status: failed
  reason: "Same as G-04-2 — Coolify API missing CORS_ORIGINS override; default still app. subdomain"
  severity: blocker
  test: 8
  artifacts:
    - path: "api/app/core/config.py"
      issue: "Default CORS_ORIGINS outdated vs D-01 pbox domain"
  missing:
    - "Set CORS_ORIGINS on Coolify API (and optionally code default) then restart"
  root_cause: ""
  debug_session: ""

- gap_id: G-05-3
  truth: "BETTER_AUTH_JWKS_URL points at /api/auth/jwks"
  status: resolved
  resolved_by: seed-agent Coolify env patch + API restart
  resolved_at: 2026-08-03
  reason: "Same as G-04-3 — prod env now https://pbox.puzzlesstool.online/api/auth/jwks"
  severity: blocker
  test: 9
  artifacts: []
  missing: []
  root_cause: "Wrong well-known path at cutover; patched during UAT seed."
  debug_session: "prod-uat-2026-08-03"

- gap_id: G-05-4
  truth: "Prod OpenAPI not publicly exposed (or intentionally documented)"
  status: resolved
  resolved_by: quick/260803-3gu openapi_url=None in prod
  resolved_at: 2026-08-03
  reason: "/openapi.json returns 200 while /docs is 404 — fixed via openapi_url=None when is_prod"
  severity: minor
  test: 10
  artifacts:
    - path: "api/app/main.py"
      issue: "openapi_url now None in prod"
  missing: []
  root_cause: "docs_url=None but openapi_url still default"
  debug_session: ""
