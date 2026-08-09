"""Google Calendar OAuth + calendar list (D-18, D-21, D-29)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.auth.jwt import get_current_owner, get_db_for_owner
from app.core.database import apply_tenant_context, get_db, set_request_owner
from app.services.calendar import calendar_service

router = APIRouter(tags=["calendar"])


@router.get("/auth/google/connect")
async def google_connect(owner_id: str = Depends(get_current_owner)) -> dict[str, str]:
    url, _state = calendar_service.authorization_url(owner_id)
    return {"authorization_url": url}


@router.get("/auth/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    owner_id, credentials = calendar_service.exchange_code(code, state)
    set_request_owner(owner_id)
    apply_tenant_context(db, owner_id)
    calendar_service.upsert_tokens(db, owner_id, credentials)
    return {"status": "connected", "owner_id": owner_id}


@router.get("/calendars")
async def list_calendars(
    db: Session = Depends(get_db_for_owner),
    owner_id: str = Depends(get_current_owner),
) -> dict[str, list[dict[str, Any]]]:
    calendars = calendar_service.list_calendars(db, owner_id)
    return {"data": calendars}


@router.post("/calendars/{calendar_id}/select")
async def select_calendar(
    calendar_id: str,
    db: Session = Depends(get_db_for_owner),
    owner_id: str = Depends(get_current_owner),
) -> dict[str, str]:
    calendar_service.select_calendar(db, owner_id, calendar_id)
    return {"selected_calendar_id": calendar_id}


@router.get("/auth/google/status")
async def google_status(
    db: Session = Depends(get_db_for_owner),
    owner_id: str = Depends(get_current_owner),
) -> dict[str, object]:
    return calendar_service.connection_status(db, owner_id)


@router.post("/auth/google/disconnect")
async def google_disconnect(
    db: Session = Depends(get_db_for_owner),
    owner_id: str = Depends(get_current_owner),
) -> dict[str, str]:
    calendar_service.disconnect(db, owner_id)
    return {"status": "disconnected"}
