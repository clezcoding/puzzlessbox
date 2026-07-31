"""RLS tenancy integration tests (AUTH-04)."""

from __future__ import annotations

import uuid

from sqlalchemy import text


def test_rls(postgres_connection, category_id) -> None:
    owner_id_a = str(uuid.uuid4())
    owner_id_b = str(uuid.uuid4())
    note_id = str(uuid.uuid4())
    postgres_connection.execute(
        text(
            """
            INSERT INTO notes (id, owner_id, category_id, status, title, summary)
            VALUES (:id, :owner_id, :category_id, 'draft', 'Tenant note', 'secret')
            """
        ),
        {"id": note_id, "owner_id": owner_id_a, "category_id": category_id},
    )

    postgres_connection.execute(text("SET LOCAL ROLE puzzlessbox_app"))
    postgres_connection.execute(
        text("SELECT set_config('app.owner_id', :owner_id, true)"),
        {"owner_id": owner_id_a},
    )
    count_a = postgres_connection.execute(text("SELECT count(*) FROM notes")).scalar_one()
    assert count_a == 1

    postgres_connection.execute(
        text("SELECT set_config('app.owner_id', :owner_id, true)"),
        {"owner_id": owner_id_b},
    )
    count_b = postgres_connection.execute(text("SELECT count(*) FROM notes")).scalar_one()
    assert count_b == 0
