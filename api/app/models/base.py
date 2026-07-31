from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.enums import ItemStatus


class TimestampMixin(SQLModel):
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)


class CoreItemMixin(TimestampMixin):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(index=True)
    category_id: uuid.UUID = Field(foreign_key="categories.id")
    status: ItemStatus = Field(default=ItemStatus.draft)
    deleted_at: datetime | None = None
