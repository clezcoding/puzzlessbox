from __future__ import annotations

from datetime import datetime

from app.models.base import CoreItemMixin


class Event(CoreItemMixin, table=True):
    __tablename__ = "events"

    title: str
    summary: str = ""
    starts_at: datetime | None = None
    ends_at: datetime | None = None
