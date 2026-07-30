"""Capture integration tests (CAP-01, AUTH-04, CAP-03)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import uuid
from sqlalchemy import text

from tests.conftest import API_HEADERS, mint_test_jwt


def _mock_better_auth_client(jwt_token: str, owner_id: str, email: str = "owner@example.com"):
    client = AsyncMock()

    async def post(url: str, **kwargs: object) -> httpx.Response:
        if url == "/sign-up/email":
            return httpx.Response(
                200,
                json={
                    "token": jwt_token,
                    "user": {"id": owner_id, "email": email, "name": "Owner"},
                },
            )
        if url == "/sign-in/email":
            return httpx.Response(200, json={"token": jwt_token})
        return httpx.Response(404)

    async def get(url: str, **kwargs: object) -> httpx.Response:
        if url == "/token":
            return httpx.Response(200, json={"token": jwt_token})
        return httpx.Response(404)

    client.post = AsyncMock(side_effect=post)
    client.get = AsyncMock(side_effect=get)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    return client


@pytest.mark.parametrize("item_type", ["note", "link", "task", "event"])
def test_draft_roundtrip(
    api_client,
    postgres_connection,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
    item_type,
) -> None:
    jwt_token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    mock_client = _mock_better_auth_client(jwt_token, owner_id_a)

    with patch("app.routers.auth.httpx.AsyncClient", return_value=mock_client):
        signup = api_client.post(
            "/auth/signup",
            headers=API_HEADERS,
            json={"email": "owner@example.com", "password": "securepass"},
        )
        assert signup.status_code == 201

        login = api_client.post(
            "/auth/login",
            headers=API_HEADERS,
            json={"email": "owner@example.com", "password": "securepass"},
        )
        assert login.status_code == 200
        assert login.json()["token"] == jwt_token

    headers = {**API_HEADERS, "Authorization": f"Bearer {jwt_token}"}
    create = api_client.post(
        "/drafts",
        headers=headers,
        json={
            "title": f"Draft {item_type}",
            "type": item_type,
            "category_id": category_id,
            "summary": "roundtrip",
        },
    )
    assert create.status_code == 201
    body = create.json()
    assert body["type"] == item_type
    assert body["id"]

    listed = api_client.get("/board-items", headers=headers)
    assert listed.status_code == 200
    items = listed.json()
    assert any(item["id"] == body["id"] and item["type"] == item_type for item in items)


def test_cross_tenant_board_items_empty(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
    owner_id_b,
) -> None:
    token_a = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    token_b = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_b)
    headers_a = {**API_HEADERS, "Authorization": f"Bearer {token_a}"}
    headers_b = {**API_HEADERS, "Authorization": f"Bearer {token_b}"}

    created = api_client.post(
        "/drafts",
        headers=headers_a,
        json={
            "title": "Tenant A draft",
            "type": "note",
            "category_id": category_id,
            "summary": "secret",
        },
    )
    assert created.status_code == 201
    created_id = created.json()["id"]

    own_items = api_client.get("/board-items", headers=headers_a).json()
    assert any(item["id"] == created_id for item in own_items)

    foreign_items = api_client.get("/board-items", headers=headers_b).json()
    assert not any(item["id"] == created_id for item in foreign_items)


def test_idempotency(api_client, category_id, mock_jwks_keypair, owner_id_a) -> None:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    idem_key = f"draft-create-{uuid.uuid4()}"
    headers = {
        **API_HEADERS,
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": idem_key,
    }
    payload = {
        "title": "Idempotent draft",
        "type": "note",
        "category_id": category_id,
        "summary": "once",
    }

    first = api_client.post("/drafts", headers=headers, json=payload)
    second = api_client.post("/drafts", headers=headers, json=payload)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json() == second.json()

    listed = api_client.get(
        "/board-items",
        headers={**API_HEADERS, "Authorization": f"Bearer {token}"},
    ).json()
    assert sum(1 for item in listed if item["id"] == first.json()["id"]) == 1


def _draft_status(postgres_connection, table: str, draft_id: str) -> str:
    row = postgres_connection.execute(
        text(f"SELECT status FROM {table} WHERE id = :id"),
        {"id": draft_id},
    ).scalar_one()
    return str(row)


@pytest.mark.asyncio
async def test_autosave(
    async_api_client,
    postgres_connection,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
    monkeypatch,
) -> None:
    monkeypatch.setenv("DRAFT_TIMEOUT_SECONDS", "1")
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}

    created = await async_api_client.post(
        "/drafts",
        headers=headers,
        json={
            "title": "Autosave note",
            "type": "note",
            "category_id": category_id,
            "summary": "wait for timer",
        },
    )
    assert created.status_code == 201
    draft_id = created.json()["id"]
    assert _draft_status(postgres_connection, "notes", draft_id) == "draft"

    await asyncio.sleep(1.2)
    assert _draft_status(postgres_connection, "notes", draft_id) == "auto_saved"

    listed = (await async_api_client.get("/board-items", headers=headers)).json()
    match = next(item for item in listed if item["id"] == draft_id)
    assert match["status"] == "auto_saved"
    assert match["type"] == "note"


@pytest.mark.asyncio
async def test_autosave_task_type(
    async_api_client,
    postgres_connection,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
    monkeypatch,
) -> None:
    monkeypatch.setenv("DRAFT_TIMEOUT_SECONDS", "1")
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}

    created = await async_api_client.post(
        "/drafts",
        headers=headers,
        json={
            "title": "Autosave task",
            "type": "task",
            "category_id": category_id,
            "summary": "polymorphic routing",
        },
    )
    assert created.status_code == 201
    draft_id = created.json()["id"]

    await asyncio.sleep(1.2)
    assert _draft_status(postgres_connection, "tasks", draft_id) == "auto_saved"

    note_row = postgres_connection.execute(
        text("SELECT status FROM notes WHERE id = :id"),
        {"id": draft_id},
    ).scalar_one_or_none()
    assert note_row is None

    listed = (await async_api_client.get("/board-items", headers=headers)).json()
    match = next(item for item in listed if item["id"] == draft_id)
    assert match["type"] == "task"
    assert match["status"] == "auto_saved"
