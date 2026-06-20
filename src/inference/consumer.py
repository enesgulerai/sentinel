import asyncio
import contextlib
import os
import warnings
from pathlib import Path

import joblib
import numpy as np
import onnxruntime as ort
import orjson
import psycopg
import uvloop
from aiokafka import AIOKafkaConsumer
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.propagate import extract
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

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
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sentinel:sentinel_password@localhost:5432/sentinel_db")

BATCH_SIZE = 500
POLL_TIMEOUT_MS = 1000


def init_tracer():
    resource = Resource.create({"service.name": "sentinel-inference-consumer"})
    provider = TracerProvider(resource=resource)
    jaeger_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    exporter = OTLPSpanExporter(endpoint=jaeger_endpoint, insecure=True)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(__name__)


tracer = init_tracer()


async def start_inference_engine():
    logger.info("Starting Async AI Inference Engine...")

    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        logger.error(f"Model or Scaler not found at paths: {MODEL_PATH}, {SCALER_PATH}. Run pipeline first.")
        return

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
        group_id="fraud-detector-v2",
        auto_offset_reset="earliest",
        max_partition_fetch_bytes=1048576,
        fetch_max_wait_ms=5,
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
            batch_contexts = []

            for _tp, messages in result.items():
                for msg in messages:
                    carrier = {}
                    if msg.headers:
                        for key, value in msg.headers:
                            carrier[key] = value.decode("utf-8")

                    ctx = extract(carrier)

                    try:
                        transaction = orjson.loads(msg.value)

                        row = [transaction.get("Time", 0.0)]
                        for i in range(1, 29):
                            row.append(transaction.get(f"V{i}", 0.0))
                        row.append(transaction.get("Amount", 0.0))

                        batch_data.append(row)
                        valid_msgs.append(transaction)
                        batch_contexts.append(ctx)
                    except Exception as e:
                        logger.warning(f"Deserialization failed despite validation: {e}")
                        continue

            # --- OTEL SUB-SPAN STRUCTURE ---
            if not batch_data:
                continue

            main_ctx = batch_contexts[0] if batch_contexts else None

            with tracer.start_as_current_span("Consumer-Process-Batch", context=main_ctx) as main_span:
                try:
                    # 1. DATA PREP AND SCALING
                    with tracer.start_as_current_span("ML-Data-Prep"):
                        X_batch = np.array(batch_data, dtype=np.float32)
                        time_amount_cols = X_batch[:, [0, 29]]
                        scaled_time_amount = scaler.transform(time_amount_cols)

                        X_batch[:, 0] = scaled_time_amount[:, 0]
                        X_batch[:, 29] = scaled_time_amount[:, 1]

                    # 2. AI INFERENCE (ONNX)
                    with tracer.start_as_current_span("ML-Inference-ONNX"):
                        outputs = session.run(None, {input_name: X_batch})
                        fraud_probs = outputs[1]

                    # 3. DATA TRANSFORMATION AND POST-PROCESSING
                    with tracer.start_as_current_span("Post-Processing"):
                        db_records = []
                        frauds_in_batch = 0

                        for i, prob_dict in enumerate(fraud_probs):
                            fraud_prob = prob_dict.get(1, 0.0) if isinstance(prob_dict, dict) else prob_dict[1]
                            amt = valid_msgs[i].get("Amount", 0.0)
                            tx_id = valid_msgs[i].get("transaction_id", "Unknown")
                            user_id = valid_msgs[i].get("user_id", "anonymous")

                            if fraud_prob > 0.50:
                                frauds_in_batch += 1
                                logger.warning(
                                    f"FRAUD DETECTED! Prob: {fraud_prob * 100:.2f}% | Amount: ${amt:.2f} | TX: {tx_id[:8]}"
                                )

                            db_records.append((tx_id, user_id, amt, float(fraud_prob)))

                    # 4. DATABASE WRITE (Async Postgres)
                    if db_records:
                        with tracer.start_as_current_span("DB-Write-Postgres"):
                            insert_query = """
                                INSERT INTO transactions (transaction_id, user_id, amount, risk_score)
                                VALUES (%s, %s, %s, %s)
                                ON CONFLICT (transaction_id) DO NOTHING;
                            """
                            await db_cursor.executemany(insert_query, db_records)
                            await db_conn.commit()

                    main_span.set_status(trace.Status(trace.StatusCode.OK))

                    if len(valid_msgs) > 0:
                        logger.info(
                            f"Processed batch of {len(valid_msgs)} txs. Frauds found: {frauds_in_batch}. Saved to DB."
                        )

                except Exception as process_err:
                    logger.error(f"Batch Processing Error: {process_err}")
                    await db_conn.rollback()
                    main_span.set_status(trace.Status(trace.StatusCode.ERROR, str(process_err)))
                    main_span.record_exception(process_err)

    except asyncio.CancelledError:
        logger.info("\nGracefully shutting down the AI engine (Cancelled)...")
    finally:
        await consumer.stop()
        await db_cursor.close()
        await db_conn.close()
        logger.info("Disconnected from Redpanda and Postgres.")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        try:
            import uvloop

            uvloop.install()
            logger.info("uvloop engine activated for high-performance I/O.")
        except ImportError:
            logger.info("uvloop not available (likely Windows dev environment). Using standard asyncio.")

        asyncio.run(start_inference_engine())
