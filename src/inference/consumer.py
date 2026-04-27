import json
import os
import warnings
from pathlib import Path

import joblib
import numpy as np
import onnxruntime as ort
from confluent_kafka import Consumer

from src.utils.logger import get_logger

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "fraud_xgboost.onnx"
SCALER_PATH = PROJECT_ROOT / "models" / "robust_scaler.joblib"

REDPANDA_BROKER = os.getenv("REDPANDA_BROKER", "localhost:19092")
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "transactions")

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

            X_batch = np.array(batch_data, dtype=np.float32)

            time_amount_cols = X_batch[:, [0, 29]]
            scaled_time_amount = scaler.transform(time_amount_cols)

            X_batch[:, 0] = scaled_time_amount[:, 0]
            X_batch[:, 29] = scaled_time_amount[:, 1]

            outputs = session.run(None, {input_name: X_batch})
            fraud_probs = outputs[1]

            frauds_in_batch = 0
            for i, prob_dict in enumerate(fraud_probs):
                fraud_prob = prob_dict.get(1, 0.0) if isinstance(prob_dict, dict) else prob_dict[1]

                if fraud_prob > 0.50:
                    frauds_in_batch += 1
                    amt = valid_msgs[i].get("Amount", 0.0)
                    tx_id = valid_msgs[i].get("transaction_id", "Unknown")
                    logger.warning(
                        f"FRAUD DETECTED! Prob: %{fraud_prob * 100:.2f} | Amount: ${amt:.2f} | TX: {tx_id[:8]}"
                    )

            if len(valid_msgs) > 50:
                logger.info(f"Processed batch of {len(valid_msgs)} txs. Frauds found: {frauds_in_batch}")

    except KeyboardInterrupt:
        logger.info("\nGracefully shutting down the AI engine...")
    finally:
        consumer.close()
        logger.info("Disconnected from Redpanda.")


if __name__ == "__main__":
    start_inference_engine()
