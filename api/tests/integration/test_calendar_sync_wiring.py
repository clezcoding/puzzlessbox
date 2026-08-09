"""Calendar sync wiring on capture + items paths (CAL-02, CAL-03, D-09–D-16)."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from sqlalchemy import text

from tests.conftest import API_HEADERS, mint_test_jwt
from tests.integration.test_calendar import (
    MOCK_CALENDAR_ID,
    MOCK_ETAG,
    MOCK_ETAG_REMOTE,
    MOCK_ETAG_STALE,
    _auth_headers,
    _mock_credentials,
    _mock_google_service,
)


def _connect_calendar(api_client, mock_jwks_keypair, owner_id_a: str, mock_service: MagicMock) -> dict[str, str]:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    mock_flow = MagicMock()
    mock_flow.authorization_url.return_value = ("https://accounts.google.com/o/oauth2/auth?mock=1", "state")
    mock_flow.credentials = _mock_credentials()

    with (
        patch("app.services.calendar.Flow.from_client_config", return_value=mock_flow),
        patch("app.services.calendar.build", return_value=mock_service),
        patch("app.services.calendar.make_oauth_state", return_value="signed-state"),
        patch("app.services.calendar.verify_oauth_state", return_value=owner_id_a),
    ):
        callback = api_client.get(
            "/auth/google/callback",
            params={"code": "mock-code", "state": "signed-state"},
            headers=API_HEADERS,
            follow_redirects=False,
        )
        assert callback.status_code == 302
        select = api_client.post(f"/calendars/{MOCK_CALENDAR_ID}/select", headers=headers)
        assert select.status_code == 200
    return headers


def _create_event_draft(api_client, headers: dict[str, str], category_id: str) -> str:
    created = api_client.post(
        "/drafts",
        headers=headers,
        json={
            "title": "Team sync",
            "type": "event",
            "category_id": category_id,
            "summary": "notes",
        },
    )
    assert created.status_code == 201
    return created.json()["id"]


def test_confirm_draft_event_syncs_existing_row_google_event_id(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
    category_id,
) -> None:
    google_event_id = "google-event-stub"
    mock_service = _mock_google_service(google_event_id=google_event_id)
    headers = _connect_calendar(api_client, mock_jwks_keypair, owner_id_a, mock_service)
    draft_id = _create_event_draft(api_client, headers, category_id)

    before_count = postgres_connection.execute(text("SELECT COUNT(*) FROM events")).scalar_one()

    with patch("app.services.calendar.build", return_value=mock_service):
        confirm = api_client.post(f"/drafts/{draft_id}/confirm", headers=headers)
    assert confirm.status_code == 200

    after_count = postgres_connection.execute(text("SELECT COUNT(*) FROM events")).scalar_one()
    assert after_count == before_count

    row = postgres_connection.execute(
        text("SELECT id, google_event_id, etag FROM events WHERE id = :id"),
        {"id": draft_id},
    ).one()
    assert str(row[0]) == draft_id
    assert row[1] == google_event_id
    assert row[2] == MOCK_ETAG


@pytest.mark.asyncio
async def test_autosave_event_syncs_when_google_connected(
    async_api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
    category_id,
    monkeypatch,
) -> None:
    monkeypatch.setenv("DRAFT_TIMEOUT_SECONDS", "1")
    google_event_id = f"google-event-{uuid4().hex[:12]}"
    mock_service = _mock_google_service(google_event_id=google_event_id)
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}

    with (
        patch("app.services.calendar.Flow.from_client_config", return_value=MagicMock()),
        patch("app.services.calendar.build", return_value=mock_service),
        patch("app.services.calendar.make_oauth_state", return_value="signed-state"),
        patch("app.services.calendar.verify_oauth_state", return_value=owner_id_a),
    ):
        mock_flow = MagicMock()
        mock_flow.credentials = _mock_credentials()
        with patch("app.services.calendar.Flow.from_client_config", return_value=mock_flow):
            callback = await async_api_client.get(
                "/auth/google/callback",
                params={"code": "mock-code", "state": "signed-state"},
                headers=API_HEADERS,
                follow_redirects=False,
            )
            assert callback.status_code == 302
        select = await async_api_client.post(
            f"/calendars/{MOCK_CALENDAR_ID}/select", headers=headers
        )
        assert select.status_code == 200

        created = await async_api_client.post(
            "/drafts",
            headers=headers,
            json={
                "title": "Autosave event",
                "type": "event",
                "category_id": category_id,
                "summary": "wait",
            },
        )
        assert created.status_code == 201
        draft_id = created.json()["id"]

        await asyncio.sleep(1.2)

    row = postgres_connection.execute(
        text("SELECT status, google_event_id FROM events WHERE id = :id"),
        {"id": draft_id},
    ).one()
    assert row[0] == "auto_saved"
    assert row[1] == google_event_id


def test_google_create_soft_fail_keeps_local_board_visible(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
    category_id,
) -> None:
    google_event_id = "google-event-fail"
    mock_service = _mock_google_service(google_event_id=google_event_id)
    insert_request = mock_service.events.return_value.insert.return_value
    insert_request.execute.side_effect = HttpError(MagicMock(status=500), b"fail")

    headers = _connect_calendar(api_client, mock_jwks_keypair, owner_id_a, mock_service)
    draft_id = _create_event_draft(api_client, headers, category_id)

    with patch("app.services.calendar.build", return_value=mock_service):
        confirm = api_client.post(f"/drafts/{draft_id}/confirm", headers=headers)
    assert confirm.status_code == 200
    assert confirm.json()["status"] == "confirmed"

    row = postgres_connection.execute(
        text("SELECT status, google_event_id FROM events WHERE id = :id"),
        {"id": draft_id},
    ).one()
    assert row[0] == "confirmed"
    assert row[1] is None


def test_patch_items_event_etag_412_returns_concurrency_conflict(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
    category_id,
) -> None:
    google_event_id = f"google-event-{uuid4().hex[:12]}"
    mock_service = _mock_google_service(
        google_event_id=google_event_id,
        remote_etag=MOCK_ETAG_REMOTE,
    )
    headers = _connect_calendar(api_client, mock_jwks_keypair, owner_id_a, mock_service)
    draft_id = _create_event_draft(api_client, headers, category_id)

    with patch("app.services.calendar.build", return_value=mock_service):
        confirm = api_client.post(f"/drafts/{draft_id}/confirm", headers=headers)
        assert confirm.status_code == 200

        response = api_client.patch(
            f"/items/{draft_id}",
            headers=headers,
            json={"title": "Updated title"},
        )

    assert response.status_code == 412
    body = response.json()
    assert body["error"]["code"] == "CONCURRENCY_CONFLICT"
    assert body["error"]["details"]["etag"] == MOCK_ETAG_REMOTE
    assert "remote_state" in body["error"]["details"]
    serialized = str(body)
    assert "access_token" not in serialized
    assert "refresh_token" not in serialized


def test_patch_items_create_on_edit_when_no_google_event_id(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
    category_id,
) -> None:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    draft_id = _create_event_draft(api_client, headers, category_id)
    confirm = api_client.post(f"/drafts/{draft_id}/confirm", headers=headers)
    assert confirm.status_code == 200

    google_event_id = f"google-event-{uuid4().hex[:12]}"
    mock_service = _mock_google_service(google_event_id=google_event_id)
    connect_headers = _connect_calendar(api_client, mock_jwks_keypair, owner_id_a, mock_service)

    with patch("app.services.calendar.build", return_value=mock_service):
        response = api_client.patch(
            f"/items/{draft_id}",
            headers=connect_headers,
            json={"title": "Edited title"},
        )
    assert response.status_code == 200

    row = postgres_connection.execute(
        text("SELECT google_event_id, title FROM events WHERE id = :id"),
        {"id": draft_id},
    ).one()
    assert row[0] == google_event_id
    assert row[1] == "Edited title"


def test_delete_item_with_google_event_id_calls_events_delete(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
    category_id,
) -> None:
    google_event_id = f"google-event-{uuid4().hex[:12]}"
    mock_service = _mock_google_service(google_event_id=google_event_id)
    headers = _connect_calendar(api_client, mock_jwks_keypair, owner_id_a, mock_service)
    draft_id = _create_event_draft(api_client, headers, category_id)

    with patch("app.services.calendar.build", return_value=mock_service):
        confirm = api_client.post(f"/drafts/{draft_id}/confirm", headers=headers)
        assert confirm.status_code == 200
        insert_count = mock_service.events.return_value.insert.call_count

        delete = api_client.delete(f"/items/{draft_id}", headers=headers)
        assert delete.status_code == 204
        mock_service.events.return_value.delete.assert_called()

        restore = api_client.post(f"/items/{draft_id}/restore", headers=headers)
        assert restore.status_code == 200
        assert mock_service.events.return_value.insert.call_count == insert_count
