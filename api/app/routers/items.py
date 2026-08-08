"""Item board endpoints (MCP-01, D-12, BOARD-03, BOARD-04)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import text
from sqlmodel import Field, Session, SQLModel

from app.auth.jwt import get_db_for_owner
from app.core.database import current_owner_id
from app.models import Event, ItemType
from app.services.calendar import calendar_service, sync_local_event_to_google
from app.services.timeout import table_for_item_type

router = APIRouter(tags=["items"])

MAX_REORDER_ITEMS = 100


class ItemMove(SQLModel):
    category_id: uuid.UUID = Field()


class ItemUpdate(SQLModel):
    title: str | None = None
    body: str | None = None
    url: str | None = None
    due: datetime | None = None
    event_start: datetime | None = None
    event_end: datetime | None = None
    category_id: uuid.UUID | None = None
    sort_order: int | None = None
    type: ItemType | None = None


class ItemReorderEntry(SQLModel):
    id: uuid.UUID
    sort_order: int


class ItemReorderPayload(SQLModel):
    items: list[ItemReorderEntry] = Field(max_length=MAX_REORDER_ITEMS)


def _lookup_item_type(db: Session, owner_id: str, item_id: str) -> ItemType:
    row = db.execute(
        text(
            """
            SELECT type FROM board_items
            WHERE id = :item_id AND owner_id = :owner_id
            """
        ),
        {"item_id": item_id, "owner_id": owner_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Item not found."},
        )
    return ItemType(row["type"])


def _fetch_item_row(db: Session, table: str, item_id: str, owner_id: str) -> dict[str, Any]:
    row = db.execute(
        text(f"SELECT * FROM {table} WHERE id = CAST(:item_id AS uuid) AND owner_id = CAST(:owner_id AS uuid)"),
        {"item_id": item_id, "owner_id": owner_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Item not found."},
        )
    return dict(row)


def _apply_type_change(
    db: Session,
    item_id: str,
    owner_id: str,
    current_type: ItemType,
    new_type: ItemType,
    payload: ItemUpdate,
    current: dict[str, Any],
) -> None:
    title = payload.title if payload.title is not None else current["title"]
    body = payload.body if payload.body is not None else current.get("summary", "")
    sort_order = payload.sort_order if payload.sort_order is not None else current.get("sort_order", 0)
    category_id = (
        str(payload.category_id)
        if payload.category_id is not None
        else str(current["category_id"])
    )
    item_status = current["status"]
    deleted_at = current.get("deleted_at")
    old_table = table_for_item_type(current_type)
    new_table = table_for_item_type(new_type)

    db.execute(
        text(f"DELETE FROM {old_table} WHERE id = CAST(:item_id AS uuid) AND owner_id = CAST(:owner_id AS uuid)"),
        {"item_id": item_id, "owner_id": owner_id},
    )

    base_params: dict[str, Any] = {
        "item_id": item_id,
        "owner_id": owner_id,
        "category_id": category_id,
        "status": item_status,
        "title": title,
        "sort_order": sort_order,
        "deleted_at": deleted_at,
    }

    if new_type == ItemType.note:
        db.execute(
            text(
                """
                INSERT INTO notes (
                    id, owner_id, category_id, status, title, summary, sort_order,
                    deleted_at, created_at, updated_at
                )
                VALUES (
                    CAST(:item_id AS uuid), CAST(:owner_id AS uuid), CAST(:category_id AS uuid),
                    :status, :title, :summary, :sort_order, :deleted_at,
                    timezone('Europe/Berlin', now()), timezone('Europe/Berlin', now())
                )
                """
            ),
            {**base_params, "summary": body or ""},
        )
    elif new_type == ItemType.link:
        url = payload.url if payload.url is not None else current.get("url") or ""
        db.execute(
            text(
                """
                INSERT INTO links (
                    id, owner_id, category_id, status, title, url, metadata, sort_order,
                    deleted_at, created_at, updated_at
                )
                VALUES (
                    CAST(:item_id AS uuid), CAST(:owner_id AS uuid), CAST(:category_id AS uuid),
                    :status, :title, :url, '{}'::jsonb, :sort_order, :deleted_at,
                    timezone('Europe/Berlin', now()), timezone('Europe/Berlin', now())
                )
                """
            ),
            {**base_params, "url": url},
        )
    elif new_type == ItemType.task:
        due = payload.due if payload.due is not None else current.get("due_at")
        db.execute(
            text(
                """
                INSERT INTO tasks (
                    id, owner_id, category_id, status, title, summary, due_at, sort_order,
                    deleted_at, created_at, updated_at
                )
                VALUES (
                    CAST(:item_id AS uuid), CAST(:owner_id AS uuid), CAST(:category_id AS uuid),
                    :status, :title, :summary, :due_at, :sort_order, :deleted_at,
                    timezone('Europe/Berlin', now()), timezone('Europe/Berlin', now())
                )
                """
            ),
            {**base_params, "summary": body or "", "due_at": due},
        )
    else:
        event_start = (
            payload.event_start
            if payload.event_start is not None
            else current.get("starts_at")
        )
        event_end = (
            payload.event_end if payload.event_end is not None else current.get("ends_at")
        )
        db.execute(
            text(
                """
                INSERT INTO events (
                    id, owner_id, category_id, status, title, summary, starts_at, ends_at,
                    sort_order, deleted_at, created_at, updated_at
                )
                VALUES (
                    CAST(:item_id AS uuid), CAST(:owner_id AS uuid), CAST(:category_id AS uuid),
                    :status, :title, :summary, :starts_at, :ends_at, :sort_order, :deleted_at,
                    timezone('Europe/Berlin', now()), timezone('Europe/Berlin', now())
                )
                """
            ),
            {
                **base_params,
                "summary": body or "",
                "starts_at": event_start,
                "ends_at": event_end,
            },
        )


def _update_item_fields(
    db: Session,
    item_type: ItemType,
    item_id: str,
    owner_id: str,
    payload: ItemUpdate,
) -> None:
    table = table_for_item_type(item_type)
    updates: list[str] = []
    params: dict[str, Any] = {"item_id": item_id, "owner_id": owner_id}

    if payload.title is not None:
        updates.append("title = :title")
        params["title"] = payload.title
    if payload.body is not None and item_type in (ItemType.note, ItemType.task, ItemType.event):
        updates.append("summary = :summary")
        params["summary"] = payload.body
    if payload.url is not None and item_type == ItemType.link:
        updates.append("url = :url")
        params["url"] = payload.url
    if payload.due is not None and item_type == ItemType.task:
        updates.append("due_at = :due_at")
        params["due_at"] = payload.due
    if payload.event_start is not None and item_type == ItemType.event:
        updates.append("starts_at = :starts_at")
        params["starts_at"] = payload.event_start
    if payload.event_end is not None and item_type == ItemType.event:
        updates.append("ends_at = :ends_at")
        params["ends_at"] = payload.event_end
    if payload.category_id is not None:
        updates.append("category_id = CAST(:category_id AS uuid)")
        params["category_id"] = str(payload.category_id)
    if payload.sort_order is not None:
        updates.append("sort_order = :sort_order")
        params["sort_order"] = payload.sort_order

    if not updates:
        return

    updates.append("updated_at = timezone('Europe/Berlin', now())")
    result = db.execute(
        text(
            f"""
            UPDATE {table}
            SET {", ".join(updates)}
            WHERE id = CAST(:item_id AS uuid) AND owner_id = CAST(:owner_id AS uuid)
            RETURNING id
            """
        ),
        params,
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Item not found."},
        )


def _event_calendar_fields_changed(payload: ItemUpdate) -> bool:
    return any(
        value is not None
        for value in (payload.title, payload.body, payload.event_start, payload.event_end)
    )


def _sync_event_after_local_update(
    db: Session,
    owner_id: str,
    item_id: str,
    payload: ItemUpdate,
    *,
    force: bool,
) -> None:
    event_row = db.get(Event, uuid.UUID(item_id))
    if event_row is None:
        return

    calendar_changed = _event_calendar_fields_changed(payload)
    status_info = calendar_service.connection_status(db, owner_id)
    connected = bool(status_info.get("connected") and status_info.get("selected_calendar_id"))

    if not event_row.google_event_id:
        if connected and calendar_changed:
            sync_local_event_to_google(db, owner_id, event_row)
        return

    if not calendar_changed:
        return

    calendar_id = status_info["selected_calendar_id"]
    body: dict[str, Any] = {}
    if payload.title is not None:
        body["summary"] = payload.title
    if payload.body is not None:
        body["description"] = payload.body
    if payload.event_start is not None and payload.event_end is not None:
        body["start"] = {"dateTime": payload.event_start.isoformat()}
        body["end"] = {"dateTime": payload.event_end.isoformat()}
    elif payload.event_start is not None:
        body["start"] = {"dateTime": payload.event_start.isoformat()}
    elif payload.event_end is not None:
        body["end"] = {"dateTime": payload.event_end.isoformat()}

    client_etag = "*" if force else (event_row.etag or "")
    remote = calendar_service.update_event_with_etag(
        db,
        owner_id,
        calendar_id=calendar_id,
        google_event_id=event_row.google_event_id,
        client_etag=client_etag,
        event_body=body,
        force=force,
    )
    event_row.etag = remote.get("etag")
    event_row.updated_at = datetime.now(timezone.utc)
    db.add(event_row)
    db.commit()


@router.patch("/items/{item_id}")
def update_item(
    item_id: str,
    payload: ItemUpdate,
    db: Session = Depends(get_db_for_owner),
    if_none_match: str | None = Header(default=None, alias="If-None-Match"),
) -> dict[str, str]:
    owner_id = current_owner_id.get()
    current_type = _lookup_item_type(db, owner_id, item_id)
    force = if_none_match == "*"

    if payload.type is not None and payload.type != current_type:
        current = _fetch_item_row(db, table_for_item_type(current_type), item_id, owner_id)
        _apply_type_change(db, item_id, owner_id, current_type, payload.type, payload, current)
    else:
        _update_item_fields(db, current_type, item_id, owner_id, payload)

    db.commit()

    if current_type == ItemType.event:
        _sync_event_after_local_update(db, owner_id, item_id, payload, force=force)

    return {"id": item_id}


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: str,
    db: Session = Depends(get_db_for_owner),
) -> None:
    owner_id = current_owner_id.get()
    item_type = _lookup_item_type(db, owner_id, item_id)
    table = table_for_item_type(item_type)

    if item_type == ItemType.event:
        event_row = db.get(Event, uuid.UUID(item_id))
        if event_row is not None and event_row.google_event_id:
            calendar_service.delete_remote_event(
                db,
                owner_id,
                google_event_id=event_row.google_event_id,
            )

    result = db.execute(
        text(
            f"""
            UPDATE {table}
            SET deleted_at = timezone('Europe/Berlin', now()),
                updated_at = timezone('Europe/Berlin', now())
            WHERE id = CAST(:item_id AS uuid) AND owner_id = CAST(:owner_id AS uuid)
            RETURNING id
            """
        ),
        {"item_id": item_id, "owner_id": owner_id},
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Item not found."},
        )
    db.commit()


@router.post("/items/{item_id}/restore")
def restore_item(
    item_id: str,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, str]:
    owner_id = current_owner_id.get()
    item_type = _lookup_item_type(db, owner_id, item_id)
    table = table_for_item_type(item_type)
    result = db.execute(
        text(
            f"""
            UPDATE {table}
            SET deleted_at = NULL,
                updated_at = timezone('Europe/Berlin', now())
            WHERE id = CAST(:item_id AS uuid) AND owner_id = CAST(:owner_id AS uuid)
            RETURNING id
            """
        ),
        {"item_id": item_id, "owner_id": owner_id},
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Item not found."},
        )
    db.commit()
    return {"id": item_id, "status": "restored"}


@router.post("/items/reorder")
def reorder_items(
    payload: ItemReorderPayload,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, str]:
    owner_id = current_owner_id.get()
    if not payload.items:
        return {"status": "ok"}

    for entry in payload.items:
        item_id = str(entry.id)
        item_type = _lookup_item_type(db, owner_id, item_id)
        table = table_for_item_type(item_type)
        result = db.execute(
            text(
                f"""
                UPDATE {table}
                SET sort_order = :sort_order,
                    updated_at = timezone('Europe/Berlin', now())
                WHERE id = CAST(:item_id AS uuid) AND owner_id = CAST(:owner_id AS uuid)
                RETURNING id
                """
            ),
            {
                "item_id": item_id,
                "sort_order": entry.sort_order,
                "owner_id": owner_id,
            },
        ).scalar_one_or_none()
        if result is None:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "Item not found."},
            )
    db.commit()
    return {"status": "ok"}
