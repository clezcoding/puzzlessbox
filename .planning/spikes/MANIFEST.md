# Spike Manifest

## Idea

Phase 3 (Hermes-Plugin & Timeout-Spike) de-risking: validate that API-side 30s timers replace Hermes cron for precision, that Hermes can drive MCP tools over HTTPS from a remote VPS, and that the confirmation UX payload is channel-agnostic before `/gsd-plan-phase 3`.

## Requirements

- 30s auto-save precision MUST live in FastAPI (`DraftTimeoutManager`), not Hermes cron (MCP-04).
- Hermes plugin MUST call MCP tools only — no direct DB access (Phase 3 success criterion).
- Confirmation message MUST include title, type, category, summary + edit affordance (CAP-02).
- Optional Hermes cron MAY notify user after API `auto_saved` — never drive the timer itself.
- Tool error semantics: 401 on bad bearer, structured `code` in tool errors (Phase 2 D-13).

## Spikes

| # | Name | Type | Validates | Verdict | Tags |
|---|------|------|-----------|---------|------|
| 001 | hermes-cron-vs-api-timer | standard | Given 30s confirmation window, when user is idle, then API autosaves — Hermes 60s cron cannot substitute | VALIDATED | hermes, timeout, mcp-04 |
| 002 | mcp-confirm-flow | standard | Given create_item draft, when confirm_item runs, then item reaches confirmed via MCP→API only | PARTIAL (mock VALIDATED) | mcp, mcp-03, confirm |
| 003 | remote-mcp-vps | standard | Given Hermes VPS path, when HTTPS+bearer to mcp.puzzlesstool.online, then health OK and auth errors are 401 | VALIDATED | mcp, remote, auth |
| 004 | confirmation-payload | standard | Given draft fields, when formatted for chat, then CAP-02 fields + edit hints render channel-agnostically | VALIDATED | cap-02, ux, hermes |
