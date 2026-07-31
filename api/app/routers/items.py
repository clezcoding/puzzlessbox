"""Item board endpoints (MCP-01, D-12)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlmodel import Field, Session, SQLModel

from app.auth.jwt import get_db_for_owner
from app.core.database import current_owner_id
from app.models import ItemType
from app.services.timeout import table_for_item_type

router = APIRouter(tags=["items"])


class ItemMove(SQLModel):
    category_id: uuid.UUID = Field()


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


@router.patch("/items/{item_id}")
def move_item(
    item_id: str,
    payload: ItemMove,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, str]:
    owner_id = current_owner_id.get()
    item_type = _lookup_item_type(db, owner_id, item_id)
    table = table_for_item_type(item_type)
    result = db.execute(
        text(
            f"""
            UPDATE {table}
            SET category_id = :category_id, updated_at = NOW()
            WHERE id = :item_id AND owner_id = :owner_id
            RETURNING id
            """
        ),
        {
            "category_id": str(payload.category_id),
            "item_id": item_id,
            "owner_id": owner_id,
        },
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Item not found."},
        )
    db.commit()
    return {"id": item_id, "category_id": str(payload.category_id)}
