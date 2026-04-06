import os
import warnings
from pathlib import Path

import onnxmltools
import pandas as pd
from onnxmltools.convert.common.data_types import FloatTensorType
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "creditcard_scaled.csv"
MODEL_DIR = PROJECT_ROOT / "models"


def train_and_export_model():
    print("Loading full dataset for production training...")
    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at: {PROCESSED_DATA_PATH}")

    df = pd.read_csv(PROCESSED_DATA_PATH)
    X = df.drop("Class", axis=1)
    y = df["Class"]

    neg_class_count = (y == 0).sum()
    pos_class_count = (y == 1).sum()
    scale_pos_weight_val = neg_class_count / pos_class_count

    print(f"Training final XGBoost model on {len(X)} records...")
    print(f"Applied scale_pos_weight: {scale_pos_weight_val:.2f}")

    model = XGBClassifier(
        n_estimators=100,
        scale_pos_weight=scale_pos_weight_val,
        random_state=42,
        n_jobs=-1,
        eval_metric="logloss",
    )

    # CRITICAL FIX: Strip Pandas column names by passing NumPy arrays
    model.fit(X.values, y.values)

    print("\nConverting XGBoost model to ONNX format...")
    initial_types = [("float_input", FloatTensorType([None, X.shape[1]]))]
    onnx_model = onnxmltools.convert_xgboost(model, initial_types=initial_types)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    onnx_path = MODEL_DIR / "fraud_xgboost.onnx"

    onnxmltools.utils.save_model(onnx_model, str(onnx_path))

    model_size_kb = os.path.getsize(onnx_path) / 1024
    print("=" * 50)
    print(f"SUCCESS: Model exported to {onnx_path}")
    print(f"FINAL ONNX MODEL SIZE: {model_size_kb:.2f} KB")
    print("=" * 50)


if __name__ == "__main__":
    train_and_export_model()
