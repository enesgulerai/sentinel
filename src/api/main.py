import hashlib
import os
from contextlib import asynccontextmanager

import orjson
import redis.asyncio as redis
from confluent_kafka import Producer
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from pyinstrument import Profiler

from src.api.schemas import TransactionRequest
from src.utils.logger import get_logger

# --- DYNAMIC ENVIRONMENT VARIABLES ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
KAFKA_BROKER = os.getenv("REDPANDA_BROKER", "localhost:19092")
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "transactions")

logger = get_logger(__name__)

producer = None
redis_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global producer, redis_client
    logger.info("Starting Sentinel ML API Gateway...")

    # 1. Connect to Redis (For Idempotency)
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    try:
        await redis_client.ping()
        logger.info(f"SUCCESS: Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        logger.error(f"FATAL: Redis connection failed -> {e}")
        raise e

    # 2. Connect to Redpanda (Optimized Producer Settings)
    conf = {
        "bootstrap.servers": KAFKA_BROKER,
        "queue.buffering.max.ms": 5,  # Reduced from default 1000ms for lower latency
        "linger.ms": 0,  # Send messages as soon as possible
        "acks": 1,  # Leader acknowledgement is enough for speed
    }
    try:
        producer = Producer(conf)
        logger.info(f"SUCCESS: Connected to Redpanda at {KAFKA_BROKER}")
    except Exception as e:
        logger.error(f"FATAL: Redpanda connection failed -> {e}")
        raise e

    yield

    logger.info("Shutting down API...")
    if producer:
        producer.flush(timeout=5.0)
    if redis_client:
        await redis_client.aclose()
    logger.info("Shutdown complete.")


app = FastAPI(
    title="Sentinel ML API",
    description="Optimized Fraud Detection Gateway",
    version="1.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def profile_request(request: Request, call_next):
    if request.query_params.get("profile"):
        profiler = Profiler(interval=0.001, async_mode="enabled")
        profiler.start()

        await call_next(request)

        profiler.stop()
        return HTMLResponse(profiler.output_html())

    return await call_next(request)


def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "service": "Sentinel ML API",
        "version": "1.1.0",
    }


@app.post("/api/v1/transactions", status_code=status.HTTP_202_ACCEPTED, tags=["Fraud Detection"])
async def ingest_transaction(transaction: TransactionRequest):
    try:
        # 1. Single model dump (The only one we need)
        tx_data = transaction.model_dump()

        # 2. Optimized Hashing Logic
        # Instead of re-dumping, we copy the dict and remove the ID (O(1) operation)
        hash_data = tx_data.copy()
        hash_data.pop("transaction_id", None)

        # orjson.dumps is significantly faster than json.dumps and returns bytes
        # OPT_SORT_KEYS ensures the hash is deterministic
        hash_payload = orjson.dumps(hash_data, option=orjson.OPT_SORT_KEYS)
        tx_hash = hashlib.sha256(hash_payload).hexdigest()

        redis_key = f"tx:{tx_hash}"

        # 3. Redis Atomic Idempotency Check
        is_new = await redis_client.set(redis_key, "1", ex=10, nx=True)

        if not is_new:
            # Short-circuit: No need to log at INFO level for every duplicate in high-traffic
            logger.debug(f"Duplicate blocked: {tx_hash[:8]}")
            return {
                "status": "ignored",
                "message": "Duplicate transaction detected",
                "source": "Redis",
            }

        # 4. Route to Redpanda (Using pre-dumped data)
        # We reuse tx_data to ensure the downstream gets the transaction_id
        full_payload = orjson.dumps(tx_data)

        producer.produce(TOPIC_NAME, value=full_payload, callback=delivery_report)
        producer.poll(0)  # Non-blocking poll to serve delivery callbacks

        return {
            "status": "success",
            "transaction_id": transaction.transaction_id,
            "amount": tx_data.get("Amount", 0.0),
            "source": "Redpanda",
        }

    except Exception as e:
        logger.error(f"Critical Gateway Error: {e!s}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error") from e
