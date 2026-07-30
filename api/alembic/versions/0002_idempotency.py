"""Idempotency keys for capture create (D-34)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_idempotency"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BERLIN_NOW = sa.text("timezone('Europe/Berlin', now())")


def upgrade() -> None:
    op.create_table(
        "idempotency_keys",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("response", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=BERLIN_NOW, nullable=False),
        sa.PrimaryKeyConstraint("owner_id", "key", name="pk_idempotency_keys"),
    )
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON idempotency_keys TO puzzlessbox_app")


def downgrade() -> None:
    op.drop_table("idempotency_keys")
