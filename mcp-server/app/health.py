from __future__ import annotations

from collections.abc import Callable

import httpx
from starlette.responses import JSONResponse

from app.api_client import make_client
from app.config import Settings, get_settings

# ponytail: well-known fallback base_url matches auth.py OwnerResolvingVerifier default;
# dev-only ceiling — prod must set MCP_PUBLIC_BASE_URL.
# static shared bearer remains project auth model; this stub is NOT full MCP Authorization Spec OAuth discovery (D-12).


def register_health(
    mcp,
    api_client_factory: Callable[[], httpx.AsyncClient],
    settings: Settings | None = None,
) -> None:
    resolved_settings = settings or get_settings()

    @mcp.custom_route("/health", methods=["GET"])
    async def health(_request) -> JSONResponse:
        return JSONResponse({"status": "ok", "service": "mcp-server"})

    @mcp.custom_route("/.well-known/oauth-protected-resource/mcp", methods=["GET"])
    async def oauth_protected_resource(_request) -> JSONResponse:
        base_url = resolved_settings.mcp_public_base_url or "http://localhost:8000"
        return JSONResponse(
            {
                "resource": f"{base_url.rstrip('/')}/mcp",
                "bearer_methods_supported": ["header"],
                "resource_name": "Puzzlessbox MCP",
            }
        )

    @mcp.custom_route("/ready", methods=["GET"])
    async def ready(_request) -> JSONResponse:
        client = api_client_factory()
        try:
            response = await client.get("/health")
            if response.status_code >= 400:
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": {
                            "code": "SERVICE_UNAVAILABLE",
                            "message": "upstream API not ready",
                        }
                    },
                )
        except httpx.HTTPError:
            return JSONResponse(
                status_code=503,
                content={
                    "error": {
                        "code": "SERVICE_UNAVAILABLE",
                        "message": "upstream API not ready",
                    }
                },
            )
        finally:
            await client.aclose()
        return JSONResponse({"status": "ready"})
