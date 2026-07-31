---
spike: 002
name: mcp-confirm-flow
type: standard
validates: "Given create_item draft, when confirm_item runs, then item reaches confirmed via MCP→API only"
verdict: PARTIAL
related: [001, 003]
tags: [mcp, mcp-03, confirm, orchestration]
---

# Spike 002: MCP Confirm Flow

## What This Validates

**Given** a capture draft from `create_item`,  
**When** Hermes plugin calls `update_item` (optional) then `confirm_item`,  
**Then** only MCP→API HTTP is used (no DB on Hermes VPS).

## How to Run

Mock (no secrets, in-process):

```bash
cd mcp-server && . .venv/bin/activate && python ../.planning/spikes/002-mcp-confirm-flow/confirm_flow.py
```

Live (production MCP):

```bash
MCP_BEARER='…' MCP_CATEGORY_ID='…' python confirm_flow.py --live
```

## What to Expect

Mock: all steps `ok: true`, `wiring` shows POST `/drafts`, PATCH `/drafts/{id}`, POST `.../confirm`.

Live: `create_item` succeeds with valid env; full confirm left to Hermes integration (needs real category UUID).

## Results

**Verdict: PARTIAL**

| Mode | Result |
|------|--------|
| Mock orchestration | ✓ VALIDATED — tool chain + API paths correct |
| Live E2E confirm | ⚠ needs Hermes VPS + real category_id |

**Impact:** Phase 3 plugin implements state machine: `create_item` → show CAP-02 card → `update_item?` → `confirm_item` or wait for API `auto_saved`.
