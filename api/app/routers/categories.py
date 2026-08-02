"""Category board endpoints (MCP-01, D-11, BOARD-02)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from pydantic import StringConstraints
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Session, SQLModel

from app.auth.jwt import get_db_for_owner
from app.core.database import current_owner_id
from app.models import Category

router = APIRouter(tags=["categories"])

HEX_COLOR_PATTERN = r"^#[0-9a-fA-F]{6}$"
MAX_REORDER_ITEMS = 100
HexColor = Annotated[str, StringConstraints(pattern=HEX_COLOR_PATTERN)]


class CategoryCreate(SQLModel):
    name: str = Field(min_length=1, max_length=40)
    color: HexColor | None = None
    sort_order: int = Field(default=0)


class CategoryUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=40)
    color: HexColor | None = None
    sort_order: int | None = None


class ReorderEntry(SQLModel):
    id: uuid.UUID
    sort_order: int


class CategoryReorderPayload(SQLModel):
    items: list[ReorderEntry] = Field(max_length=MAX_REORDER_ITEMS)


def _active_category_count(db: Session, owner_id: str) -> int:
    return db.execute(
        text(
            """
            SELECT count(*) FROM categories
            WHERE deleted_at IS NULL
              AND (owner_id = CAST(:owner_id AS uuid) OR owner_id IS NULL)
            """
        ),
        {"owner_id": owner_id},
    ).scalar_one()


def _inbox_category_id(db: Session) -> str:
    inbox_id = db.execute(
        text(
            """
            SELECT id FROM categories
            WHERE owner_id IS NULL AND name = 'Inbox' AND deleted_at IS NULL
            LIMIT 1
            """
        )
    ).scalar_one_or_none()
    if inbox_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Inbox category missing."},
        )
    return str(inbox_id)


@router.get("/categories")
def list_categories(db: Session = Depends(get_db_for_owner)) -> list[Category]:
    owner_id = current_owner_id.get()
    rows = db.execute(
        text(
            """
            SELECT id, owner_id, name, color, sort_order, deleted_at, created_at
            FROM categories
            WHERE (owner_id = CAST(:owner_id AS uuid) OR owner_id IS NULL)
              AND deleted_at IS NULL
            ORDER BY sort_order ASC, name ASC
            """
        ),
        {"owner_id": owner_id},
    ).mappings()
    return [Category.model_validate(dict(row)) for row in rows]


@router.post("/categories", status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, str]:
    owner_id = current_owner_id.get()
    try:
        new_id = db.execute(
            text(
                """
                INSERT INTO categories (id, owner_id, name, color, sort_order, created_at)
                VALUES (
                    gen_random_uuid(),
                    CAST(:owner_id AS uuid),
                    :name,
                    :color,
                    :sort_order,
                    timezone('Europe/Berlin', now())
                )
                RETURNING id
                """
            ),
            {
                "owner_id": owner_id,
                "name": payload.name,
                "color": payload.color,
                "sort_order": payload.sort_order,
            },
        ).scalar_one()
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "CONFLICT", "message": "Category name already exists."},
        ) from exc
    return {"id": str(new_id), "name": payload.name}


@router.patch("/categories/{category_id}")
def update_category(
    category_id: str,
    payload: CategoryUpdate,
    db: Session = Depends(get_db_for_owner),
) -> Category:
    owner_id = current_owner_id.get()
    if (
        payload.name is None
        and payload.color is None
        and payload.sort_order is None
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "VALIDATION_ERROR", "message": "No fields to update."},
        )

    row = db.execute(
        text(
            """
            UPDATE categories
            SET
                name = COALESCE(:name, name),
                color = COALESCE(:color, color),
                sort_order = COALESCE(:sort_order, sort_order)
            WHERE id = CAST(:category_id AS uuid)
              AND owner_id = CAST(:owner_id AS uuid)
              AND deleted_at IS NULL
            RETURNING id, owner_id, name, color, sort_order, deleted_at, created_at
            """
        ),
        {
            "category_id": category_id,
            "owner_id": owner_id,
            "name": payload.name,
            "color": payload.color,
            "sort_order": payload.sort_order,
        },
    ).mappings().first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Category not found."},
        )
    db.commit()
    return Category.model_validate(dict(row))


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    db: Session = Depends(get_db_for_owner),
) -> None:
    owner_id = current_owner_id.get()
    if _active_category_count(db, owner_id) <= 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "CONFLICT",
                "message": "Letzte Kategorie kann nicht gelöscht werden.",
            },
        )

    inbox_id = _inbox_category_id(db)
    exists = db.execute(
        text(
            """
            SELECT id FROM categories
            WHERE id = CAST(:category_id AS uuid)
              AND owner_id = CAST(:owner_id AS uuid)
              AND deleted_at IS NULL
            """
        ),
        {"category_id": category_id, "owner_id": owner_id},
    ).scalar_one_or_none()
    if exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Category not found."},
        )

    for table in ("notes", "links", "tasks", "events"):
        db.execute(
            text(
                f"""
                UPDATE {table}
                SET category_id = CAST(:inbox_id AS uuid), updated_at = NOW()
                WHERE category_id = CAST(:category_id AS uuid)
                  AND owner_id = CAST(:owner_id AS uuid)
                """
            ),
            {
                "inbox_id": inbox_id,
                "category_id": category_id,
                "owner_id": owner_id,
            },
        )

    db.execute(
        text(
            """
            UPDATE categories
            SET deleted_at = timezone('Europe/Berlin', now())
            WHERE id = CAST(:category_id AS uuid)
              AND owner_id = CAST(:owner_id AS uuid)
              AND deleted_at IS NULL
            """
        ),
        {"category_id": category_id, "owner_id": owner_id},
    )
    db.commit()


@router.post("/categories/reorder")
def reorder_categories(
    payload: CategoryReorderPayload,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, str]:
    owner_id = current_owner_id.get()
    if not payload.items:
        return {"status": "ok"}

    for entry in payload.items:
        result = db.execute(
            text(
                """
                UPDATE categories
                SET sort_order = :sort_order
                WHERE id = CAST(:category_id AS uuid)
                  AND (
                    owner_id = CAST(:owner_id AS uuid)
                    OR owner_id IS NULL
                  )
                  AND deleted_at IS NULL
                RETURNING id
                """
            ),
            {
                "category_id": str(entry.id),
                "sort_order": entry.sort_order,
                "owner_id": owner_id,
            },
        ).scalar_one_or_none()
        if result is None:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "Category not found."},
            )
    db.commit()
    return {"status": "ok"}
