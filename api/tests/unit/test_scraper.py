"""Scraper unit tests (LINK-02 category invariant)."""

from __future__ import annotations

import uuid

from sqlmodel import Session

from app.models import Category
from app.routers.links import _links_category_id


def test_default_cat(mock_db: Session) -> None:
    links_id = uuid.uuid4()
    mock_db.add(Category(id=links_id, name="Links"))
    mock_db.commit()

    assert _links_category_id(mock_db) == links_id
