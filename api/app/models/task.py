from __future__ import annotations

from datetime import datetime

from sqlmodel import Field

from app.models.base import CoreItemMixin


class Task(CoreItemMixin, table=True):
    __tablename__ = "tasks"

    title: str
    summary: str = ""
    due_at: datetime | None = None
