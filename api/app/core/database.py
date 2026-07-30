from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, text
from sqlmodel import Session, create_engine

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.DATABASE_URL, pool_pre_ping=True)


def get_db() -> Generator[Session, None, None]:
    """Yield a DB session; SET app.owner_id wired in Plan 05 once tables exist."""
    with Session(get_engine()) as session:
        # ponytail: RLS owner_id SET deferred to Plan 05 — session stub only here
        yield session


def check_db_connection() -> bool:
    """Return True when SELECT 1 succeeds."""
    try:
        with Session(get_engine()) as session:
            session.exec(text("SELECT 1")).scalar_one()
        return True
    except Exception:
        return False
