"""MCP auth seam tests (MCP-02)."""

from __future__ import annotations

import httpx
import pytest
from httpx import ASGITransport

from tests.conftest import TEST_BEARER


@pytest.mark.asyncio
async def test_missing_bearer_401(mcp_stack) -> None:
    http_app, _mcp, _client = mcp_stack
    transport = ASGITransport(app=http_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/mcp")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate", "").lower().startswith("bearer")


@pytest.mark.asyncio
async def test_invalid_bearer_401(mcp_stack) -> None:
    http_app, _mcp, _client = mcp_stack
    transport = ASGITransport(app=http_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/mcp", headers={"Authorization": "Bearer bad-token"})
    assert response.status_code == 401
    assert "invalid_token" in response.text


@pytest.mark.asyncio
async def test_invalid_bearer_401_when_api_unreachable(mcp_stack, monkeypatch) -> None:
    http_app, _mcp, client = mcp_stack

    async def _boom(*_args, **_kwargs):
        raise httpx.ConnectError("dns fail", request=httpx.Request("POST", "http://bad"))

    monkeypatch.setattr(client, "post", _boom)
    transport = ASGITransport(app=http_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http:
        response = await http.post("/mcp", headers={"Authorization": "Bearer bad-token"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_owner_reject(mcp_stack, mock_api_state) -> None:
    mock_api_state["auth_reject"] = True
    http_app, _mcp, _client = mcp_stack
    transport = ASGITransport(app=http_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/mcp",
            headers={"Authorization": f"Bearer {TEST_BEARER}"},
        )
    assert response.status_code == 401
