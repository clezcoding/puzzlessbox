from __future__ import annotations

from collections.abc import Callable

import httpx
from starlette.responses import JSONResponse

from app.api_client import make_client
from app.config import Settings


def register_health(
    mcp,
    api_client_factory: Callable[[], httpx.AsyncClient],
) -> None:
    @mcp.custom_route("/health", methods=["GET"])
    async def health(_request) -> JSONResponse:
        return JSONResponse({"status": "ok", "service": "mcp-server"})

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
