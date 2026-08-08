from __future__ import annotations

import httpx
from fastmcp import FastMCP

from app.api_client import make_client
from app.auth import OwnerResolvingVerifier
from app.config import Settings, get_settings
from app.health import register_health
from app.tools import register_tools


def build_mcp_stack(
    settings: Settings | None = None,
    *,
    api_transport: httpx.AsyncBaseTransport | None = None,
) -> tuple[object, FastMCP, httpx.AsyncClient]:
    settings = settings or get_settings()
    client = make_client(settings, transport=api_transport)
    verifier = OwnerResolvingVerifier(
        settings,
        client=client,
        base_url=settings.mcp_public_base_url,
    )
    mcp = FastMCP(name="Puzzlessbox MCP", auth=verifier)
    register_health(mcp, lambda: make_client(settings, transport=api_transport), settings)
    register_tools(mcp, client)

    allowed_hosts = ["mcp.puzzlesstool.online"]
    if not settings.is_prod:
        allowed_hosts.extend(["localhost", "127.0.0.1", "test"])

    http_app = mcp.http_app(
        path="/mcp",
        stateless_http=True,
        allowed_hosts=allowed_hosts,
    )
    return http_app, mcp, client
