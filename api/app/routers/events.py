"""Event CRUD with Google Calendar sync (CAL-02, CAL-03, D-19, D-20)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.auth.jwt import get_current_owner, get_db_for_owner
from app.models import CalendarToken, Event
from app.services.calendar import calendar_service, events_category_id

router = APIRouter(tags=["events"])


class EventCreate(BaseModel):
    title: str
    summary: str = ""
    starts_at: datetime | None = None
    ends_at: datetime | None = None


class EventUpdate(BaseModel):
    etag: str
    title: str | None = None
    summary: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None


def _serialize_event(row: Event) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "title": row.title,
        "summary": row.summary,
        "starts_at": row.starts_at.isoformat() if row.starts_at else None,
        "ends_at": row.ends_at.isoformat() if row.ends_at else None,
        "google_event_id": row.google_event_id,
        "etag": row.etag,
        "category_id": str(row.category_id),
        "status": row.status.value if hasattr(row.status, "value") else row.status,
    }


@router.post("/events", status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db_for_owner),
    owner_id: str = Depends(get_current_owner),
) -> dict[str, Any]:
    event, _remote = calendar_service.create_event(
        db,
        owner_id,
        title=payload.title,
        summary=payload.summary,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        category_id=events_category_id(db),
    )
    return _serialize_event(event)


@router.get("/events")
async def list_events(
    db: Session = Depends(get_db_for_owner),
    owner_id: str = Depends(get_current_owner),
) -> dict[str, list[dict[str, Any]]]:
    rows = db.exec(
        select(Event).where(Event.owner_id == uuid.UUID(owner_id), Event.deleted_at.is_(None))
    ).all()
    return {"data": [_serialize_event(row) for row in rows]}


@router.patch("/events/{event_id}")
async def update_event(
    event_id: uuid.UUID,
    payload: EventUpdate,
    db: Session = Depends(get_db_for_owner),
    owner_id: str = Depends(get_current_owner),
) -> dict[str, Any]:
    row = db.get(Event, event_id)
    if row is None or str(row.owner_id) != owner_id or row.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Event not found."},
        )
    if not row.google_event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "NOT_SYNCED",
                "message": "Event is not linked to Google Calendar.",
            },
        )

    token_row = db.get(CalendarToken, uuid.UUID(owner_id))
    if token_row is None or not token_row.selected_calendar_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CALENDAR_NOT_SELECTED",
                "message": "Select a Google calendar before updating events.",
            },
        )

    body: dict[str, Any] = {}
    if payload.title is not None:
        body["summary"] = payload.title
    if payload.summary is not None:
        body["description"] = payload.summary
    if payload.starts_at is not None and payload.ends_at is not None:
        body["start"] = {"dateTime": payload.starts_at.isoformat()}
        body["end"] = {"dateTime": payload.ends_at.isoformat()}

    remote = calendar_service.update_event_with_etag(
        db,
        owner_id,
        calendar_id=token_row.selected_calendar_id,
        google_event_id=row.google_event_id,
        client_etag=payload.etag,
        event_body=body,
    )

    if payload.title is not None:
        row.title = payload.title
    if payload.summary is not None:
        row.summary = payload.summary
    if payload.starts_at is not None:
        row.starts_at = payload.starts_at
    if payload.ends_at is not None:
        row.ends_at = payload.ends_at
    row.etag = remote.get("etag")
    row.updated_at = datetime.now(timezone.utc)
    db.add(row)
    db.commit()
    db.refresh(row)
    return _serialize_event(row)
