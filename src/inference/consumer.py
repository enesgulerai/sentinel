import asyncio
import contextlib
import os
import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
import onnxruntime as ort
import orjson
import psycopg
from aiokafka import AIOKafkaConsumer

from src.utils.logger import get_logger

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
logger = get_logger(__name__)

if Path("/app/models").exists():
    models_dir = Path("/app/models")
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    models_dir = PROJECT_ROOT / "models"

onnx_files = list(models_dir.glob("*.onnx"))
if not onnx_files:
    raise FileNotFoundError(f"No .onnx model found in {models_dir}. Run training pipeline first.")

MODEL_PATH = sorted(onnx_files)[-1]
SCALER_PATH = models_dir / "robust_scaler.joblib"

REDPANDA_BROKER = os.getenv("REDPANDA_BROKER", "localhost:19092")
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "clean-events")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sentinel_user:secure_password@localhost:5432/sentinel_db")

BATCH_SIZE = 5000
POLL_TIMEOUT_MS = 1000

FEATURE_KEYS = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]


def run_onnx_inference_sync(session, input_name, scaler, batch_data):
    """This function runs in a separate thread to freeze the main event loop."""
    X_batch = np.array(batch_data, dtype=np.float32)

    time_amount_cols = X_batch[:, [0, 29]]
    scaled_time_amount = scaler.transform(time_amount_cols)
    X_batch[:, 0] = scaled_time_amount[:, 0]
    X_batch[:, 29] = scaled_time_amount[:, 1]

    outputs = session.run(None, {input_name: X_batch})
    return outputs[1]


async def start_inference_engine():
    logger.info("Starting Async AI Inference Engine (Zero-Block Version)...")

    logger.info("Loading highly optimized ONNX model & Scaler...")
    session = ort.InferenceSession(str(MODEL_PATH))
    input_name = session.get_inputs()[0].name
    scaler = joblib.load(SCALER_PATH)

    try:
        db_conn = await psycopg.AsyncConnection.connect(DATABASE_URL)
        db_cursor = db_conn.cursor()
        logger.info("SUCCESS: Connected to Postgres database asynchronously.")
    except Exception as e:
        logger.error(f"FATAL: Database connection failed -> {e}")
        return

    consumer = AIOKafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=REDPANDA_BROKER,
        group_id="fraud-detector-v3",
        auto_offset_reset="earliest",
        max_partition_fetch_bytes=5242880,
        fetch_max_wait_ms=50,
    )

    await consumer.start()
    logger.info(f"Subscribed to topic: '{TOPIC_NAME}'. Awaiting validated data from Rust...")
    logger.info("-" * 60)

    try:
        while True:
            result = await consumer.getmany(timeout_ms=POLL_TIMEOUT_MS, max_records=BATCH_SIZE)

            if not result:
                continue

            batch_data = []
            valid_msgs = []

            for _tp, messages in result.items():
                for msg in messages:
                    try:
                        transaction = orjson.loads(msg.value)
                        valid_msgs.append(transaction)

                        batch_data.append([transaction[k] for k in FEATURE_KEYS])
                    except Exception as e:
                        logger.warning(f"Deserialization failed: {e}")
                        continue

            if not batch_data:
                continue

            try:
                fraud_probs = await asyncio.to_thread(run_onnx_inference_sync, session, input_name, scaler, batch_data)

                # Post-Processing
                db_records = []
                frauds_in_batch = 0

                for i, prob_dict in enumerate(fraud_probs):
                    fraud_prob = prob_dict.get(1, 0.0) if isinstance(prob_dict, dict) else prob_dict[1]

                    if fraud_prob > 0.50:
                        frauds_in_batch += 1
                        logger.warning(
                            f"FRAUD DETECTED! Prob: {fraud_prob * 100:.2f}% | Amount: ${valid_msgs[i]['Amount']:.2f} | TX: {valid_msgs[i]['transaction_id'][:8]}"
                        )

                    db_records.append(
                        (
                            valid_msgs[i]["transaction_id"],
                            valid_msgs[i].get("user_id", "anonymous"),
                            valid_msgs[i]["Amount"],
                            float(fraud_prob),
                        )
                    )

                # Database Write
                if db_records:
                    insert_query = """
                        INSERT INTO transactions (transaction_id, user_id, amount, risk_score)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (transaction_id) DO NOTHING;
                    """
                    await db_cursor.executemany(insert_query, db_records)
                    await db_conn.commit()

                logger.info(f"Processed batch of {len(valid_msgs)} txs. Frauds found: {frauds_in_batch}. Saved to DB.")

            except Exception as process_err:
                logger.error(f"Batch Processing Error: {process_err}")
                await db_conn.rollback()

    except asyncio.CancelledError:
        logger.info("\nGracefully shutting down the AI engine (Cancelled)...")
    finally:
        await consumer.stop()
        await db_cursor.close()
        await db_conn.close()
        logger.info("Disconnected from Redpanda and Postgres.")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        if sys.platform != "win32":
            try:
                import uvloop

                uvloop.install()
                logger.info("uvloop engine activated for high-performance I/O.")
            except ImportError:
                logger.info("uvloop not available. Using standard asyncio.")
        else:
            logger.info("Windows environment detected. Using standard asyncio.")

        asyncio.run(start_inference_engine())
