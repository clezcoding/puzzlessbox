from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.database import check_db_connection

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> JSONResponse:
    if not check_db_connection():
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "Database is not ready",
                }
            },
        )
    return JSONResponse(status_code=200, content={"status": "ready"})
