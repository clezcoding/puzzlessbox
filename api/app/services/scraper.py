"""Link metadata scraper: Firecrawl (primary) → Camoufox (fallback) → hostname (D-09..D-16).

Self-hosted Firecrawl lacks Fire-engine (D-12); Cloudflare/WAF bypass is best-effort.
"""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException, status

from app.core.config import Settings, get_settings

ScrapeStatus = Literal[
    "pending",
    "scraping",
    "ok",
    "partial",
    "timed_out",
    "failed",
    "skipped",
]

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

FIRECRAWL_TIMEOUT = 8.0
CAMOUFOX_TIMEOUT = 4.0

_OG_PROPERTY_RE = re.compile(
    r'<meta[^>]+(?:property|name)=["\'](?P<prop>og:[^"\']+)["\'][^>]+content=["\'](?P<content>[^"\']*)["\']',
    re.IGNORECASE,
)
_OG_CONTENT_FIRST_RE = re.compile(
    r'<meta[^>]+content=["\'](?P<content>[^"\']*)["\'][^>]+(?:property|name)=["\'](?P<prop>og:[^"\']+)["\']',
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ScrapeResult:
    title: str
    description: str | None
    image: str | None
    scrape_status: ScrapeStatus


def _is_blocked_ip(ip_str: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped is not None:
        addr = addr.ipv4_mapped
    if (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    ):
        return True
    if addr == ipaddress.ip_address("0.0.0.0"):
        return True
    return any(addr in network for network in _BLOCKED_NETWORKS)


def validate_url_ssrf(url: str) -> None:
    """Reject private/reserved targets before outbound scrape (T-01-ssrf)."""
    if len(url) > 2048:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "SSRF_BLOCKED", "message": "URL exceeds maximum length."},
        )

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "SSRF_BLOCKED", "message": "Only http and https URLs are allowed."},
        )

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "SSRF_BLOCKED", "message": "URL has no hostname."},
        )

    try:
        addr_infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "SSRF_BLOCKED", "message": f"Hostname resolution failed: {exc}"},
        ) from exc

    for info in addr_infos:
        ip = info[4][0]
        if _is_blocked_ip(ip):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "SSRF_BLOCKED", "message": "URL resolves to a blocked address."},
            )


def parse_open_graph(html: str) -> dict[str, str | None]:
    tags: dict[str, str | None] = {
        "og:title": None,
        "og:description": None,
        "og:image": None,
    }
    for pattern in (_OG_PROPERTY_RE, _OG_CONTENT_FIRST_RE):
        for match in pattern.finditer(html):
            prop = match.group("prop").lower()
            if prop in tags and tags[prop] is None:
                tags[prop] = match.group("content") or None
    return {
        "title": tags["og:title"],
        "description": tags["og:description"],
        "image": tags["og:image"],
    }


def _auth_headers(bearer: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {bearer}"}


class ScrapeService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    async def scrape(self, url: str) -> ScrapeResult:
        validate_url_ssrf(url)
        parsed = urlparse(url)
        hostname = parsed.netloc or url

        og = await self._scrape_firecrawl(url)
        if og is None:
            og = await self._scrape_camoufox(url)

        if og is None or not og.get("title"):
            return ScrapeResult(
                title=hostname,
                description=None,
                image=None,
                scrape_status="failed",
            )

        return ScrapeResult(
            title=og["title"] or hostname,
            description=og.get("description"),
            image=og.get("image"),
            scrape_status="ok",
        )

    async def _scrape_firecrawl(self, url: str) -> dict[str, str | None] | None:
        base = self._settings.FIRECRAWL_URL.rstrip("/")
        if not base:
            return None

        try:
            async with httpx.AsyncClient(timeout=FIRECRAWL_TIMEOUT) as client:
                response = await client.post(
                    f"{base}/v1/scrape",
                    headers=_auth_headers(self._settings.FIRECRAWL_BEARER),
                    json={"url": url, "formats": ["html"]},
                )
                if response.status_code >= 400:
                    return None
                payload = response.json()
        except (httpx.HTTPError, ValueError):
            return None

        data = payload.get("data") if isinstance(payload, dict) else None
        html = ""
        if isinstance(data, dict):
            html = data.get("html") or ""
            metadata = data.get("metadata") or {}
            if isinstance(metadata, dict) and metadata.get("title"):
                return {
                    "title": metadata.get("title"),
                    "description": metadata.get("description"),
                    "image": metadata.get("ogImage") or metadata.get("image"),
                }

        if not html:
            return None

        parsed = parse_open_graph(html)
        if parsed["title"]:
            return parsed
        return None

    async def _scrape_camoufox(self, url: str) -> dict[str, str | None] | None:
        base = self._settings.CAMOUFOX_URL.rstrip("/")
        if not base:
            return None

        try:
            async with httpx.AsyncClient(timeout=CAMOUFOX_TIMEOUT) as client:
                response = await client.get(
                    f"{base}/",
                    params={"url": url},
                    headers=_auth_headers(self._settings.CAMOUFOX_BEARER),
                )
                if response.status_code >= 400:
                    return None
                html = response.text
        except httpx.HTTPError:
            return None

        parsed = parse_open_graph(html)
        if parsed["title"]:
            return parsed
        return None


async def ping_scraper_health(settings: Settings | None = None) -> str | None:
    """Return unhealthy service name, or None when all scraper pings succeed."""
    cfg = settings or get_settings()
    if not cfg.SCRAPER_ENABLED:
        return None

    async with httpx.AsyncClient(timeout=2.0) as client:
        firecrawl_base = cfg.FIRECRAWL_URL.rstrip("/")
        if firecrawl_base:
            try:
                response = await client.get(f"{firecrawl_base}/v0/health/liveness")
                if response.status_code >= 400:
                    return "firecrawl"
            except httpx.HTTPError:
                return "firecrawl"

        camoufox_base = cfg.CAMOUFOX_URL.rstrip("/")
        if camoufox_base:
            try:
                response = await client.get(
                    f"{camoufox_base}/health",
                    headers=_auth_headers(cfg.CAMOUFOX_BEARER),
                )
                if response.status_code >= 400:
                    return "camoufox"
            except httpx.HTTPError:
                return "camoufox"

    return None


scrape_service = ScrapeService()
