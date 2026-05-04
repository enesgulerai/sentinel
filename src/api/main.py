import hashlib
import json
import os
from contextlib import asynccontextmanager

import redis.asyncio as redis
from confluent_kafka import Producer
from fastapi import FastAPI, HTTPException, status

from src.api.schemas import TransactionRequest
from src.utils.logger import get_logger

# --- DYNAMIC ENVIRONMENT VARIABLES ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
KAFKA_BROKER = os.getenv("REDPANDA_BROKER", "localhost:19092")

logger = get_logger(__name__)

producer = None
redis_client = None
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "transactions")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global producer, redis_client
    logger.info("Starting FastAPI Gateway...")

    # 1. Connect to Redis (For Idempotency)
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    try:
        await redis_client.ping()
        logger.info(f"SUCCESS: Connected to Redis Cache at {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        logger.error(f"FATAL: Redis connection failed -> {e}")
        raise e

    # 2. Connect to Redpanda/Kafka (The Event Stream)
    conf = {"bootstrap.servers": KAFKA_BROKER}
    try:
        producer = Producer(conf)
        logger.info(f"SUCCESS: Connected to Redpanda Stream at {KAFKA_BROKER}")
    except Exception as e:
        logger.error(f"FATAL: Redpanda connection failed -> {e}")
        raise e  # Fail Fast

    yield

    logger.info("Shutting down API...")
    if producer:
        producer.flush(timeout=5.0)
    if redis_client:
        await redis_client.aclose()
    logger.info("Shutdown complete.")


app = FastAPI(
    title="Sentinel ML API",
    description="Real-time Fraud Detection Gateway with Redis Idempotency and Kafka Event Streaming",
    version="1.0.0",
    lifespan=lifespan,
)


def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "service": "Sentinel ML API Gateway",
        "version": "1.0.0",
    }


@app.post("/api/v1/transactions", status_code=status.HTTP_202_ACCEPTED, tags=["Fraud Detection"])
async def ingest_transaction(transaction: TransactionRequest):
    try:
        # 1. Convert Pydantic model to dictionary (For Redpanda and Response)
        tx_data = transaction.model_dump()

        # 2. Hash payload for idempotency checking (THE REAL ARMOR)
        # We exclude the auto-generated transaction_id to get the true fingerprint of the data
        hash_data = transaction.model_dump(exclude={"transaction_id"})
        hash_payload_str = json.dumps(hash_data, sort_keys=True)
        tx_hash = hashlib.sha256(hash_payload_str.encode("utf-8")).hexdigest()

        # We prefix the hash with "tx:" for clean Redis key management
        redis_key = f"tx:{tx_hash}"

        # 3. Redis Atomic Operation: Check if THIS EXACT PAYLOAD was seen
        is_new_transaction = await redis_client.set(redis_key, "processed", ex=10, nx=True)

        if not is_new_transaction:
            logger.warning(f"DUPLICATE BLOCKED by Redis! Hash: {tx_hash[:8]}")
            return {
                "status": "ignored",
                "message": "Duplicate transaction detected",
                "amount": tx_data.get("Amount", 0.0),
                "source": "Redis",
            }

        # 4. Route to Redpanda Topic
        # Note: We serialize the full tx_data here so downstream services have the transaction_id
        full_payload_str = json.dumps(tx_data, sort_keys=True)
        payload_bytes = full_payload_str.encode("utf-8")

        producer.produce(TOPIC_NAME, value=payload_bytes, callback=delivery_report)
        producer.poll(0)

        logger.info(f"NEW transaction routed to Redpanda. Amount: ${tx_data.get('Amount', 0.0):.2f}")

        return {
            "status": "success",
            "message": "Transaction queued for fraud analysis",
            "transaction_id": transaction.transaction_id,
            "amount": tx_data.get("Amount", 0.0),
            "source": "Redpanda",
        }

    except Exception as e:
        logger.error(f"API Error during transaction ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
