---
name: spike-findings-puzzlessbox
description: Implementation blueprint from spike experiments. Requirements, proven patterns, and verified knowledge for building Puzzlessbox Phase 3 (Hermes plugin). Auto-loaded during implementation work.
---

<context>
## Project: puzzlessbox

Phase 3 (Hermes-Plugin & Timeout-Spike) de-risking: validate that API-side 30s timers replace Hermes cron for precision, that Hermes can drive MCP tools over HTTPS from a remote VPS, and that the confirmation UX payload is channel-agnostic before `/gsd-plan-phase 3`.

Spike sessions wrapped: 2026-07-31
</context>

<requirements>
## Requirements

- 30s auto-save precision MUST live in FastAPI (`DraftTimeoutManager`), not Hermes cron (MCP-04).
- Hermes plugin MUST call MCP tools only — no direct DB access (Phase 3 success criterion).
- Confirmation message MUST include title, type, category, summary + edit affordance (CAP-02).
- Optional Hermes cron MAY notify user after API `auto_saved` — never drive the timer itself.
- Tool error semantics: 401 on bad bearer, structured `code` in tool errors (Phase 2 D-13).
</requirements>

<findings_index>
## Feature Areas

| Area | Reference | Key Finding |
|------|-----------|-------------|
| Draft timeout | references/draft-timeout.md | API asyncio timer VALIDATED; Hermes cron INVALIDATED for 30s |
| MCP remote integration | references/mcp-remote-integration.md | Mock confirm flow VALIDATED; live MCP auth 401 VALIDATED |
| Capture confirmation UX | references/capture-confirmation-ux.md | Plain-text CAP-02 template VALIDATED |

## Source Files

Original spike source files are preserved in `sources/` for complete reference.
</findings_index>

<metadata>
## Processed Spikes

- 001-hermes-cron-vs-api-timer
- 002-mcp-confirm-flow
- 003-remote-mcp-vps
- 004-confirmation-payload
</metadata>

## When to Use

Load this skill before `/gsd-plan-phase 3`, `/gsd-execute-phase 3`, or any `hermes-plugin/` implementation work.

Read the feature-area reference that matches your task — do not re-spike validated questions unless production behavior diverges.
