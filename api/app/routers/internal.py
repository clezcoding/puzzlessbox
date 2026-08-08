"""Internal service-to-service endpoints (D-06)."""

from __future__ import annotations

import hmac

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlmodel import Session

from app.core.bootstrap import check_and_bootstrap_first_user
from app.core.config import get_settings
from app.core.database import get_engine

router = APIRouter(tags=["internal"])


class MCPAuthRequest(BaseModel):
    bearer_hash: str


@router.post("/internal/mcp-auth")
async def resolve_mcp_auth(payload: MCPAuthRequest, request: Request) -> dict[str, str]:
    settings = get_settings()
    service_bearer = request.headers.get("X-Service-Bearer")
    expected = settings.SERVICE_BEARER_TOKEN
    if (
        not service_bearer
        or len(service_bearer) != len(expected)
        or not hmac.compare_digest(service_bearer, expected)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid service bearer token."},
        )

    with Session(get_engine()) as session:
        check_and_bootstrap_first_user(session, settings)
        session.commit()

    with Session(get_engine()) as session:
        owner_id = session.execute(
            text(
                """
                SELECT owner_id FROM mcp_clients
                WHERE bearer_hash = :hash
                  AND status IN ('active', 'grace')
                  AND (expires_at IS NULL OR expires_at > timezone('Europe/Berlin', now()))
                LIMIT 1
                """
            ),
            {"hash": payload.bearer_hash},
        ).scalar_one_or_none()

    if owner_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Unknown or expired MCP client."},
        )

    return {"owner_id": str(owner_id)}
