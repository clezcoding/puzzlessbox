"""ASGI entrypoint for uvicorn (`uvicorn app.server:app`)."""

from app.config import get_settings
from app.factory import build_mcp_stack

_settings = get_settings()
app, _mcp, _client = build_mcp_stack(_settings)
