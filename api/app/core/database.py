from collections.abc import Generator
from contextvars import ContextVar
from functools import lru_cache

from sqlalchemy import Engine, text
from sqlmodel import Session, create_engine

from app.core.config import get_settings

current_owner_id: ContextVar[str | None] = ContextVar("current_owner_id", default=None)


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.DATABASE_URL, pool_pre_ping=True)


def set_request_owner(owner_id: str | None) -> None:
    """Set tenant context for the current request (consumed by get_db)."""
    current_owner_id.set(owner_id)


def apply_tenant_context(session: Session, owner_id: str) -> None:
    session.execute(
        text("SELECT set_config('app.owner_id', :owner_id, true)"),
        {"owner_id": owner_id},
    )
    session.execute(text("SET LOCAL ROLE puzzlessbox_app"))


def get_db() -> Generator[Session, None, None]:
    """Yield a DB session with RLS tenant context when owner_id is set."""
    with Session(get_engine()) as session:
        owner_id = current_owner_id.get()
        if owner_id:
            apply_tenant_context(session, owner_id)
        yield session


def check_db_connection() -> bool:
    """Return True when SELECT 1 succeeds."""
    try:
        with Session(get_engine()) as session:
            session.exec(text("SELECT 1")).scalar_one()
        return True
    except Exception:
        return False
