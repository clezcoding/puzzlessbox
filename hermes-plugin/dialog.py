from __future__ import annotations

import asyncio
import re
import uuid
from typing import Any

from formatters import format_confirmation
from schemas import DraftPreview
from tools import (
    call_mcp_confirm_item,
    call_mcp_create_item,
    call_mcp_discard_item,
    call_mcp_get_item_status,
    call_mcp_list_categories,
    call_mcp_update_item,
)

_URL_RE = re.compile(r"https?://\S+", re.I)
_DATETIME_RE = re.compile(r"\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2}|\d{1,2}\.\d{1,2}\.")

_TYPE_CATEGORY_HINTS: dict[str, list[str]] = {
    "link": ["Links", "Link"],
    "event": ["Termine", "Termin"],
    "task": ["Tasks", "Task"],
    "note": ["Inbox", "Notizen", "Notiz"],
}

_CONFIRM_PHRASES = frozenset({"eintrag sichern", "sichern", "confirm"})
_DISCARD_PHRASES = frozenset({"verwerfen", "löschen", "discard"})
_WAIT_PHRASES = frozenset({"warten", "wait", "später"})

# ponytail: hardcoded Inbox UUID for low-confidence fallback when categories lack Inbox row
_INBOX_FALLBACK_ID = "33333333-3333-4333-8333-333333333333"


def _llm_extract_edits(text: str, active_draft: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for line in text.split("\n"):
        stripped = line.strip()
        lower = stripped.lower()
        if lower.startswith("titel:"):
            fields["title"] = stripped.split(":", 1)[1].strip()
        elif lower.startswith("kurz:"):
            fields["summary"] = stripped.split(":", 1)[1].strip()
        elif lower.startswith("kategorie:"):
            fields["category_id"] = stripped.split(":", 1)[1].strip()
    return fields


def _llm_choose_type_category(
    text: str,
    categories: list[dict[str, Any]],
) -> tuple[str, str, str, float]:
    if _URL_RE.search(text):
        item_type = "link"
    elif _DATETIME_RE.search(text):
        item_type = "event"
    else:
        item_type = "note"

    cat_by_name = {c.get("name", ""): c for c in categories}
    hints = _TYPE_CATEGORY_HINTS.get(item_type, ["Inbox"])
    category_id: str | None = None
    category_name = "Inbox"
    confidence = 1.0

    for hint in hints:
        if hint in cat_by_name:
            category_name = hint
            category_id = str(cat_by_name[hint]["id"])
            break
    else:
        confidence = 0.3
        if "Inbox" in cat_by_name:
            category_id = str(cat_by_name["Inbox"]["id"])
            category_name = "Inbox"
            confidence = 0.5

    if category_id is None:
        confidence = 0.2
        category_id = _INBOX_FALLBACK_ID
        category_name = "Inbox"

    if confidence < 0.5:
        category_id = _INBOX_FALLBACK_ID
        category_name = "Inbox"

    return item_type, category_id, category_name, confidence


async def schedule_autosave_poll(
    session: Any,
    draft_id: str,
    delay_seconds: float = 32.0,
) -> None:
    await asyncio.sleep(delay_seconds)
    status = await call_mcp_get_item_status(draft_id)
    if status == "auto_saved":
        await session.send_message("📦 Automatisch gestasht (lands on board).")
        active_draft = await session.get_state("active_draft")
        if active_draft:
            active_draft["status"] = "auto_saved"
            await session.set_state("active_draft", active_draft)


async def start_capture_flow(session: Any, text: str) -> str:
    active_draft = await session.get_state("active_draft")
    if active_draft:
        await session.set_state("pending_capture_text", text)
        return (
            "⚠️ Du hast noch einen offenen Entwurf. "
            "Sichern, Verwerfen oder Warten?"
        )

    categories = await call_mcp_list_categories()
    item_type, category_id, category_name, _confidence = _llm_choose_type_category(
        text, categories
    )

    title = (text.split("\n", 1)[0] if text else "Neue Notiz")[:200]
    summary = text[:500]

    result = await call_mcp_create_item(
        title=title,
        type=item_type,
        category_id=category_id,
        summary=summary,
    )

    draft_id = str(result["id"])
    await session.set_state(
        "active_draft",
        {
            "id": draft_id,
            "title": result.get("title", title),
            "type": result.get("type", item_type),
            "category": category_name,
            "summary": result.get("summary", summary),
            "status": "draft",
        },
    )

    asyncio.create_task(schedule_autosave_poll(session, draft_id))

    draft = DraftPreview(
        id=uuid.UUID(draft_id),
        title=result.get("title", title),
        type=result.get("type", item_type),
        category=category_name,
        summary=result.get("summary", summary),
    )
    return format_confirmation(draft)


async def handle_user_message(session: Any, message_text: str) -> str:
    text = message_text.strip()
    text_lower = text.lower()

    active_draft = await session.get_state("active_draft")
    if not active_draft:
        return await start_capture_flow(session, text)

    pending_capture_text = await session.get_state("pending_capture_text")
    if pending_capture_text:
        if text_lower in _CONFIRM_PHRASES:
            await call_mcp_confirm_item(active_draft["id"])
            await session.clear_state("active_draft")
            pending = pending_capture_text
            await session.clear_state("pending_capture_text")
            return await start_capture_flow(session, pending)
        if text_lower in _DISCARD_PHRASES:
            await call_mcp_discard_item(active_draft["id"])
            await session.clear_state("active_draft")
            pending = pending_capture_text
            await session.clear_state("pending_capture_text")
            return await start_capture_flow(session, pending)
        if text_lower in _WAIT_PHRASES:
            return (
                "⏸️ Okay, ich halte die neue Notiz zurück. "
                "Sichere oder verwerfe erst den offenen Entwurf."
            )

    if text_lower in _CONFIRM_PHRASES:
        live_status = await call_mcp_get_item_status(active_draft["id"])
        await call_mcp_confirm_item(active_draft["id"])
        await session.clear_state("active_draft")
        if live_status == "auto_saved":
            return "✅ War schon automatisch gestasht."
        return "✅ Eintrag erfolgreich gesichert!"

    if text_lower in _DISCARD_PHRASES:
        await call_mcp_discard_item(active_draft["id"])
        await session.clear_state("active_draft")
        return "🗑️ Eintrag verworfen."

    updated_fields = _llm_extract_edits(text, active_draft)
    if updated_fields:
        await call_mcp_update_item(active_draft["id"], **updated_fields)
        active_draft.update(updated_fields)
        await session.set_state("active_draft", active_draft)
        return "✍️ Änderungen übernommen."

    if not pending_capture_text:
        return await start_capture_flow(session, text)

    return (
        "Ich habe dich nicht verstanden. Antworte mit „Eintrag sichern“, "
        "„Verwerfen“ oder beschreibe deine Änderungen."
    )
