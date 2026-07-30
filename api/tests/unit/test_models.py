"""Schema + draft validation tests (CAP-01)."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from app.models.enums import ItemType
from app.models.note import DraftCreate


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
