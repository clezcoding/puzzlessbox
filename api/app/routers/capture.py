"""Draft capture endpoints (CAP-01, D-01, D-30).

Phase 1 consolidates polymorphic draft creation for note/link/task/event into POST /drafts
because all four types share identical create-time validation and draft status lifecycle.
Per-type routers (links.py, events.py, etc.) split out when read/update fields diverge (Plans 03/04).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy import text
from sqlmodel import Session

from app.auth.jwt import get_db_for_owner
from app.core.database import current_owner_id
from app.models import BoardItem, DraftCreate, Event, ItemType, Link, Note, Task
from app.services.timeout import timeout_manager

router = APIRouter(tags=["capture"])


def _insert_draft(owner_id: str, payload: DraftCreate) -> tuple[Note | Link | Task | Event, ItemType]:
    owner_uuid = uuid.UUID(owner_id)
    if payload.type == ItemType.note:
        row: Note | Link | Task | Event = Note(
            owner_id=owner_uuid,
            category_id=payload.category_id,
            title=payload.title,
            summary=payload.summary,
        )
    elif payload.type == ItemType.link:
        row = Link(
            owner_id=owner_uuid,
            category_id=payload.category_id,
            title=payload.title,
            url=payload.summary or payload.title,
        )
    elif payload.type == ItemType.task:
        row = Task(
            owner_id=owner_uuid,
            category_id=payload.category_id,
            title=payload.title,
            summary=payload.summary,
        )
    else:
        row = Event(
            owner_id=owner_uuid,
            category_id=payload.category_id,
            title=payload.title,
            summary=payload.summary,
        )
    now = datetime.now(timezone.utc)
    row.created_at = now
    row.updated_at = now
    return row, payload.type


@router.post("/drafts", status_code=status.HTTP_201_CREATED)
async def create_draft(
    payload: DraftCreate,
    db: Session = Depends(get_db_for_owner),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, Any]:
    owner_id = current_owner_id.get()
    if not owner_id:
        raise RuntimeError("owner_id missing after auth dependency")

    if idempotency_key:
        cached = db.execute(
            text(
                """
                SELECT response FROM idempotency_keys
                WHERE owner_id = :owner_id AND key = :key
                """
            ),
            {"owner_id": owner_id, "key": idempotency_key},
        ).scalar_one_or_none()
        if cached is not None:
            return cached

    row, item_type = _insert_draft(owner_id, payload)
    db.add(row)
    db.commit()
    db.refresh(row)
    response_body = {"id": str(row.id), "type": item_type.value}

    if idempotency_key:
        db.execute(
            text(
                """
                INSERT INTO idempotency_keys (owner_id, key, response)
                VALUES (:owner_id, :key, CAST(:response AS jsonb))
                ON CONFLICT (owner_id, key) DO NOTHING
                """
            ),
            {"owner_id": owner_id, "key": idempotency_key, "response": json.dumps(response_body)},
        )
        db.commit()

    timeout_manager.schedule_timeout(str(row.id), owner_id, item_type)
    return response_body


@router.get("/board-items")
def list_board_items(db: Session = Depends(get_db_for_owner)) -> list[BoardItem]:
    owner_id = current_owner_id.get()
    rows = db.execute(
        text(
            """
            SELECT id, owner_id, category_id, status, title, summary, type,
                   created_at, updated_at, deleted_at
            FROM board_items
            WHERE owner_id = :owner_id
            ORDER BY created_at DESC
            """
        ),
        {"owner_id": owner_id},
    ).mappings()
    return [BoardItem.model_validate(dict(row)) for row in rows]
