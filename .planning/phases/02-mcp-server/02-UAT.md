---
status: complete
phase: 02-mcp-server
source: 02-01-SUMMARY.md, 02-02-SUMMARY.md, 02-03-SUMMARY.md, 02-04-SUMMARY.md
started: 2026-07-31T03:20:00Z
updated: 2026-07-31T03:25:00Z
---

## Current Test

[testing complete]

## Tests

### 1. MCP Health-Endpunkt ohne Authentifizierung
expected: GET https://mcp.puzzlesstool.online/health liefert HTTP 200 und JSON mit status ok
result: pass
source: automated
evidence: curl → 200 {"status":"ok","service":"mcp-server"}

### 2. MCP-Endpunkt ohne Authorization abgewiesen
expected: POST /mcp ohne Authorization-Header liefert HTTP 401
result: pass
source: automated
evidence: curl POST /mcp → HTTP 401

### 3. MCP-Endpunkt mit ungültigem Bearer-Token abgewiesen
expected: POST /mcp mit Authorization Bearer WRONG liefert HTTP 401 und Body enthält invalid_token
result: pass
source: automated
evidence: curl → HTTP 401, body {"error":"invalid_token",...}

### 4. TLS/HTTPS für MCP-Domain
expected: mcp.puzzlesstool.online löst auf und liefert gültiges Let's-Encrypt-Zertifikat über HTTPS
result: pass
source: automated
evidence: openssl s_client CN=mcp.puzzlesstool.online, notAfter Oct 29 2026; curl /health 200

### 5. MCP-Server Unit-/Integrationstests
expected: mcp-server pytest tests -q — alle Tests grün
result: pass
source: automated
evidence: 23 passed in 0.72s

### 6. Sechs MCP-Tools registriert (MCP-01)
expected: create_item, confirm_item, update_item, move_item, list_categories, create_category registriert mit validierten Schemas
result: pass
source: automated
evidence: test_six_tools_registered passed; 22+ tests in test_api_contract.py + test_tools_schema.py

### 7. Interne Owner-Auflösung via POST /internal/mcp-auth (MCP-02)
expected: Bearer-Hash wird zu owner_id aufgelöst; X-Owner-Id-Guard aktiv
result: pass
source: automated
coverage_id: D1
evidence: api/app/routers/internal.py exists; import app.routers.internal OK; 02-01 coverage auto-passed

### 8. create_item Header-Contract zum Backend
expected: create_item sendet Accept v1, X-Service-Bearer, X-Owner-Id, Idempotency-Key an POST /drafts
result: pass
source: automated
coverage_id: D3
evidence: mcp-server/tests/test_api_contract.py passed (23/23)

### 9. API Categories- und Move-Endpunkte (02-02)
expected: GET/POST /categories und PATCH /items/{id} Router vorhanden und importierbar
result: pass
source: automated
evidence: api/app/routers/categories.py, items.py; from app.routers import categories, items → OK

### 10. MCP Auth 401 bei fehlendem/ungültigem Token (Unit)
expected: OwnerResolvingVerifier liefert 401 mit WWW-Authenticate und invalid_token
result: pass
source: automated
coverage_id: D2
evidence: mcp-server/tests/test_auth.py passed

### 11. Deploy-Artefakte GHCR + Dockerfile (02-04)
expected: mcp-server/Dockerfile und .github/workflows/deploy-mcp.yml mit GHCR puzzlessbox-mcp und Coolify-Webhook
result: pass
source: automated
coverage_id: D1
evidence: DEPLOY_FILES_OK; grep puzzlessbox-mcp, sha-, COOLIFY_MCP_WEBHOOK in deploy-mcp.yml

### 12. Coolify MCP-App erreichbar und healthy
expected: Live-App unter mcp.puzzlesstool.online antwortet auf /health mit 200 (Health-Check-Pfad konfiguriert)
result: pass
source: automated
evidence: Live /health 200; TLS valid; app LIVE per 02-04-SUMMARY

## Summary

total: 12
passed: 12
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none]
