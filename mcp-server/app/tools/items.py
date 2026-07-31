from __future__ import annotations

import uuid
from typing import Annotated, Literal

import httpx
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


def register_tools(mcp, client: httpx.AsyncClient) -> None:
    global _api_client
    _api_client = client
    mcp.tool(create_item)
