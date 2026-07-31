from __future__ import annotations

import httpx
from fastmcp.exceptions import ToolError

from app.config import Settings

API_VERSION_ACCEPT = "application/vnd.puzzlessbox.v1+json"


def make_client(
    settings: Settings,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=settings.MCP_API_BASE_URL,
        timeout=httpx.Timeout(15.0),
        transport=transport,
        headers={
            "Accept": API_VERSION_ACCEPT,
            "X-Service-Bearer": settings.SERVICE_BEARER_TOKEN,
        },
    )


async def resolve_owner(client: httpx.AsyncClient, bearer_hash: str) -> str | None:
    response = await client.post("/internal/mcp-auth", json={"bearer_hash": bearer_hash})
    if response.status_code != 200:
        return None
    data = response.json()
    owner_id = data.get("owner_id")
    return str(owner_id) if owner_id else None


def _to_tool_error(resp: httpx.Response) -> ToolError:
    try:
        err = resp.json().get("error", {})
    except Exception:
        err = {}
    code = err.get("code", "API_ERROR")
    message = err.get("message", "Request failed")
    return ToolError(f"{code}: {message}")


async def call_api(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    owner_id: str,
    *,
    json: dict | None = None,
    idempotency_key: str | None = None,
) -> dict:
    headers = {"X-Owner-Id": owner_id}
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    response: httpx.Response | None = None
    for attempt in range(2):
        response = await client.request(method, path, json=json, headers=headers)
        if response.status_code in (502, 503) and attempt == 0:
            continue
        break

    assert response is not None
    if response.status_code >= 400:
        raise _to_tool_error(response)
    return response.json()
