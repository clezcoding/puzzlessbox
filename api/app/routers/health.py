from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import check_db_connection
from app.services.scraper import ping_scraper_health

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> JSONResponse:
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

    settings = get_settings()
    if settings.SCRAPER_ENABLED:
        unhealthy = await ping_scraper_health(settings)
        if unhealthy:
            return JSONResponse(
                status_code=503,
                content={
                    "error": {
                        "code": "SCRAPER_UNHEALTHY",
                        "message": "Scraper service is not ready",
                        "details": {"service": unhealthy},
                    }
                },
            )

    return JSONResponse(status_code=200, content={"status": "ready"})
