# Capture Confirmation UX (CAP-02)

## Requirements

- Confirmation message **MUST** include: title, type, category, summary + edit affordance (CAP-02).
- Plain-text first — channel-agnostic (Telegram, WhatsApp, Discord); map buttons in Hermes plugin.
- Voice: Apollo / `brand/VOICE.md` — trocken, physisch, kein Corporate-Slop.

## How to Build It

1. **Port formatter to `hermes-plugin/`** from spike source:

```python
def format_confirmation(draft: DraftPreview) -> str:
    return "\n".join([
        "📥 Stash-Check — passt das so?",
        "",
        f"Titel: {draft['title']}",
        f"Typ: {TYPE_LABELS[draft['type']]}",
        f"Kategorie: {draft['category']}",
        f"Kurz: {draft['summary']}",
        "",
        "Antworte mit „Eintrag sichern“ oder tippe Bearbeiten.",
        "(Auto-Save in 30s wenn du nichts tust — API-Timer, nicht Hermes-Cron.)",
    ])
```

2. **Action mapping** (plugin layer):

| User action | MCP call |
|-------------|----------|
| „Eintrag sichern“ / Confirm button | `confirm_item(item_id)` |
| Bearbeiten + new text | `update_item(item_id, …)` then re-send card |
| Verwerfen | no MCP delete in v1 — let 30s autosave or add later |
| Silence 30s | none — API autosaves |

3. **Preview spike UI** for stakeholder review:
   ```bash
   open .planning/spikes/004-confirmation-payload/preview.html
   ```

4. **Primary CTA label** from brand: „Eintrag sichern“ (`brand/VOICE.md` example #7).

## What to Avoid

- Channel-specific markup in core formatter — keep in adapter layer.
- Promising Hermes-Cron timing in user copy — always attribute autosave to API timer.
- English corporate copy („Your entry was successfully persisted“).

## Constraints

- German microcopy locked for v1; type labels: Notiz, Task, Link, Termin.
- Emoji 📥 optional but tested in spike preview.

## Origin

Synthesized from spikes: 004  
Source files: `sources/004-confirmation-payload/`
