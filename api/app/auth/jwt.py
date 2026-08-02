"""JWT verification via Better Auth JWKS (D-21) and session cookie extraction (D-22)."""

from __future__ import annotations

import hashlib
import hmac
import uuid
from collections.abc import Generator
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlmodel import Session

from app.core.config import get_settings
from app.core.database import get_db, get_engine, set_request_owner

SESSION_COOKIE = "puzzlessbox_session"
SERVICE_BEARER_HEADER = "X-Service-Bearer"
OWNER_ID_HEADER = "X-Owner-Id"
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
            # Better Auth jwt() defaults to EdDSA; tests use RS256
            algorithms=["EdDSA", "RS256"],
            options={"verify_exp": True, "verify_aud": False},
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


def _resolve_service_owner(service_bearer: str) -> str:
    settings = get_settings()
    if not hmac.compare_digest(service_bearer, settings.SERVICE_BEARER_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid service bearer token."},
        )

    bearer_hash = hashlib.sha256(service_bearer.encode()).hexdigest()
    with Session(get_engine()) as session:
        owner_id = session.execute(
            text("SELECT owner_id FROM service_principals WHERE bearer_hash = :hash LIMIT 1"),
            {"hash": bearer_hash},
        ).scalar_one_or_none()

    if not owner_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Service principal not configured."},
        )
    return str(owner_id)


def _validate_owner_header(owner_id_header: str) -> str:
    try:
        uuid.UUID(owner_id_header)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Invalid owner id format."},
        ) from exc

    with Session(get_engine()) as session:
        exists = session.execute(
            text('SELECT 1 FROM "user" WHERE id = CAST(:oid AS uuid) LIMIT 1'),
            {"oid": owner_id_header},
        ).scalar_one_or_none()

    if not exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Owner not provisioned."},
        )
    return owner_id_header


async def get_current_owner(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    service_bearer = request.headers.get(SERVICE_BEARER_HEADER)
    if service_bearer:
        owner_id = _resolve_service_owner(service_bearer)
        owner_id_header = request.headers.get(OWNER_ID_HEADER)
        if owner_id_header:
            owner_id = _validate_owner_header(owner_id_header)
        set_request_owner(owner_id)
        return owner_id

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
