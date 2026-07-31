from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.bootstrap import ensure_mcp_client, ensure_service_principal
from app.core.config import get_settings
from app.core.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.routers import auth, calendar, capture, categories, events, health, internal, links

API_VERSION_ACCEPT = "application/vnd.puzzlessbox.v1+json"
_VERSION_SKIP_PREFIXES = ("/health", "/ready", "/docs", "/redoc", "/openapi.json")


class AcceptVersionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path
        if any(path == prefix or path.startswith(f"{prefix}/") for prefix in _VERSION_SKIP_PREFIXES):
            return await call_next(request)

        accept = request.headers.get("accept", "")
        if API_VERSION_ACCEPT not in accept:
            return Response(
                status_code=415,
                media_type="application/json",
                content=(
                    '{"error":{"code":"UNSUPPORTED_MEDIA_TYPE",'
                    f'"message":"Accept header must include {API_VERSION_ACCEPT}"}}}}'
                ),
            )
        return await call_next(request)


@asynccontextmanager
async def _lifespan(application: FastAPI):
    settings = get_settings()
    ensure_service_principal(settings)
    ensure_mcp_client(settings)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    docs_url = None if settings.is_prod else "/docs"
    redoc_url = None if settings.is_prod else "/redoc"

    application = FastAPI(
        title="Puzzlessbox API",
        lifespan=_lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
    )
    application.add_middleware(AcceptVersionMiddleware)
    application.include_router(health.router)
    application.include_router(internal.router)
    application.include_router(auth.router)
    application.include_router(capture.router)
    application.include_router(categories.router)
    application.include_router(links.router)
    application.include_router(calendar.router)
    application.include_router(events.router)

    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(Exception, unhandled_exception_handler)
    from fastapi.exceptions import RequestValidationError

    application.add_exception_handler(RequestValidationError, validation_exception_handler)

    @application.get("/__test-error__", include_in_schema=False)
    def _test_error() -> None:
        raise HTTPException(
            status_code=418,
            detail={
                "code": "TEAPOT",
                "message": "test error",
                "details": {"hint": "unified shape"},
            },
        )

    return application


app = create_app()
