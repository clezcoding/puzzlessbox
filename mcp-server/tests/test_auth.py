"""MCP auth seam tests (MCP-02)."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport

from app.config import Settings
from tests.conftest import TEST_BEARER

WELL_KNOWN_PATH = "/.well-known/oauth-protected-resource/mcp"


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


@pytest.mark.asyncio
async def test_well_known_returns_rfc9728_metadata(mcp_stack) -> None:
    http_app, _mcp, _client = mcp_stack
    transport = ASGITransport(app=http_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(WELL_KNOWN_PATH)
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")
    body = response.json()
    assert "resource" in body
    assert body.get("bearer_methods_supported") == ["header"]
    assert "authorization_servers" not in body


@pytest.mark.asyncio
async def test_resource_matches_mcp_public_base_url(
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
        response = await http_client.get(WELL_KNOWN_PATH)
    await client.aclose()
    assert response.status_code == 200
    assert response.json()["resource"] == "https://mcp.puzzlesstool.online/mcp"


@pytest.mark.asyncio
async def test_resource_fallback_when_no_base_url(
    build_test_stack,
    mock_api_transport,
) -> None:
    custom_settings = Settings(MCP_PUBLIC_BASE_URL=None)
    http_app, _mcp, client = build_test_stack(settings=custom_settings)
    transport = ASGITransport(app=http_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
        response = await http_client.get(WELL_KNOWN_PATH)
    await client.aclose()
    assert response.status_code == 200
    assert response.json()["resource"] == "http://localhost:8000/mcp"


@pytest.mark.asyncio
async def test_well_known_no_authorization_servers(mcp_stack) -> None:
    http_app, _mcp, _client = mcp_stack
    transport = ASGITransport(app=http_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(WELL_KNOWN_PATH)
    assert response.status_code == 200
    assert "authorization_servers" not in response.json()


@pytest.mark.asyncio
async def test_well_known_closes_404(mcp_stack) -> None:
    http_app, _mcp, _client = mcp_stack
    transport = ASGITransport(app=http_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(WELL_KNOWN_PATH)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_d12_static_bearer_documented(mcp_stack) -> None:
    http_app, _mcp, _client = mcp_stack
    transport = ASGITransport(app=http_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(WELL_KNOWN_PATH)
    assert response.status_code == 200
    health_source = Path(__file__).resolve().parents[1] / "app" / "health.py"
    source_text = health_source.read_text(encoding="utf-8")
    assert "static shared bearer" in source_text.lower()
    assert "not full mcp authorization spec oauth discovery" in source_text.lower()
