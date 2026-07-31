"""Link create with synchronous metadata scrape (LINK-01, D-09)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy import text
from sqlmodel import Session

from app.auth.jwt import get_db_for_owner
from app.core.database import current_owner_id
from app.models import Link
from app.models.enums import ItemStatus
from app.services.scraper import scrape_service

router = APIRouter(tags=["links"])


class LinkCreate(BaseModel):
    url: HttpUrl


def _links_category_id(db: Session) -> uuid.UUID:
    category_id = db.execute(
        text("SELECT id FROM categories WHERE name = 'Links' LIMIT 1")
    ).scalar_one_or_none()
    if category_id is None:
        raise RuntimeError("Default Links category is not seeded")
    return uuid.UUID(str(category_id))


@router.post("/links", status_code=status.HTTP_201_CREATED)
async def create_link(
    payload: LinkCreate,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, Any]:
    owner_id = current_owner_id.get()
    if not owner_id:
        raise RuntimeError("owner_id missing after auth dependency")

    url = str(payload.url)
    scraped = await scrape_service.scrape(url)
    metadata = {
        "title": scraped.title,
        "url": url,
        "description": scraped.description,
        "image": scraped.image,
    }

    now = datetime.now(timezone.utc)
    row = Link(
        owner_id=uuid.UUID(owner_id),
        category_id=_links_category_id(db),
        status=ItemStatus.confirmed,
        title=scraped.title,
        url=url,
        metadata_=metadata,
        scrape_status=scraped.scrape_status,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "id": str(row.id),
        "url": row.url,
        "title": row.title,
        "metadata": row.metadata_,
        "scrape_status": row.scrape_status,
        "category_id": str(row.category_id),
    }
