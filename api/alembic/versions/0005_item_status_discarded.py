"""Add discarded to item_status enum (D-04 soft-delete)."""

from typing import Sequence, Union

from alembic import op

revision: str = "0005_item_status_discarded"
down_revision: Union[str, None] = "0004_mcp_clients"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE item_status ADD VALUE IF NOT EXISTS 'discarded'")


def downgrade() -> None:
    # PostgreSQL cannot remove enum values safely; no-op downgrade.
    pass
