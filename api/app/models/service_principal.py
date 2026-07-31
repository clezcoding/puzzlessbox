from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.base import CoreItemMixin


class ServicePrincipal(SQLModel, table=True):
    __tablename__ = "service_principals"

    owner_id: uuid.UUID = Field(primary_key=True)
    name: str
    bearer_hash: str
    created_at: datetime | None = None
