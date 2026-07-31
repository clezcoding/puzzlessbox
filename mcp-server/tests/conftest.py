from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import AsyncGenerator, Callable
from typing import Any

import httpx
import pytest
from httpx import ASGITransport

TEST_OWNER_ID = "11111111-1111-4111-8111-111111111111"
TEST_BEARER = "hermes-test-token"
TEST_BEARER_HASH = hashlib.sha256(TEST_BEARER.encode()).hexdigest()
TEST_CATEGORY_ID = "33333333-3333-4333-8333-333333333333"


@pytest.fixture
def mock_api_state() -> dict[str, Any]:
    return {"drafts_calls": [], "auth_reject": False}


@pytest.fixture
def mock_api_transport(mock_api_state: dict[str, Any]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/internal/mcp-auth":
            if mock_api_state.get("auth_reject"):
                return httpx.Response(
                    401,
                    json={"error": {"code": "UNAUTHORIZED", "message": "Unknown or expired MCP client."}},
                )
            body = json.loads(request.content) if request.content else {}
            if body.get("bearer_hash") == TEST_BEARER_HASH:
                return httpx.Response(200, json={"owner_id": TEST_OWNER_ID})
            return httpx.Response(
                401,
                json={"error": {"code": "UNAUTHORIZED", "message": "Unknown or expired MCP client."}},
            )

        if request.url.path == "/drafts" and request.method == "POST":
            mock_api_state["drafts_calls"].append(
                {
                    "headers": dict(request.headers),
                    "json": json.loads(request.content) if request.content else None,
                }
            )
            return httpx.Response(201, json={"id": str(uuid.uuid4()), "status": "draft"})

        if request.url.path == "/health" and request.method == "GET":
            return httpx.Response(200, json={"status": "ok"})

        return httpx.Response(404)

    return httpx.MockTransport(handler)


@pytest.fixture
def build_test_stack(mock_api_transport: httpx.MockTransport) -> Callable[..., tuple[Any, Any, httpx.AsyncClient]]:
    from app.server import build_mcp_stack

    def _build(**kwargs: Any) -> tuple[Any, Any, httpx.AsyncClient]:
        return build_mcp_stack(api_transport=mock_api_transport, **kwargs)

    return _build


@pytest.fixture
async def mcp_stack(
    build_test_stack: Callable[..., tuple[Any, Any, httpx.AsyncClient]],
) -> AsyncGenerator[tuple[Any, Any, httpx.AsyncClient], None]:
    http_app, mcp, client = build_test_stack()
    yield http_app, mcp, client
    await client.aclose()
