"""Auth unit tests (AUTH-02, D-23)."""

from __future__ import annotations

import hashlib
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from sqlalchemy import text

from app.auth.jwt import get_current_owner
from app.core.config import get_settings
from tests.conftest import mint_test_jwt


@pytest.mark.asyncio
async def test_jwt_decode(mock_jwks_keypair, owner_id_a) -> None:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)

    class _TestPyJWKClient:
        def get_signing_key_from_jwt(self, _token: str):
            from cryptography.hazmat.primitives import serialization

            private_key = serialization.load_pem_private_key(
                mock_jwks_keypair["private_key"],
                password=None,
            )
            return type("SigningKey", (), {"key": private_key.public_key()})()

    class _FakeRequest:
        cookies: dict[str, str] = {}
        headers: dict[str, str] = {}

    with patch("app.auth.jwt.get_jwks_client", return_value=_TestPyJWKClient()):
        owner_id = await get_current_owner(
            _FakeRequest(),
            credentials=type("Creds", (), {"credentials": token})(),
        )
    assert owner_id == owner_id_a


@pytest.mark.asyncio
async def test_jwt_decode_expired(mock_jwks_keypair, owner_id_a) -> None:
    token = mint_test_jwt(
        mock_jwks_keypair["private_key"],
        owner_id_a,
        expired=True,
    )

    class _TestPyJWKClient:
        def get_signing_key_from_jwt(self, _token: str):
            from cryptography.hazmat.primitives import serialization

            private_key = serialization.load_pem_private_key(
                mock_jwks_keypair["private_key"],
                password=None,
            )
            return type("SigningKey", (), {"key": private_key.public_key()})()

    class _FakeRequest:
        cookies: dict[str, str] = {}
        headers: dict[str, str] = {}

    with patch("app.auth.jwt.get_jwks_client", return_value=_TestPyJWKClient()):
        with pytest.raises(HTTPException) as exc:
            await get_current_owner(
                _FakeRequest(),
                credentials=type("Creds", (), {"credentials": token})(),
            )
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_service_bearer(postgres_connection, owner_id_a) -> None:
    settings = get_settings()
    bearer_hash = hashlib.sha256(settings.SERVICE_BEARER_TOKEN.encode()).hexdigest()
    postgres_connection.execute(
        text(
            """
            INSERT INTO service_principals (owner_id, name, bearer_hash)
            VALUES (:owner_id, 'mcp', :bearer_hash)
            ON CONFLICT (owner_id) DO UPDATE SET bearer_hash = EXCLUDED.bearer_hash
            """
        ),
        {"owner_id": owner_id_a, "bearer_hash": bearer_hash},
    )
    postgres_connection.commit()

    class _FakeRequest:
        cookies: dict[str, str] = {}
        headers: dict[str, str] = {"X-Service-Bearer": settings.SERVICE_BEARER_TOKEN}

    owner_id = await get_current_owner(_FakeRequest(), credentials=None)
    assert owner_id == owner_id_a
