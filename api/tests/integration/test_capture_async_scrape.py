"""Wave 0 stubs: async link scrape contracts (LINK-01, LINK-02, D-01, D-03, D-19, D-26).

Implemented in plans 05.2-01/02. Each test is xfail until production wiring lands.
"""

from __future__ import annotations

import pytest

from tests.integration.test_scraper import _dual_scraper_mock

WAVE0 = "05.2 Wave 0 stub — implemented in plan 01/02"


@pytest.mark.xfail(strict=False, reason=WAVE0)
def test_draft_link_returns_immediately_without_awaiting_scrape(
    api_client,
    postgres_connection,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """POST /drafts type=link must return {id, type} immediately without waiting on scrape (D-03)."""
    pytest.fail("Wave 0 stub")


@pytest.mark.xfail(strict=False, reason=WAVE0)
def test_async_scrape_writes_metadata_and_scrape_status(
    api_client,
    postgres_connection,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """Background scrape persists metadata title/description/image and scrape_status on link row (LINK-01, D-01)."""
    _ = _dual_scraper_mock()
    pytest.fail("Wave 0 stub")


@pytest.mark.xfail(strict=False, reason=WAVE0)
def test_schedule_scrape_cancels_prior_inflight_for_same_link_id(
    api_client,
    postgres_connection,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """Only one in-flight scrape per link_id; duplicate schedule cancels prior task (D-19)."""
    pytest.fail("Wave 0 stub")


@pytest.mark.xfail(strict=False, reason=WAVE0)
def test_scrape_job_retries_transient_failure_twice(
    api_client,
    postgres_connection,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """Transient scrape failures auto-retry exactly twice before terminal failed/timed_out status (D-26)."""
    pytest.fail("Wave 0 stub")
