---
phase: 2
slug: mcp-server
status: verified
threats_open: 0
asvs_level: 1
created: 2026-07-31
---

# Phase 2 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Public HTTPS → MCP (FastMCP) | Hermes / remote clients hit mcp.puzzlesstool.online | Bearer token, MCP tool payloads |
| MCP → API (internal) | httpx service client on Docker network | X-Service-Bearer, X-Owner-Id, draft/item/category payloads |
| API → Postgres | App DB role + RLS | owner_id scoped rows via resolved MCP client |
| API internal → mcp-auth | POST /internal/mcp-auth | bearer_hash → owner_id lookup |
| GHCR → Coolify | deploy-mcp.yml image push + webhook | Image digest, webhook bearer |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-02-bearer-missing | Spoofing | POST /mcp | high | mitigate | FastMCP auth → 401 + WWW-Authenticate Bearer | closed |
| T-02-bearer-invalid | Spoofing | OwnerResolvingVerifier | high | mitigate | /internal/mcp-auth reject → 401 invalid_token | closed |
| T-02-owner-spoof | Spoofing | X-Owner-Id | high | mitigate | UUID format + Better Auth user row required (403) | closed |
| T-02-http-plain | Tampering | MCP transport | high | mitigate | allowed_hosts prod; TLS at Traefik/Coolify | closed |
| T-02-internal-auth | Spoofing | /internal/mcp-auth | high | mitigate | Service bearer + bearer_hash lookup in mcp_clients | closed |
| T-02-tool-injection | Tampering | MCP tool schemas | medium | mitigate | Pydantic validation + FunctionTool schema reject tests | closed |
| T-02-api-retry | DoS | call_api retry | medium | mitigate | No retry on 4xx/500; bounded retries on transient errors | closed |
| T-02-deploy-webhook | Spoofing | Coolify webhook | high | mitigate | API bearer auth on webhook POST (cfdfb19) | closed |
| T-02-SC | Tampering | fastmcp/uvicorn pins | high | mitigate | fastmcp==3.4.4, uvicorn==0.52.0 pinned | closed |

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| — | — | No accepted risks this phase | — | — |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-07-31 | 9 | 9 | 0 | ship-preflight / live verification |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-07-31
