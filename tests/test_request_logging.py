
import importlib
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(monkeypatch):
    main_module = importlib.import_module("app.main")

    # Evitamos depender de MongoDB en estas pruebas.
    monkeypatch.setattr(
        main_module,
        "initialize_indexes",
        AsyncMock(),
    )

    with TestClient(app) as test_client:
        yield test_client


def test_generates_request_id(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]


def test_preserves_request_id(client):
    response = client.get(
        "/health",
        headers={"X-Request-ID": "storage-123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "storage-123"


def test_replaces_invalid_request_id(client):
    response = client.get(
        "/health",
        headers={"X-Request-ID": "id con espacios"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "id con espacios"
