"""Async link scrape integration tests (LINK-01, LINK-02, D-01, D-03, D-19, D-26)."""

from __future__ import annotations

import asyncio
import time
from unittest.mock import patch

import httpx
import pytest
from sqlalchemy import text

from app.services.scraper import ScrapeResult, scrape_service
from app.services.link_scrape import scrape_manager

from tests.conftest import API_HEADERS, mint_test_jwt
from tests.integration.test_scraper import _dual_scraper_mock

WAVE0 = "05.2 Wave 0 stub — implemented in plan 01/02"


@pytest.fixture
def links_category_id(postgres_connection) -> str:
    row = postgres_connection.execute(
        text("SELECT id FROM categories WHERE name = 'Links' LIMIT 1")
    ).one()
    return str(row[0])


def _link_row(postgres_connection, link_id: str) -> dict:
    row = postgres_connection.execute(
        text(
            """
            SELECT title, metadata, scrape_status, category_id
            FROM links WHERE id = :id
            """
        ),
        {"id": link_id},
    ).mappings().one()
    return dict(row)


async def _poll_scrape_terminal(postgres_connection, link_id: str, timeout: float = 5.0) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        row = _link_row(postgres_connection, link_id)
        if row["scrape_status"] in ("ok", "partial", "failed", "timed_out"):
            return row
        await asyncio.sleep(0.05)
    return _link_row(postgres_connection, link_id)


@pytest.mark.asyncio
async def test_draft_link_returns_immediately_without_awaiting_scrape(
    async_api_client,
    postgres_connection,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """POST /drafts type=link must return {id, type} immediately without waiting on scrape (D-03)."""
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}

    async def slow_scrape(url: str) -> ScrapeResult:
        await asyncio.sleep(1.5)
        return ScrapeResult(
            title="Delayed",
            description=None,
            image="https://example.com/image.png",
            scrape_status="ok",
        )

    start = time.monotonic()
    with patch.object(scrape_service, "scrape", side_effect=slow_scrape):
        response = await async_api_client.post(
            "/drafts",
            headers=headers,
            json={
                "title": "https://example.com/page",
                "type": "link",
                "category_id": category_id,
                "summary": "https://example.com/page",
            },
        )
    elapsed = time.monotonic() - start

    assert response.status_code == 201
    body = response.json()
    assert set(body.keys()) == {"id", "type"}
    assert body["type"] == "link"
    assert elapsed < 1.0


@pytest.mark.asyncio
async def test_async_scrape_writes_metadata_and_scrape_status(
    async_api_client,
    postgres_connection,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """Background scrape persists metadata title/description/image and scrape_status on link row (LINK-01, D-01)."""
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    url = "https://example.com/page"
    mock_client = _dual_scraper_mock()

    with patch("app.services.scraper.httpx.AsyncClient", return_value=mock_client):
        created = await async_api_client.post(
            "/drafts",
            headers=headers,
            json={
                "title": url,
                "type": "link",
                "category_id": category_id,
                "summary": url,
            },
        )
    assert created.status_code == 201
    draft_id = created.json()["id"]

    row = await _poll_scrape_terminal(postgres_connection, draft_id)
    assert row["scrape_status"] in ("ok", "partial")
    metadata = row["metadata"]
    assert metadata["title"] == "Example Domain"
    assert metadata["image"] == "https://example.com/image.png"

    confirmed = await async_api_client.post(f"/drafts/{draft_id}/confirm", headers=headers)
    assert confirmed.status_code == 200

    listed = (await async_api_client.get("/board-items", headers=headers)).json()
    match = next(item for item in listed if item["id"] == draft_id)
    assert match["summary"] == url
    assert match["image"] == "https://example.com/image.png"


@pytest.mark.asyncio
async def test_async_scrape_fail_or_timeout_sets_hostname_and_links_category(
    async_api_client,
    postgres_connection,
    category_id,
    links_category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """Failed scrape sets hostname fallback title and Links category (D-02 → Phase 1 D-11)."""
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    url = "https://example.com/fail-page"
    mock_client = _dual_scraper_mock(firecrawl_html=None, camoufox_html=None)

    with patch("app.services.scraper.httpx.AsyncClient", return_value=mock_client):
        created = await async_api_client.post(
            "/drafts",
            headers=headers,
            json={
                "title": url,
                "type": "link",
                "category_id": category_id,
                "summary": url,
            },
        )
    assert created.status_code == 201
    draft_id = created.json()["id"]

    row = await _poll_scrape_terminal(postgres_connection, draft_id)
    assert row["scrape_status"] == "failed"
    assert row["title"] == "example.com"
    assert str(row["category_id"]) == links_category_id


@pytest.mark.asyncio
async def test_schedule_scrape_cancels_prior_inflight_for_same_link_id(
    async_api_client,
    postgres_connection,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """Only one in-flight scrape per link_id; duplicate schedule cancels prior task (D-19)."""
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    url = "https://example.com/cancel-test"

    async def slow_scrape(scrape_url: str) -> ScrapeResult:
        await asyncio.sleep(5.0)
        return ScrapeResult(
            title="Slow",
            description=None,
            image=None,
            scrape_status="ok",
        )

    with patch.object(scrape_service, "scrape", side_effect=slow_scrape):
        created = await async_api_client.post(
            "/drafts",
            headers=headers,
            json={
                "title": url,
                "type": "link",
                "category_id": category_id,
                "summary": url,
            },
        )
        assert created.status_code == 201
        link_id = created.json()["id"]

        first_task = scrape_manager._active_tasks.get(link_id)
        assert first_task is not None

        scrape_manager.schedule_scrape(link_id, owner_id_a, url)
        await asyncio.sleep(0.05)
        second_task = scrape_manager._active_tasks.get(link_id)
        assert second_task is not None
        assert second_task is not first_task
        assert first_task.cancelled() or first_task.done()
        assert len(scrape_manager._active_tasks) == 1


@pytest.mark.asyncio
async def test_scrape_job_retries_transient_failure_twice(
    async_api_client,
    postgres_connection,
    category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    """Transient scrape failures auto-retry exactly twice before terminal failed/timed_out status (D-26)."""
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    url = "https://example.com/retry-test"
    attempts = 0

    async def flaky_scrape(scrape_url: str) -> ScrapeResult:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ConnectionError("transient")
        return ScrapeResult(
            title="Recovered",
            description=None,
            image="https://example.com/og.png",
            scrape_status="ok",
        )

    with patch.object(scrape_service, "scrape", side_effect=flaky_scrape):
        created = await async_api_client.post(
            "/drafts",
            headers=headers,
            json={
                "title": url,
                "type": "link",
                "category_id": category_id,
                "summary": url,
            },
        )
        assert created.status_code == 201
        link_id = created.json()["id"]

        row = await _poll_scrape_terminal(postgres_connection, link_id, timeout=15.0)
    assert attempts == 3
    assert row["scrape_status"] in ("ok", "partial", "failed", "timed_out")


@pytest.mark.asyncio
async def test_rescrape_endpoint_schedules_scrape_for_owner_link(
    async_api_client,
    postgres_connection,
    category_id,
    links_category_id,
    mock_jwks_keypair,
    owner_id_a,
    owner_id_b,
) -> None:
    """POST /links/{id}/rescrape schedules scrape for owner; foreign owner gets 404 (D-26)."""
    token_a = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    token_b = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_b)
    headers_a = {**API_HEADERS, "Authorization": f"Bearer {token_a}"}
    headers_b = {**API_HEADERS, "Authorization": f"Bearer {token_b}"}
    url = "https://example.com/rescrape-test"
    mock_client = _dual_scraper_mock(firecrawl_html=None, camoufox_html=None)

    with patch("app.services.scraper.httpx.AsyncClient", return_value=mock_client):
        created = await async_api_client.post(
            "/drafts",
            headers=headers_a,
            json={
                "title": url,
                "type": "link",
                "category_id": category_id,
                "summary": url,
            },
        )
    assert created.status_code == 201
    link_id = created.json()["id"]
    await _poll_scrape_terminal(postgres_connection, link_id)

    with patch.object(scrape_manager, "schedule_scrape") as schedule_mock:
        response = await async_api_client.post(
            f"/links/{link_id}/rescrape",
            headers=headers_a,
        )
    assert response.status_code == 202
    body = response.json()
    assert body["id"] == link_id
    assert body["scrape_status"] in ("pending", "scraping")
    schedule_mock.assert_called_once_with(link_id, owner_id_a, url)

    foreign = await async_api_client.post(
        f"/links/{link_id}/rescrape",
        headers=headers_b,
    )
    assert foreign.status_code == 404
