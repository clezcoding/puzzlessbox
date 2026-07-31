"""Category board endpoints (MCP-01, D-11)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Session, SQLModel

from app.auth.jwt import get_db_for_owner
from app.core.database import current_owner_id
from app.models import Category

router = APIRouter(tags=["categories"])


class CategoryCreate(SQLModel):
    name: str = Field(min_length=1)


@router.get("/categories")
def list_categories(db: Session = Depends(get_db_for_owner)) -> list[Category]:
    owner_id = current_owner_id.get()
    rows = db.execute(
        text(
            """
            SELECT id, owner_id, name, created_at
            FROM categories
            WHERE owner_id = :owner_id OR owner_id IS NULL
            ORDER BY name
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
                INSERT INTO categories (id, owner_id, name, created_at)
                VALUES (
                    gen_random_uuid(),
                    CAST(:owner_id AS uuid),
                    :name,
                    timezone('Europe/Berlin', now())
                )
                RETURNING id
                """
            ),
            {"owner_id": owner_id, "name": payload.name},
        ).scalar_one()
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "CONFLICT", "message": "Category name already exists."},
        ) from exc
    return {"id": str(new_id), "name": payload.name}
