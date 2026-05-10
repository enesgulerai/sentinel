import json
import os
import warnings
from pathlib import Path

import joblib
import numpy as np
import onnxruntime as ort
import psycopg2
from confluent_kafka import Consumer
from psycopg2 import extras

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
POLL_TIMEOUT = 1.0


def start_inference_engine():
    logger.info("Starting AI Inference Engine (Kafka Consumer)...")

    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        logger.error("Model or Scaler not found. Run pipeline first.")
        return

    logger.info("Loading highly optimized ONNX model & Scaler...")
    session = ort.InferenceSession(str(MODEL_PATH))
    input_name = session.get_inputs()[0].name
    scaler = joblib.load(SCALER_PATH)

    # 1. Connect to Postgres
    try:
        db_conn = psycopg2.connect(DATABASE_URL)
        db_cursor = db_conn.cursor()
        logger.info("SUCCESS: Connected to Postgres database.")
    except Exception as e:
        logger.error(f"FATAL: Database connection failed -> {e}")
        return

    # Kafka Consumer Settings (Optimize for Throughput)
    conf = {
        "bootstrap.servers": REDPANDA_BROKER,
        "group.id": "fraud-detector-v2",
        "auto.offset.reset": "earliest",
        "fetch.min.bytes": 100000,
        "fetch.wait.max.ms": 100,
    }

    consumer = Consumer(conf)
    consumer.subscribe([TOPIC_NAME])
    logger.info(f"Subscribed to topic: '{TOPIC_NAME}'. Awaiting data...")
    logger.info("-" * 60)

    try:
        while True:
            msgs = consumer.consume(num_messages=BATCH_SIZE, timeout=POLL_TIMEOUT)

            if not msgs:
                continue

            batch_data = []
            valid_msgs = []

            for msg in msgs:
                if msg.error():
                    continue

                transaction = json.loads(msg.value().decode("utf-8"))

                row = [transaction.get("Time", 0.0)]
                for i in range(1, 29):
                    row.append(transaction.get(f"V{i}", 0.0))
                row.append(transaction.get("Amount", 0.0))

                batch_data.append(row)
                valid_msgs.append(transaction)

            if not batch_data:
                continue

            # Model Inference
            X_batch = np.array(batch_data, dtype=np.float32)

            time_amount_cols = X_batch[:, [0, 29]]
            scaled_time_amount = scaler.transform(time_amount_cols)

            X_batch[:, 0] = scaled_time_amount[:, 0]
            X_batch[:, 29] = scaled_time_amount[:, 1]

            outputs = session.run(None, {input_name: X_batch})
            fraud_probs = outputs[1]

            # 2. Prepare Data for Bulk Insert
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

            # 3. Execute Bulk Insert to Postgres
            if db_records:
                insert_query = """
                    INSERT INTO transactions (transaction_id, user_id, amount, risk_score)
                    VALUES %s
                    ON CONFLICT (transaction_id) DO NOTHING;
                """
                try:
                    extras.execute_values(db_cursor, insert_query, db_records)
                    db_conn.commit()
                except Exception as db_err:
                    logger.error(f"Database Insert Error: {db_err}")
                    db_conn.rollback()

            if len(valid_msgs) > 50 or frauds_in_batch > 0:
                logger.info(f"Processed batch of {len(valid_msgs)} txs. Frauds found: {frauds_in_batch}. Saved to DB.")

    except KeyboardInterrupt:
        logger.info("\nGracefully shutting down the AI engine...")
    finally:
        consumer.close()
        db_cursor.close()
        db_conn.close()
        logger.info("Disconnected from Redpanda and Postgres.")


if __name__ == "__main__":
    start_inference_engine()
