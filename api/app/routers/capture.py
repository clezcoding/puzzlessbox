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

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import text
from sqlmodel import Session

from app.auth.jwt import get_db_for_owner
from app.core.database import current_owner_id
from app.models import BoardItem, DraftCreate, DraftUpdate, Event, ItemType, Link, Note, Task
from app.services.timeout import table_for_item_type, timeout_manager

router = APIRouter(tags=["capture"])


def _lookup_draft_type(db: Session, owner_id: str, draft_id: str) -> ItemType:
    row = db.execute(
        text(
            """
            SELECT type FROM board_items
            WHERE id = :draft_id AND owner_id = :owner_id
            """
        ),
        {"draft_id": draft_id, "owner_id": owner_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Draft not found."},
        )
    return ItemType(row["type"])


def _apply_draft_patch(
    db: Session,
    owner_id: str,
    draft_id: str,
    item_type: ItemType,
    payload: DraftUpdate,
) -> None:
    if payload.title is None and payload.summary is None and payload.category_id is None:
        return

    table = table_for_item_type(item_type)
    updates: list[str] = []
    params: dict[str, Any] = {"draft_id": draft_id, "owner_id": owner_id}

    if payload.title is not None:
        updates.append("title = :title")
        params["title"] = payload.title
    if payload.summary is not None:
        column = "url" if item_type == ItemType.link else "summary"
        updates.append(f"{column} = :summary")
        params["summary"] = payload.summary
    if payload.category_id is not None:
        updates.append("category_id = :category_id")
        params["category_id"] = str(payload.category_id)

    updates.append("updated_at = NOW()")
    result = db.execute(
        text(
            f"""
            UPDATE {table}
            SET {", ".join(updates)}
            WHERE id = :draft_id
              AND owner_id = :owner_id
              AND status IN ('draft', 'auto_saved')
            RETURNING id
            """
        ),
        params,
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Draft not found."},
        )


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


@router.patch("/drafts/{draft_id}")
async def patch_draft(
    draft_id: str,
    payload: DraftUpdate,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, Any]:
    owner_id = current_owner_id.get()
    if not owner_id:
        raise RuntimeError("owner_id missing after auth dependency")

    item_type = _lookup_draft_type(db, owner_id, draft_id)
    _apply_draft_patch(db, owner_id, draft_id, item_type, payload)
    db.commit()
    timeout_manager.schedule_timeout(draft_id, owner_id, item_type)
    return {"id": draft_id, "type": item_type.value}


@router.post("/drafts/{draft_id}/confirm")
async def confirm_draft(
    draft_id: str,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, Any]:
    owner_id = current_owner_id.get()
    if not owner_id:
        raise RuntimeError("owner_id missing after auth dependency")

    item_type = _lookup_draft_type(db, owner_id, draft_id)
    table = table_for_item_type(item_type)
    confirmed = db.execute(
        text(
            f"""
            UPDATE {table}
            SET status = 'confirmed', updated_at = NOW()
            WHERE id = :draft_id
              AND owner_id = :owner_id
              AND status IN ('draft', 'auto_saved')
            RETURNING id
            """
        ),
        {"draft_id": draft_id, "owner_id": owner_id},
    ).scalar_one_or_none()
    if confirmed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Draft not found."},
        )
    db.commit()
    timeout_manager.cancel_timeout(draft_id)
    return {"id": draft_id, "type": item_type.value, "status": "confirmed"}


@router.post("/drafts/{draft_id}/discard")
async def discard_draft(
    draft_id: str,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, Any]:
    owner_id = current_owner_id.get()
    if not owner_id:
        raise RuntimeError("owner_id missing after auth dependency")

    item_type = _lookup_draft_type(db, owner_id, draft_id)
    table = table_for_item_type(item_type)
    discarded = db.execute(
        text(
            f"""
            UPDATE {table}
            SET deleted_at = NOW(), updated_at = NOW(), status = 'discarded'
            WHERE id = :draft_id
              AND owner_id = :owner_id
              AND status IN ('draft', 'auto_saved')
            RETURNING id
            """
        ),
        {"draft_id": draft_id, "owner_id": owner_id},
    ).scalar_one_or_none()
    if discarded is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Draft not found."},
        )
    db.commit()
    timeout_manager.cancel_timeout(draft_id)
    return {"id": draft_id, "type": item_type.value, "status": "discarded"}


@router.get("/drafts/{draft_id}")
async def get_draft(
    draft_id: str,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, Any]:
    owner_id = current_owner_id.get()
    if not owner_id:
        raise RuntimeError("owner_id missing after auth dependency")

    row = db.execute(
        text(
            """
            SELECT id, type, status, title, category_id, summary
            FROM board_items
            WHERE id = :draft_id
              AND owner_id = :owner_id
              AND deleted_at IS NULL
            """
        ),
        {"draft_id": draft_id, "owner_id": owner_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Draft not found."},
        )
    return {
        "id": str(row["id"]),
        "type": row["type"],
        "status": row["status"],
        "title": row["title"],
        "category_id": str(row["category_id"]) if row["category_id"] is not None else None,
        "summary": row["summary"],
    }


@router.get("/board-items")
def list_board_items(db: Session = Depends(get_db_for_owner)) -> list[BoardItem]:
    owner_id = current_owner_id.get()
    rows = db.execute(
        text(
            """
            SELECT id, owner_id, category_id, status, title, summary, type,
                   sort_order, created_at, updated_at, deleted_at
            FROM board_items
            WHERE owner_id = :owner_id
              AND deleted_at IS NULL
              AND status IN ('auto_saved', 'confirmed')
            ORDER BY category_id ASC, sort_order ASC, created_at DESC
            """
        ),
        {"owner_id": owner_id},
    ).mappings()
    return [BoardItem.model_validate(dict(row)) for row in rows]
