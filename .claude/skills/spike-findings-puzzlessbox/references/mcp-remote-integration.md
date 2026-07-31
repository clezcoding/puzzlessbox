# MCP Remote Integration (Hermes VPS)

## Requirements

- Hermes plugin **MUST** call MCP tools only — no direct Postgres/API DB access on Hermes VPS.
- Tool error semantics: **401** on missing/invalid bearer (not 500); structured `code` in tool errors (D-13).
- MCP URL: `https://mcp.puzzlesstool.online/mcp` with rotatable bearer (Coolify secret).

## How to Build It

1. **Environment on Hermes VPS:**
   ```bash
   MCP_URL=https://mcp.puzzlesstool.online/mcp
   MCP_BEARER=<hermes-rotatable-token>   # matches mcp_clients bearer_hash in API
   ```

2. **Plugin orchestration state machine** (mock-validated in spike 002):
   ```
   create_item(title, type, category_id, summary)
     → show confirmation (CAP-02)
   optional: update_item(item_id, title?, summary?, category_id?)
     → re-show confirmation
   confirm_item(item_id, optional patches)
     OR wait for API auto_saved (30s)
   ```
   API paths wired: `POST /drafts` → `PATCH /drafts/{id}` → `POST /drafts/{id}/confirm`.

3. **Health / auth probe** (run from Hermes host or CI):
   ```bash
   python3 .planning/spikes/003-remote-mcp-vps/probe_remote_mcp.py
   MCP_BEARER='…' python3 .planning/spikes/003-remote-mcp-vps/probe_remote_mcp.py
   ```
   Expect: `/health` → 200; no auth / bad bearer `POST /mcp` → 401.

4. **Mock integration test** (no secrets):
   ```bash
   cd mcp-server && . .venv/bin/activate
   python ../.planning/spikes/002-mcp-confirm-flow/confirm_flow.py
   ```
   All steps `ok: true`; wiring lists `/drafts`, `/drafts/{id}`, `/drafts/{id}/confirm`.

5. **Live MCP tool calls** — use `mcp` Python client with `streamablehttp_client` + bearer header, or Hermes native MCP remote config pointing at production URL.

6. **`list_categories` first** on cold start to resolve `category_id` UUID for `create_item` (system defaults + owner categories).

## What to Avoid

- Passing `owner_id` as tool argument — owner comes from bearer → `/internal/mcp-auth` (tenancy leak).
- Using Hermes cron to trigger confirm/autosave timing (see `draft-timeout.md`).
- Treating 500 on auth failure — must be 401 for retry/rotate-token logic.

## Constraints

- MCP→API uses internal Docker network on server; Hermes→MCP is public HTTPS only.
- `confirm_item` / `update_item` use param `item_id` (draft UUID), not `draft_id`.
- Live E2E confirm on production needs real `MCP_CATEGORY_ID` — mock flow validated; Hermes VPS E2E remains Phase 3 build task.

## Origin

Synthesized from spikes: 002, 003  
Source files: `sources/002-mcp-confirm-flow/`, `sources/003-remote-mcp-vps/`
