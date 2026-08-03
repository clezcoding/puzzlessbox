---
phase: 3
slug: hermes-plugin-timeout-spike
status: verified
threats_open: 0
asvs_level: 1
created: 2026-08-01
---

# Phase 3 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> Consolidated from plan-level threat models (03-01 through 03-04).

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Hermes VPS → MCP (HTTPS) | Plugin on separate VPS; MCP tools only | Bearer token, draft/item payloads |
| MCP → API (internal) | Inherited from Phase 2 | X-Service-Bearer, X-Owner-Id, RLS-scoped rows |
| Plugin session state | Per-chat active_draft / pending_capture_text | In-memory only; no cross-chat cache |
| VPS operator → setup.sh | Interactive MCP_URL / MCP_BEARER entry | Secrets written to `.env` (chmod 600), never committed |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-03-01 | Information Disclosure | MCP_BEARER in code/.git | high | mitigate | pydantic-settings env-only; `.gitignore` + `setup.sh` `read -rs`; `git check-ignore .env` | closed |
| T-03-02 | Elevation of Privilege | Cross-tenant / direct DB | high | mitigate | owner_id from token claims + API RLS; plugin MCP-only (no DB libs in pyproject.toml) | closed |
| T-03-03 | Tampering | Hermes-Cron as 30s timer | high | mitigate | Spike 001 INVALIDATED; API `DraftTimeoutManager` authoritative; plugin polls status only | closed |
| T-03-04 | Spoofing | confirm after auto_saved | medium | mitigate | `confirm_draft` WHERE status IN ('draft','auto_saved') → idempotent 200 (D-08) | closed |
| T-03-05 | Information Disclosure | get_draft / session cross-chat leak | high | mitigate | API filters owner_id + deleted_at; session state per chat isolated | closed |
| T-03-06 | Tampering | Poll abused as timer | low | accept | Poll reads `get_draft_status` only; timer reset is API-side PATCH | accepted |
| T-03-07 | Spoofing | Channel-specific branching | medium | mitigate | `test_channels.py` asserts no channel tokens in dialog/formatters (CAP-04) | closed |
| T-03-08 | Spoofing | list_categories skipped (D-09) | medium | mitigate | `start_capture_flow` calls `list_categories` before `create_item`; test asserts call order | closed |
| T-03-09 | Information Disclosure | status-aware ACK leak | low | accept | ACK distinguishes draft/auto_saved only after explicit user confirm | accepted |
| T-03-SC | Tampering | pip / setup deps | high | mitigate | Package legitimacy audit in RESEARCH.md; httpx/mcp/pydantic verified; setup.sh is bash-only (no pip) | closed |

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-03-06 | T-03-06 | Poll is read-only status check; API owns timer lifecycle | ship-preflight | 2026-08-01 |
| AR-03-09 | T-03-09 | Status text revealed only on explicit confirm, not preemptively | ship-preflight | 2026-08-01 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Accepted | Run By |
|------------|---------------|--------|------|----------|--------|
| 2026-08-01 | 10 | 8 | 0 | 2 | ship-preflight / UAT |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-01
