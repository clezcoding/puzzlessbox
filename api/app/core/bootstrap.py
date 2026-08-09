"""One-shot startup bootstrap for ops gaps (ponytail: idempotent INSERT only)."""

from __future__ import annotations

import hashlib
import logging
import secrets
import sys
from pathlib import Path

from sqlalchemy import text
from sqlmodel import Session

from app.core.config import Settings
from app.core.database import get_engine

logger = logging.getLogger(__name__)

_DEV_BOOTSTRAP_TOKEN_FILE = Path(".local/mcp-bootstrap-token")


def _write_dev_bootstrap_token(token: str) -> Path:
    path = _DEV_BOOTSTRAP_TOKEN_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{token}\n", encoding="utf-8")
    path.chmod(0o600)
    return path.resolve()


def _resolve_bootstrap_token(settings: Settings) -> str | None:
    bootstrap_token = settings.MCP_BOOTSTRAP_TOKEN.strip()
    if bootstrap_token:
        return bootstrap_token
    if settings.is_prod:
        logger.error("Production MCP bootstrap blocked: bootstrap token env is empty.")
        return None
    bootstrap_token = secrets.token_urlsafe(32)
    token_path = _write_dev_bootstrap_token(bootstrap_token)
    sys.stdout.write(
        f"\n[BOOTSTRAP] MCP_BOOTSTRAP_TOKEN written to {token_path} "
        "(copy to .env / Hermes config)\n"
    )
    sys.stdout.flush()
    return bootstrap_token


def ensure_service_principal(settings: Settings) -> None:
    owner_id = settings.SERVICE_OWNER_ID.strip()
    if not owner_id:
        return

    bearer_hash = hashlib.sha256(settings.SERVICE_BEARER_TOKEN.encode()).hexdigest()
    with Session(get_engine()) as session:
        session.execute(
            text(
                """
                INSERT INTO service_principals (owner_id, name, bearer_hash, created_at)
                VALUES (CAST(:owner_id AS uuid), 'mcp', :bearer_hash, timezone('Europe/Berlin', now()))
                ON CONFLICT (owner_id) DO UPDATE
                SET bearer_hash = EXCLUDED.bearer_hash,
                    name = EXCLUDED.name
                """
            ),
            {"owner_id": owner_id, "bearer_hash": bearer_hash},
        )
        session.commit()
    logger.info("service_principal bootstrap ok for owner_id=%s", owner_id)


def ensure_mcp_client(settings: Settings) -> None:
    bootstrap_token = settings.MCP_BOOTSTRAP_TOKEN.strip()
    owner_id = settings.SERVICE_OWNER_ID.strip()
    if not bootstrap_token or not owner_id:
        return

    bearer_hash = hashlib.sha256(bootstrap_token.encode()).hexdigest()
    with Session(get_engine()) as session:
        count = session.execute(text("SELECT count(*) FROM mcp_clients")).scalar_one()
        if count == 0:
            session.execute(
                text(
                    """
                    INSERT INTO mcp_clients (id, owner_id, bearer_hash, status, expires_at, created_at)
                    VALUES (
                        gen_random_uuid(),
                        CAST(:owner_id AS uuid),
                        :bearer_hash,
                        'active',
                        NULL,
                        timezone('Europe/Berlin', now())
                    )
                    """
                ),
                {"owner_id": owner_id, "bearer_hash": bearer_hash},
            )
            session.commit()
    logger.info("mcp_client bootstrap ok for owner_id=%s", owner_id)


def check_and_bootstrap_first_user(session: Session, settings: Settings) -> None:
    """Auto-bootstrap MCP client + service principal for first registered user (D-01..D-05).

    Single-user: auto-bind first account. Multi-user: require SERVICE_OWNER_ID (WR-04 / D-08).
    """
    # ponytail: EXCLUSIVE lock serializes first-boot; acceptable for v1; upgrade: NOWAIT + retry
    session.execute(text("LOCK TABLE mcp_clients IN EXCLUSIVE MODE"))
    mcp_count = session.execute(text("SELECT count(*) FROM mcp_clients")).scalar_one()
    if mcp_count > 0:
        return

    first_user_id = session.execute(
        text('SELECT id FROM "user" ORDER BY "createdAt" ASC LIMIT 1')
    ).scalar_one_or_none()
    if first_user_id is None:
        return

    user_count = session.execute(text('SELECT count(*) FROM "user"')).scalar_one()
    if user_count == 1:
        bootstrap_owner_id = str(first_user_id)
    elif user_count > 1:
        owner_id_env = settings.SERVICE_OWNER_ID.strip()
        if not owner_id_env:
            logger.error(
                "Multi-user setup detected but SERVICE_OWNER_ID is empty. Aborting bootstrap."
            )
            return
        exists = session.execute(
            text('SELECT 1 FROM "user" WHERE id = :oid LIMIT 1'),
            {"oid": owner_id_env},
        ).scalar_one_or_none()
        if not exists:
            logger.error(
                "SERVICE_OWNER_ID %s does not exist in 'user' table. Aborting bootstrap.",
                owner_id_env,
            )
            return
        bootstrap_owner_id = owner_id_env
    else:
        return

    bootstrap_token = _resolve_bootstrap_token(settings)
    if bootstrap_token is None:
        return

    sp_count = session.execute(text("SELECT count(*) FROM service_principals")).scalar_one()
    if sp_count == 0:
        service_bearer = settings.SERVICE_BEARER_TOKEN.strip()
        if service_bearer:
            sp_hash = hashlib.sha256(service_bearer.encode()).hexdigest()
            session.execute(
                text(
                    """
                    INSERT INTO service_principals (owner_id, name, bearer_hash, created_at)
                    VALUES (CAST(:owner_id AS uuid), 'mcp', :sp_hash, timezone('Europe/Berlin', now()))
                    ON CONFLICT (owner_id) DO NOTHING
                    """
                ),
                {"owner_id": bootstrap_owner_id, "sp_hash": sp_hash},
            )

    mcp_hash = hashlib.sha256(bootstrap_token.encode()).hexdigest()
    session.execute(
        text(
            """
            INSERT INTO mcp_clients (id, owner_id, bearer_hash, status, expires_at, created_at)
            VALUES (
                gen_random_uuid(),
                CAST(:owner_id AS uuid),
                :mcp_hash,
                'active',
                NULL,
                timezone('Europe/Berlin', now())
            )
            """
        ),
        {"owner_id": bootstrap_owner_id, "mcp_hash": mcp_hash},
    )
