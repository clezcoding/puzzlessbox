"""board_items VIEW: link url summary, image, scrape_status (D-05, D-08, D-24)."""

from typing import Sequence, Union

from alembic import op

revision: str = "0007_board_items_link_fields"
down_revision: Union[str, None] = "0006_board_color_sortorder"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BOARD_ITEMS_VIEW = """
CREATE VIEW board_items AS
SELECT id, owner_id, category_id, status, title, summary,
       'note'::text AS type, sort_order, created_at, updated_at, deleted_at,
       NULL::text AS image, NULL::text AS scrape_status
FROM notes
UNION ALL
SELECT id, owner_id, category_id, status, title, url AS summary,
       'link'::text AS type, sort_order, created_at, updated_at, deleted_at,
       (metadata->>'image') AS image, scrape_status
FROM links
UNION ALL
SELECT id, owner_id, category_id, status, title, summary,
       'task'::text AS type, sort_order, created_at, updated_at, deleted_at,
       NULL::text AS image, NULL::text AS scrape_status
FROM tasks
UNION ALL
SELECT id, owner_id, category_id, status, title, summary,
       'event'::text AS type, sort_order, created_at, updated_at, deleted_at,
       NULL::text AS image, NULL::text AS scrape_status
FROM events
"""

BOARD_ITEMS_VIEW_0006 = """
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


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS board_items")
    op.execute(BOARD_ITEMS_VIEW)
    op.execute("GRANT SELECT ON board_items TO puzzlessbox_app")


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS board_items")
    op.execute(BOARD_ITEMS_VIEW_0006)
    op.execute("GRANT SELECT ON board_items TO puzzlessbox_app")
