# Spike Wrap-Up Summary

**Date:** 2026-07-31  
**Spikes processed:** 4  
**Feature areas:** draft-timeout, mcp-remote-integration, capture-confirmation-ux  
**Skill output:** `.claude/skills/spike-findings-puzzlessbox/`

## Processed Spikes

| # | Name | Type | Verdict | Feature Area |
|---|------|------|---------|--------------|
| 001 | hermes-cron-vs-api-timer | standard | VALIDATED | draft-timeout |
| 002 | mcp-confirm-flow | standard | PARTIAL (mock VALIDATED) | mcp-remote-integration |
| 003 | remote-mcp-vps | standard | VALIDATED | mcp-remote-integration |
| 004 | confirmation-payload | standard | VALIDATED | capture-confirmation-ux |

## Key Findings

- **MCP-04 gate cleared:** 30s precision is API `DraftTimeoutManager` only; Hermes 60s cron cannot substitute (INVALIDATED as timer).
- **Hermes plugin** orchestrates `create_item` → optional `update_item` → `confirm_item`; no DB on Hermes VPS.
- **Production MCP** at `mcp.puzzlesstool.online`: health OK, auth failures return 401.
- **CAP-02** confirmation is plain-text German template with edit/confirm actions; port `format_confirmation()` to `hermes-plugin/`.
- **Open for Phase 3 build:** live E2E confirm on Hermes VPS; optional post-autosave user notification via poll/webhook.
