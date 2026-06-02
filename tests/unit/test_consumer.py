import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from src.inference.consumer import start_inference_engine


@pytest.fixture
def mock_env_paths(monkeypatch):
    # Bypass actual file system checks for MODEL_PATH and SCALER_PATH
    monkeypatch.setattr("src.inference.consumer.Path.exists", lambda self: True)


@pytest.mark.asyncio
@patch("src.inference.consumer.AIOKafkaConsumer")
@patch("src.inference.consumer.psycopg.AsyncConnection.connect")
@patch("src.inference.consumer.ort.InferenceSession")
@patch("src.inference.consumer.joblib.load")
async def test_inference_engine_batch_processing(
    mock_joblib_load, mock_onnx_session, mock_db_connect, mock_kafka_consumer, mock_env_paths
):
    # ==========================================
    # 1. MOCK ML COMPONENTS (SCALER & ONNX)
    # ==========================================
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.array([[0.5, 100.0], [0.1, 20.0]])
    mock_joblib_load.return_value = mock_scaler

    mock_session_instance = MagicMock()
    mock_input = MagicMock()
    mock_input.name = "float_input"
    mock_session_instance.get_inputs.return_value = [mock_input]

    mock_session_instance.run.return_value = [None, [{0: 0.15, 1: 0.85}, {0: 0.95, 1: 0.05}]]
    mock_onnx_session.return_value = mock_session_instance

    # ==========================================
    # 2. MOCK POSTGRESQL (ASYNC)
    # ==========================================
    mock_db_conn = AsyncMock()
    mock_db_cursor = AsyncMock()

    mock_db_conn.cursor = MagicMock(return_value=mock_db_cursor)
    mock_db_connect.return_value = mock_db_conn

    # ==========================================
    # 3. MOCK KAFKA & INFINITE LOOP BREAKER
    # ==========================================
    mock_consumer_instance = AsyncMock()

    # Construct fake incoming Kafka messages
    msg1 = MagicMock()
    msg1.value = json.dumps({"transaction_id": "TX100", "Amount": 1500.0, "Time": 10.0}).encode("utf-8")
    msg1.headers = []

    msg2 = MagicMock()
    msg2.value = json.dumps({"transaction_id": "TX101", "Amount": 20.0, "Time": 15.0}).encode("utf-8")
    msg2.headers = []

    # The genius part: yield the batch on the first call,
    # then instantly throw CancelledError to break the `while True` loop gracefully.
    mock_consumer_instance.getmany.side_effect = [{MagicMock(): [msg1, msg2]}, asyncio.CancelledError()]
    mock_kafka_consumer.return_value = mock_consumer_instance

    # ==========================================
    # 4. EXECUTE THE ENGINE
    # ==========================================
    await start_inference_engine()

    # ==========================================
    # 5. VERIFY SYSTEM BEHAVIOR
    # ==========================================

    # Verify ML transformations were applied
    assert mock_scaler.transform.called
    assert mock_session_instance.run.called

    # Verify Database interactions (Only the Fraud transaction TX100 should be inserted)
    assert mock_db_cursor.executemany.called

    # Inspect the exact query and data sent to PostgreSQL
    call_args = mock_db_cursor.executemany.call_args[0]
    inserted_records = call_args[1]

    assert len(inserted_records) == 2

    assert inserted_records[0][0] == "TX100"
    assert inserted_records[0][3] == 0.85

    assert inserted_records[1][0] == "TX101"
    assert inserted_records[1][3] == 0.05

    assert mock_db_conn.commit.called

    assert mock_consumer_instance.stop.called
    assert mock_db_cursor.close.called
    assert mock_db_conn.close.called
