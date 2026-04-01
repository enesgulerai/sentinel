import json
import hashlib
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from confluent_kafka import Producer
import redis.asyncio as redis

from src.api.schemas import TransactionRequest
from src.utils.logger import get_logger

logger = get_logger(__name__)

producer = None
redis_client = None
TOPIC_NAME = "transactions"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global producer, redis_client
    logger.info("Starting FastAPI Gateway...")
    
    # 1. Connect to Redis (The Guardian)
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    try:
        await redis_client.ping()
        logger.info("SUCCESS: Connected to Redis Cache.")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        
    # 2. Connect to Redpanda (The Highway)
    conf = {'bootstrap.servers': 'localhost:19092'}
    producer = Producer(conf)
    logger.info("SUCCESS: Connected to Redpanda Stream.")
    
    yield
    
    logger.info("Shutting down API...")
    producer.flush(timeout=5.0)
    await redis_client.aclose()
    logger.info("Shutdown complete.")

app = FastAPI(
    title="Sentinel ML API",
    description="Real-time Fraud Detection with Redis Idempotency",
    version="0.4.0",
    lifespan=lifespan
)

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")

@app.get("/", tags=["Health"])
async def root():
    return {"status": "online", "service": "Sentinel ML API Gateway", "version": "0.4.0"}

@app.post("/api/v1/transactions", status_code=status.HTTP_202_ACCEPTED)
async def ingest_transaction(transaction: TransactionRequest):
    try:
        tx_data = transaction.model_dump()
        
        # 1. Create a unique deterministic hash for the transaction payload
        payload_str = json.dumps(tx_data, sort_keys=True)
        tx_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
        
        # 2. REDIS ATOMIC OPERATION
        is_new_transaction = await redis_client.set(tx_hash, "processed", ex=10, nx=True)
        
        if not is_new_transaction:
            # BLOCKED BY REDIS
            logger.warning(f"DUPLICATE BLOCKED by Redis! Hash: {tx_hash[:8]}")
            return {
                "status": "ignored",
                "message": "Duplicate transaction detected",
                "amount": tx_data["Amount"],
                "source": "Redis Cache (Duplicate)"
            }
            
        # 3. IF NEW: Route to Redpanda
        payload_bytes = payload_str.encode('utf-8')
        producer.produce(TOPIC_NAME, value=payload_bytes, callback=delivery_report)
        producer.poll(0)
        
        logger.info(f"NEW transaction routed to Redpanda. Amount: ${tx_data['Amount']:.2f}")
        
        return {
            "status": "success",
            "message": "Transaction queued for fraud analysis",
            "amount": tx_data["Amount"],
            "source": "Redpanda Stream (New)"
        }
        
    except Exception as e:
        logger.error(f"Failed to ingest transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during event streaming"
        )