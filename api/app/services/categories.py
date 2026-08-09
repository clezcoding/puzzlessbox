"""Shared category lookups (Phase 1 D-11 Links fallback)."""

from __future__ import annotations

import uuid

from sqlalchemy import text
from sqlmodel import Session


def links_category_id(db: Session) -> uuid.UUID:
    category_id = db.execute(
        text("SELECT id FROM categories WHERE name = 'Links' LIMIT 1")
    ).scalar_one_or_none()
    if category_id is None:
        raise RuntimeError("Default Links category is not seeded")
    return uuid.UUID(str(category_id))
