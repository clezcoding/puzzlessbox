"""Link scrape integration tests (LINK-01, LINK-02, T-01-ssrf)."""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from sqlalchemy import text

from app.core.config import get_settings
from tests.conftest import API_HEADERS, mint_test_jwt

SAMPLE_HTML = """
<html><head>
<meta property="og:title" content="Example Domain" />
<meta property="og:description" content="Illustrative text" />
<meta property="og:image" content="https://example.com/image.png" />
</head><body></body></html>
"""

CAMOUFOX_HTML = """
<html><head>
<meta property="og:title" content="Camoufox Title" />
</head><body></body></html>
"""


@pytest.fixture
def links_category_id(postgres_connection) -> str:
    row = postgres_connection.execute(
        text("SELECT id FROM categories WHERE name = 'Links' LIMIT 1")
    ).one()
    return str(row[0])


def _dual_scraper_mock(
    *,
    firecrawl_status: int = 200,
    firecrawl_html: str | None = SAMPLE_HTML,
    camoufox_status: int = 200,
    camoufox_html: str | None = None,
    firecrawl_delay: float = 0.0,
    camoufox_delay: float = 0.0,
) -> AsyncMock:
    client = AsyncMock()

    async def post(url: str, **kwargs: object) -> httpx.Response:
        if firecrawl_delay:
            time.sleep(firecrawl_delay)
        if url.endswith("/v1/scrape"):
            if firecrawl_status >= 400 or firecrawl_html is None:
                return httpx.Response(firecrawl_status, json={"success": False})
            return httpx.Response(
                200,
                json={"success": True, "data": {"html": firecrawl_html}},
            )
        return httpx.Response(404)

    async def get(url: str, **kwargs: object) -> httpx.Response:
        if "/health" in url:
            if firecrawl_status >= 400:
                return httpx.Response(firecrawl_status, json={"status": "error"})
            return httpx.Response(200, json={"status": "ok"})
        if kwargs.get("params"):
            if camoufox_delay:
                time.sleep(camoufox_delay)
            if camoufox_status >= 400 or camoufox_html is None:
                return httpx.Response(camoufox_status, text="")
            return httpx.Response(200, text=camoufox_html)
        return httpx.Response(404)

    client.post = AsyncMock(side_effect=post)
    client.get = AsyncMock(side_effect=get)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    return client


def _firecrawl_mock(html: str = SAMPLE_HTML) -> AsyncMock:
    return _dual_scraper_mock(firecrawl_html=html)


def test_scrape(
    api_client,
    postgres_connection,
    links_category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    mock_client = _firecrawl_mock()

    with patch("app.services.scraper.httpx.AsyncClient", return_value=mock_client):
        response = api_client.post(
            "/links",
            headers=headers,
            json={"url": "https://example.com"},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Example Domain"
    assert body["scrape_status"] == "ok"
    assert body["category_id"] == links_category_id
    assert body["metadata"]["title"] == "Example Domain"
    assert body["metadata"]["url"] == "https://example.com/"
    assert body["metadata"]["description"] == "Illustrative text"
    assert body["metadata"]["image"] == "https://example.com/image.png"

    row = postgres_connection.execute(
        text(
            """
            SELECT title, scrape_status, category_id, metadata
            FROM links
            WHERE id = :id
            """
        ),
        {"id": body["id"]},
    ).mappings().one()
    assert row["title"] == "Example Domain"
    assert row["scrape_status"] == "ok"
    assert str(row["category_id"]) == links_category_id


def test_camoufox_fallback(
    api_client,
    links_category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    mock_client = _dual_scraper_mock(
        firecrawl_status=500,
        firecrawl_html=None,
        camoufox_html=CAMOUFOX_HTML,
    )

    with patch("app.services.scraper.httpx.AsyncClient", return_value=mock_client):
        response = api_client.post(
            "/links",
            headers=headers,
            json={"url": "https://example.com/camoufox"},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Camoufox Title"
    assert body["scrape_status"] == "ok"
    assert body["category_id"] == links_category_id


def test_scrape_fail_fallback(
    api_client,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    mock_client = _dual_scraper_mock(
        firecrawl_status=500,
        firecrawl_html=None,
        camoufox_status=500,
        camoufox_html=None,
    )

    with patch("app.services.scraper.httpx.AsyncClient", return_value=mock_client):
        response = api_client.post(
            "/links",
            headers=headers,
            json={"url": "https://example.com"},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "example.com"
    assert body["scrape_status"] == "failed"
    assert body["metadata"]["description"] is None
    assert body["metadata"]["image"] is None


def test_default_cat(
    api_client,
    links_category_id,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    mock_client = _dual_scraper_mock(
        firecrawl_status=500,
        firecrawl_html=None,
        camoufox_status=500,
        camoufox_html=None,
    )

    with patch("app.services.scraper.httpx.AsyncClient", return_value=mock_client):
        response = api_client.post(
            "/links",
            headers=headers,
            json={"url": "https://example.com"},
        )

    assert response.status_code == 201
    assert response.json()["category_id"] == links_category_id


def test_12s_budget(
    api_client,
    mock_jwks_keypair,
    owner_id_a,
) -> None:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    mock_client = _dual_scraper_mock(
        firecrawl_status=500,
        firecrawl_html=None,
        camoufox_status=500,
        camoufox_html=None,
        firecrawl_delay=0.05,
        camoufox_delay=0.05,
    )

    started = time.monotonic()
    with patch("app.services.scraper.httpx.AsyncClient", return_value=mock_client):
        response = api_client.post(
            "/links",
            headers=headers,
            json={"url": "https://example.com/slow"},
        )
    elapsed = time.monotonic() - started

    assert response.status_code == 201
    assert elapsed < 12.0


def test_ready_scraper_ping(api_client, monkeypatch) -> None:
    monkeypatch.setenv("SCRAPER_ENABLED", "true")
    get_settings.cache_clear()

    healthy = _dual_scraper_mock()

    with patch("app.routers.health.check_db_connection", return_value=True):
        with patch("app.services.scraper.httpx.AsyncClient", return_value=healthy):
            ok = api_client.get("/ready", headers=API_HEADERS)
    assert ok.status_code == 200

    unhealthy = _dual_scraper_mock(firecrawl_status=503, firecrawl_html=None)

    with patch("app.routers.health.check_db_connection", return_value=True):
        with patch("app.services.scraper.httpx.AsyncClient", return_value=unhealthy):
            down = api_client.get("/ready", headers=API_HEADERS)

    get_settings.cache_clear()
    assert down.status_code == 503
    assert down.json()["error"]["code"] == "SCRAPER_UNHEALTHY"
    assert down.json()["error"]["details"]["service"] == "firecrawl"


@pytest.mark.parametrize(
    "blocked_url",
    [
        "http://127.0.0.1",
        "http://169.254.169.254",
    ],
)
def test_ssrf_blocked(
    api_client,
    mock_jwks_keypair,
    owner_id_a,
    blocked_url: str,
) -> None:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}

    response = api_client.post(
        "/links",
        headers=headers,
        json={"url": blocked_url},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "SSRF_BLOCKED"
