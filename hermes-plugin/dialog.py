from __future__ import annotations

import os
import uuid
from typing import Any

from formatters import format_confirmation
from schemas import DraftPreview
from tools import call_mcp_create_item


def _stub_category_id() -> str:
    # ponytail: inbox UUID stub until Plan 03 list_categories — upgrade via MCP_CATEGORY_ID env
    return os.environ.get(
        "MCP_CATEGORY_ID",
        "33333333-3333-4333-8333-333333333333",
    )


async def handle_user_message(session: Any, message_text: str) -> str:
    text = message_text.strip()
    title = (text.split("\n", 1)[0] if text else "Neue Notiz")[:200]
    summary = text[:500]

    result = await call_mcp_create_item(
        title=title,
        type="note",
        category_id=_stub_category_id(),
        summary=summary,
    )

    draft = DraftPreview(
        id=uuid.UUID(str(result["id"])),
        title=result.get("title", title),
        type=result.get("type", "note"),
        category="Inbox",
        summary=result.get("summary", summary),
    )
    return format_confirmation(draft)
