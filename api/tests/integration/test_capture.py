"""Capture integration tests (CAP-01, AUTH-04, CAP-03)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

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

    fetched = api_client.get(f"/drafts/{body['id']}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["type"] == item_type

    listed = api_client.get("/board-items", headers=headers)
    assert listed.status_code == 200
    # D-04: draft items stay chat-only; board shows auto_saved/confirmed only
    assert not any(item["id"] == body["id"] for item in listed.json())


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
    confirm = api_client.post(f"/drafts/{created_id}/confirm", headers=headers_a)
    assert confirm.status_code == 200

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

    draft_id = first.json()["id"]
    confirm = api_client.post(
        f"/drafts/{draft_id}/confirm",
        headers={**API_HEADERS, "Authorization": f"Bearer {token}"},
    )
    assert confirm.status_code == 200

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


@pytest.mark.asyncio
async def test_patch_resets(
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
            "title": "Before patch",
            "type": "note",
            "category_id": category_id,
            "summary": "original",
        },
    )
    draft_id = created.json()["id"]
    await asyncio.sleep(0.5)

    patched = await async_api_client.patch(
        f"/drafts/{draft_id}",
        headers=headers,
        json={"title": "After patch"},
    )
    assert patched.status_code == 200
    assert _draft_status(postgres_connection, "notes", draft_id) == "draft"

    await asyncio.sleep(1.2)
    assert _draft_status(postgres_connection, "notes", draft_id) == "auto_saved"


@pytest.mark.asyncio
async def test_confirm_cancels(
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
            "title": "Confirm me",
            "type": "note",
            "category_id": category_id,
            "summary": "no autosave",
        },
    )
    draft_id = created.json()["id"]

    confirmed = await async_api_client.post(f"/drafts/{draft_id}/confirm", headers=headers)
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"
    assert _draft_status(postgres_connection, "notes", draft_id) == "confirmed"

    await asyncio.sleep(1.5)
    assert _draft_status(postgres_connection, "notes", draft_id) == "confirmed"


@pytest.mark.asyncio
async def test_parallel_edits(
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
            "title": "Parallel",
            "type": "note",
            "category_id": category_id,
            "summary": "race",
        },
    )
    draft_id = created.json()["id"]

    responses = await asyncio.gather(
        async_api_client.patch(
            f"/drafts/{draft_id}",
            headers=headers,
            json={"title": "Patch A"},
        ),
        async_api_client.patch(
            f"/drafts/{draft_id}",
            headers=headers,
            json={"summary": "Patch B"},
        ),
    )
    assert all(response.status_code == 200 for response in responses)

    await asyncio.sleep(1.2)
    assert _draft_status(postgres_connection, "notes", draft_id) == "auto_saved"


@pytest.mark.asyncio
async def test_no_orphan_autosave(
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
            "title": "Orphan guard",
            "type": "note",
            "category_id": category_id,
            "summary": "confirmed stays",
        },
    )
    draft_id = created.json()["id"]
    await async_api_client.post(f"/drafts/{draft_id}/confirm", headers=headers)

    await asyncio.sleep(1.5)
    assert _draft_status(postgres_connection, "notes", draft_id) == "confirmed"


@pytest.mark.asyncio
async def test_patch_task_type_resets(
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
            "title": "Task patch",
            "type": "task",
            "category_id": category_id,
            "summary": "polymorphic patch",
        },
    )
    draft_id = created.json()["id"]
    await asyncio.sleep(0.5)

    patched = await async_api_client.patch(
        f"/drafts/{draft_id}",
        headers=headers,
        json={"summary": "updated task"},
    )
    assert patched.status_code == 200

    await asyncio.sleep(1.2)
    assert _draft_status(postgres_connection, "tasks", draft_id) == "auto_saved"


def _create_draft(api_client, headers, category_id, *, title="Test draft", item_type="note"):
    response = api_client.post(
        "/drafts",
        headers=headers,
        json={
            "title": title,
            "type": item_type,
            "category_id": category_id,
            "summary": "summary text",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def _draft_deleted_at(postgres_connection, table: str, draft_id: str):
    return postgres_connection.execute(
        text(f"SELECT deleted_at FROM {table} WHERE id = :id"),
        {"id": draft_id},
    ).scalar_one()


def test_discard_draft_204(
    api_client,
    postgres_connection,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
    monkeypatch,
) -> None:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    draft_id = _create_draft(api_client, headers, category_id)

    cancel_mock = MagicMock()
    monkeypatch.setattr("app.routers.capture.timeout_manager.cancel_timeout", cancel_mock)

    response = api_client.post(f"/drafts/{draft_id}/discard", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body == {"id": draft_id, "type": "note", "status": "discarded"}
    assert _draft_status(postgres_connection, "notes", draft_id) == "discarded"
    assert _draft_deleted_at(postgres_connection, "notes", draft_id) is not None
    cancel_mock.assert_called_once_with(draft_id)


@pytest.mark.asyncio
async def test_discard_draft_auto_saved(
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
            "title": "Autosave discard",
            "type": "note",
            "category_id": category_id,
            "summary": "wait",
        },
    )
    draft_id = created.json()["id"]
    await asyncio.sleep(1.2)
    assert _draft_status(postgres_connection, "notes", draft_id) == "auto_saved"

    response = await async_api_client.post(f"/drafts/{draft_id}/discard", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "discarded"
    assert _draft_deleted_at(postgres_connection, "notes", draft_id) is not None


def test_discard_draft_not_found(
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
    draft_id = _create_draft(api_client, headers_a, category_id)

    foreign = api_client.post(f"/drafts/{draft_id}/discard", headers=headers_b)
    assert foreign.status_code == 404
    assert foreign.json()["error"]["code"] == "NOT_FOUND"

    unknown = api_client.post(
        f"/drafts/{uuid.uuid4()}/discard",
        headers=headers_a,
    )
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "NOT_FOUND"


def test_discard_draft_already_confirmed(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    draft_id = _create_draft(api_client, headers, category_id)

    confirmed = api_client.post(f"/drafts/{draft_id}/confirm", headers=headers)
    assert confirmed.status_code == 200

    response = api_client.post(f"/drafts/{draft_id}/discard", headers=headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_get_draft_returns_status_and_fields(
    api_client,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    draft_id = _create_draft(api_client, headers, category_id, title="Poll draft")

    response = api_client.get(f"/drafts/{draft_id}", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == draft_id
    assert body["type"] == "note"
    assert body["status"] == "draft"
    assert body["title"] == "Poll draft"
    assert body["category_id"] == category_id
    assert body["summary"] == "summary text"
    assert "deleted_at" not in body


@pytest.mark.asyncio
async def test_get_draft_auto_saved_status(
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
            "title": "Poll autosave",
            "type": "note",
            "category_id": category_id,
            "summary": "poll",
        },
    )
    draft_id = created.json()["id"]
    await asyncio.sleep(1.2)

    response = await async_api_client.get(f"/drafts/{draft_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "auto_saved"


def test_get_draft_not_found(
    api_client,
    postgres_connection,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
    owner_id_b,
) -> None:
    token_a = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    token_b = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_b)
    headers_a = {**API_HEADERS, "Authorization": f"Bearer {token_a}"}
    headers_b = {**API_HEADERS, "Authorization": f"Bearer {token_b}"}
    draft_id = _create_draft(api_client, headers_a, category_id)

    foreign = api_client.get(f"/drafts/{draft_id}", headers=headers_b)
    assert foreign.status_code == 404
    assert foreign.json()["error"]["code"] == "NOT_FOUND"

    unknown = api_client.get(f"/drafts/{uuid.uuid4()}", headers=headers_a)
    assert unknown.status_code == 404

    api_client.post(f"/drafts/{draft_id}/discard", headers=headers_a)
    deleted = api_client.get(f"/drafts/{draft_id}", headers=headers_a)
    assert deleted.status_code == 404
    assert deleted.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_confirm_after_autosave_idempotent(
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
            "title": "Late confirm",
            "type": "note",
            "category_id": category_id,
            "summary": "after autosave",
        },
    )
    draft_id = created.json()["id"]
    await asyncio.sleep(1.2)
    assert _draft_status(postgres_connection, "notes", draft_id) == "auto_saved"

    confirmed = await async_api_client.post(f"/drafts/{draft_id}/confirm", headers=headers)
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"
