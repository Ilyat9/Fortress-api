"""
Main Application Tests
======================

Tests for application entry point and middleware.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI application."""
    return TestClient(app)


def test_root(client: TestClient) -> None:
    """Test root endpoint."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert "docs" in data
    assert "metrics" in data
    assert "health" in data


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_metrics_endpoint(client: TestClient) -> None:
    """Test metrics endpoint."""
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; version=0.0.4"
    assert response.text.startswith("# HELP")


def test_openapi_endpoint(client: TestClient) -> None:
    """Test OpenAPI schema endpoint."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()

    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
    assert "info" in data
    assert data["info"]["title"] == "Todo API"
    assert data["info"]["version"] == "0.1.0"


def test_docs_endpoint(client: TestClient) -> None:
    """Test API documentation endpoint."""
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_redoc_endpoint(client: TestClient) -> None:
    """Test alternative documentation endpoint."""
    response = client.get("/redoc")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_not_found(client: TestClient) -> None:
    """Test 404 for non-existent endpoint."""
    response = client.get("/nonexistent")

    assert response.status_code == 404


def test_method_not_allowed(client: TestClient) -> None:
    """Test 405 for wrong HTTP method."""
    # GET to POST endpoint
    response = client.get("/api/v1/todos")

    assert response.status_code == 405
