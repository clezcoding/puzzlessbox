"""JWT verification via Better Auth JWKS (D-21) and session cookie extraction (D-22)."""

from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.config import get_settings
from app.core.database import get_db, set_request_owner

SESSION_COOKIE = "puzzlessbox_session"
_bearer = HTTPBearer(auto_error=False)


@lru_cache
def get_jwks_client() -> jwt.PyJWKClient:
    settings = get_settings()
    return jwt.PyJWKClient(
        settings.BETTER_AUTH_JWKS_URL,
        cache_jwk_set=True,
        lifespan=300,
    )


def _decode_owner_from_token(token: str) -> str:
    try:
        signing_key = get_jwks_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": f"Authentication failed: {exc}"},
        ) from exc

    owner_id = payload.get("sub")
    if not owner_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid token: missing subject."},
        )
    return str(owner_id)


def _extract_bearer_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
) -> str | None:
    if credentials and credentials.credentials:
        return credentials.credentials
    return request.cookies.get(SESSION_COOKIE)


async def get_current_owner(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    token = _extract_bearer_token(request, credentials)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Missing authentication token."},
        )
    owner_id = _decode_owner_from_token(token)
    set_request_owner(owner_id)
    return owner_id


def get_db_for_owner(
    owner_id: str = Depends(get_current_owner),
) -> Generator[Session, None, None]:
    set_request_owner(owner_id)
    yield from get_db()
