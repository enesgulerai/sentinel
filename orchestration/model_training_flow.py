import os
import warnings
from datetime import datetime
from pathlib import Path

import onnxmltools
import pandas as pd
from onnxmltools.convert.common.data_types import FloatTensorType
from prefect import flow, task
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "creditcard_scaled.csv"
MODEL_DIR = PROJECT_ROOT / "models"


def generate_run_name():
    return datetime.now().strftime("%d-%m-%y_Model-Training_%H-%M")


@task(name="Load Production Data", retries=2)
def load_data(data_path: Path):
    print("Loading full dataset for production training...")
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at: {data_path}")

    df = pd.read_csv(data_path)
    X = df.drop("Class", axis=1)
    y = df["Class"]
    return X, y


@task(name="Train XGBoost Model")
def train_model(X, y):
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

    model.fit(X.values, y.values)
    return model


@task(name="Export Model to ONNX")
def export_to_onnx(model, num_features: int, output_dir: Path, save_model: bool = False):
    if not save_model:
        print("Skipping model export phase (save_model=False).")
        return None

    print("\nConverting XGBoost model to ONNX format...")
    initial_types = [("float_input", FloatTensorType([None, num_features]))]
    onnx_model = onnxmltools.convert_xgboost(model, initial_types=initial_types)

    output_dir.mkdir(parents=True, exist_ok=True)
    onnx_path = output_dir / "fraud_xgboost.onnx"

    onnxmltools.utils.save_model(onnx_model, str(onnx_path))

    model_size_kb = os.path.getsize(onnx_path) / 1024
    print("=" * 50)
    print(f"SUCCESS: Model exported to {onnx_path}")
    print(f"FINAL ONNX MODEL SIZE: {model_size_kb:.2f} KB")
    print("=" * 50)

    return onnx_path


@flow(name="Model Training Pipeline", flow_run_name=generate_run_name)
def model_training_flow(save_model: bool = False):
    X, y = load_data(PROCESSED_DATA_PATH)
    model = train_model(X, y)

    num_features = X.shape[1]
    export_to_onnx(model, num_features, MODEL_DIR, save_model=save_model)


if __name__ == "__main__":
    model_training_flow(save_model=False)
