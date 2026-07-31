---
spike: 004
name: confirmation-payload
type: standard
validates: "Given draft fields, when formatted for chat, then CAP-02 fields + edit hints render channel-agnostically"
verdict: VALIDATED
related: [002]
tags: [cap-02, ux, hermes, voice]
---

# Spike 004: Confirmation Payload (CAP-02)

## What This Validates

**Given** structured draft (title, type, category, summary),  
**When** Hermes sends pre-save confirmation,  
**Then** user sees all CAP-02 fields + edit/confirm/discard actions — plain text, no channel-specific markup required.

## How to Run

Interactive preview:

```bash
open .planning/spikes/004-confirmation-payload/preview.html
```

Formatter self-check:

```bash
python3 .planning/spikes/004-confirmation-payload/format_confirmation.py
```

## What to Expect

- Preview updates live as fields change.
- Message includes 30s API-timer note (Spike 001 alignment).
- Buttons map to plugin actions: `confirm` → `confirm_item`, `edit` → conversational edit → `update_item`.

## Results

**Verdict: VALIDATED**

Plain-text template works for Telegram/WhatsApp/Discord; brand tone aligned with `brand/VOICE.md` (trocken, physisch, „Stash-Check“). Edit affordance via reply + optional inline buttons.

**Impact:** Port `format_confirmation()` to `hermes-plugin/`; map button labels to MCP tool calls in Phase 3.
