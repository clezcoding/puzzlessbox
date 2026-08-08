"""Wave 0 stubs: calendar sync wiring contracts (CAL-02, CAL-03, D-09–D-16).

Implemented in plan 05.2-03. Each test is xfail until capture→Google wiring lands.
"""

from __future__ import annotations

import pytest

from tests.integration.test_calendar import (
    MOCK_ETAG,
    _auth_headers,
    _mock_google_service,
)

WAVE0 = "05.2 Wave 0 stub — implemented in plan 03"


@pytest.mark.xfail(strict=False, reason=WAVE0)
def test_confirm_draft_event_syncs_existing_row_google_event_id(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """Confirming event draft calls Google events.insert on existing local row; sets google_event_id (CAL-02, D-09)."""
    _ = _mock_google_service(google_event_id="google-event-stub")
    pytest.fail("Wave 0 stub")


@pytest.mark.xfail(strict=False, reason=WAVE0)
def test_autosave_event_syncs_when_google_connected(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """Auto-save transition to board-visible syncs to Google when calendar connected (D-09)."""
    _ = _auth_headers(mock_jwks_keypair, owner_id_a)
    pytest.fail("Wave 0 stub")


@pytest.mark.xfail(strict=False, reason=WAVE0)
def test_google_create_soft_fail_keeps_local_board_visible(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """Google API error on create still commits local auto_saved/confirmed; google_event_id stays null (D-11)."""
    pytest.fail("Wave 0 stub")


@pytest.mark.xfail(strict=False, reason=WAVE0)
def test_patch_items_event_etag_412_returns_concurrency_conflict(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """PATCH event with stale etag returns 412 CONCURRENCY_CONFLICT with remote state (CAL-03, D-14)."""
    _ = MOCK_ETAG
    pytest.fail("Wave 0 stub")


@pytest.mark.xfail(strict=False, reason=WAVE0)
def test_patch_items_create_on_edit_when_no_google_event_id(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """PATCH event without google_event_id creates Google event when connected (D-15)."""
    pytest.fail("Wave 0 stub")


@pytest.mark.xfail(strict=False, reason=WAVE0)
def test_delete_item_with_google_event_id_calls_events_delete(
    api_client,
    postgres_connection,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """Soft-delete event with google_event_id calls Google events.delete (D-16)."""
    pytest.fail("Wave 0 stub")
