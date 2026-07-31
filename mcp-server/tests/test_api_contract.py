"""create_item API contract tests (MCP-01)."""

from __future__ import annotations

import inspect

import pytest
from fastmcp import Client

from tests.conftest import TEST_BEARER, TEST_CATEGORY_ID, TEST_OWNER_ID


@pytest.mark.asyncio
async def test_create_item_headers(mcp_stack, mock_api_state) -> None:
    _http_app, mcp, _client = mcp_stack
    async with Client(mcp, auth=TEST_BEARER) as client:
        await client.call_tool(
            "create_item",
            {
                "title": "Test note",
                "type": "note",
                "category_id": TEST_CATEGORY_ID,
                "summary": "hello",
            },
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
    _http_app, mcp, _client = mcp_stack
    provided_key = "client-key-123"

    async with Client(mcp, auth=TEST_BEARER) as client:
        await client.call_tool(
            "create_item",
            {
                "title": "With key",
                "type": "task",
                "category_id": TEST_CATEGORY_ID,
                "idempotency_key": provided_key,
            },
        )

    assert mock_api_state["drafts_calls"][0]["headers"].get("idempotency-key") == provided_key

    mock_api_state["drafts_calls"].clear()
    async with Client(mcp, auth=TEST_BEARER) as client:
        await client.call_tool(
            "create_item",
            {
                "title": "Generated key",
                "type": "note",
                "category_id": TEST_CATEGORY_ID,
            },
        )

    generated = mock_api_state["drafts_calls"][0]["headers"].get("idempotency-key")
    assert generated
    assert generated != provided_key


def test_create_item_owner_from_claim() -> None:
    from app.tools import items

    sig = inspect.signature(items.create_item)
    assert "owner_id" not in sig.parameters
