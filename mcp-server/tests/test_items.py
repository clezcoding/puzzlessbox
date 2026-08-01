"""MCP item tool tests (discard_item, get_draft_status)."""

from __future__ import annotations

import inspect
from unittest.mock import patch

import httpx
import pytest
from fastmcp.exceptions import ToolError
from fastmcp.server.auth import AccessToken

from tests.conftest import TEST_ITEM_ID, TEST_OWNER_ID


def _access_token() -> AccessToken:
    return AccessToken(
        token="test",
        client_id=TEST_OWNER_ID,
        scopes=[],
        claims={"owner_id": TEST_OWNER_ID, "sub": TEST_OWNER_ID},
    )


@pytest.mark.asyncio
async def test_discard_item_calls_api(mcp_stack, mock_api_state) -> None:
    from app.tools.items import discard_item

    mock_api_state["api_calls"].clear()
    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        result = await discard_item(item_id=TEST_ITEM_ID)

    assert result == {"id": TEST_ITEM_ID, "type": "note", "status": "discarded"}
    calls = mock_api_state["api_calls"]
    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert calls[0]["path"] == f"/drafts/{TEST_ITEM_ID}/discard"


@pytest.mark.asyncio
async def test_discard_item_404_passthrough(mcp_stack, mock_api_state) -> None:
    from app.tools.items import discard_item

    mock_api_state["api_calls"].clear()

    def not_found_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/discard"):
            return httpx.Response(
                404,
                json={"error": {"code": "NOT_FOUND", "message": "Draft not found."}},
            )
        return httpx.Response(404)

    _, mcp, client = mcp_stack
    client._transport = httpx.MockTransport(not_found_handler)

    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        with pytest.raises(ToolError) as exc_info:
            await discard_item(item_id=TEST_ITEM_ID)
    assert str(exc_info.value).startswith("NOT_FOUND:")


@pytest.mark.asyncio
async def test_discard_item_registered(mcp_stack) -> None:
    _, mcp, _ = mcp_stack
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert "discard_item" in names


def test_discard_item_owner_id_from_claims() -> None:
    from app.tools.items import discard_item

    sig = inspect.signature(discard_item)
    assert "owner_id" not in sig.parameters


@pytest.mark.asyncio
async def test_get_draft_status_calls_api(mcp_stack, mock_api_state) -> None:
    from app.tools.items import get_draft_status

    mock_api_state["api_calls"].clear()
    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        result = await get_draft_status(item_id=TEST_ITEM_ID)

    assert result == {"id": TEST_ITEM_ID, "type": "note", "status": "draft"}
    calls = mock_api_state["api_calls"]
    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["path"] == f"/drafts/{TEST_ITEM_ID}"


@pytest.mark.asyncio
async def test_get_draft_status_returns_auto_saved(mcp_stack, mock_api_state) -> None:
    from app.tools.items import get_draft_status

    def auto_saved_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and request.url.path == f"/drafts/{TEST_ITEM_ID}":
            return httpx.Response(
                200,
                json={
                    "id": TEST_ITEM_ID,
                    "type": "note",
                    "status": "auto_saved",
                    "title": "t",
                    "category_id": None,
                    "summary": "s",
                },
            )
        return httpx.Response(404)

    _, mcp, client = mcp_stack
    client._transport = httpx.MockTransport(auto_saved_handler)

    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        result = await get_draft_status(item_id=TEST_ITEM_ID)

    assert result["status"] == "auto_saved"


@pytest.mark.asyncio
async def test_get_draft_status_404_passthrough(mcp_stack, mock_api_state) -> None:
    from app.tools.items import get_draft_status

    def not_found_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and request.url.path.startswith("/drafts/"):
            return httpx.Response(
                404,
                json={"error": {"code": "NOT_FOUND", "message": "Draft not found."}},
            )
        return httpx.Response(404)

    _, mcp, client = mcp_stack
    client._transport = httpx.MockTransport(not_found_handler)

    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        with pytest.raises(ToolError) as exc_info:
            await get_draft_status(item_id=TEST_ITEM_ID)
    assert str(exc_info.value).startswith("NOT_FOUND:")


@pytest.mark.asyncio
async def test_get_draft_status_registered(mcp_stack) -> None:
    _, mcp, _ = mcp_stack
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert "get_draft_status" in names


def test_get_draft_status_owner_id_from_claims() -> None:
    from app.tools.items import get_draft_status

    sig = inspect.signature(get_draft_status)
    assert "owner_id" not in sig.parameters
