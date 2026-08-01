from __future__ import annotations

import uuid
from typing import Annotated, Literal

import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_access_token
from pydantic import Field

from app.api_client import call_api

_api_client: httpx.AsyncClient | None = None


async def create_item(
    title: Annotated[str, Field(description="Item title", min_length=1)],
    type: Annotated[
        Literal["note", "link", "task", "event"],
        Field(description="Item type"),
    ],
    category_id: Annotated[str, Field(description="Target category UUID")],
    summary: Annotated[str, Field(description="Short summary")] = "",
    idempotency_key: Annotated[
        str | None,
        Field(description="Optional client idempotency key"),
    ] = None,
) -> dict:
    """Create a capture draft (starts the 30s confirmation timer)."""
    if _api_client is None:
        raise RuntimeError("MCP tools not registered")
    owner_id = get_access_token().claims["owner_id"]
    body = {
        "title": title,
        "type": type,
        "category_id": category_id,
        "summary": summary,
    }
    return await call_api(
        _api_client,
        "POST",
        "/drafts",
        owner_id,
        json=body,
        idempotency_key=idempotency_key or str(uuid.uuid4()),
    )


async def confirm_item(
    item_id: Annotated[str, Field(description="Draft UUID")],
    title: Annotated[str | None, Field(description="Optional title patch")] = None,
    summary: Annotated[str | None, Field(description="Optional summary patch")] = None,
    category_id: Annotated[str | None, Field(description="Optional category UUID patch")] = None,
) -> dict:
    """Confirm a draft. Optionally patch title/summary/category before confirm."""
    if _api_client is None:
        raise RuntimeError("MCP tools not registered")
    owner_id = get_access_token().claims["owner_id"]
    patch = {
        k: v
        for k, v in {
            "title": title,
            "summary": summary,
            "category_id": category_id,
        }.items()
        if v is not None
    }
    if patch:
        await call_api(
            _api_client,
            "PATCH",
            f"/drafts/{item_id}",
            owner_id,
            json=patch,
        )
    return await call_api(
        _api_client,
        "POST",
        f"/drafts/{item_id}/confirm",
        owner_id,
    )


async def update_item(
    item_id: Annotated[str, Field(description="Draft UUID")],
    title: Annotated[str | None, Field(description="Optional title")] = None,
    summary: Annotated[str | None, Field(description="Optional summary")] = None,
    category_id: Annotated[str | None, Field(description="Optional category UUID")] = None,
) -> dict:
    """Patch a draft (draft/auto_saved only). Use move_item for confirmed items."""
    if _api_client is None:
        raise RuntimeError("MCP tools not registered")
    owner_id = get_access_token().claims["owner_id"]
    patch = {
        k: v
        for k, v in {
            "title": title,
            "summary": summary,
            "category_id": category_id,
        }.items()
        if v is not None
    }
    if not patch:
        raise ToolError("VALIDATION_ERROR: no fields to update")
    return await call_api(
        _api_client,
        "PATCH",
        f"/drafts/{item_id}",
        owner_id,
        json=patch,
    )


async def move_item(
    item_id: Annotated[str, Field(description="Item UUID")],
    category_id: Annotated[str, Field(description="Target category UUID")],
) -> dict:
    """Move a board item to another category (any status)."""
    if _api_client is None:
        raise RuntimeError("MCP tools not registered")
    owner_id = get_access_token().claims["owner_id"]
    return await call_api(
        _api_client,
        "PATCH",
        f"/items/{item_id}",
        owner_id,
        json={"category_id": category_id},
    )


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


async def get_draft_status(
    item_id: Annotated[str, Field(description="Draft UUID to poll status for")],
) -> dict:
    """Read a draft's status (id, type, status) — poll path for autosave detection."""
    if _api_client is None:
        raise RuntimeError("MCP tools not registered")
    owner_id = get_access_token().claims["owner_id"]
    response = await call_api(
        _api_client,
        "GET",
        f"/drafts/{item_id}",
        owner_id,
    )
    return {
        "id": response["id"],
        "type": response["type"],
        "status": response["status"],
    }


def register_tools(mcp, client: httpx.AsyncClient) -> None:
    global _api_client
    _api_client = client
    mcp.tool(create_item)
    mcp.tool(confirm_item)
    mcp.tool(update_item)
    mcp.tool(move_item)
    mcp.tool(discard_item)
    mcp.tool(get_draft_status)
