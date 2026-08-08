"""In-process async link metadata scrape (D-01, D-17)."""

from __future__ import annotations

import asyncio
import json
from typing import Dict
from urllib.parse import urlparse

from sqlalchemy import text
from sqlmodel import Session

from app.core.database import get_engine
from app.services.categories import links_category_id
from app.services.scraper import scrape_service

SOFT_SCRAPE_TIMEOUT = 12.0


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
        terminal_failed = False
        scrape_status = "failed"
        title = hostname
        metadata: dict[str, object] = {"title": hostname, "url": url}
        category_id: str | None = None

        try:
            await self._set_scrape_status(link_id, owner_id, "scraping")
            try:
                result = await asyncio.wait_for(
                    scrape_service.scrape(url),
                    timeout=SOFT_SCRAPE_TIMEOUT,
                )
                scrape_status = self._map_scrape_status(result)
                title = result.title
                metadata = {
                    "title": result.title,
                    "url": url,
                    "description": result.description,
                    "image": result.image,
                }
                if scrape_status in ("failed", "timed_out"):
                    terminal_failed = True
            except asyncio.TimeoutError:
                scrape_status = "timed_out"
                terminal_failed = True
            except Exception:
                scrape_status = "failed"
                terminal_failed = True

            if terminal_failed:
                with Session(get_engine()) as session:
                    session.execute(
                        text("SELECT set_config('app.owner_id', :owner_id, true)"),
                        {"owner_id": owner_id},
                    )
                    session.execute(text("SET LOCAL ROLE puzzlessbox_app"))
                    category_id = str(links_category_id(session))

            await self._write_scrape_result(
                link_id,
                owner_id,
                title=title,
                metadata=metadata,
                scrape_status=scrape_status,
                category_id=category_id,
            )
        except asyncio.CancelledError:
            pass
        finally:
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

    async def _write_scrape_result(
        self,
        link_id: str,
        owner_id: str,
        *,
        title: str,
        metadata: dict[str, object],
        scrape_status: str,
        category_id: str | None,
    ) -> None:
        with Session(get_engine()) as session:
            session.execute(
                text("SELECT set_config('app.owner_id', :owner_id, true)"),
                {"owner_id": owner_id},
            )
            session.execute(text("SET LOCAL ROLE puzzlessbox_app"))
            params: dict[str, object] = {
                "link_id": link_id,
                "owner_id": owner_id,
                "title": title,
                "metadata": json.dumps(metadata),
                "scrape_status": scrape_status,
            }
            if category_id is not None:
                session.execute(
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
                    {**params, "category_id": category_id},
                )
            else:
                session.execute(
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
                    params,
                )
            session.commit()

    def _map_scrape_status(self, result: object) -> str:
        raw_status = getattr(result, "scrape_status", "failed")
        if raw_status == "failed":
            return "failed"
        image = getattr(result, "image", None)
        if image:
            return "ok"
        return "partial"


scrape_manager = LinkScrapeManager()
