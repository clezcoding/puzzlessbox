# Phase 3: Hermes-Plugin & Timeout-Spike - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-01
**Phase:** 3-Hermes-Plugin & Timeout-Spike
**Mode:** `--batch` (4 questions/turn) + recommended answers marked
**Areas discussed:** Edit-Flow im Chat, Post-Autosave-Notify, Parallele Drafts, Typ-/Kategorie-Vorschlag, Verwerfen-Semantik, Plugin-Deploy auf Hermes-VPS

---

## Edit-Flow im Chat

| Option | Description | Selected |
|--------|-------------|----------|
| Keyword „Bearbeiten“ then freetext | Extra hop before correction | |
| Direct freetext / NL rewrite | Next message = edit | ✓ |
| Guided field prompts | Title? Type? … | |

**User's choice:** Direct freetext/NL rewrite (1b)
**Notes:** Aligns with low-friction capture; confirm CTA remains „Eintrag sichern“

| Option | Description | Selected |
|--------|-------------|----------|
| LLM maps fields → update_item changed keys | Semantic edit parse | ✓ |
| Regex/heuristic | No LLM | |
| Whole rewrite as summary/title only | Coarse | |

**User's choice:** LLM field mapping (2a)

| Option | Description | Selected |
|--------|-------------|----------|
| Silent ACK | No second card | ✓ |
| Re-send Stash-Check card | Spike default | |
| Diff line only | Minimal | |

**User's choice:** Silent ACK (3a) — overrode ★ recommendation (re-send card)

---

## Verwerfen-Semantik

| Option | Description | Selected |
|--------|-------------|----------|
| No delete in v1 | Spike default | |
| Soft-delete via new MCP tool | Scope pull | ✓ |
| Copy without backend | Dishonest UX | |

**User's choice:** Soft-delete MCP tool (4b), then clarified **Phase 3 ships `discard_item`** (4x a)

**Notes:** Expands MCP tool surface beyond MCP-01; uses existing `deleted_at`

---

## Post-Autosave-Notify

| Option | Description | Selected |
|--------|-------------|----------|
| Silent | No chat ping | |
| Always chat ping | After auto_saved | ✓ |
| Ping only if session active | Needs session signal | |

**User's choice:** Always ping (1b)

| Option | Description | Selected |
|--------|-------------|----------|
| Poll ~30–35s | No new infra | ✓ |
| API webhook → Hermes | New OPS surface | |
| Hermes cron 60s scan | Too coarse | |

**User's choice:** Poll (2a)

---

## Parallele Drafts

| Option | Description | Selected |
|--------|-------------|----------|
| Queue parallel cards | Multi pending | |
| One active draft + ask | confirm/discard/wait | ✓ |
| Auto confirm/discard old | Data-loss risk | |

**User's choice:** One active + ask (3b)

| Option | Description | Selected |
|--------|-------------|----------|
| Show error on late confirm | Punishes slow typing | |
| Idempotent OK / friendly ACK | | ✓ |
| Silent ignore | Confusing | |

**User's choice:** Idempotent OK (4b)

---

## Typ-/Kategorie-Vorschlag

| Option | Description | Selected |
|--------|-------------|----------|
| LLM + list_categories + heuristic hints | | ✓ |
| Always Inbox + note | More friction | |
| Heuristics only | Thin for voice | |

**User's choice:** LLM + heuristics (1a)

| Option | Description | Selected |
|--------|-------------|----------|
| Best guess anyway | Silent wrong category | |
| Inbox fallback | Honest | ✓ |
| Ask before create_item | Blocks capture | |

**User's choice:** Inbox fallback (2b)

---

## Plugin-Deploy auf Hermes-VPS

| Option | Description | Selected |
|--------|-------------|----------|
| Monorepo + git pull/rsync | | ✓ |
| npm/pip publish | Overkill | |
| Coolify app for plugin | Overkill | |

**User's choice:** Monorepo path (3a)

| Option | Description | Selected |
|--------|-------------|----------|
| Hardcoded in plugin | Leak risk | |
| Env/secrets only | ★ rec | |
| Interactive first-start setup | | ✓ |

**User's choice:** Interactive setup (4c) — clarified: script **writes** `MCP_URL`/`MCP_BEARER` to Hermes env/secrets (never git)

---

## Claude's Discretion

- Exact German microcopy (VOICE.md)
- Poll implementation details
- Soft-delete API route shape if missing
- Setup-script prompt UX
- Per-channel button adapters vs text-only v1

## Deferred Ideas

- Webhook autosave notify
- Multi-draft queue
- Plugin package publish / Coolify plugin app
- Board UX for discarded items → Phase 4
