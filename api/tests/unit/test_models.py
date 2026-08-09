"""Schema + draft validation tests (CAP-01)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.board import BoardItem
from app.models.enums import ItemStatus, ItemType
from app.models.note import DraftCreate


def test_board_item_optional_link_and_calendar_fields() -> None:
    """Regression: google_event_id must be str | None (not JS null) so GET /board-items validates."""
    now = datetime.now(UTC)
    oid = uuid.uuid4()
    item = BoardItem.model_validate(
        {
            "id": oid,
            "owner_id": oid,
            "category_id": oid,
            "status": ItemStatus.confirmed,
            "title": "Example",
            "summary": "https://example.com",
            "image": "https://cdn.example/og.png",
            "scrape_status": "ok",
            "google_event_id": None,
            "type": ItemType.link,
            "sort_order": 0,
            "created_at": now,
            "updated_at": now,
            "deleted_at": None,
        }
    )
    assert item.image == "https://cdn.example/og.png"
    assert item.scrape_status == "ok"
    assert item.google_event_id is None


def test_draft_validation() -> None:
    category_id = uuid.UUID("11111111-1111-4111-8111-111111111111")
    draft = DraftCreate(
        title="Capture me",
        type=ItemType.note,
        category_id=category_id,
        summary="short",
    )
    assert draft.title == "Capture me"
    assert draft.type == ItemType.note
    assert draft.category_id == category_id
    assert draft.summary == "short"

    for item_type in (ItemType.note, ItemType.link, ItemType.task, ItemType.event):
        row = DraftCreate(title="ok", type=item_type, category_id=category_id)
        assert row.type == item_type

    with pytest.raises(ValidationError):
        DraftCreate(
            title="Bad",
            type="invalid",  # type: ignore[arg-type]
            category_id=category_id,
        )
