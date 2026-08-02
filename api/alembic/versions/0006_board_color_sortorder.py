"""Board color, sort_order, category soft-delete; board_items VIEW sort_order."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_board_color_sortorder"
down_revision: Union[str, None] = "0005_item_status_discarded"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ITEM_TABLES = ("notes", "links", "tasks", "events")

BOARD_ITEMS_VIEW = """
CREATE VIEW board_items AS
SELECT id, owner_id, category_id, status, title, summary,
       'note'::text AS type, sort_order, created_at, updated_at, deleted_at
FROM notes
UNION ALL
SELECT id, owner_id, category_id, status, title, ''::text AS summary,
       'link'::text AS type, sort_order, created_at, updated_at, deleted_at
FROM links
UNION ALL
SELECT id, owner_id, category_id, status, title, summary,
       'task'::text AS type, sort_order, created_at, updated_at, deleted_at
FROM tasks
UNION ALL
SELECT id, owner_id, category_id, status, title, summary,
       'event'::text AS type, sort_order, created_at, updated_at, deleted_at
FROM events
"""

BOARD_ITEMS_VIEW_LEGACY = """
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

DEFAULT_CATEGORY_SORT = (
    ("Inbox", 0),
    ("Notizen", 1),
    ("Links", 2),
    ("Tasks", 3),
    ("Termine", 4),
)


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS board_items")

    op.add_column("categories", sa.Column("color", sa.Text(), nullable=True))
    op.add_column(
        "categories",
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "categories",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    for table in ITEM_TABLES:
        op.add_column(
            table,
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        )

    for name, sort_order in DEFAULT_CATEGORY_SORT:
        op.execute(
            sa.text(
                "UPDATE categories SET sort_order = :sort_order WHERE name = :name"
            ).bindparams(sort_order=sort_order, name=name)
        )

    op.execute(BOARD_ITEMS_VIEW)
    op.execute("GRANT SELECT ON board_items TO puzzlessbox_app")


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS board_items")

    for table in reversed(ITEM_TABLES):
        op.drop_column(table, "sort_order")

    op.drop_column("categories", "deleted_at")
    op.drop_column("categories", "sort_order")
    op.drop_column("categories", "color")

    op.execute(BOARD_ITEMS_VIEW_LEGACY)
    op.execute("GRANT SELECT ON board_items TO puzzlessbox_app")
