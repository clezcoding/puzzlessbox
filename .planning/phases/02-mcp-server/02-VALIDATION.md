<!-- generated-by: gsd-doc-writer -->
---
phase: 2
slug: mcp-server
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-31
validated: 2026-08-05
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + `pytest-asyncio` (Projekt-Standard, spiegelt `api/`) |
| **Config file** | `mcp-server/pytest.ini` (`asyncio_mode = auto`) — **Wave 0** anlegen |
| **Quick run command** | `pytest mcp-server/tests -x -q` |
| **Full suite command** | `pytest mcp-server/tests` |
| **Estimated runtime** | ~30–60 seconds |

API-Tasks in Plan 01/02 nutzen zusätzlich `cd api && python -m pytest tests -x -q` (bestehende Infrastruktur unter `api/tests/`).

---

## Sampling Rate

- **After every task commit:** Run `pytest mcp-server/tests -x -q` (MCP-Tasks) bzw. `cd api && python -m pytest tests -x -q -k "<filter>"` (API-Tasks laut Verification Map)
- **After every plan wave:** Run `pytest mcp-server/tests` (volle MCP-Suite) + `cd api && python -m pytest tests` nach API-Wellen (02-01, 02-02)
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | MCP-01, MCP-02 | T-02-02, T-02-03, T-02-05 | `bearer_hash` → `owner_id` via `POST /internal/mcp-auth`; `X-Owner-Id` nur bei gültigem Service-Bearer + provisioniertem user (D-08) | integration | `cd api && python -c "import app.models, app.routers.internal, app.core.bootstrap; print('imports ok')" && python -m pytest tests -x -q -k "auth or schema or tenancy"` | ✅ | ✅ green |
| 02-01-02 | 01 | 1 | MCP-01, MCP-02 | T-02-01, T-02-04 | 401 ohne/ungültigem Bearer (RFC-6750); `owner_id` aus `get_access_token().claims`, nie Tool-Input; `create_item` → `POST /drafts` mit Header-Contract | integration | `cd mcp-server && python -m pytest tests -x -q` | ✅ | ✅ green |
| 02-02-01 | 02 | 2 | MCP-01 | T-02-07, T-02-09 | `GET/POST /categories` owner-gefiltert; kein Cross-Tenant-Leak; Duplicate-Name → 409 | integration | `cd api && python -c "import app.routers.categories" && python -m pytest tests -x -q -k "categor or capture or tenancy"` | ✅ | ✅ green |
| 02-02-02 | 02 | 2 | MCP-01 | T-02-07, T-02-08 | `PATCH /items/{id}` nur eigenes Item; fremdes/nicht existierendes → 404; Move statusunabhängig (D-12) | integration | `cd api && python -c "import app.routers.items" && python -m pytest tests -x -q -k "item or capture or tenancy"` | ✅ | ✅ green |
| 02-03-01 | 03 | 3 | MCP-01 | T-02-10, T-02-11 | `confirm_item`/`update_item`/`move_item`: owner aus Claim; Retry nur 502/503 ×1, nicht 500 (D-18) | contract | `cd mcp-server && python -m pytest tests/test_api_contract.py tests/test_tools_schema.py -x -q` | ✅ | ✅ green |
| 02-03-02 | 03 | 3 | MCP-01 | T-02-12, T-02-13 | Schema-Reject vor Netzwerk-Hop; API `{error:{code,message}}` → `ToolError`; exakt 6 Tools registriert | unit + contract | `cd mcp-server && python -m pytest tests -x -q` | ✅ | ✅ green |
| 02-04-01 | 04 | 2 | MCP-02 | T-02-14, T-02-15, T-02-SC | Keine Secrets im Workflow; SHA-gepinnte Actions; Dockerfile ohne alembic (D-06) | build | `cd mcp-server && ../mcp-server/.venv/bin/pytest tests/test_dockerfile_deploy.py -q` | ✅ | ✅ green |
| 02-04-02 | 04 | 2 | MCP-02 | T-02-16 | Live HTTPS `/health` 200; `POST /mcp` ohne/mit falschem Bearer → 401; TLS gültig (D-05) | manual | — (human-check, siehe Manual-Only) | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Hinweis: Plan 04 Task 1 (`checkpoint:decision` Deploy-Topologie D-23) ist bewusst nicht in der Map — Gate-Entscheidung, kein automatisierbarer Verify.*

---

## Wave 0 Requirements

- [x] `mcp-server/tests/conftest.py` — In-Memory-`Client(mcp)` fixture ODER `httpx.ASGITransport(app=mcp.http_app())`; `httpx.MockTransport`-Fixture für interne API
- [x] `mcp-server/tests/test_auth.py` — 401/403-Seams (`test_missing_bearer_401`, `test_invalid_bearer_401`, `test_owner_reject`) — MCP-02
- [x] `mcp-server/tests/test_tools_schema.py` — Pydantic-Reject (fehlender `type`, invalid Enum, fehlende `category_id`) — MCP-01
- [x] `mcp-server/tests/test_api_contract.py` — Header/Idempotency/Retry/Error/Mapping für alle 6 Tools — MCP-01
- [x] `mcp-server/tests/test_health.py` — `/health` 200 unauth, `/ready` pingt API — MCP-02
- [x] `mcp-server/pytest.ini` — `[pytest]` mit `asyncio_mode = auto`
- [x] Framework install: `pytest`, `pytest-asyncio` in `mcp-server/requirements.txt` (dev-Sektion)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live MCP Deploy: HTTPS Health + Auth-Enforcement | MCP-02 (SC2) | Erfordert produktiven Coolify-Deploy unter `mcp.puzzlesstool.online`, gültiges TLS-Zertifikat und Traefik-Routing — nicht reproduzierbar in CI/In-Memory-Tests | 1. `curl -sS https://mcp.puzzlesstool.online/health` → 200 `{"status":"ok","service":"mcp-server"}` (TLS-Zertifikat gültig). 2. `curl -sS -o /dev/null -w "%{http_code}" -X POST https://mcp.puzzlesstool.online/mcp` (ohne `Authorization`) → 401. 3. `curl -sS -X POST https://mcp.puzzlesstool.online/mcp -H "Authorization: Bearer WRONG"` → 401 `invalid_token`. 4. Coolify Health-Check zeigt App als healthy; Health-Check-Pfad `/health` konfiguriert. Bestätige „approved" oder benenne Abweichungen in `02-04-SUMMARY.md`. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved

---

## Validation Audit 2026-08-05
- **Gaps:** 1
- **Resolved:** 1
- **Escalated:** 0
- **Details:** Filled Dockerfile & Workflow Deploy static checks with `tests/test_dockerfile_deploy.py`.
