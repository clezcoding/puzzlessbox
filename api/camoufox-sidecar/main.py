"""Minimal Camoufox sidecar: GET /?url= → HTML (D-16). Bearer auth on scrape routes."""

from __future__ import annotations

import ipaddress
import os
import socket
from urllib.parse import urlparse

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

BEARER = os.environ.get("CAMOUFOX_BEARER", "")

_BLOCKED_NETWORKS = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
)

app = FastAPI()


def require_bearer(request: Request) -> None:
    if not BEARER:
        return
    header = request.headers.get("Authorization", "")
    if header != f"Bearer {BEARER}":
        raise HTTPException(status_code=401, detail="Unauthorized")


def _is_blocked_ip(ip_str: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    return any(addr in network for network in _BLOCKED_NETWORKS)


def validate_url_ssrf(url: str) -> None:
    """Reject private/reserved targets before outbound fetch (CodeQL py/full-ssrf)."""
    if len(url) > 2048:
        raise HTTPException(status_code=422, detail="URL exceeds maximum length")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=422, detail="url must be http(s)")

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=422, detail="URL has no hostname")

    try:
        addr_infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise HTTPException(status_code=422, detail=f"Hostname resolution failed: {exc}") from exc

    for info in addr_infos:
        if _is_blocked_ip(info[4][0]):
            raise HTTPException(status_code=422, detail="URL resolves to a blocked address")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def fetch_url(url: str, _: None = Depends(require_bearer)) -> PlainTextResponse:
    validate_url_ssrf(url)
    # No redirects: a 3xx to a private IP would bypass the pre-resolve check.
    async with httpx.AsyncClient(timeout=4.0, follow_redirects=False) as client:
        response = await client.get(
            url,
            headers={"User-Agent": "Puzzlessbox-Camoufox-Sidecar/1.0"},
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail="upstream fetch failed")
        return PlainTextResponse(response.text)
