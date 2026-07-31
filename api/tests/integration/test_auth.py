"""Auth integration tests (AUTH-01, AUTH-03, D-22)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.auth.jwt import SESSION_COOKIE
from tests.conftest import API_HEADERS, mint_test_jwt


def _mock_better_auth_client(
    jwt_token: str,
    owner_id: str,
    *,
    signup_status: int = 200,
    signup_body: dict | None = None,
):
    client = AsyncMock()

    async def post(url: str, **kwargs: object) -> httpx.Response:
        if url == "/sign-up/email":
            if signup_body is not None:
                return httpx.Response(signup_status, json=signup_body)
            return httpx.Response(
                signup_status,
                json={
                    "token": jwt_token,
                    "user": {"id": owner_id, "email": "owner@example.com", "name": "Owner"},
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


def test_registration(api_client, mock_jwks_keypair, owner_id_a) -> None:
    jwt_token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    mock_client = _mock_better_auth_client(jwt_token, owner_id_a)

    with patch("app.routers.auth.httpx.AsyncClient", return_value=mock_client):
        response = api_client.post(
            "/auth/signup",
            headers=API_HEADERS,
            json={"email": "owner@example.com", "password": "securepass"},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["id"] == owner_id_a
    mock_client.post.assert_called_once()


def test_signup_lock(api_client, mock_jwks_keypair, owner_id_a) -> None:
    jwt_token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    mock_client = _mock_better_auth_client(
        jwt_token,
        owner_id_a,
        signup_status=409,
        signup_body={"message": "SIGNUP_LOCKED"},
    )

    with patch("app.routers.auth.httpx.AsyncClient", return_value=mock_client):
        response = api_client.post(
            "/auth/signup",
            headers=API_HEADERS,
            json={"email": "second@example.com", "password": "securepass"},
        )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "SIGNUP_LOCKED"


def test_login_persists_session(api_client, mock_jwks_keypair, owner_id_a) -> None:
    jwt_token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    mock_client = _mock_better_auth_client(jwt_token, owner_id_a)

    with patch("app.routers.auth.httpx.AsyncClient", return_value=mock_client):
        response = api_client.post(
            "/auth/login",
            headers=API_HEADERS,
            json={"email": "owner@example.com", "password": "securepass"},
        )

    assert response.status_code == 200
    assert response.json()["token"] == jwt_token
    cookie_header = response.headers.get("set-cookie", "")
    assert SESSION_COOKIE in cookie_header
    assert "domain=.puzzlesstool.online" in cookie_header.lower()
    assert "httponly" in cookie_header.lower()


def test_cookie_session_replays_on_verify(api_client, mock_jwks_keypair, owner_id_a) -> None:
    """AUTH-02: session cookie alone authenticates follow-up request (no Authorization)."""
    jwt_token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    mock_client = _mock_better_auth_client(jwt_token, owner_id_a)

    with patch("app.routers.auth.httpx.AsyncClient", return_value=mock_client):
        login = api_client.post(
            "/auth/login",
            headers=API_HEADERS,
            json={"email": "owner@example.com", "password": "securepass"},
        )
    assert login.status_code == 200

    # Domain=.puzzlesstool.online is not jarred for TestClient host — set cookie on client.
    api_client.cookies.set(SESSION_COOKIE, jwt_token)
    verify = api_client.get("/auth/verify", headers=API_HEADERS)  # Accept only; no Authorization
    assert verify.status_code == 200
    assert verify.json()["owner_id"] == owner_id_a
    assert "Authorization" not in verify.request.headers
