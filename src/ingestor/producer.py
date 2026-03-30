import json
import time
import pandas as pd
from confluent_kafka import Producer
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "creditcard.csv"
TOPIC_NAME = "transactions"

def delivery_report(err, msg):
    """A callback function that checks Kafka whether the message has been received."""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Delivered to topic '{msg.topic()}'")

def start_streaming():
    logger.info("Starting Data Ingestor (Kafka Producer)...")
    
    conf = {'bootstrap.servers': 'localhost:19092'} 
    producer = Producer(conf)

    logger.info(f"Loading data from {DATA_PATH}...")
    if not DATA_PATH.exists():
        logger.error(f"Raw data not found at {DATA_PATH}")
        raise FileNotFoundError(f"Raw data not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    
    if 'Class' in df.columns:
        df = df.drop(columns=['Class'])
        logger.info("Dropped 'Class' column for real-world simulation.")

    logger.info(f"Streaming {len(df)} transactions to topic '{TOPIC_NAME}'...")
    logger.info("-" * 50)
    
    for index, row in df.iterrows():
        transaction = row.to_dict()
        
        producer.produce(
            TOPIC_NAME, 
            value=json.dumps(transaction).encode('utf-8'), 
            callback=delivery_report
        )
        producer.poll(0) 
        
        time.sleep(0.2) 

    producer.flush()
    logger.info("Streaming completed.")

if __name__ == "__main__":
    start_streaming()