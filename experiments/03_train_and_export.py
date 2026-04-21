import logging
import os
import warnings
from datetime import datetime
from pathlib import Path

import onnxmltools
import pandas as pd
from onnxmltools.convert.common.data_types import FloatTensorType
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "train_scaled.csv"
MODEL_DIR = PROJECT_ROOT / "models"


def train_and_export_model():
    logger.info("Loading dataset for production-level training...")

    # Note: For the final production model, we usually combine train + test.
    # For simplicity, we'll assume the train_scaled.csv is our primary source here.
    if not PROCESSED_DATA_PATH.exists():
        logger.error(f"Processed data not found at: {PROCESSED_DATA_PATH}")
        raise FileNotFoundError("Run 01_eda_and_preprocessing.py first.")

    df = pd.read_csv(PROCESSED_DATA_PATH)

    # Memory Optimization: O(1) target extraction
    y = df.pop("Class")
    X = df

    neg_class_count = (y == 0).sum()
    pos_class_count = (y == 1).sum()
    scale_pos_weight_val = neg_class_count / pos_class_count

    logger.info(f"Training final XGBoost model on {len(X)} records...")
    logger.info(f"Final scale_pos_weight: {scale_pos_weight_val:.2f}")

    model = XGBClassifier(
        n_estimators=100,
        scale_pos_weight=scale_pos_weight_val,
        random_state=42,
        n_jobs=-1,
        eval_metric="logloss",
    )

    # Use .values to strip metadata and prevent serving skew
    model.fit(X.values, y.values)

    logger.info("Converting model to ONNX format...")
    initial_types = [("float_input", FloatTensorType([None, X.shape[1]]))]
    onnx_model = onnxmltools.convert_xgboost(model, initial_types=initial_types)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # Versioning: models/fraud_xgboost_20260421.onnx
    timestamp = datetime.now().strftime("%Y%m%d")
    onnx_path = MODEL_DIR / f"fraud_xgboost_{timestamp}.onnx"
    latest_path = MODEL_DIR / "fraud_xgboost_latest.onnx"

    # Save versioned model
    onnxmltools.utils.save_model(onnx_model, str(onnx_path))
    # Also save as 'latest' for the API to pick up easily
    onnxmltools.utils.save_model(onnx_model, str(latest_path))

    model_size_kb = os.path.getsize(onnx_path) / 1024
    logger.info("=" * 50)
    logger.info(f"SUCCESS: Model exported to {onnx_path}")
    logger.info(f"FINAL ONNX MODEL SIZE: {model_size_kb:.2f} KB")
    logger.info("=" * 50)


if __name__ == "__main__":
    train_and_export_model()
