"""Wave 0 pytest fixtures: mock Postgres sessions, JWKS, tenant owner IDs."""

from __future__ import annotations

import base64
import os
import subprocess
import time
import uuid
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import patch

import httpx
import jwt as pyjwt
import pytest
from httpx import ASGITransport, AsyncClient
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import Connection, create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

from app.main import API_VERSION_ACCEPT, app
from app.models import Category, Event, Link, Note, ServicePrincipal, Task  # noqa: F401

API_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_URL = "postgresql+psycopg2://puzzless@localhost:5432/puzzlessbox"

# --- mock Postgres (transactional rollback per test) ---

_test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
_TestSessionLocal = sessionmaker(bind=_test_engine, class_=Session, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def _create_test_schema() -> Generator[None, None, None]:
    SQLModel.metadata.create_all(_test_engine)
    yield
    SQLModel.metadata.drop_all(_test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = _test_engine.connect()
    transaction = connection.begin()
    session = _TestSessionLocal(bind=connection)

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess: Session, trans: Any) -> None:
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    session.begin_nested()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def mock_db(db_session: Session) -> Generator[Session, None, None]:
    """Transactional sqlite session for unit tests that do not need Postgres RLS."""
    yield db_session


# --- real Postgres (RLS + migration integration tests) ---

_postgres_engine = None


def _postgres_database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


@pytest.fixture(scope="session")
def postgres_engine() -> Generator[Any, None, None]:
    global _postgres_engine
    url = _postgres_database_url()
    _postgres_engine = create_engine(url, pool_pre_ping=True)
    env = {**os.environ, "DATABASE_URL": url}
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=API_ROOT,
        env=env,
        check=True,
        capture_output=True,
    )
    yield _postgres_engine
    _postgres_engine.dispose()


@pytest.fixture
def postgres_connection(postgres_engine: Any) -> Generator[Connection, None, None]:
    connection = postgres_engine.connect()
    transaction = connection.begin()
    yield connection
    transaction.rollback()
    connection.close()


@pytest.fixture
def category_id(postgres_connection: Connection) -> str:
    row = postgres_connection.execute(
        text("SELECT id FROM categories WHERE name = 'Inbox' LIMIT 1")
    ).one()
    return str(row[0])


# --- mock JWKS (RS256 keypair for Plan 06 auth tests) ---

_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_public_key = _private_key.public_key()
_public_numbers = _public_key.public_numbers()


def _int_to_base64url(value: int) -> str:
    length = (value.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(value.to_bytes(length, "big")).decode("ascii").rstrip("=")


MOCK_JWKS: dict[str, Any] = {
    "keys": [
        {
            "kty": "RSA",
            "kid": "test-key-1",
            "use": "sig",
            "alg": "RS256",
            "n": _int_to_base64url(_public_numbers.n),
            "e": _int_to_base64url(_public_numbers.e),
        }
    ]
}


@pytest.fixture
def mock_jwks_keypair() -> dict[str, Any]:
    return {
        "private_key": _private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
        "public_jwks": MOCK_JWKS,
        "kid": "test-key-1",
    }


@pytest.fixture
def mock_jwks_client() -> Generator[httpx.Client, None, None]:
    """httpx client whose /jwks route serves the generated RS256 JWKS document."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/jwks"):
            return httpx.Response(200, json=MOCK_JWKS)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport, base_url="http://mock-auth.test") as client:
        yield client


# --- tenancy owner fixtures (Plan 05 RLS + Plan 06 cross-tenant) ---

@pytest.fixture
def owner_id_a() -> str:
    return str(uuid.UUID("11111111-1111-4111-8111-111111111111"))


@pytest.fixture
def owner_id_b() -> str:
    return str(uuid.UUID("22222222-2222-4222-8222-222222222222"))


API_HEADERS = {"Accept": API_VERSION_ACCEPT}


def mint_test_jwt(
    private_key_pem: bytes,
    owner_id: str,
    *,
    kid: str = "test-key-1",
    expired: bool = False,
) -> str:
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    exp = int(time.time()) - 60 if expired else int(time.time()) + 3600
    return pyjwt.encode(
        {"sub": owner_id, "exp": exp},
        private_key,
        algorithm="RS256",
        headers={"kid": kid},
    )


@pytest.fixture
def api_client(mock_jwks_keypair: dict[str, Any]) -> Generator[TestClient, None, None]:
    """FastAPI client with JWKS verification patched to the generated test keypair."""

    class _TestPyJWKClient:
        def get_signing_key_from_jwt(self, token: str) -> Any:
            private_key = serialization.load_pem_private_key(
                mock_jwks_keypair["private_key"],
                password=None,
            )
            public_key = private_key.public_key()
            return type("SigningKey", (), {"key": public_key})()

    with patch("app.auth.jwt.get_jwks_client", return_value=_TestPyJWKClient()):
        yield TestClient(app)


@pytest.fixture
async def async_api_client(mock_jwks_keypair: dict[str, Any]) -> AsyncClient:
    """Async HTTP client sharing the ASGI event loop (background asyncio tasks)."""

    class _TestPyJWKClient:
        def get_signing_key_from_jwt(self, token: str) -> Any:
            private_key = serialization.load_pem_private_key(
                mock_jwks_keypair["private_key"],
                password=None,
            )
            public_key = private_key.public_key()
            return type("SigningKey", (), {"key": public_key})()

    with patch("app.auth.jwt.get_jwks_client", return_value=_TestPyJWKClient()):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.fixture
def auth_headers(
    mock_jwks_keypair: dict[str, Any],
    owner_id_a: str,
) -> dict[str, str]:
    token = mint_test_jwt(mock_jwks_keypair["private_key"], owner_id_a)
    return {**API_HEADERS, "Authorization": f"Bearer {token}"}
