from __future__ import annotations

import json
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from config import get_settings


def _parse_tool_result(content: list[Any]) -> dict[str, Any]:
    for block in content:
        text = getattr(block, "text", None)
        if text:
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    return parsed
                if isinstance(parsed, list):
                    return {"items": parsed}
            except json.JSONDecodeError:
                continue
    raise RuntimeError(f"MCP tool returned unparseable content: {content!r}")


async def _call_mcp_tool(tool_name: str, args: dict[str, Any]) -> dict[str, Any] | list[Any]:
    settings = get_settings()
    headers = {"Authorization": f"Bearer {settings.MCP_BEARER}"}
    async with streamable_http_client(settings.MCP_URL, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, args)
            if result.isError:
                raise RuntimeError(f"MCP {tool_name} error: {result.content}")
            parsed = _parse_tool_result(result.content)
            if isinstance(parsed, dict) and "items" in parsed and len(parsed) == 1:
                return parsed["items"]
            return parsed


async def call_mcp_create_item(
    title: str,
    type: str,
    category_id: str,
    summary: str = "",
) -> dict[str, Any]:
    result = await _call_mcp_tool(
        "create_item",
        {
            "title": title,
            "type": type,
            "category_id": category_id,
            "summary": summary,
        },
    )
    assert isinstance(result, dict)
    return result


async def call_mcp_update_item(item_id: str, **fields: Any) -> dict[str, Any]:
    args = {"item_id": item_id, **fields}
    result = await _call_mcp_tool("update_item", args)
    assert isinstance(result, dict)
    return result


async def call_mcp_confirm_item(item_id: str) -> dict[str, Any]:
    result = await _call_mcp_tool("confirm_item", {"item_id": item_id})
    assert isinstance(result, dict)
    return result


async def call_mcp_discard_item(item_id: str) -> dict[str, Any]:
    result = await _call_mcp_tool("discard_item", {"item_id": item_id})
    assert isinstance(result, dict)
    return result


async def call_mcp_get_item_status(item_id: str) -> str:
    result = await _call_mcp_tool("get_draft_status", {"item_id": item_id})
    assert isinstance(result, dict)
    return str(result["status"])


async def call_mcp_list_categories() -> list[dict[str, Any]]:
    result = await _call_mcp_tool("list_categories", {})
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        for key in ("categories", "items"):
            if key in result and isinstance(result[key], list):
                return result[key]
    return []
