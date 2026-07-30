from __future__ import annotations

import uuid

from sqlmodel import SQLModel

from app.models.base import CoreItemMixin
from app.models.enums import ItemType


class Note(CoreItemMixin, table=True):
    __tablename__ = "notes"

    title: str
    summary: str = ""


class DraftCreate(SQLModel):
    """Capture draft payload validation (CAP-01, D-02, D-30)."""

    title: str
    type: ItemType
    category_id: uuid.UUID
    summary: str = ""


class DraftUpdate(SQLModel):
    """PATCH /drafts/{id} partial update (D-06)."""

    title: str | None = None
    summary: str | None = None
    category_id: uuid.UUID | None = None
