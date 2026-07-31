"""Schema migration behavior tests."""

from __future__ import annotations

from sqlalchemy import text


def test_seed_categories(postgres_connection) -> None:
    rows = postgres_connection.execute(
        text("SELECT name FROM categories ORDER BY name")
    ).fetchall()
    names = [row[0] for row in rows]
    assert names == ["Inbox", "Links", "Notizen", "Tasks", "Termine"]


def test_service_principals_table(postgres_connection) -> None:
    exists = postgres_connection.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'service_principals'
            )
            """
        )
    ).scalar_one()
    assert exists is True


def test_board_items_view(postgres_connection, owner_id_a, category_id) -> None:
    postgres_connection.execute(
        text(
            """
            INSERT INTO notes (owner_id, category_id, status, title, summary)
            VALUES (:owner_id, :category_id, 'draft', 'Board note', 'hello')
            """
        ),
        {"owner_id": owner_id_a, "category_id": category_id},
    )
    rows = postgres_connection.execute(
        text("SELECT type, title FROM board_items WHERE title = 'Board note'")
    ).fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "note"
    assert rows[0][1] == "Board note"


def test_no_users_table(postgres_connection) -> None:
    exists = postgres_connection.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'users'
            )
            """
        )
    ).scalar_one()
    assert exists is False
