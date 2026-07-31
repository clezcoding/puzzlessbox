from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import get_settings


def _error_payload(
    code: str,
    message: str,
    details: dict | list | str | None = None,
) -> dict:
    payload: dict = {"code": code, "message": message}
    if details is not None:
        payload["details"] = details
    return {"error": payload}


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        code = exc.detail.get("code", "API_ERROR")
        message = exc.detail.get("message", "Request failed")
        details = exc.detail.get("details")
    else:
        code = "API_ERROR"
        message = str(exc.detail)
        details = None
    return JSONResponse(status_code=exc.status_code, content=_error_payload(code, message, details))


async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_error_payload(
            "VALIDATION_ERROR",
            "Request validation failed",
            exc.errors(),
        ),
    )


async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    settings = get_settings()
    details = None if settings.is_prod else {"type": type(exc).__name__, "reason": str(exc)}
    return JSONResponse(
        status_code=500,
        content=_error_payload("INTERNAL_ERROR", "An unexpected error occurred", details),
    )
