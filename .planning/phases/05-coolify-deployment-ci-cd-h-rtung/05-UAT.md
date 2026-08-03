---
status: complete
phase: 05-coolify-deployment-ci-cd-h-rtung
source: [05-01-SUMMARY.md, 05-02-SUMMARY.md, 05-03-SUMMARY.md, 05-04-SUMMARY.md, 05-VERIFICATION.md]
started: 2026-08-03T00:49:00Z
updated: 2026-08-03T01:05:00Z
environment: production (pbox / api / mcp *.puzzlesstool.online)
tester: gsd-browser + curl + Coolify + dbhub + shell subagent
suite: deep-prod-2026-08-03
response_language: de
---

## Current Test

[testing complete]

## Tests

### 1. Web Health HTTPS (OPS-04)
expected: GET pbox /api/health → 200 {"status":"ok"} unauth
result: pass
tested_by: curl
notes: HTTP 200 {"status":"ok"}

### 2. API Health HTTPS (OPS-04)
expected: GET api /health → 200 {"status":"ok"}
result: pass
tested_by: curl
notes: HTTP 200 {"status":"ok"}

### 3. MCP Health HTTPS (OPS-04)
expected: GET mcp /health → 200 service mcp-server
result: pass
tested_by: curl
notes: HTTP 200 {"status":"ok","service":"mcp-server"}

### 4. Three Separate FQDNs + TLS (OPS-01)
expected: pbox/api/mcp distinct; LE certs; HTTP→HTTPS redirect
result: pass
tested_by: curl + openssl
notes: LE certs; HTTP 302→HTTPS for all three FQDNs.

### 5. MCP Unauth 401 (MCP-02)
expected: POST /mcp without Bearer → 401
result: pass
tested_by: curl
notes: |
  HTTP 401 (auth required). See test 16 for WWW-Authenticate header quality issue.

### 6. API Unauth 401 on protected routes
expected: GET /categories without JWT → 401
result: pass
tested_by: curl
notes: Accept vnd.puzzlessbox.v1+json → UNAUTHORIZED Missing authentication token.

### 7. DB Backup Schedule (OPS-03)
expected: cron 0 3 * * *; retention local; ≥1 success baseline (Coolify)
result: pass
tested_by: Coolify get_database_backups uuid=pfqgb5pcvgi9oh64bpe3shtn
notes: |
  Schedule jl0skzwpd3ot7hgfmohlny9s enabled, frequency 0 3 * * *,
  retention 14/14 local. Execution ibaby40uszso4coqgxjtgp1b status=success.

### 8. Web→API Env Wiring (OPS-01/02)
expected: Client bundle calls api.puzzlesstool.online; CORS erlaubt pbox Origin
result: pass
tested_by: gsd-browser network + curl OPTIONS
notes: |
  Live board fetches https://api.puzzlesstool.online/categories + /board-items 200.
  OPTIONS Origin pbox → ACAO=https://pbox.puzzlesstool.online.
  deploy-web.yml has NEXT_PUBLIC_API_URL build-arg. Prior G-05-1/G-04-1 RESOLVED.

### 9. JWKS Path for API Auth
expected: /api/auth/jwks → 200; wrong /.well-known/jwks.json → 404
result: pass
tested_by: curl
notes: JWKS keys[1] EdDSA. Wrong path 404. Prior G-05-2/G-04-3 RESOLVED.

### 10. OpenAPI Surface Hardened
expected: /docs → 404; /openapi.json → 404 in prod
result: pass
tested_by: curl
notes: Both 404 {"detail":"Not Found"}. Prior G-05-4 RESOLVED.

### 11. End-to-End Capture→Board (CAP-05 prod)
expected: Item via API/MCP erstellt → erscheint auf pbox Board ≤20s (poll)
result: pass
tested_by: API draft+confirm + gsd-browser
notes: |
  Created draft e3012af1… „UAT Poll Pulse Item“ → confirm 200.
  Board showed item + toast „Eintrag gesichert…“ on navigate/poll.
  Hermes channel path not re-fired (API create path validates board merge).

### 12. GHCR Deploy Pipeline Artifacts (OPS-02)
expected: deploy-web/api/mcp workflows + NEXT_PUBLIC build-args + webhook pattern
result: pass
tested_by: artifact read
notes: |
  deploy-{web,api,mcp}.yml present with COOLIFY_*_WEBHOOK+TOKEN.
  web build-args NEXT_PUBLIC_API_URL + NEXT_PUBLIC_APP_URL.

### 13. CORS Reject Evil Origin
expected: OPTIONS Origin:evil.example → kein ACAO allow
result: pass
tested_by: curl
notes: HTTP 400 Disallowed CORS origin; no ACAO.

### 14. Web Unauth Middleware Redirect
expected: /board|/settings ohne Cookie → 307 login?next=
result: pass
tested_by: curl
notes: Location /login?next=%2Fboard and /login?next=%2Fsettings.

### 15. Public Brand Assets on CDN/Web
expected: apollo-*.png public assets 200
result: pass
tested_by: curl
notes: onboard/splash/wordmark/avatar 200.

### 16. MCP WWW-Authenticate Metadata Host
expected: 401 WWW-Authenticate resource_metadata uses prod MCP/API host (not localhost)
result: issue
reported: "401 ok but WWW-Authenticate Bearer resource_metadata=\"http://localhost:8000/.well-known/oauth-protected-resource/mcp\""
severity: minor
tested_by: curl
notes: |
  Auth rejection works; header advertises localhost OAuth protected-resource URL.
  Clients following RFC 9728 metadata discovery would hit wrong host.

## Summary

total: 16
passed: 15
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-05-5
  truth: "MCP 401 WWW-Authenticate resource_metadata points at production host (mcp/api.puzzlesstool.online), not localhost:8000"
  status: failed
  reason: "User reported: 401 ok but WWW-Authenticate Bearer resource_metadata=\"http://localhost:8000/.well-known/oauth-protected-resource/mcp\""
  severity: minor
  test: 16
  artifacts:
    - path: "mcp-server / Coolify MCP env"
      issue: "OAuth resource metadata base URL defaults to localhost:8000"
  missing:
    - "Set MCP public base URL / resource metadata env for prod FQDN"
  root_cause: "MCP OAuth protected-resource metadata URL not wired to mcp.puzzlesstool.online in Coolify runtime; localhost bake/default leaks into WWW-Authenticate."
  debug_session: "deep-prod-uat-2026-08-03"

## Prior Gaps Reconciliation

| gap_id | prior | now |
|--------|-------|-----|
| G-05-1 | failed (API URL bake) | resolved (live api.puzzlesstool.online) |
| G-05-2 | failed (JWKS path) | resolved |
| G-05-3 | (CORS related) | resolved |
| G-05-4 | failed (openapi public) | resolved (/openapi.json 404) |
| G-05-5 | new | open (MCP WWW-Authenticate localhost) |
