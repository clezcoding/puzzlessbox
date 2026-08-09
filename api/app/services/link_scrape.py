"""In-process async link metadata scrape (D-01, D-17, D-19, D-26)."""

from __future__ import annotations

import asyncio
import json
from typing import Dict
from urllib.parse import urlparse

from sqlalchemy import text
from sqlmodel import Session

from app.core.database import get_engine
from app.services.categories import links_category_id
from app.services.scraper import ScrapeResult, ScrapeStatus, scrape_service

SOFT_SCRAPE_TIMEOUT = 12.0
SCRAPE_RETRY_BACKOFF = 2.0
MAX_SCRAPE_RETRIES = 2


def map_scrape_status(result: ScrapeResult) -> ScrapeStatus:
    if result.scrape_status == "failed":
        return "failed"
    if result.image:
        return "ok"
    return "partial"


def scrape_fields_from_result(url: str, result: ScrapeResult) -> tuple[str, dict[str, object], ScrapeStatus]:
    parsed = urlparse(url)
    hostname = parsed.netloc or url
    scrape_status = map_scrape_status(result)
    title = result.title or hostname
    metadata: dict[str, object] = {
        "title": title,
        "url": url,
        "description": result.description,
        "image": result.image,
    }
    if scrape_status in ("failed", "timed_out"):
        title = hostname
        metadata["title"] = hostname
    return title, metadata, scrape_status


def apply_scrape_to_link(
    db: Session,
    *,
    link_id: str,
    owner_id: str,
    url: str,
    title: str,
    metadata: dict[str, object],
    scrape_status: ScrapeStatus,
) -> None:
    """Write scrape outcome on link row; failed/timed_out get Links category (D-02, D-04, D-11)."""
    parsed = urlparse(url)
    hostname = parsed.netloc or url
    if scrape_status in ("failed", "timed_out"):
        title = hostname
        metadata = {**metadata, "title": hostname}
        category_id = str(links_category_id(db))
        db.execute(
            text(
                """
                UPDATE links
                SET title = :title,
                    metadata = CAST(:metadata AS json),
                    scrape_status = :scrape_status,
                    category_id = :category_id,
                    updated_at = NOW()
                WHERE id = :link_id AND owner_id = :owner_id
                """
            ),
            {
                "link_id": link_id,
                "owner_id": owner_id,
                "title": title,
                "metadata": json.dumps(metadata),
                "scrape_status": scrape_status,
                "category_id": category_id,
            },
        )
    else:
        db.execute(
            text(
                """
                UPDATE links
                SET title = :title,
                    metadata = CAST(:metadata AS json),
                    scrape_status = :scrape_status,
                    updated_at = NOW()
                WHERE id = :link_id AND owner_id = :owner_id
                """
            ),
            {
                "link_id": link_id,
                "owner_id": owner_id,
                "title": title,
                "metadata": json.dumps(metadata),
                "scrape_status": scrape_status,
            },
        )
    db.commit()


class LinkScrapeManager:
    def __init__(self) -> None:
        self._active_tasks: Dict[str, asyncio.Task[None]] = {}

    def schedule_scrape(self, link_id: str, owner_id: str, url: str) -> None:
        self.cancel_scrape(link_id)
        task = asyncio.create_task(self._run_scrape_job(link_id, owner_id, url))
        self._active_tasks[link_id] = task

    def cancel_scrape(self, link_id: str) -> None:
        task = self._active_tasks.pop(link_id, None)
        if task and not task.done():
            task.cancel()

    async def _run_scrape_job(self, link_id: str, owner_id: str, url: str) -> None:
        parsed = urlparse(url)
        hostname = parsed.netloc or url
        title = hostname
        metadata: dict[str, object] = {"title": hostname, "url": url}
        scrape_status: ScrapeStatus = "failed"
        result: ScrapeResult | None = None

        try:
            await self._set_scrape_status(link_id, owner_id, "scraping")

            for attempt in range(MAX_SCRAPE_RETRIES + 1):
                try:
                    result = await asyncio.wait_for(
                        scrape_service.scrape(url),
                        timeout=SOFT_SCRAPE_TIMEOUT,
                    )
                    title, metadata, scrape_status = scrape_fields_from_result(url, result)
                    if scrape_status != "failed":
                        break
                    if attempt < MAX_SCRAPE_RETRIES:
                        await asyncio.sleep(SCRAPE_RETRY_BACKOFF)
                        continue
                    break
                except asyncio.TimeoutError:
                    scrape_status = "timed_out"
                    title = hostname
                    metadata = {"title": hostname, "url": url}
                    if attempt < MAX_SCRAPE_RETRIES:
                        await asyncio.sleep(SCRAPE_RETRY_BACKOFF)
                        continue
                    break
                except Exception:
                    scrape_status = "failed"
                    title = hostname
                    metadata = {"title": hostname, "url": url}
                    if attempt < MAX_SCRAPE_RETRIES:
                        await asyncio.sleep(SCRAPE_RETRY_BACKOFF)
                        continue
                    break

            with Session(get_engine()) as session:
                session.execute(
                    text("SELECT set_config('app.owner_id', :owner_id, true)"),
                    {"owner_id": owner_id},
                )
                session.execute(text("SET LOCAL ROLE puzzlessbox_app"))
                apply_scrape_to_link(
                    session,
                    link_id=link_id,
                    owner_id=owner_id,
                    url=url,
                    title=title,
                    metadata=metadata,
                    scrape_status=scrape_status,
                )
        except asyncio.CancelledError:
            if self._active_tasks.get(link_id) is asyncio.current_task():
                await self._set_scrape_status(link_id, owner_id, "pending")
            raise
        finally:
            current = asyncio.current_task()
            if self._active_tasks.get(link_id) is current:
                self._active_tasks.pop(link_id, None)

    async def _set_scrape_status(self, link_id: str, owner_id: str, status: str) -> None:
        with Session(get_engine()) as session:
            session.execute(
                text("SELECT set_config('app.owner_id', :owner_id, true)"),
                {"owner_id": owner_id},
            )
            session.execute(text("SET LOCAL ROLE puzzlessbox_app"))
            session.execute(
                text(
                    """
                    UPDATE links
                    SET scrape_status = :status, updated_at = NOW()
                    WHERE id = :link_id AND owner_id = :owner_id
                    """
                ),
                {"link_id": link_id, "owner_id": owner_id, "status": status},
            )
            session.commit()


scrape_manager = LinkScrapeManager()
