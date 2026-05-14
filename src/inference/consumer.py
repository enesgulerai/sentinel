import asyncio
import contextlib
import json
import os
import warnings
from pathlib import Path

import joblib
import numpy as np
import onnxruntime as ort
import psycopg
from aiokafka import AIOKafkaConsumer

from src.utils.logger import get_logger

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "fraud_xgboost.onnx"
SCALER_PATH = PROJECT_ROOT / "models" / "robust_scaler.joblib"

REDPANDA_BROKER = os.getenv("REDPANDA_BROKER", "localhost:19092")
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "transactions")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sentinel:sentinel_password@localhost:5432/sentinel_db")

BATCH_SIZE = 500
POLL_TIMEOUT_MS = 1000


async def start_inference_engine():
    logger.info("Starting Async AI Inference Engine (AIOKafka Consumer)...")

    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        logger.error("Model or Scaler not found. Run pipeline first.")
        return

    logger.info("Loading highly optimized ONNX model & Scaler...")
    session = ort.InferenceSession(str(MODEL_PATH))
    input_name = session.get_inputs()[0].name
    scaler = joblib.load(SCALER_PATH)

    try:
        db_conn = await psycopg.AsyncConnection.connect(DATABASE_URL)
        db_cursor = db_conn.cursor()
        logger.info("SUCCESS: Connected to Postgres database asynchronously.")
    except Exception as e:
        logger.error(f"FATAL: Database connection failed -> {e}")
        return

    consumer = AIOKafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=REDPANDA_BROKER,
        group_id="fraud-detector-v2",
        auto_offset_reset="earliest",
        max_partition_fetch_bytes=1048576,
        fetch_max_wait_ms=100,
    )

    await consumer.start()
    logger.info(f"Subscribed to topic: '{TOPIC_NAME}'. Awaiting data...")
    logger.info("-" * 60)

    try:
        while True:
            result = await consumer.getmany(timeout_ms=POLL_TIMEOUT_MS, max_records=BATCH_SIZE)

            if not result:
                continue

            batch_data = []
            valid_msgs = []

            for _tp, messages in result.items():
                for msg in messages:
                    try:
                        transaction = json.loads(msg.value.decode("utf-8"))

                        row = [transaction.get("Time", 0.0)]
                        for i in range(1, 29):
                            row.append(transaction.get(f"V{i}", 0.0))
                        row.append(transaction.get("Amount", 0.0))

                        batch_data.append(row)
                        valid_msgs.append(transaction)
                    except Exception as e:
                        logger.warning(f"Failed to parse message: {e}")
                        continue

            if not batch_data:
                continue

            X_batch = np.array(batch_data, dtype=np.float32)

            time_amount_cols = X_batch[:, [0, 29]]
            scaled_time_amount = scaler.transform(time_amount_cols)

            X_batch[:, 0] = scaled_time_amount[:, 0]
            X_batch[:, 29] = scaled_time_amount[:, 1]

            outputs = session.run(None, {input_name: X_batch})
            fraud_probs = outputs[1]

            db_records = []
            frauds_in_batch = 0

            for i, prob_dict in enumerate(fraud_probs):
                fraud_prob = prob_dict.get(1, 0.0) if isinstance(prob_dict, dict) else prob_dict[1]
                amt = valid_msgs[i].get("Amount", 0.0)
                tx_id = valid_msgs[i].get("transaction_id", "Unknown")
                user_id = valid_msgs[i].get("user_id", "anonymous")

                if fraud_prob > 0.50:
                    frauds_in_batch += 1
                    logger.warning(
                        f"FRAUD DETECTED! Prob: %{fraud_prob * 100:.2f} | Amount: ${amt:.2f} | TX: {tx_id[:8]}"
                    )

                db_records.append((tx_id, user_id, amt, float(fraud_prob)))

            if db_records:
                insert_query = """
                    INSERT INTO transactions (transaction_id, user_id, amount, risk_score)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (transaction_id) DO NOTHING;
                """
                try:
                    await db_cursor.executemany(insert_query, db_records)
                    await db_conn.commit()
                except Exception as db_err:
                    logger.error(f"Database Insert Error: {db_err}")
                    await db_conn.rollback()

            if len(valid_msgs) > 50 or frauds_in_batch > 0:
                logger.info(f"Processed batch of {len(valid_msgs)} txs. Frauds found: {frauds_in_batch}. Saved to DB.")

    except asyncio.CancelledError:
        logger.info("\nGracefully shutting down the AI engine (Cancelled)...")
    finally:
        await consumer.stop()
        await db_cursor.close()
        await db_conn.close()
        logger.info("Disconnected from Redpanda and Postgres.")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(start_inference_engine())
