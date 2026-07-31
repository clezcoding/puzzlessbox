"""One-shot startup bootstrap for ops gaps (ponytail: idempotent INSERT only)."""

from __future__ import annotations

import hashlib
import logging

from sqlalchemy import text
from sqlmodel import Session

from app.core.config import Settings
from app.core.database import get_engine

logger = logging.getLogger(__name__)


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
