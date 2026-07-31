"""MCP tool API contract tests (MCP-01)."""

from __future__ import annotations

import inspect
import uuid
from unittest.mock import patch

import httpx
import pytest
from fastmcp.exceptions import ToolError
from fastmcp.server.auth import AccessToken

from app.api_client import call_api, make_client
from app.config import get_settings
from tests.conftest import (
    TEST_CATEGORY_ID,
    TEST_ITEM_ID,
    TEST_OWNER_ID,
    TEST_TARGET_CATEGORY_ID,
)


def _access_token() -> AccessToken:
    return AccessToken(
        token="test",
        client_id=TEST_OWNER_ID,
        scopes=[],
        claims={"owner_id": TEST_OWNER_ID, "sub": TEST_OWNER_ID},
    )


@pytest.mark.asyncio
async def test_create_item_headers(mcp_stack, mock_api_state) -> None:
    from app.tools.items import create_item

    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        await create_item(
            title="Test note",
            type="note",
            category_id=TEST_CATEGORY_ID,
            summary="hello",
        )

    assert len(mock_api_state["drafts_calls"]) == 1
    call = mock_api_state["drafts_calls"][0]
    headers = call["headers"]
    assert headers.get("accept") == "application/vnd.puzzlessbox.v1+json"
    assert headers.get("x-service-bearer")
    assert headers.get("x-owner-id") == TEST_OWNER_ID
    assert headers.get("idempotency-key")


@pytest.mark.asyncio
async def test_create_item_idempotency(mcp_stack, mock_api_state) -> None:
    from app.tools.items import create_item

    provided_key = "client-key-123"
    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        await create_item(
            title="With key",
            type="task",
            category_id=TEST_CATEGORY_ID,
            idempotency_key=provided_key,
        )

    assert mock_api_state["drafts_calls"][0]["headers"].get("idempotency-key") == provided_key

    mock_api_state["drafts_calls"].clear()
    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        await create_item(
            title="Generated key",
            type="note",
            category_id=TEST_CATEGORY_ID,
        )

    generated = mock_api_state["drafts_calls"][0]["headers"].get("idempotency-key")
    assert generated
    assert generated != provided_key


def test_create_item_owner_from_claim() -> None:
    from app.tools.items import create_item

    sig = inspect.signature(create_item)
    assert "owner_id" not in sig.parameters


@pytest.mark.asyncio
async def test_confirm_item_confirm_only(mcp_stack, mock_api_state) -> None:
    from app.tools.items import confirm_item

    mock_api_state["api_calls"].clear()
    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        result = await confirm_item(item_id=TEST_ITEM_ID)

    assert result["status"] == "confirmed"
    calls = mock_api_state["api_calls"]
    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert calls[0]["path"] == f"/drafts/{TEST_ITEM_ID}/confirm"


@pytest.mark.asyncio
async def test_confirm_item_patch_then_confirm(mcp_stack, mock_api_state) -> None:
    from app.tools.items import confirm_item

    mock_api_state["api_calls"].clear()
    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        await confirm_item(
            item_id=TEST_ITEM_ID,
            title="Updated title",
            summary="Updated summary",
        )

    calls = mock_api_state["api_calls"]
    assert len(calls) == 2
    assert calls[0]["method"] == "PATCH"
    assert calls[0]["path"] == f"/drafts/{TEST_ITEM_ID}"
    assert calls[0]["json"] == {"title": "Updated title", "summary": "Updated summary"}
    assert calls[1]["method"] == "POST"
    assert calls[1]["path"] == f"/drafts/{TEST_ITEM_ID}/confirm"


@pytest.mark.asyncio
async def test_update_item_patch_drafts(mcp_stack, mock_api_state) -> None:
    from app.tools.items import update_item

    mock_api_state["api_calls"].clear()
    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        await update_item(item_id=TEST_ITEM_ID, category_id=TEST_TARGET_CATEGORY_ID)

    calls = mock_api_state["api_calls"]
    assert len(calls) == 1
    assert calls[0]["method"] == "PATCH"
    assert calls[0]["path"] == f"/drafts/{TEST_ITEM_ID}"
    assert calls[0]["json"] == {"category_id": TEST_TARGET_CATEGORY_ID}


@pytest.mark.asyncio
async def test_update_item_no_fields_raises(mcp_stack) -> None:
    from app.tools.items import update_item

    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        with pytest.raises(ToolError, match="VALIDATION_ERROR"):
            await update_item(item_id=TEST_ITEM_ID)


@pytest.mark.asyncio
async def test_move_item_patch_items(mcp_stack, mock_api_state) -> None:
    from app.tools.items import move_item

    mock_api_state["api_calls"].clear()
    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        await move_item(item_id=TEST_ITEM_ID, category_id=TEST_TARGET_CATEGORY_ID)

    calls = mock_api_state["api_calls"]
    assert len(calls) == 1
    assert calls[0]["method"] == "PATCH"
    assert calls[0]["path"] == f"/items/{TEST_ITEM_ID}"
    assert calls[0]["json"] == {"category_id": TEST_TARGET_CATEGORY_ID}


@pytest.mark.asyncio
async def test_call_api_retries_502_once() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(502, json={"error": {"code": "BAD_GATEWAY", "message": "retry"}})
        return httpx.Response(200, json={"ok": True})

    settings = get_settings()
    client = make_client(settings, transport=httpx.MockTransport(handler))
    try:
        result = await call_api(client, "GET", "/health", TEST_OWNER_ID)
        assert result == {"ok": True}
        assert attempts == 2
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_call_api_no_retry_on_500() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(500, json={"error": {"code": "INTERNAL", "message": "fail"}})

    settings = get_settings()
    client = make_client(settings, transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(ToolError, match="INTERNAL"):
            await call_api(client, "GET", "/health", TEST_OWNER_ID)
        assert attempts == 1
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_call_api_503_twice_raises() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(503, json={"error": {"code": "UNAVAILABLE", "message": "down"}})

    settings = get_settings()
    client = make_client(settings, transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(ToolError, match="UNAVAILABLE"):
            await call_api(client, "GET", "/health", TEST_OWNER_ID)
        assert attempts == 2
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_error_map_not_found(mcp_stack, mock_api_state) -> None:
    from app.tools.items import update_item

    mock_api_state["api_calls"].clear()
    mock_api_state["retry_paths"] = {
        f"PATCH:/drafts/{TEST_ITEM_ID}": [404],
    }

    def not_found_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == f"/drafts/{TEST_ITEM_ID}" and request.method == "PATCH":
            return httpx.Response(
                404,
                json={"error": {"code": "NOT_FOUND", "message": "Draft not found."}},
            )
        return httpx.Response(404)

    _, mcp, client = mcp_stack
    client._transport = httpx.MockTransport(not_found_handler)

    with patch("app.tools.items.get_access_token", return_value=_access_token()):
        with pytest.raises(ToolError) as exc_info:
            await update_item(item_id=TEST_ITEM_ID, title="x")
    assert str(exc_info.value).startswith("NOT_FOUND:")


@pytest.mark.asyncio
async def test_list_categories_get(mcp_stack, mock_api_state) -> None:
    from app.tools.categories import list_categories

    mock_api_state["api_calls"].clear()
    with patch("app.tools.categories.get_access_token", return_value=_access_token()):
        result = await list_categories()

    assert isinstance(result, list)
    calls = mock_api_state["api_calls"]
    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["path"] == "/categories"


@pytest.mark.asyncio
async def test_create_category_post(mcp_stack, mock_api_state) -> None:
    from app.tools.categories import create_category

    mock_api_state["api_calls"].clear()
    with patch("app.tools.categories.get_access_token", return_value=_access_token()):
        result = await create_category(name="Work")

    assert result["name"] == "Work"
    calls = mock_api_state["api_calls"]
    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert calls[0]["path"] == "/categories"
    assert calls[0]["json"] == {"name": "Work"}


@pytest.mark.asyncio
async def test_six_tools_registered(mcp_stack) -> None:
    _, mcp, _ = mcp_stack
    tools = await mcp.list_tools()
    names = sorted(t.name for t in tools)
    expected = sorted(
        [
            "create_item",
            "confirm_item",
            "update_item",
            "move_item",
            "list_categories",
            "create_category",
        ]
    )
    assert names == expected
