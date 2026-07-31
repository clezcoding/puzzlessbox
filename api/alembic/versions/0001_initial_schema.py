"""Initial schema: core tables, board_items VIEW, RLS, service_principals.

Auth table contract (D-21): Better Auth (Next.js) owns the singular `user` table.
Core domain tables use owner_id UUID NOT NULL referencing Better Auth user.id
without FK constraint (cross-service). This migration does NOT create a `users` table.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BERLIN_NOW = sa.text("timezone('Europe/Berlin', now())")

RLS_TABLES = ("notes", "links", "tasks", "events", "categories")


def _core_columns() -> list[sa.Column]:
    return [
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM("draft", "auto_saved", "confirmed", name="item_status", create_type=False),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=BERLIN_NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=BERLIN_NOW, nullable=False),
    ]


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    item_status = postgresql.ENUM("draft", "auto_saved", "confirmed", name="item_status")
    item_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=BERLIN_NOW, nullable=False),
        sa.UniqueConstraint("name", name="uq_categories_name"),
    )
    op.create_index("ix_categories_owner_id", "categories", ["owner_id"])

    op.create_table(
        "notes",
        *_core_columns(),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
    )
    op.create_index("ix_notes_owner_id", "notes", ["owner_id"])

    op.create_table(
        "links",
        *_core_columns(),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("scrape_status", sa.Text(), nullable=True),
    )
    op.create_index("ix_links_owner_id", "links", ["owner_id"])

    op.create_table(
        "tasks",
        *_core_columns(),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tasks_owner_id", "tasks", ["owner_id"])

    op.create_table(
        "events",
        *_core_columns(),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_events_owner_id", "events", ["owner_id"])

    op.create_table(
        "service_principals",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("bearer_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=BERLIN_NOW, nullable=False),
    )

    op.execute(
        """
        CREATE VIEW board_items AS
        SELECT id, owner_id, category_id, status, title, summary,
               'note'::text AS type, created_at, updated_at, deleted_at
        FROM notes
        UNION ALL
        SELECT id, owner_id, category_id, status, title, ''::text AS summary,
               'link'::text AS type, created_at, updated_at, deleted_at
        FROM links
        UNION ALL
        SELECT id, owner_id, category_id, status, title, summary,
               'task'::text AS type, created_at, updated_at, deleted_at
        FROM tasks
        UNION ALL
        SELECT id, owner_id, category_id, status, title, summary,
               'event'::text AS type, created_at, updated_at, deleted_at
        FROM events
        """
    )

    for table in RLS_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        if table == "categories":
            policy_sql = """
                CREATE POLICY tenant_isolation ON categories
                USING (
                    owner_id IS NULL
                    OR owner_id = current_setting('app.owner_id', true)::uuid
                )
            """
        else:
            policy_sql = f"""
                CREATE POLICY tenant_isolation ON {table}
                USING (owner_id = current_setting('app.owner_id', true)::uuid)
            """
        op.execute(policy_sql)

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'puzzlessbox_app') THEN
                CREATE ROLE puzzlessbox_app NOLOGIN;
            END IF;
        END
        $$
        """
    )
    op.execute("GRANT USAGE ON SCHEMA public TO puzzlessbox_app")
    for table in (*RLS_TABLES, "service_principals"):
        op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {table} TO puzzlessbox_app")
    op.execute("GRANT SELECT ON board_items TO puzzlessbox_app")
    op.execute("GRANT puzzlessbox_app TO CURRENT_USER")

    op.execute(
        """
        INSERT INTO categories (name) VALUES
            ('Inbox'),
            ('Notizen'),
            ('Links'),
            ('Tasks'),
            ('Termine')
        ON CONFLICT (name) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS board_items")
    for table in reversed(RLS_TABLES):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
    op.drop_table("service_principals")
    op.drop_table("events")
    op.drop_table("tasks")
    op.drop_table("links")
    op.drop_table("notes")
    op.drop_table("categories")
    op.execute("DROP TYPE IF EXISTS item_status")
    op.execute("DROP ROLE IF EXISTS puzzlessbox_app")
