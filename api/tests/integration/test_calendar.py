"""Google Calendar integration tests (CAL-02, CAL-03, D-17, D-21)."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse
from uuid import uuid4

from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from sqlalchemy import text

from app.core.security import decrypt_token, encrypt_token
from tests.conftest import API_HEADERS, mint_test_jwt

MOCK_ACCESS = "ya29.mock-access-token"
MOCK_REFRESH = "1//mock-refresh-token"
MOCK_CALENDAR_ID = "primary"
MOCK_GOOGLE_EVENT_ID = "google-event-123"
MOCK_ETAG = '"etag-v1"'
MOCK_ETAG_STALE = '"etag-stale"'
MOCK_ETAG_REMOTE = '"etag-v2"'


def _mock_credentials() -> Credentials:
    return Credentials(
        token=MOCK_ACCESS,
        refresh_token=MOCK_REFRESH,
        token_uri="https://oauth2.googleapis.com/token",
        client_id="test-client",
        client_secret="test-secret",
        scopes=["https://www.googleapis.com/auth/calendar"],
    )


def _mock_google_service(
    *,
    google_event_id: str,
    remote_etag: str = MOCK_ETAG,
    update_raises_412: bool = False,
) -> MagicMock:
    service = MagicMock()
    calendar_list = service.calendarList.return_value.list.return_value
    calendar_list.execute.return_value = {
        "items": [{"id": MOCK_CALENDAR_ID, "summary": "Primary", "primary": True}]
    }

    created_event = {
        "id": google_event_id,
        "etag": MOCK_ETAG,
        "summary": "Team sync",
    }
    insert_request = service.events.return_value.insert.return_value
    insert_request.execute.return_value = created_event

    remote_event = {
        "id": google_event_id,
        "etag": remote_etag,
        "summary": "Team sync",
        "description": "notes",
    }
    get_request = service.events.return_value.get.return_value
    get_request.execute.return_value = remote_event

    updated_event = {**remote_event, "etag": '"etag-v3"', "summary": "Updated title"}
    update_request = service.events.return_value.update.return_value
    if update_raises_412:
        response = MagicMock()
        response.status = 412
        update_request.execute.side_effect = HttpError(response, b"Precondition Failed")
    else:
        update_request.execute.return_value = updated_event

    return service


def _auth_headers(mock_jwks_keypair, owner_id_a: str) -> dict[str, str]:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    return {**API_HEADERS, "Authorization": f"Bearer {token}"}


def _run_sync_flow(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a: str,
) -> tuple[str, str]:
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    google_event_id = f"google-event-{uuid4().hex[:12]}"
    mock_flow = MagicMock()
    mock_flow.authorization_url.return_value = ("https://accounts.google.com/o/oauth2/auth?mock=1", "state")
    mock_flow.credentials = _mock_credentials()

    with (
        patch("app.services.calendar.Flow.from_client_config", return_value=mock_flow),
        patch("app.services.calendar.build", return_value=_mock_google_service(google_event_id=google_event_id)),
        patch("app.services.calendar.make_oauth_state", return_value="signed-state"),
        patch("app.services.calendar.verify_oauth_state", return_value=owner_id_a),
    ):
        connect = api_client.get("/auth/google/connect", headers=headers, follow_redirects=False)
        assert connect.status_code == 200
        auth_url = connect.json()["authorization_url"]
        location_host = urlparse(auth_url).hostname
        assert location_host == "accounts.google.com"

        callback = api_client.get(
            "/auth/google/callback",
            params={"code": "mock-code", "state": "signed-state"},
            headers=API_HEADERS,
            follow_redirects=False,
        )
        assert callback.status_code == 302
        assert "/settings" in callback.headers["location"]

        row = postgres_connection.execute(
            text(
                "SELECT encrypted_access, encrypted_refresh FROM calendar_tokens WHERE owner_id = :owner"
            ),
            {"owner": owner_id_a},
        ).one()
        assert row[0] != MOCK_ACCESS
        assert row[1] != MOCK_REFRESH
        assert decrypt_token(row[0]) == MOCK_ACCESS
        assert decrypt_token(row[1]) == MOCK_REFRESH

        calendars = api_client.get("/calendars", headers=headers)
        assert calendars.status_code == 200
        assert calendars.json()["data"][0]["id"] == MOCK_CALENDAR_ID

        select = api_client.post(f"/calendars/{MOCK_CALENDAR_ID}/select", headers=headers)
        assert select.status_code == 200

        starts = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)
        ends = datetime(2026, 8, 1, 11, 0, tzinfo=timezone.utc)
        create = api_client.post(
            "/events",
            headers=headers,
            json={
                "title": "Team sync",
                "summary": "notes",
                "starts_at": starts.isoformat(),
                "ends_at": ends.isoformat(),
            },
        )
        assert create.status_code == 201
        body = create.json()
        assert body["google_event_id"] == google_event_id
        assert body["etag"] == MOCK_ETAG

        listed = api_client.get("/events", headers=headers)
        assert listed.status_code == 200
        assert any(item["id"] == body["id"] for item in listed.json()["data"])
        return body["id"], google_event_id


def test_sync(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    event_id, google_event_id = _run_sync_flow(
        api_client, postgres_connection, mock_jwks_keypair, owner_id_a
    )
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    listed = api_client.get("/events", headers=headers)
    match = next(item for item in listed.json()["data"] if item["id"] == event_id)
    assert match["google_event_id"] == google_event_id
    assert match["etag"] == MOCK_ETAG


def test_patch_matching_etag(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    event_id, google_event_id = _run_sync_flow(
        api_client, postgres_connection, mock_jwks_keypair, owner_id_a
    )
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)

    with patch(
        "app.services.calendar.build",
        return_value=_mock_google_service(google_event_id=google_event_id),
    ):
        response = api_client.patch(
            f"/events/{event_id}",
            headers=headers,
            json={"etag": MOCK_ETAG, "title": "Updated title"},
        )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"
    assert response.json()["etag"] == '"etag-v3"'


def test_conflict(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    event_id, google_event_id = _run_sync_flow(
        api_client, postgres_connection, mock_jwks_keypair, owner_id_a
    )
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)

    with patch(
        "app.services.calendar.build",
        return_value=_mock_google_service(
            google_event_id=google_event_id,
            remote_etag=MOCK_ETAG_REMOTE,
        ),
    ):
        response = api_client.patch(
            f"/events/{event_id}",
            headers=headers,
            json={"etag": MOCK_ETAG_STALE, "title": "Should fail"},
        )

    assert response.status_code == 412
    error = response.json()["error"]
    assert error["code"] == "CONCURRENCY_CONFLICT"
    assert error["details"]["etag"] == MOCK_ETAG_REMOTE
    assert error["details"]["remote_state"]["id"] == google_event_id


def test_pull_before_write(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    event_id, google_event_id = _run_sync_flow(
        api_client, postgres_connection, mock_jwks_keypair, owner_id_a
    )
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    service = _mock_google_service(google_event_id=google_event_id)

    with patch("app.services.calendar.build", return_value=service):
        api_client.patch(
            f"/events/{event_id}",
            headers=headers,
            json={"etag": MOCK_ETAG, "title": "Pulled then updated"},
        )

    service.events.return_value.get.return_value.execute.assert_called()


def test_no_silent_overwrite(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    event_id, google_event_id = _run_sync_flow(
        api_client, postgres_connection, mock_jwks_keypair, owner_id_a
    )
    headers = _auth_headers(mock_jwks_keypair, owner_id_a)
    service = _mock_google_service(google_event_id=google_event_id, update_raises_412=True)

    with patch("app.services.calendar.build", return_value=service):
        response = api_client.patch(
            f"/events/{event_id}",
            headers=headers,
            json={"etag": MOCK_ETAG, "title": "Race loser"},
        )

    assert response.status_code == 412
    assert response.json()["error"]["code"] == "CONCURRENCY_CONFLICT"
    service.events.return_value.update.return_value.headers.__setitem__.assert_called_with(
        "If-Match", MOCK_ETAG
    )
