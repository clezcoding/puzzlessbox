# Phase 2: MCP-Server - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-31
**Phase:** 2-MCP-Server
**Mode:** `--batch`
**Areas discussed:** Auth & Token-Modell, Tool-Semantik, MCP↔API Client, Deploy-Schnitt, Token-Provisioning, Grace, update_item, Tool-Sprache, mcp_clients Lookup, Bootstrap, X-Owner-Id Guard, Idempotency-Key

---

## Hermes→MCP Auth & Token-Modell

| Option | Description | Selected |
|--------|-------------|----------|
| Ein Shared Secret | Hermes↔MCP und MCP↔API gleiches Secret | |
| Zwei Secrets | Hermes-Bearer am MCP; API `SERVICE_BEARER` | ✓ |
| Env SERVICE_OWNER_ID only | Solo owner from env | |
| Mapping-Tabelle/Claim | SaaS-ready bearer→owner | ✓ |
| X-Owner-Id Header | MCP sends resolved owner to API | ✓ |
| Pro-Owner Service-Principal | N API bearers | |
| Manuelle Rotation | Coolify secret swap only | |
| Dual-token Grace | alt+neu gültig | ✓ (later refined to DB flags) |
| Traefik-only auth | | |
| FastMCP/App validation | 401/403 testable | ✓ |

**User's choice:** 1b, 2b, 3b, 4b; follow-up owner hop → ★ X-Owner-Id
**Notes:** Two-hop clarification later for API URL.

---

## Tool-Semantik & Payload-Mapping

| Option | Description | Selected |
|--------|-------------|----------|
| create → always /drafts | | ✓ |
| Typ-spezifische Routes | /links /events bypass draft | |
| confirm = status only | | |
| Patch+Confirm | | ✓ |
| Categories API in Phase 2 | | ✓ |
| MCP stubs only | API Phase 4 | |
| Errors: raw API JSON | | |
| Errors: text + code | | ✓ |

**User's choice:** 1a, 2b, 3a, 4b

---

## MCP↔API Client-Vertrag

| Option | Description | Selected |
|--------|-------------|----------|
| Internal Docker URL | | ✓ |
| Public api. URL | | (user considered, then a) |
| All required headers | Accept + service + owner + idempotency | ✓ |
| Timeout 15s | | ✓ |
| No write retry | | |
| 1× Retry 502/503 | | ✓ |

**User's choice:** 1a (after hop clarification), 2a, 3b, 4b
**Notes:** User thought public needed because Hermes is remote — clarified Hermes→MCP public, MCP→API internal.

---

## Deploy-Schnitt Phase 2

| Option | Description | Selected |
|--------|-------------|----------|
| Code only | | |
| Coolify+domain without GH Actions | | |
| Full GHCR+Actions+Coolify | | ✓ |
| Streamable HTTP | | ✓ |
| Health+Ready+Coolify check Phase 2 | | ✓ |
| mcp-server/ separate image | | ✓ |

**User's choice:** 1c, 2a, 3b, 4b
**Notes:** Pulls MCP OPS slice into Phase 2.

---

## Provisioning / Grace / update_item / Tool language

| Option | Description | Selected |
|--------|-------------|----------|
| mcp_clients Postgres table | | ✓ |
| Env-only token map | | |
| Grace: env PRIMARY+PREVIOUS | | |
| Grace: DB active\|grace + expiry | | ✓ |
| update_item: draft\|auto_saved full; confirmed move-only | | ✓ |
| Tool schemas English | | ✓ |

**User's choice:** 1b, 2b (after SaaS coherence note), 3a, 4b

---

## Lookup / Bootstrap / Owner guard / Idempotency

| Option | Description | Selected |
|--------|-------------|----------|
| MCP direct DB | | (chosen then reverted) |
| API POST /internal/mcp-auth | | ✓ |
| Bootstrap MCP_BOOTSTRAP_TOKEN when empty | | ✓ |
| Manual SQL only | | |
| X-Owner-Id: UUID + Better Auth user | | ✓ |
| Idempotency: Hermes key, MCP UUID fallback | | ✓ |

**User's choice:** final 1b, 2a, 3b, 4a
**Notes:** User asked safest+pleasant bootstrap → ★ 2a; flipped 1a→1b.

---

## Claude's Discretion

- FastMCP path / 3.4.x pin, mcp_clients columns, grace TTL, internal route name, category fields, GHCR workflow naming

## Deferred Ideas

- Phase 3 Hermes plugin / spike
- Phase 4 WebApp board
- Phase 5 remaining OPS (API/WebApp/backups)
- v2 MCP OAuth / IP allowlist
