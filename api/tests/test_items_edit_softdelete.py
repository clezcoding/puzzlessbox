"""Item field edit, type-change, soft-delete, reorder tests (BOARD-03, BOARD-04, D-12)."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, text

from tests.conftest import API_HEADERS, mint_test_jwt


def _test_engine():
    url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://puzzless:puzzless@localhost:5432/puzzlessbox",
    )
    return create_engine(url)


def _auth_headers(mock_jwks_keypair, owner_id: str) -> dict[str, str]:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id)
    return {**API_HEADERS, "Authorization": f"Bearer {token}"}


def _create_confirmed_item(
    api_client,
    headers: dict[str, str],
    category_id: str,
    item_type: str,
    *,
    title: str | None = None,
    summary: str = "seed",
) -> str:
    title = title or f"{item_type}-{uuid.uuid4().hex[:8]}"
    created = api_client.post(
        "/drafts",
        headers=headers,
        json={
            "title": title,
            "type": item_type,
            "category_id": category_id,
            "summary": summary,
        },
    )
    assert created.status_code == 201
    item_id = created.json()["id"]
    confirmed = api_client.post(f"/drafts/{item_id}/confirm", headers=headers)
    assert confirmed.status_code == 200
    return item_id


def test_patch_item_title(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    item_id = _create_confirmed_item(api_client, headers, category_id, "note")

    response = api_client.patch(
        f"/items/{item_id}",
        headers=headers,
        json={"title": "Updated title"},
    )
    assert response.status_code == 200

    board = api_client.get("/board-items", headers=headers).json()
    match = next(item for item in board if item["id"] == item_id)
    assert match["title"] == "Updated title"


def test_patch_note_body(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    item_id = _create_confirmed_item(api_client, headers, category_id, "note")

    response = api_client.patch(
        f"/items/{item_id}",
        headers=headers,
        json={"body": "Updated body"},
    )
    assert response.status_code == 200

    board = api_client.get("/board-items", headers=headers).json()
    match = next(item for item in board if item["id"] == item_id)
    assert match["summary"] == "Updated body"


def test_patch_link_url(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    item_id = _create_confirmed_item(
        api_client, headers, category_id, "link", summary="https://old.example"
    )

    response = api_client.patch(
        f"/items/{item_id}",
        headers=headers,
        json={"url": "https://new.example"},
    )
    assert response.status_code == 200

    with _test_engine().connect() as conn:
        row = conn.execute(
            text("SELECT url FROM links WHERE id = CAST(:id AS uuid)"),
            {"id": item_id},
        ).one()
    assert row[0] == "https://new.example"


def test_patch_task_due(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    item_id = _create_confirmed_item(api_client, headers, category_id, "task")
    due = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc).isoformat()

    response = api_client.patch(
        f"/items/{item_id}",
        headers=headers,
        json={"due": due},
    )
    assert response.status_code == 200


def test_patch_event_times(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    item_id = _create_confirmed_item(api_client, headers, category_id, "event")
    start = datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc).isoformat()
    end = datetime(2026, 9, 1, 11, 0, tzinfo=timezone.utc).isoformat()

    response = api_client.patch(
        f"/items/{item_id}",
        headers=headers,
        json={"event_start": start, "event_end": end},
    )
    assert response.status_code == 200


def test_patch_item_sort_order(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    item_id = _create_confirmed_item(api_client, headers, category_id, "note")

    response = api_client.patch(
        f"/items/{item_id}",
        headers=headers,
        json={"sort_order": 5},
    )
    assert response.status_code == 200

    board = api_client.get("/board-items", headers=headers).json()
    match = next(item for item in board if item["id"] == item_id)
    assert match["sort_order"] == 5


def test_reorder_items(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    item_a = _create_confirmed_item(api_client, headers, category_id, "note", title="A")
    item_b = _create_confirmed_item(api_client, headers, category_id, "note", title="B")

    response = api_client.post(
        "/items/reorder",
        headers=headers,
        json={
            "items": [
                {"id": item_a, "sort_order": 20},
                {"id": item_b, "sort_order": 21},
            ]
        },
    )
    assert response.status_code == 200

    board = api_client.get("/board-items", headers=headers).json()
    in_category = [item for item in board if item["category_id"] == category_id]
    by_id = {item["id"]: item for item in in_category}
    assert by_id[item_a]["sort_order"] == 20
    assert by_id[item_b]["sort_order"] == 21


def test_board_items_sorted_by_category_sort_order_created_at(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    first = _create_confirmed_item(api_client, headers, category_id, "note", title="First")
    second = _create_confirmed_item(api_client, headers, category_id, "note", title="Second")

    api_client.patch(f"/items/{first}", headers=headers, json={"sort_order": 1})
    api_client.patch(f"/items/{second}", headers=headers, json={"sort_order": 1})

    board = api_client.get("/board-items", headers=headers).json()
    same_bucket = [
        item
        for item in board
        if item["category_id"] == category_id and item["sort_order"] == 1
    ]
    assert len(same_bucket) >= 2
    titles = [item["title"] for item in same_bucket[:2]]
    assert titles[0] == "Second"
    assert titles[1] == "First"


def test_patch_item_type_change_note_to_task(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    item_id = _create_confirmed_item(
        api_client, headers, category_id, "note", title="Convert me", summary="note body"
    )

    response = api_client.patch(
        f"/items/{item_id}",
        headers=headers,
        json={"type": "task"},
    )
    assert response.status_code == 200

    board = api_client.get("/board-items", headers=headers).json()
    match = next(item for item in board if item["id"] == item_id)
    assert match["type"] == "task"
    assert match["title"] == "Convert me"
    assert match["summary"] == "note body"


def test_delete_item_soft_deletes(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    item_id = _create_confirmed_item(api_client, headers, category_id, "note")

    delete = api_client.delete(f"/items/{item_id}", headers=headers)
    assert delete.status_code == 204

    board = api_client.get("/board-items", headers=headers).json()
    assert not any(item["id"] == item_id for item in board)


def test_restore_item_after_delete(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    item_id = _create_confirmed_item(api_client, headers, category_id, "note")

    api_client.delete(f"/items/{item_id}", headers=headers)
    restore = api_client.post(f"/items/{item_id}/restore", headers=headers)
    assert restore.status_code == 200

    board = api_client.get("/board-items", headers=headers).json()
    assert any(item["id"] == item_id for item in board)


def test_item_mutations_are_owner_scoped(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
    owner_id_b,
) -> None:
    headers_a = _auth_headers(mock_jwks_keypair, owner_id_a)
    item_id = _create_confirmed_item(api_client, headers_a, category_id, "note")
    headers_b = _auth_headers(mock_jwks_keypair, owner_id_b)

    patch = api_client.patch(
        f"/items/{item_id}",
        headers=headers_b,
        json={"title": "Hijacked"},
    )
    assert patch.status_code == 404

    delete = api_client.delete(f"/items/{item_id}", headers=headers_b)
    assert delete.status_code == 404

    restore = api_client.post(f"/items/{item_id}/restore", headers=headers_b)
    assert restore.status_code == 404

    reorder = api_client.post(
        "/items/reorder",
        headers=headers_b,
        json={"items": [{"id": item_id, "sort_order": 99}]},
    )
    assert reorder.status_code == 404
