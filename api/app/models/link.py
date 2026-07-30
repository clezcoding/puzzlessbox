from __future__ import annotations

from typing import Any

from sqlalchemy import Column, JSON
from sqlmodel import Field

from app.models.base import CoreItemMixin


class Link(CoreItemMixin, table=True):
    __tablename__ = "links"

    title: str
    url: str
    metadata_: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSON, nullable=False, server_default="{}"),
    )
    scrape_status: str | None = None
