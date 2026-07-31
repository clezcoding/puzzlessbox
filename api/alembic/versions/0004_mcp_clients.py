"""MCP client bearer hashes for Hermes owner resolution (D-02, D-04)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_mcp_clients"
down_revision: Union[str, None] = "0003_calendar_tokens"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BERLIN_NOW = sa.text("timezone('Europe/Berlin', now())")


def upgrade() -> None:
    op.create_table(
        "mcp_clients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bearer_hash", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), server_default="active", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=BERLIN_NOW, nullable=False),
    )
    op.create_index("ix_mcp_clients_bearer_hash", "mcp_clients", ["bearer_hash"])
    op.create_index("ix_mcp_clients_owner_id", "mcp_clients", ["owner_id"])
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON mcp_clients TO puzzlessbox_app")


def downgrade() -> None:
    op.drop_index("ix_mcp_clients_owner_id", table_name="mcp_clients")
    op.drop_index("ix_mcp_clients_bearer_hash", table_name="mcp_clients")
    op.drop_table("mcp_clients")
