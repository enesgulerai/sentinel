from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_ingest_transaction_mocked(monkeypatch):
    # Mock Redis: Simulate a new transaction using AsyncMock for the 'await' call
    mock_redis = MagicMock()
    mock_redis.set = AsyncMock(return_value=True)  # THE FIX

    # Mock Producer: Simulate Redpanda delivery (produce is usually synchronous)
    mock_producer = MagicMock()

    # Inject our mocks into the running app's module
    monkeypatch.setattr("src.api.main.redis_client", mock_redis)
    monkeypatch.setattr("src.api.main.producer", mock_producer)

    payload = {
        "Time": 1.0,
        "V1": 0.0,
        "V2": 0.0,
        "V3": 0.0,
        "V4": 0.0,
        "V5": 0.0,
        "V6": 0.0,
        "V7": 0.0,
        "V8": 0.0,
        "V9": 0.0,
        "V10": 0.0,
        "V11": 0.0,
        "V12": 0.0,
        "V13": 0.0,
        "V14": 0.0,
        "V15": 0.0,
        "V16": 0.0,
        "V17": 0.0,
        "V18": 0.0,
        "V19": 0.0,
        "V20": 0.0,
        "V21": 0.0,
        "V22": 0.0,
        "V23": 0.0,
        "V24": 0.0,
        "V25": 0.0,
        "V26": 0.0,
        "V27": 0.0,
        "V28": 0.0,
        "Amount": 500.0,
    }

    response = client.post("/api/v1/transactions", json=payload)

    assert response.status_code == 202
    assert response.json()["status"] == "success"

    mock_redis.set.assert_called_once()
    mock_producer.produce.assert_called_once()


def test_duplicate_transaction_mocked(monkeypatch):
    # Mock Redis: Simulate an existing transaction with AsyncMock
    mock_redis = MagicMock()
    mock_redis.set = AsyncMock(return_value=False)  # THE FIX

    monkeypatch.setattr("src.api.main.redis_client", mock_redis)

    full_payload = {f"V{i}": 0.0 for i in range(1, 29)}
    full_payload.update({"Time": 1.0, "Amount": 500.0})

    response = client.post("/api/v1/transactions", json=full_payload)

    assert response.json()["status"] == "ignored"
    assert "Duplicate" in response.json()["message"]
