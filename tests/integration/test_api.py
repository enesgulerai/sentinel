from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


# ==========================================
# FIXTURES (TEST DATA AND MOCKS)
# ==========================================
@pytest.fixture
def valid_payload():
    payload = {f"V{i}": 0.0 for i in range(1, 29)}
    payload.update({"Time": 1.0, "Amount": 500.0})
    return payload


@pytest.fixture
def mock_infrastructure(monkeypatch):
    """Mocks Redis and Redpanda using standard monkeypatch."""
    mock_redis = MagicMock()
    mock_redis.set = AsyncMock(return_value=True)

    mock_producer = MagicMock()

    monkeypatch.setattr("src.api.main.redis_client", mock_redis)
    monkeypatch.setattr("src.api.main.producer", mock_producer)

    return mock_redis, mock_producer


# ==========================================
# 1. SYSTEM TESTS
# ==========================================
def test_health_check():
    """Verifies if the system is up and running."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


# ==========================================
# 2. TRANSACTION INGESTION TESTS (HAPPY PATH)
# ==========================================
def test_valid_transaction_ingestion(mock_infrastructure, valid_payload):
    """Verifies that a valid transaction is successfully ingested."""
    mock_redis, mock_producer = mock_infrastructure

    response = client.post("/api/v1/transactions", json=valid_payload)

    assert response.status_code == 202
    data = response.json()
    assert data["status"] in ["success", "ignored"]

    # Verify that the mocks were actually called
    mock_redis.set.assert_called_once()
    mock_producer.produce.assert_called_once()


def test_duplicate_transaction_rejected(mock_infrastructure, valid_payload):
    """Verifies that duplicate transactions are ignored with a 202 Accepted status."""
    mock_redis, _ = mock_infrastructure
    mock_redis.set = AsyncMock(return_value=False)

    response = client.post("/api/v1/transactions", json=valid_payload)

    assert response.status_code == 202
    assert response.json()["status"] == "ignored"


# ==========================================
# 3. VALIDATION TESTS (NEGATIVE PATH)
# ==========================================
def test_invalid_transaction_missing_fields():
    """Verifies that Pydantic throws a 422 error for missing payload fields."""
    bad_payload = {"Time": 100.0, "V1": 1.5}  # Missing other V columns and Amount

    response = client.post("/api/v1/transactions", json=bad_payload)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_invalid_transaction_wrong_data_type(valid_payload):
    """Verifies system protection against incorrect data types."""
    valid_payload["Amount"] = "OneHundredDollars"

    response = client.post("/api/v1/transactions", json=valid_payload)
    assert response.status_code == 422
