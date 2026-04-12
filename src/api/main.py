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
# K8s ConfigMap üzerinden gelecek, bulamazsa lokale (localhost) dönecek
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Helm config.yaml dosyamızda KAFKA_BROKER_URL olarak tanımlamıştık
KAFKA_BROKER = os.getenv("REDPANDA_BROKER", "localhost:19092")

logger = get_logger(__name__)

producer = None
redis_client = None
TOPIC_NAME = "transactions"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global producer, redis_client
    logger.info("Starting FastAPI Gateway...")

    # 1. Connect to Redis (The Guardian)
    redis_client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
    )
    try:
        await redis_client.ping()
        logger.info(f"SUCCESS: Connected to Redis Cache at {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        logger.error(f"Redis connection failed at {REDIS_HOST}:{REDIS_PORT} -> {e}")

    # 2. Connect to Redpanda (The Highway)
    conf = {"bootstrap.servers": KAFKA_BROKER}
    try:
        producer = Producer(conf)
        logger.info(f"SUCCESS: Connected to Redpanda Stream at {KAFKA_BROKER}")
    except Exception as e:
        logger.error(f"Redpanda connection failed at {KAFKA_BROKER} -> {e}")

    yield

    logger.info("Shutting down API...")
    if producer:
        producer.flush(timeout=5.0)
    if redis_client:
        await redis_client.aclose()
    logger.info("Shutdown complete.")


app = FastAPI(
    title="Sentinel ML API",
    description="Real-time Fraud Detection with Redis Idempotency",
    version="0.4.0",
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
        "version": "0.4.0",
    }


@app.post("/api/v1/transactions", status_code=status.HTTP_202_ACCEPTED)
async def ingest_transaction(transaction: TransactionRequest):
    try:
        tx_data = transaction.model_dump()

        # 1. Create a unique deterministic hash for the transaction payload
        payload_str = json.dumps(tx_data, sort_keys=True)
        tx_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        # 2. REDIS ATOMIC OPERATION
        is_new_transaction = await redis_client.set(
            tx_hash, "processed", ex=10, nx=True
        )

        if not is_new_transaction:
            # BLOCKED BY REDIS
            logger.warning(f"DUPLICATE BLOCKED by Redis! Hash: {tx_hash[:8]}")
            return {
                "status": "ignored",
                "message": "Duplicate transaction detected",
                "amount": tx_data["Amount"],
                "source": "Redis Cache (Duplicate)",
            }

        # 3. IF NEW: Route to Redpanda
        payload_bytes = payload_str.encode("utf-8")
        producer.produce(TOPIC_NAME, value=payload_bytes, callback=delivery_report)
        producer.poll(0)

        logger.info(
            f"NEW transaction routed to Redpanda. Amount: ${tx_data['Amount']:.2f}"
        )

        return {
            "status": "success",
            "message": "Transaction queued for fraud analysis",
            "amount": tx_data["Amount"],
            "source": "Redpanda Stream (New)",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
