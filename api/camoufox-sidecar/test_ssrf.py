"""Self-check: SSRF guard rejects private targets (ponytail: one runnable check)."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from main import validate_url_ssrf


def test_rejects_loopback() -> None:
    with pytest.raises(HTTPException) as exc:
        validate_url_ssrf("http://127.0.0.1/")
    assert exc.value.status_code == 422


def test_rejects_non_http() -> None:
    with pytest.raises(HTTPException) as exc:
        validate_url_ssrf("file:///etc/passwd")
    assert exc.value.status_code == 422


def test_allows_public_example() -> None:
    validate_url_ssrf("https://example.com/")
