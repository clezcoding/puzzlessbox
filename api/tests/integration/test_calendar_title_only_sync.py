"""Title-only Google Calendar sync — derive 1h window (CAL-EDGE, D-01)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy import text

from app.services.calendar import _normalize_times
from tests.conftest import API_HEADERS
from tests.integration.test_calendar import (
    MOCK_CALENDAR_ID,
    _auth_headers,
    _mock_credentials,
    _mock_google_service,
)
from tests.integration.test_calendar_sync_wiring import (
    _connect_calendar,
    _create_event_draft,
)


def test_normalize_times_null_null_derives_one_hour_window() -> None:
    before = datetime.now(timezone.utc)
    start, end = _normalize_times(None, None)
    after = datetime.now(timezone.utc)
    assert start.tzinfo is not None
    assert end.tzinfo is not None
    assert before <= start <= after
    assert end - start == timedelta(hours=1)


def test_normalize_times_null_start_derives_start_from_end() -> None:
    end = datetime(2026, 8, 1, 11, 0, tzinfo=timezone.utc)
    start, normalized_end = _normalize_times(None, end)
    assert start == end - timedelta(hours=1)
    assert normalized_end == end


def test_normalize_times_null_end_derives_end_from_start() -> None:
    start = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)
    normalized_start, end = _normalize_times(start, None)
    assert normalized_start == start
    assert end == start + timedelta(hours=1)


def test_normalize_times_both_provided_passthrough() -> None:
    start = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)
    end = datetime(2026, 8, 1, 11, 30, tzinfo=timezone.utc)
    assert _normalize_times(start, end) == (start, end)


def test_sync_title_only_confirm_derives_persists_and_inserts_datetimes(
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

    before = postgres_connection.execute(
        text("SELECT starts_at, ends_at FROM events WHERE id = :id"),
        {"id": draft_id},
    ).one()
    assert before[0] is None
    assert before[1] is None

    with patch("app.services.calendar.build", return_value=mock_service):
        confirm = api_client.post(f"/drafts/{draft_id}/confirm", headers=headers)
    assert confirm.status_code == 200

    insert_call = mock_service.events.return_value.insert.call_args
    body = insert_call.kwargs["body"]
    assert "dateTime" in body["start"]
    assert "dateTime" in body["end"]
    assert "date" not in body["start"]
    assert "date" not in body["end"]

    row = postgres_connection.execute(
        text("SELECT starts_at, ends_at, google_event_id FROM events WHERE id = :id"),
        {"id": draft_id},
    ).one()
    assert row[0] is not None
    assert row[1] is not None
    assert row[1] - row[0] == timedelta(hours=1)
    assert row[2] == google_event_id


def test_create_event_title_only_normalizes_via_api(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    google_event_id = f"google-event-{uuid4().hex[:12]}"
    mock_service = _mock_google_service(google_event_id=google_event_id)
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

        create = api_client.post(
            "/events",
            headers=headers,
            json={"title": "Title only", "summary": "notes"},
        )

    assert create.status_code == 201
    payload = create.json()
    assert payload["starts_at"] is not None
    assert payload["ends_at"] is not None

    insert_body = mock_service.events.return_value.insert.call_args.kwargs["body"]
    assert "dateTime" in insert_body["start"]
    assert "dateTime" in insert_body["end"]


def test_sync_idempotent_when_google_event_id_already_set(
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

        row = postgres_connection.execute(
            text("SELECT starts_at, google_event_id FROM events WHERE id = :id"),
            {"id": draft_id},
        ).one()
        persisted_start = row[0]
        assert row[1] == google_event_id

        confirm_again = api_client.post(f"/drafts/{draft_id}/confirm", headers=headers)
        assert confirm_again.status_code == 404

    unchanged = postgres_connection.execute(
        text("SELECT starts_at FROM events WHERE id = :id"),
        {"id": draft_id},
    ).scalar_one()
    assert unchanged == persisted_start
    assert mock_service.events.return_value.insert.call_count == insert_count
