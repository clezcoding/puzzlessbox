import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ItemStatus, ItemType


class BoardItem(BaseModel):
    """Read model for board_items VIEW (D-01)."""

    id: uuid.UUID
    owner_id: uuid.UUID
    category_id: uuid.UUID
    status: ItemStatus
    title: str
    summary: str
    image: str | None = None
    scrape_status: str | None = None
    google_event_id: str | None = None
    board_type: ItemType = Field(validation_alias="type", serialization_alias="type")
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"populate_by_name": True}
