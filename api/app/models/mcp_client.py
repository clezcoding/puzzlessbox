from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class MCPClient(SQLModel, table=True):
    __tablename__ = "mcp_clients"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(index=True)
    bearer_hash: str = Field(index=True)
    status: str = Field(default="active")
    expires_at: datetime | None = Field(default=None)
    created_at: datetime | None = None
