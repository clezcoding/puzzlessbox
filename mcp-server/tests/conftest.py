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
TEST_ITEM_ID = "22222222-2222-4222-8222-222222222222"
TEST_TARGET_CATEGORY_ID = "44444444-4444-4444-8444-444444444444"


@pytest.fixture
def mock_api_state() -> dict[str, Any]:
    return {
        "drafts_calls": [],
        "api_calls": [],
        "auth_reject": False,
        "retry_paths": {},
    }


def _record_call(state: dict[str, Any], request: httpx.Request) -> None:
    entry = {
        "method": request.method,
        "path": request.url.path,
        "headers": dict(request.headers),
        "json": json.loads(request.content) if request.content else None,
    }
    state["api_calls"].append(entry)
    if request.url.path == "/drafts" and request.method == "POST":
        state["drafts_calls"].append(
            {"headers": dict(request.headers), "json": entry["json"]}
        )


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

        if request.url.path == "/health" and request.method == "GET":
            return httpx.Response(200, json={"status": "ok"})

        retry_key = f"{request.method}:{request.url.path}"
        retry_seq = mock_api_state.get("retry_paths", {}).get(retry_key)
        if retry_seq:
            attempt = len(
                [c for c in mock_api_state["api_calls"] if c["method"] == request.method and c["path"] == request.url.path]
            )
            status = retry_seq[min(attempt, len(retry_seq) - 1)]
            _record_call(mock_api_state, request)
            if status >= 400:
                return httpx.Response(
                    status,
                    json={"error": {"code": "API_ERROR", "message": f"status {status}"}},
                )
            return httpx.Response(status, json={"id": TEST_ITEM_ID, "status": "confirmed"})

        _record_call(mock_api_state, request)

        if request.url.path == "/drafts" and request.method == "POST":
            return httpx.Response(201, json={"id": str(uuid.uuid4()), "status": "draft"})

        if request.url.path.startswith("/drafts/") and request.method == "PATCH":
            return httpx.Response(200, json={"id": TEST_ITEM_ID, "status": "draft"})

        if request.url.path.endswith("/confirm") and request.method == "POST":
            return httpx.Response(200, json={"id": TEST_ITEM_ID, "status": "confirmed"})

        if request.url.path.endswith("/discard") and request.method == "POST":
            return httpx.Response(
                200,
                json={"id": TEST_ITEM_ID, "type": "note", "status": "discarded"},
            )

        if request.url.path.startswith("/drafts/") and request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "id": TEST_ITEM_ID,
                    "type": "note",
                    "status": "draft",
                    "title": "Draft",
                    "category_id": TEST_CATEGORY_ID,
                    "summary": "summary",
                },
            )

        if request.url.path.startswith("/items/") and request.method == "PATCH":
            return httpx.Response(200, json={"id": TEST_ITEM_ID, "category_id": TEST_TARGET_CATEGORY_ID})

        if request.url.path == "/categories" and request.method == "GET":
            return httpx.Response(200, json=[{"id": TEST_CATEGORY_ID, "name": "Default"}])

        if request.url.path == "/categories" and request.method == "POST":
            body = json.loads(request.content) if request.content else {}
            return httpx.Response(201, json={"id": str(uuid.uuid4()), "name": body.get("name", "")})

        return httpx.Response(404)

    return httpx.MockTransport(handler)


@pytest.fixture
def build_test_stack(mock_api_transport: httpx.MockTransport) -> Callable[..., tuple[Any, Any, httpx.AsyncClient]]:
    from app.factory import build_mcp_stack

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
