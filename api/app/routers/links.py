"""Link create with synchronous metadata scrape (LINK-01, D-04, D-09)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy import text
from sqlmodel import Session

from app.auth.jwt import get_db_for_owner
from app.core.database import current_owner_id
from app.models import Link
from app.models.enums import ItemStatus
from app.services.categories import links_category_id
from app.services.link_scrape import (
    apply_scrape_to_link,
    scrape_fields_from_result,
    scrape_manager,
)
from app.services.scraper import scrape_service

router = APIRouter(tags=["links"])


class LinkCreate(BaseModel):
    url: HttpUrl


@router.post("/links", status_code=status.HTTP_201_CREATED)
async def create_link(
    payload: LinkCreate,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, Any]:
    owner_id = current_owner_id.get()
    if not owner_id:
        raise RuntimeError("owner_id missing after auth dependency")

    url = str(payload.url)
    now = datetime.now(timezone.utc)
    row = Link(
        owner_id=uuid.UUID(owner_id),
        category_id=links_category_id(db),
        status=ItemStatus.confirmed,
        title=url,
        url=url,
        metadata_={"title": url, "url": url},
        scrape_status="pending",
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    scraped = await scrape_service.scrape(url)
    title, metadata, scrape_status = scrape_fields_from_result(url, scraped)
    apply_scrape_to_link(
        db,
        link_id=str(row.id),
        owner_id=owner_id,
        url=url,
        title=title,
        metadata=metadata,
        scrape_status=scrape_status,
    )
    db.refresh(row)

    return {
        "id": str(row.id),
        "url": row.url,
        "title": row.title,
        "metadata": row.metadata_,
        "scrape_status": row.scrape_status,
        "category_id": str(row.category_id),
    }


@router.post("/links/{link_id}/rescrape", status_code=status.HTTP_202_ACCEPTED)
async def rescrape_link(
    link_id: str,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, str]:
    owner_id = current_owner_id.get()
    if not owner_id:
        raise RuntimeError("owner_id missing after auth dependency")

    row = db.execute(
        text(
            """
            SELECT id, url, scrape_status
            FROM links
            WHERE id = :link_id AND owner_id = :owner_id
            """
        ),
        {"link_id": link_id, "owner_id": owner_id},
    ).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    db.execute(
        text(
            """
            UPDATE links
            SET scrape_status = 'pending', updated_at = NOW()
            WHERE id = :link_id AND owner_id = :owner_id
            """
        ),
        {"link_id": link_id, "owner_id": owner_id},
    )
    db.commit()

    scrape_manager.schedule_scrape(link_id, owner_id, row["url"])

    return {"id": link_id, "scrape_status": "pending"}
