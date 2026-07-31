"""MCP health route tests (D-22)."""

from __future__ import annotations

import httpx
import pytest
from httpx import ASGITransport


@pytest.mark.asyncio
async def test_health_ok(mcp_stack) -> None:
    http_app, _mcp, _client = mcp_stack
    transport = ASGITransport(app=http_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
