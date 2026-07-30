from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class CalendarToken(SQLModel, table=True):
    __tablename__ = "calendar_tokens"

    owner_id: uuid.UUID = Field(primary_key=True)
    encrypted_access: str
    encrypted_refresh: str
    selected_calendar_id: str | None = None
    expires_at: datetime | None = None
    updated_at: datetime | None = None
