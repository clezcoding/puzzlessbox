"""Calendar OAuth tokens + event Google sync columns (D-17, D-18, CAL-02).

Auth table contract (D-21): owner_id references Better Auth user.id via application
check only — no FK to the cross-service `user` table.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_calendar_tokens"
down_revision: Union[str, None] = "0002_idempotency"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BERLIN_NOW = sa.text("timezone('Europe/Berlin', now())")


def upgrade() -> None:
    op.create_table(
        "calendar_tokens",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("encrypted_access", sa.Text(), nullable=False),
        sa.Column("encrypted_refresh", sa.Text(), nullable=False),
        sa.Column("selected_calendar_id", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=BERLIN_NOW, nullable=False),
    )
    op.execute("ALTER TABLE calendar_tokens ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE calendar_tokens FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY tenant_isolation ON calendar_tokens
        USING (owner_id = current_setting('app.owner_id', true)::uuid)
        """
    )
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON calendar_tokens TO puzzlessbox_app")

    op.add_column("events", sa.Column("google_event_id", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("etag", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("events", "etag")
    op.drop_column("events", "google_event_id")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON calendar_tokens")
    op.drop_table("calendar_tokens")
