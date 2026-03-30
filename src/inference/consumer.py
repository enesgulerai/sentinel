import json
import numpy as np
import pandas as pd
import onnxruntime as ort
from confluent_kafka import Consumer
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "fraud_xgboost.onnx"
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

    # Kafka Consumer Settings
    conf = {
        'bootstrap.servers': 'localhost:19092',
        'group.id': 'fraud-detector-v1',
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(conf)
    consumer.subscribe([TOPIC_NAME])
    logger.info(f"📡 Subscribed to topic: '{TOPIC_NAME}'. Waiting for transactions...")
    logger.info("-" * 60)

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue

            record_value = msg.value().decode('utf-8')
            transaction = json.loads(record_value)

            df = pd.DataFrame([transaction])
            X_input = df.values.astype(np.float32)

            outputs = session.run(None, {input_name: X_input})

            fraud_prob = float(outputs[1][0][1])

            amount = transaction.get('Amount', 0.0)

            if fraud_prob > 0.50:
                logger.warning(f"FRAUD DETECTED! Prob: %{fraud_prob*100:.2f} | Amount: ${amount:.2f}")
            else:
                logger.info(f"Normal Tx. Prob: %{fraud_prob*100:.2f} | Amount: ${amount:.2f}")
    
    except KeyboardInterrupt:
        logger.info("\n Gracefully shutting down the AI engine...")
    finally:
        consumer.close()
        logger.info("Disconnected from Redpanda.")

if __name__ == "__main__":
    start_inference_engine()
