from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    # ponytail: NULL owner_id = system default category visible to all tenants (D-04)
    owner_id: uuid.UUID | None = Field(default=None, index=True)
    name: str = Field(unique=True, index=True)
    created_at: datetime | None = None
