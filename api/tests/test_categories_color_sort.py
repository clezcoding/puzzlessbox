"""Category color, sort_order, reorder, soft-delete tests (BOARD-02)."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text

from app.core.database import get_engine
from tests.conftest import API_HEADERS, mint_test_jwt


def _auth_headers(mock_jwks_keypair, owner_id: str) -> dict[str, str]:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id)
    return {**API_HEADERS, "Authorization": f"Bearer {token}"}


def _create_owned_category(api_client, headers: dict[str, str], name: str) -> str:
    response = api_client.post(
        "/categories",
        headers=headers,
        json={"name": name},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_list_categories_includes_color_and_sort_order(
    api_client,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    response = api_client.get("/categories", headers=headers)
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) >= 5
    for category in categories:
        assert "color" in category
        assert "sort_order" in category

    sort_keys = [(c["sort_order"], c["name"]) for c in categories]
    assert sort_keys == sorted(sort_keys)


def test_patch_category_name_and_color(
    api_client,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    category_id = _create_owned_category(api_client, headers, f"PatchMe-{uuid.uuid4().hex[:8]}")
    new_name = f"Renamed-{uuid.uuid4().hex[:8]}"

    response = api_client.patch(
        f"/categories/{category_id}",
        headers=headers,
        json={"name": new_name, "color": "#aabbcc"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == new_name
    assert body["color"] == "#aabbcc"


def test_patch_category_invalid_color_returns_422(
    api_client,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    category_id = _create_owned_category(api_client, headers, f"Color-{uuid.uuid4().hex[:8]}")

    for invalid in ("red", "<script>"):
        response = api_client.patch(
            f"/categories/{category_id}",
            headers=headers,
            json={"color": invalid},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_reorder_categories_sets_sort_order(
    api_client,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    cat_a = _create_owned_category(api_client, headers, f"ReorderA-{uuid.uuid4().hex[:6]}")
    cat_b = _create_owned_category(api_client, headers, f"ReorderB-{uuid.uuid4().hex[:6]}")

    response = api_client.post(
        "/categories/reorder",
        headers=headers,
        json={
            "items": [
                {"id": cat_a, "sort_order": 50},
                {"id": cat_b, "sort_order": 51},
            ]
        },
    )
    assert response.status_code == 200

    listed = api_client.get("/categories", headers=headers).json()
    by_id = {item["id"]: item for item in listed}
    assert by_id[cat_a]["sort_order"] == 50
    assert by_id[cat_b]["sort_order"] == 51


def test_delete_last_category_returns_409(
    api_client,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    with get_engine().begin() as conn:
        conn.execute(text("UPDATE categories SET deleted_at = NOW()"))
    try:
        category_id = _create_owned_category(api_client, headers, f"Solo-{uuid.uuid4().hex[:8]}")

        response = api_client.delete(f"/categories/{category_id}", headers=headers)
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "CONFLICT"
    finally:
        with get_engine().begin() as conn:
            conn.execute(text("UPDATE categories SET deleted_at = NULL WHERE owner_id IS NULL"))
            conn.execute(
                text("DELETE FROM categories WHERE owner_id = CAST(:owner_id AS uuid)"),
                {"owner_id": owner_id_a},
            )


def test_delete_category_reassigns_items_to_inbox(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    custom_id = _create_owned_category(api_client, headers, f"Items-{uuid.uuid4().hex[:8]}")

    draft = api_client.post(
        "/drafts",
        headers=headers,
        json={
            "title": "Stay alive",
            "type": "note",
            "category_id": custom_id,
            "summary": "body",
        },
    )
    assert draft.status_code == 201
    note_id = draft.json()["id"]

    delete = api_client.delete(f"/categories/{custom_id}", headers=headers)
    assert delete.status_code == 204

    with get_engine().connect() as conn:
        row = conn.execute(
            text("SELECT category_id FROM notes WHERE id = CAST(:id AS uuid)"),
            {"id": note_id},
        ).one()
    assert str(row[0]) == category_id


def test_category_mutations_are_owner_scoped(
    api_client,
    mock_jwks_keypair,
    owner_id_a,
    owner_id_b,
) -> None:
    headers_a = _auth_headers(mock_jwks_keypair, owner_id_a)
    category_id = _create_owned_category(api_client, headers_a, f"Scoped-{uuid.uuid4().hex[:8]}")
    headers_b = _auth_headers(mock_jwks_keypair, owner_id_b)

    patch = api_client.patch(
        f"/categories/{category_id}",
        headers=headers_b,
        json={"name": "Hijacked"},
    )
    assert patch.status_code == 404
    assert patch.json()["error"]["code"] == "NOT_FOUND"

    delete = api_client.delete(f"/categories/{category_id}", headers=headers_b)
    assert delete.status_code == 404

    reorder = api_client.post(
        "/categories/reorder",
        headers=headers_b,
        json={"items": [{"id": category_id, "sort_order": 99}]},
    )
    assert reorder.status_code == 404
