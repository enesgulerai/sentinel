import json
import os
import time
from pathlib import Path

import pandas as pd
from confluent_kafka import Producer

from src.utils.logger import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "creditcard.csv"

REDPANDA_BROKER = os.getenv("REDPANDA_BROKER", "localhost:19092")
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "transactions")


def delivery_report(err, msg):
    """A callback function that checks Kafka whether the message has been received."""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        # Reduced logging level to DEBUG for delivery reports to avoid spamming the console
        # You can change it to info if you want to see every single delivery confirmation
        logger.debug(f"Delivered to topic '{msg.topic()}'")


def start_streaming():
    logger.info("Starting Data Ingestor (Kafka Producer)...")

    conf = {"bootstrap.servers": REDPANDA_BROKER}
    producer = Producer(conf)

    logger.info(f"Loading data from {DATA_PATH}...")
    if not DATA_PATH.exists():
        logger.error(f"Raw data not found at {DATA_PATH}. Run pipeline first.")
        raise FileNotFoundError(f"Raw data not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    if "Class" in df.columns:
        df = df.drop(columns=["Class"])
        logger.info("Dropped 'Class' column for real-world simulation.")

    logger.info(
        f"Streaming {len(df)} transactions to topic '{TOPIC_NAME}' at {REDPANDA_BROKER}..."
    )
    logger.info("-" * 60)

    transactions = df.to_dict(orient="records")

    try:
        for transaction in transactions:
            producer.produce(
                TOPIC_NAME,
                value=json.dumps(transaction).encode("utf-8"),
                callback=delivery_report,
            )
            producer.poll(0)

            # Simulate real-time stream (5 transactions per second)
            time.sleep(0.2)

    except KeyboardInterrupt:
        logger.info("\nStopping the stream gracefully...")
    finally:
        logger.info("Flushing remaining messages to Redpanda...")
        producer.flush()
        logger.info("Streaming completed. Producer disconnected.")


if __name__ == "__main__":
    start_streaming()
