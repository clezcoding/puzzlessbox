from __future__ import annotations

from typing import Annotated

import httpx
from fastmcp.server.dependencies import get_access_token
from pydantic import Field

from app.api_client import call_api

_api_client: httpx.AsyncClient | None = None


async def list_categories() -> list | dict:
    """List system default and owner categories."""
    if _api_client is None:
        raise RuntimeError("MCP tools not registered")
    owner_id = get_access_token().claims["owner_id"]
    return await call_api(_api_client, "GET", "/categories", owner_id)


async def create_category(
    name: Annotated[str, Field(description="Category name", min_length=1)],
) -> dict:
    """Create an owner category."""
    if _api_client is None:
        raise RuntimeError("MCP tools not registered")
    owner_id = get_access_token().claims["owner_id"]
    return await call_api(
        _api_client,
        "POST",
        "/categories",
        owner_id,
        json={"name": name},
    )


def register_tools(mcp, client: httpx.AsyncClient) -> None:
    global _api_client
    _api_client = client
    mcp.tool(list_categories)
    mcp.tool(create_category)
