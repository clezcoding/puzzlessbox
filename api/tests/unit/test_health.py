"""Health, readiness, versioning, and error-shape tests (D-27, D-31, D-32, D-33)."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import API_VERSION_ACCEPT, app, create_app

VERSION_HEADERS = {"Accept": API_VERSION_ACCEPT}


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_db_up(client):
    with patch("app.routers.health.check_db_connection", return_value=True):
        response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_db_down(client):
    with patch("app.routers.health.check_db_connection", return_value=False):
        response = client.get("/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "SERVICE_UNAVAILABLE"
    assert "database" in body["error"]["message"].lower()


def test_versioning_415(client):
    response = client.get("/__test-error__")
    assert response.status_code == 415
    body = response.json()
    assert body["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"
    assert API_VERSION_ACCEPT in body["error"]["message"]


def test_oauth_connect_skips_accept_versioning(client):
    response = client.get(
        "/auth/google/connect",
        headers={"Accept": "text/html"},
    )
    assert response.status_code != 415


def test_oauth_callback_skips_accept_versioning(client):
    response = client.get(
        "/auth/google/callback",
        headers={"Accept": "text/html"},
    )
    assert response.status_code != 415


def test_docs_disabled_prod(monkeypatch):
    monkeypatch.setenv("ENV", "prod")
    get_settings.cache_clear()
    prod_app = create_app()
    prod_client = TestClient(prod_app)
    assert prod_client.get("/docs").status_code == 404
    assert prod_client.get("/redoc").status_code == 404
    assert prod_client.get("/openapi.json").status_code == 404
    get_settings.cache_clear()


def test_error_shape(client):
    response = client.get("/__test-error__", headers=VERSION_HEADERS)
    assert response.status_code == 418
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "TEAPOT"
    assert body["error"]["message"] == "test error"
    assert body["error"]["details"] == {"hint": "unified shape"}
