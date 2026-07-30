"""Minimal Camoufox sidecar: GET /?url= → HTML (D-16). Bearer auth on scrape routes."""

from __future__ import annotations

import os

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse

BEARER = os.environ.get("CAMOUFOX_BEARER", "")

app = FastAPI()


def require_bearer(request: Request) -> None:
    if not BEARER:
        return
    header = request.headers.get("Authorization", "")
    if header != f"Bearer {BEARER}":
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def fetch_url(url: str, _: None = Depends(require_bearer)) -> PlainTextResponse:
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=422, detail="url must be http(s)")
    async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
        response = await client.get(
            url,
            headers={"User-Agent": "Puzzlessbox-Camoufox-Sidecar/1.0"},
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail="upstream fetch failed")
        return PlainTextResponse(response.text)
