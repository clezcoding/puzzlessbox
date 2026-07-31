from __future__ import annotations

import hashlib

import httpx
from fastmcp.server.auth import AccessToken, TokenVerifier

from app.api_client import make_client, resolve_owner
from app.config import Settings, get_settings


class OwnerResolvingVerifier(TokenVerifier):
    def __init__(
        self,
        settings: Settings | None = None,
        client: httpx.AsyncClient | None = None,
        *,
        base_url: str = "http://localhost:8000",
    ) -> None:
        super().__init__(base_url=base_url)
        self._settings = settings or get_settings()
        self._client = client

    async def verify_token(self, token: str) -> AccessToken | None:
        bearer_hash = hashlib.sha256(token.encode()).hexdigest()
        client = self._client or make_client(self._settings)
        owner_id = await resolve_owner(client, bearer_hash)
        if owner_id is None:
            return None
        return AccessToken(
            token=token,
            client_id=owner_id,
            scopes=[],
            expires_at=None,
            claims={"owner_id": owner_id, "sub": owner_id},
        )
