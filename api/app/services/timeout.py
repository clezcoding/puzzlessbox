"""In-process draft inactivity timer (CAP-03, D-05, D-08).

30s asyncio.Task per draft — not Hermes cron (60s tick too coarse).
"""

from __future__ import annotations

import asyncio
import os
import uuid
from typing import Dict

from sqlalchemy import text
from sqlmodel import Session

from app.core.database import get_engine
from app.models.enums import ItemType

_TABLE_BY_TYPE: dict[ItemType, str] = {
    ItemType.note: "notes",
    ItemType.link: "links",
    ItemType.task: "tasks",
    ItemType.event: "events",
}


def _default_timeout_seconds() -> float:
    return float(os.environ.get("DRAFT_TIMEOUT_SECONDS", "30.0"))


class DraftTimeoutManager:
    def __init__(self) -> None:
        self._active_tasks: Dict[str, asyncio.Task[None]] = {}

    def schedule_timeout(
        self,
        draft_id: str,
        owner_id: str,
        item_type: ItemType,
        delay_seconds: float | None = None,
    ) -> None:
        # Single-threaded asyncio loop: cancel-then-spawn is atomic (T-01-timer-race).
        self.cancel_timeout(draft_id)
        delay = _default_timeout_seconds() if delay_seconds is None else delay_seconds
        task = asyncio.create_task(
            self._wait_and_autosave(draft_id, owner_id, item_type, delay)
        )
        self._active_tasks[draft_id] = task

    def cancel_timeout(self, draft_id: str) -> None:
        task = self._active_tasks.pop(draft_id, None)
        if task and not task.done():
            task.cancel()

    async def _wait_and_autosave(
        self,
        draft_id: str,
        owner_id: str,
        item_type: ItemType,
        delay_seconds: float,
    ) -> None:
        try:
            await asyncio.sleep(delay_seconds)
            await self._execute_autosave(draft_id, owner_id, item_type)
        except asyncio.CancelledError:
            pass
        finally:
            self._active_tasks.pop(draft_id, None)

    async def _execute_autosave(
        self,
        draft_id: str,
        owner_id: str,
        item_type: ItemType,
    ) -> None:
        table = _TABLE_BY_TYPE[item_type]
        with Session(get_engine()) as session:
            session.execute(
                text("SELECT set_config('app.owner_id', :owner_id, true)"),
                {"owner_id": owner_id},
            )
            session.execute(text("SET LOCAL ROLE puzzlessbox_app"))
            session.execute(
                text(
                    f"""
                    UPDATE {table}
                    SET status = 'auto_saved', updated_at = NOW()
                    WHERE id = :draft_id
                      AND owner_id = :owner_id
                      AND status = 'draft'
                    """
                ),
                {"draft_id": draft_id, "owner_id": owner_id},
            )
            session.commit()


timeout_manager = DraftTimeoutManager()
