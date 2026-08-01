# Phase 03: Hermes-Plugin & Timeout-Spike - Pattern Map

**Mapped:** 2026-08-01
**Files analyzed:** 10
**Analogs found:** 10 / 10

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `hermes-plugin/plugin.yaml` | config | config | `mcp-server/app/config.py` | partial |
| `hermes-plugin/__init__.py` | entrypoint | setup | `mcp-server/app/__init__.py` | exact |
| `hermes-plugin/config.py` | config | config | `mcp-server/app/config.py` | exact |
| `hermes-plugin/schemas.py` | model | transform | `api/app/models/board.py` | exact |
| `hermes-plugin/tools.py` | service | request-response | `.planning/spikes/002-mcp-confirm-flow/confirm_flow.py` | exact |
| `hermes-plugin/formatters.py` | utility | transform | `.planning/spikes/004-confirmation-payload/format_confirmation.py` | exact |
| `hermes-plugin/dialog.py` | controller | event-driven | `api/app/routers/capture.py` | role-match |
| `hermes-plugin/setup.sh` | script | setup | `api/app/core/bootstrap.py` | partial |
| `mcp-server/app/tools/items.py` | controller | request-response | `mcp-server/app/tools/items.py` | exact |
| `api/app/routers/capture.py` | controller | request-response | `api/app/routers/capture.py` | exact |

## Pattern Assignments

### `hermes-plugin/config.py` (config, config)

**Analog:** `mcp-server/app/config.py`

**Imports and Settings pattern** (lines 1-21):
```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    MCP_URL: str = "https://mcp.puzzlesstool.online/mcp"
    MCP_BEARER: str = ""
    ENV: str = "dev"

    @property
    def is_prod(self) -> bool:
        return self.ENV.lower() == "prod"

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

### `hermes-plugin/schemas.py` (model, transform)

**Analog:** `api/app/models/board.py`

**Imports and Model pattern** (lines 1-24):
```python
import uuid
from pydantic import BaseModel, Field

class DraftPreview(BaseModel):
    id: uuid.UUID
    title: str
    type: str
    category: str
    summary: str
```

---

### `hermes-plugin/tools.py` (service, request-response)

**Analog:** `.planning/spikes/002-mcp-confirm-flow/confirm_flow.py`

**MCP Client Connection pattern** (lines 113-164):
```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from hermes_plugin.config import get_settings

async def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    settings = get_settings()
    headers = {"Authorization": f"Bearer {settings.MCP_BEARER}"}
    async with streamablehttp_client(settings.MCP_URL, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            if result.isError:
                raise RuntimeError(f"MCP Tool Error: {result.content}")
            return result.content
```

---

### `hermes-plugin/formatters.py` (utility, transform)

**Analog:** `.planning/spikes/004-confirmation-payload/format_confirmation.py`

**CAP-02 Formatter pattern** (lines 1-37):
```python
from typing import TypedDict

TYPE_LABELS = {
    "note": "Notiz",
    "task": "Task",
    "link": "Link",
    "event": "Termin",
}

class DraftPreview(TypedDict):
    title: str
    type: str
    category: str
    summary: str

def format_confirmation(draft: DraftPreview) -> str:
    type_label = TYPE_LABELS.get(draft["type"], draft["type"])
    return "\n".join(
        [
            "📥 Stash-Check — passt das so?",
            "",
            f"Titel: {draft['title']}",
            f"Typ: {type_label}",
            f"Kategorie: {draft['category']}",
            f"Kurz: {draft['summary']}",
            "",
            "Antworte mit „Eintrag sichern“ oder tippe Bearbeiten.",
            "(Auto-Save in 30s wenn du nichts tust — API-Timer, nicht Hermes-Cron.)",
        ]
    )
```

---

### `hermes-plugin/dialog.py` (controller, event-driven)

**Analog:** `api/app/routers/capture.py` (State machine/dialog handler)

**Conversational Edit & Concurrency pattern** (RESEARCH.md Pattern 1, 2, 3):
```python
import asyncio

async def handle_user_message(session, message_text: str) -> str:
    active_draft = await session.get_state("active_draft")
    if not active_draft:
        return await start_capture_flow(session, message_text)
        
    if message_text.strip().lower() in ["eintrag sichern", "sichern", "confirm"]:
        await call_mcp_confirm_item(active_draft["id"])
        await session.clear_state("active_draft")
        return "✅ Eintrag erfolgreich gesichert!"
        
    if message_text.strip().lower() in ["verwerfen", "löschen", "discard"]:
        await call_mcp_discard_item(active_draft["id"])
        await session.clear_state("active_draft")
        return "🗑️ Eintrag verworfen."

    # Conversational Edit (D-01/D-02)
    updated_fields = await llm_extract_edits(message_text, active_draft)
    if updated_fields:
        await call_mcp_update_item(active_draft["id"], **updated_fields)
        active_draft.update(updated_fields)
        await session.set_state("active_draft", active_draft)
        return "✍️ Änderungen übernommen." # Silent ACK (D-03)
    
    return "Ich habe dich nicht verstanden. Antworte mit „Eintrag sichern“, „Verwerfen“ oder beschreibe deine Änderungen."

async def schedule_autosave_poll(session, draft_id: str, delay_seconds: float = 32.0):
    await asyncio.sleep(delay_seconds)
    status = await call_mcp_get_item_status(draft_id)
    if status == "auto_saved":
        await session.send_message("📦 Automatisch gestasht (lands on board).")

async def start_capture_flow(session, text: str) -> str:
    active_draft = await session.get_state("active_draft")
    if active_draft:
        await session.set_state("pending_capture_text", text)
        return (
            "⚠️ Du hast noch einen offenen Entwurf.\n"
            "Möchtest du den alten Eintrag sichern oder verwerfen, bevor wir fortfahren?"
        )
    # Normal capture flow starts here...
```

---

### `mcp-server/app/tools/items.py` (controller, request-response)

**Analog:** `mcp-server/app/tools/items.py`

**Tool definition pattern** (lines 49-81):
```python
from typing import Annotated
from pydantic import Field
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_access_token
from app.api_client import call_api

async def discard_item(
    item_id: Annotated[str, Field(description="Draft UUID to discard/soft-delete")],
) -> dict:
    """Soft-delete a capture draft by setting deleted_at."""
    if _api_client is None:
        raise RuntimeError("MCP tools not registered")
    owner_id = get_access_token().claims["owner_id"]
    return await call_api(
        _api_client,
        "POST",
        f"/drafts/{item_id}/discard",
        owner_id,
    )
```

---

### `api/app/routers/capture.py` (controller, request-response)

**Analog:** `api/app/routers/capture.py`

**FastAPI endpoint pattern** (lines 190-221):
```python
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlmodel import Session
from app.auth.jwt import get_db_for_owner
from app.core.database import current_owner_id
from app.services.timeout import table_for_item_type, timeout_manager

@router.post("/drafts/{draft_id}/discard")
async def discard_draft(
    draft_id: str,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, Any]:
    owner_id = current_owner_id.get()
    if not owner_id:
        raise RuntimeError("owner_id missing after auth dependency")

    item_type = _lookup_draft_type(db, owner_id, draft_id)
    table = table_for_item_type(item_type)
    discarded = db.execute(
        text(
            f"""
            UPDATE {table}
            SET deleted_at = NOW(), updated_at = NOW()
            WHERE id = :draft_id
              AND owner_id = :owner_id
              AND status IN ('draft', 'auto_saved')
            RETURNING id
            """
        ),
        {"draft_id": draft_id, "owner_id": owner_id},
    ).scalar_one_or_none()
    if discarded is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Draft not found."},
        )
    db.commit()
    timeout_manager.cancel_timeout(draft_id)
    return {"id": draft_id, "type": item_type.value, "status": "discarded"}
```

## Shared Patterns

### Configuration Loading
**Source:** `hermes-plugin/config.py`
**Apply to:** All plugin modules requiring environment variables.
```python
from hermes_plugin.config import get_settings
settings = get_settings()
# Use settings.MCP_URL, settings.MCP_BEARER
```

### Error Handling
**Source:** `mcp-server/app/api_client.py`
**Apply to:** All outgoing API/MCP requests in the plugin.
```python
import httpx
# Handle httpx.RequestError and raise ToolError or RuntimeError
```

## No Analog Found

All files to be created have clear analogs in terms of their roles and data flows.

## Metadata

**Analog search scope:** `mcp-server/`, `api/`, `.planning/spikes/`
**Files scanned:** 15 (mcp-server) + 57 (api) + 4 (spikes) = 76
**Pattern extraction date:** 2026-08-01
