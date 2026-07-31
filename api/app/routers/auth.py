"""Auth proxy to Better Auth (D-21, D-24) with session cookie forwarding (D-22)."""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.auth.jwt import SESSION_COOKIE, get_current_owner
from app.core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_DOMAIN = ".puzzlesstool.online"


class SignupBody(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=8)
    name: str | None = None


class LoginBody(BaseModel):
    email: str = Field(min_length=3)
    password: str


def _session_cookie_kwargs() -> dict[str, Any]:
    settings = get_settings()
    return {
        "domain": COOKIE_DOMAIN,
        "httponly": True,
        "samesite": "lax",
        "secure": settings.is_prod,
        "path": "/",
    }


def _map_better_auth_error(resp: httpx.Response) -> HTTPException:
    try:
        body = resp.json()
    except ValueError:
        body = {}

    message = ""
    if isinstance(body, dict):
        message = str(body.get("message") or body.get("error") or "")
        if not message and isinstance(body.get("error"), dict):
            message = str(body["error"].get("message") or "")

    if resp.status_code == 409 or "SIGNUP_LOCKED" in message:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "SIGNUP_LOCKED", "message": "Signup is locked after first user."},
        )

    return HTTPException(
        status_code=resp.status_code,
        detail={
            "code": "AUTH_ERROR",
            "message": message or "Authentication request failed.",
            "details": body if body else None,
        },
    )


async def _fetch_jwt_token(client: httpx.AsyncClient, cookies: httpx.Cookies) -> str | None:
    token_resp = await client.get("/token", cookies=cookies)
    if token_resp.status_code != 200:
        return None
    data = token_resp.json()
    if isinstance(data, dict):
        token = data.get("token")
        return str(token) if token else None
    return None


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(body: SignupBody) -> dict[str, Any]:
    settings = get_settings()
    payload = {
        "email": body.email,
        "password": body.password,
        "name": body.name or body.email.split("@", 1)[0],
    }
    async with httpx.AsyncClient(
        base_url=settings.BETTER_AUTH_BASE_URL,
        timeout=30.0,
    ) as client:
        resp = await client.post("/sign-up/email", json=payload)

    if resp.status_code >= 400:
        raise _map_better_auth_error(resp)

    data = resp.json()
    user = data.get("user", data)
    return {"user": user, "token": data.get("token")}


@router.post("/login")
async def login(body: LoginBody, response: Response) -> dict[str, Any]:
    settings = get_settings()
    async with httpx.AsyncClient(
        base_url=settings.BETTER_AUTH_BASE_URL,
        timeout=30.0,
    ) as client:
        resp = await client.post(
            "/sign-in/email",
            json={"email": body.email, "password": body.password},
        )
        if resp.status_code >= 400:
            raise _map_better_auth_error(resp)

        login_data = resp.json()
        jwt_token = login_data.get("token")
        if not jwt_token:
            jwt_token = await _fetch_jwt_token(client, resp.cookies)
        if jwt_token:
            jwt_token = str(jwt_token)

    if not jwt_token:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "AUTH_ERROR", "message": "Better Auth did not return a JWT."},
        )

    response.set_cookie(SESSION_COOKIE, jwt_token, **_session_cookie_kwargs())
    return {"token": jwt_token}


@router.get("/verify")
async def verify(owner_id: str = Depends(get_current_owner)) -> dict[str, str]:
    return {"owner_id": owner_id}
