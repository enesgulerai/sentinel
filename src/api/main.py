import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from confluent_kafka import Producer

from src.api.schemas import TransactionRequest
from src.utils.logger import get_logger

logger = get_logger(__name__)

producer = None
TOPIC_NAME = "transactions"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    API Lifespan:
    It connects to Kafka at startup and safely transfers the last data remaining
    in memory to Redpanda upon shutdown.
    """
    global producer
    logger.info("Starting FastAPI Gateway and connecting to Redpanda...")

    conf = {'bootstrap.servers': 'localhost:19092'}
    producer = Producer(conf)

    yield

    logger.info("Shutting down API. Flushing remaining messages to Redpanda...")
    producer.flush(timeout=5.0)
    logger.info("Shutdown complete.")

app = FastAPI(
    title="Sentinel API",
    description="Async Real-time Fraud Detection Gateway",
    version="0.3.0",
    lifespan=lifespan
)

def delivery_report(err, msg):
    """An asynchronous callback that checks if the message reached Kafka."""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        pass

@app.get("/", tags=["Health"])
async def root():
    """The main page that checks if the API is up and running."""
    return {
        "status": "online",
        "service": "Sentinel ML API Gateway",
        "version": "0.3.0",
        "docs_url": "/docs"
    }

@app.post("/api/v1/transactions", status_code=status.HTTP_202_ACCEPTED)
async def ingest_transaction(transaction: TransactionRequest):
    """
    It receives transactions from the outside world (POS, Web, Mobile), verifies them with Pydantic,
    and immediately sends them to the Redpanda highway for analysis.
    """

    try:
        tx_data = transaction.model_dump()
        payload = json.dumps(tx_data).encode('utf-8')

        producer.produce(
            TOPIC_NAME,
            value=payload,
            callback=delivery_report
        )

        producer.poll(0)

        logger.info(f"Transaction received via API. Amount: ${tx_data['Amount']:.2f}")

        return {
            "status": "success",
            "message": "Transaction queued for fraud analysis",
            "amount": tx_data["Amount"]
        }
    
    except Exception as e:
        logger.error(f"Failed to ingest transaction via API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during event streaming"
        )