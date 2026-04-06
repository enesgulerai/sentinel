import json
from pathlib import Path

import joblib
import numpy as np
import onnxruntime as ort
from confluent_kafka import Consumer

from src.utils.logger import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "fraud_xgboost.onnx"
SCALER_AMOUNT_PATH = PROJECT_ROOT / "models" / "scaler_amount.joblib"
SCALER_TIME_PATH = PROJECT_ROOT / "models" / "scaler_time.joblib"
TOPIC_NAME = "transactions"


def start_inference_engine():
    logger.info("Starting AI Inference Engine (Kafka Consumer)...")

    # Load ONNX Model
    if not MODEL_PATH.exists():
        logger.error(f"Model not found at {MODEL_PATH}")
        return

    logger.info("Loading highly optimized 176 KB ONNX model...")
    session = ort.InferenceSession(str(MODEL_PATH))
    input_name = session.get_inputs()[0].name

    # Load Scalers
    if not SCALER_AMOUNT_PATH.exists() or not SCALER_TIME_PATH.exists():
        logger.error("Scalers not found. Run save_scalers.py first.")
        return

    logger.info("Loading RobustScalers for data transformation...")
    scaler_amount = joblib.load(SCALER_AMOUNT_PATH)
    scaler_time = joblib.load(SCALER_TIME_PATH)

    # Kafka Consumer Settings
    # Changed group.id to 'v2' to force reading from the earliest offset again
    conf = {
        "bootstrap.servers": "localhost:19092",
        "group.id": "fraud-detector-v2",
        "auto.offset.reset": "earliest",
    }

    consumer = Consumer(conf)
    consumer.subscribe([TOPIC_NAME])
    logger.info(f"Subscribed to topic: '{TOPIC_NAME}'. Waiting for transactions...")
    logger.info("-" * 60)

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue

            record_value = msg.value().decode("utf-8")
            transaction = json.loads(record_value)

            # Extract raw features
            raw_amount = transaction.get("Amount", 0.0)
            raw_time = transaction.get("Time", 0.0)

            # Scale features
            scaled_amount = scaler_amount.transform(np.array([[raw_amount]]))[0][0]
            scaled_time = scaler_time.transform(np.array([[raw_time]]))[0][0]

            # Reconstruct features in the exact training order: [scaled_amount, scaled_time, V1...V28]
            ordered_features = [scaled_amount, scaled_time]
            for i in range(1, 29):
                ordered_features.append(transaction.get(f"V{i}", 0.0))

            X_input = np.array([ordered_features], dtype=np.float32)

            # Run Inference
            outputs = session.run(None, {input_name: X_input})
            fraud_prob = float(outputs[1][0][1])

            # Logging
            if fraud_prob > 0.50:
                logger.warning(
                    f"FRAUD DETECTED! Prob: %{fraud_prob*100:.2f} | Amount: ${raw_amount:.2f}"
                )
            else:
                logger.info(
                    f"Normal Tx. Prob: %{fraud_prob*100:.2f} | Amount: ${raw_amount:.2f}"
                )

    except KeyboardInterrupt:
        logger.info("\nGracefully shutting down the AI engine...")
    finally:
        consumer.close()
        logger.info("Disconnected from Redpanda.")


if __name__ == "__main__":
    start_inference_engine()
