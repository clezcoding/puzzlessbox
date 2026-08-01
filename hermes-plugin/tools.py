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
            except json.JSONDecodeError:
                continue
    raise RuntimeError(f"MCP tool returned unparseable content: {content!r}")


async def call_mcp_create_item(
    title: str,
    type: str,
    category_id: str,
    summary: str = "",
) -> dict[str, Any]:
    settings = get_settings()
    headers = {"Authorization": f"Bearer {settings.MCP_BEARER}"}
    async with streamable_http_client(settings.MCP_URL, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "create_item",
                {
                    "title": title,
                    "type": type,
                    "category_id": category_id,
                    "summary": summary,
                },
            )
            if result.isError:
                raise RuntimeError(f"MCP create_item error: {result.content}")
            return _parse_tool_result(result.content)
