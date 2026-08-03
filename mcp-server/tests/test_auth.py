"""MCP auth seam tests (MCP-02)."""

from __future__ import annotations

import httpx
import pytest
from httpx import ASGITransport

from app.config import Settings
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


@pytest.mark.asyncio
async def test_www_authenticate_uses_public_base_url_in_prod_like_config(
    build_test_stack,
    mock_api_transport,
) -> None:
    custom_settings = Settings(
        MCP_PUBLIC_BASE_URL="https://mcp.puzzlesstool.online",
        ENV="prod",
    )
    http_app, _mcp, client = build_test_stack(settings=custom_settings)
    transport = ASGITransport(app=http_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
        response = await http_client.post("/mcp")
    await client.aclose()
    assert response.status_code == 401
    www_authenticate = response.headers.get("www-authenticate", "").lower()
    assert "localhost" not in www_authenticate
    assert "mcp.puzzlesstool.online" in www_authenticate
