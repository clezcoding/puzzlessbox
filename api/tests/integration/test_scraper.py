"""Link scrape integration tests (LINK-01, LINK-02, T-01-ssrf)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from sqlalchemy import text

from tests.conftest import API_HEADERS, mint_test_jwt

SAMPLE_HTML = """
<html><head>
<meta property="og:title" content="Example Domain" />
<meta property="og:description" content="Illustrative text" />
<meta property="og:image" content="https://example.com/image.png" />
</head><body></body></html>
"""


@pytest.fixture
def links_category_id(postgres_connection) -> str:
    row = postgres_connection.execute(
        text("SELECT id FROM categories WHERE name = 'Links' LIMIT 1")
    ).one()
    return str(row[0])


def _firecrawl_mock(html: str = SAMPLE_HTML) -> AsyncMock:
    client = AsyncMock()

    async def post(url: str, **kwargs: object) -> httpx.Response:
        if url.endswith("/v1/scrape"):
            return httpx.Response(
                200,
                json={"success": True, "data": {"html": html}},
            )
        return httpx.Response(404)

    client.post = AsyncMock(side_effect=post)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    return client


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
