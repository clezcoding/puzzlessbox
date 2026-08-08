"""MCP first-user bootstrap integration tests (G-05-7, D-01..D-05)."""

from __future__ import annotations

import asyncio
import hashlib
import logging

import pytest
from sqlalchemy import text

from app.core.bootstrap import ensure_mcp_client, ensure_service_principal
from app.core.config import Settings, get_settings
from tests.conftest import API_HEADERS

SERVICE_BEARER = "test-service-bearer-token"
MCP_BOOTSTRAP = "test-mcp-bootstrap-token"


def _ensure_user_table(conn) -> None:
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS "user" (
                id text PRIMARY KEY,
                name text NOT NULL,
                email text NOT NULL UNIQUE,
                "emailVerified" boolean NOT NULL,
                image text,
                "createdAt" timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
                "updatedAt" timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )


def _clear_bootstrap_tables(conn) -> None:
    conn.execute(text("DELETE FROM mcp_clients"))
    conn.execute(text("DELETE FROM service_principals"))
    conn.commit()


def _insert_user(conn, user_id: str, *, email: str = "first@example.com") -> None:
    _ensure_user_table(conn)
    conn.execute(
        text(
            """
            INSERT INTO "user" (id, name, email, "emailVerified", "createdAt", "updatedAt")
            VALUES (:id, 'First User', :email, true, timezone('Europe/Berlin', now()), timezone('Europe/Berlin', now()))
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {"id": user_id, "email": email},
    )
    conn.commit()


def _mcp_auth_payload() -> dict[str, str]:
    bearer_hash = hashlib.sha256(MCP_BOOTSTRAP.encode()).hexdigest()
    return {"bearer_hash": bearer_hash}


def _service_headers() -> dict[str, str]:
    return {**API_HEADERS, "X-Service-Bearer": SERVICE_BEARER, "Content-Type": "application/json"}


@pytest.fixture
def bootstrap_settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("SERVICE_BEARER_TOKEN", SERVICE_BEARER)
    monkeypatch.setenv("MCP_BOOTSTRAP_TOKEN", MCP_BOOTSTRAP)
    monkeypatch.setenv("ENV", "dev")
    get_settings.cache_clear()
    yield get_settings()
    get_settings.cache_clear()


def test_happy_path_first_user_bootstraps(
    api_client,
    postgres_connection,
    bootstrap_settings: Settings,
    owner_id_a: str,
) -> None:
    _clear_bootstrap_tables(postgres_connection)
    _insert_user(postgres_connection, owner_id_a)

    response = api_client.post(
        "/internal/mcp-auth",
        headers=_service_headers(),
        json=_mcp_auth_payload(),
    )

    assert response.status_code == 200
    assert response.json()["owner_id"] == owner_id_a

    mcp_count = postgres_connection.execute(text("SELECT count(*) FROM mcp_clients")).scalar_one()
    sp_count = postgres_connection.execute(text("SELECT count(*) FROM service_principals")).scalar_one()
    assert mcp_count == 1
    assert sp_count == 1

    mcp_owner = postgres_connection.execute(text("SELECT owner_id FROM mcp_clients LIMIT 1")).scalar_one()
    sp_owner = postgres_connection.execute(text("SELECT owner_id FROM service_principals LIMIT 1")).scalar_one()
    assert str(mcp_owner) == owner_id_a
    assert str(sp_owner) == owner_id_a


def test_no_op_when_mcp_clients_not_empty(
    api_client,
    postgres_connection,
    bootstrap_settings: Settings,
    owner_id_a: str,
) -> None:
    _clear_bootstrap_tables(postgres_connection)
    _insert_user(postgres_connection, owner_id_a)
    bearer_hash = hashlib.sha256(MCP_BOOTSTRAP.encode()).hexdigest()
    postgres_connection.execute(
        text(
            """
            INSERT INTO mcp_clients (id, owner_id, bearer_hash, status, expires_at, created_at)
            VALUES (gen_random_uuid(), CAST(:owner_id AS uuid), :bearer_hash, 'active', NULL, timezone('Europe/Berlin', now()))
            """
        ),
        {"owner_id": owner_id_a, "bearer_hash": bearer_hash},
    )
    postgres_connection.commit()

    response = api_client.post(
        "/internal/mcp-auth",
        headers=_service_headers(),
        json=_mcp_auth_payload(),
    )

    assert response.status_code == 200
    mcp_count = postgres_connection.execute(text("SELECT count(*) FROM mcp_clients")).scalar_one()
    assert mcp_count == 1


def test_no_op_when_no_user(
    api_client,
    postgres_connection,
    bootstrap_settings: Settings,
) -> None:
    _clear_bootstrap_tables(postgres_connection)
    _ensure_user_table(postgres_connection)
    postgres_connection.execute(text('DELETE FROM "user"'))
    postgres_connection.commit()

    response = api_client.post(
        "/internal/mcp-auth",
        headers=_service_headers(),
        json=_mcp_auth_payload(),
    )

    assert response.status_code == 401
    mcp_count = postgres_connection.execute(text("SELECT count(*) FROM mcp_clients")).scalar_one()
    assert mcp_count == 0


def test_prod_refuse_when_env_token_empty(
    api_client,
    postgres_connection,
    monkeypatch: pytest.MonkeyPatch,
    owner_id_a: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("SERVICE_BEARER_TOKEN", SERVICE_BEARER)
    monkeypatch.setenv("MCP_BOOTSTRAP_TOKEN", "")
    monkeypatch.setenv("ENV", "prod")
    get_settings.cache_clear()

    _clear_bootstrap_tables(postgres_connection)
    _insert_user(postgres_connection, owner_id_a)

    with caplog.at_level(logging.ERROR):
        response = api_client.post(
            "/internal/mcp-auth",
            headers=_service_headers(),
            json={"bearer_hash": hashlib.sha256(b"any-token").hexdigest()},
        )

    assert response.status_code == 401
    mcp_count = postgres_connection.execute(text("SELECT count(*) FROM mcp_clients")).scalar_one()
    sp_count = postgres_connection.execute(text("SELECT count(*) FROM service_principals")).scalar_one()
    assert mcp_count == 0
    assert sp_count == 0
    assert "Production MCP bootstrap blocked" in caplog.text
    get_settings.cache_clear()


def test_dev_generate_when_env_token_empty(
    api_client,
    postgres_connection,
    monkeypatch: pytest.MonkeyPatch,
    owner_id_a: str,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
    tmp_path,
) -> None:
    monkeypatch.setenv("SERVICE_BEARER_TOKEN", SERVICE_BEARER)
    monkeypatch.setenv("MCP_BOOTSTRAP_TOKEN", "")
    monkeypatch.setenv("ENV", "dev")
    get_settings.cache_clear()
    monkeypatch.chdir(tmp_path)

    _clear_bootstrap_tables(postgres_connection)
    _insert_user(postgres_connection, owner_id_a)

    with caplog.at_level(logging.DEBUG):
        response = api_client.post(
            "/internal/mcp-auth",
            headers=_service_headers(),
            json={"bearer_hash": hashlib.sha256(b"placeholder").hexdigest()},
        )

    captured = capsys.readouterr()
    assert "[BOOTSTRAP] MCP_BOOTSTRAP_TOKEN written to" in captured.out
    assert "copy to .env / Hermes config" in captured.out
    assert captured.out.count("[BOOTSTRAP]") == 1

    token_path = tmp_path / ".local" / "mcp-bootstrap-token"
    assert token_path.is_file()
    generated_token = token_path.read_text(encoding="utf-8").strip()
    assert generated_token
    assert generated_token not in captured.out
    assert generated_token not in caplog.text

    mcp_count = postgres_connection.execute(text("SELECT count(*) FROM mcp_clients")).scalar_one()
    assert mcp_count == 1

    assert response.status_code == 401  # placeholder hash does not match generated token
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_race_only_one_row(
    async_api_client,
    postgres_connection,
    bootstrap_settings: Settings,
    owner_id_a: str,
) -> None:
    _clear_bootstrap_tables(postgres_connection)
    _insert_user(postgres_connection, owner_id_a)

    async def _post() -> int:
        response = await async_api_client.post(
            "/internal/mcp-auth",
            headers=_service_headers(),
            json=_mcp_auth_payload(),
        )
        return response.status_code

    statuses = await asyncio.gather(_post(), _post())
    assert 200 in statuses

    mcp_count = postgres_connection.execute(text("SELECT count(*) FROM mcp_clients")).scalar_one()
    assert mcp_count == 1


def test_malformed_service_bearer_returns_401_not_500(
    api_client,
    postgres_connection,
    bootstrap_settings: Settings,
) -> None:
    _clear_bootstrap_tables(postgres_connection)

    response = api_client.post(
        "/internal/mcp-auth",
        headers={**API_HEADERS, "X-Service-Bearer": "short", "Content-Type": "application/json"},
        json=_mcp_auth_payload(),
    )

    assert response.status_code == 401


def test_lifespan_ensure_paths_preserved(
    postgres_connection,
    monkeypatch: pytest.MonkeyPatch,
    owner_id_a: str,
) -> None:
    owner_env = owner_id_a
    token_env = "lifespan-mcp-bootstrap-token"
    monkeypatch.setenv("SERVICE_OWNER_ID", owner_env)
    monkeypatch.setenv("MCP_BOOTSTRAP_TOKEN", token_env)
    monkeypatch.setenv("SERVICE_BEARER_TOKEN", SERVICE_BEARER)
    get_settings.cache_clear()
    settings = get_settings()

    _clear_bootstrap_tables(postgres_connection)

    ensure_service_principal(settings)
    ensure_mcp_client(settings)

    mcp_count = postgres_connection.execute(text("SELECT count(*) FROM mcp_clients")).scalar_one()
    sp_count = postgres_connection.execute(text("SELECT count(*) FROM service_principals")).scalar_one()
    assert mcp_count == 1
    assert sp_count == 1

    mcp_owner = postgres_connection.execute(text("SELECT owner_id FROM mcp_clients LIMIT 1")).scalar_one()
    assert str(mcp_owner) == owner_env
    get_settings.cache_clear()
