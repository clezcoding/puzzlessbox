"""CAP-02 confirmation formatter — shared contract for Hermes plugin."""

from __future__ import annotations

from schemas import DraftPreview

TYPE_LABELS = {
    "note": "Notiz",
    "task": "Task",
    "link": "Link",
    "event": "Termin",
}


def format_confirmation(draft: DraftPreview) -> str:
    type_label = TYPE_LABELS.get(draft.type, draft.type)
    return "\n".join(
        [
            "📥 Stash-Check — passt das so?",
            "",
            f"Titel: {draft.title}",
            f"Typ: {type_label}",
            f"Kategorie: {draft.category}",
            f"Kurz: {draft.summary}",
            "",
            "Antworte mit „Eintrag sichern“ oder tippe Bearbeiten.",
            "(Auto-Save in 30s wenn du nichts tust — API-Timer, nicht Hermes-Cron.)",
        ]
    )
