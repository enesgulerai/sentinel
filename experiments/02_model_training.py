import logging
import time
import warnings
from pathlib import Path

# ONNX Conversion Libraries
import onnxmltools
import pandas as pd
from lightgbm import LGBMClassifier
from onnxmltools.convert.common.data_types import FloatTensorType
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
)
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"


def load_split_data(data_dir: Path):
    train_path = data_dir / "train_scaled.csv"
    test_path = data_dir / "test_scaled.csv"

    logger.info(f"Loading split datasets from: {data_dir}")
    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError(
            "Split datasets not found. Run 01_eda_and_preprocessing.py first."
        )

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    # Memory Optimization: Use pop() instead of drop() for O(1) complexity
    y_train = train_df.pop("Class")
    X_train = train_df

    y_test = test_df.pop("Class")
    X_test = test_df

    return X_train, X_test, y_train, y_test


def export_model_to_onnx(
    model, model_name: str, input_feature_count: int, output_dir: Path
):
    """
    Exports the trained tree-based model to the universal ONNX format
    for microsecond-latency inference in production.
    """
    logger.info(f"Exporting {model_name} to ONNX format...")
    output_dir.mkdir(parents=True, exist_ok=True)
    onnx_path = output_dir / f"fraud_{model_name.lower().replace(' ', '_')}.onnx"

    # Define the input type explicitly for ONNX
    initial_type = [("float_input", FloatTensorType([None, input_feature_count]))]

    try:
        if model_name == "LightGBM":
            onnx_model = onnxmltools.convert_lightgbm(model, initial_types=initial_type)
        elif model_name == "XGBoost":
            onnx_model = onnxmltools.convert_xgboost(model, initial_types=initial_type)
        elif model_name == "Random Forest":
            onnx_model = onnxmltools.convert_sklearn(model, initial_types=initial_type)

        onnxmltools.utils.save_model(onnx_model, str(onnx_path))
        logger.info(f"Successfully saved ONNX model to: {onnx_path}")
    except Exception as e:
        logger.error(f"ONNX export failed for {model_name}. Error: {e}")


def run_model_benchmark(X_train, X_test, y_train, y_test):
    logger.info("\n" + "=" * 50)
    logger.info("Starting Model Benchmarking Phase...")
    logger.info("=" * 50)

    neg_class_count = (y_train == 0).sum()
    pos_class_count = (y_train == 1).sum()
    scale_pos_weight_val = neg_class_count / pos_class_count

    logger.info(f"Training Set Shape: {X_train.shape}")
    logger.info(f"Class Imbalance Ratio (Neg/Pos): {scale_pos_weight_val:.2f}")

    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=100, class_weight="balanced", n_jobs=-1, random_state=42
        ),
        "LightGBM": LGBMClassifier(
            n_estimators=100,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
            verbose=-1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=100,
            scale_pos_weight=scale_pos_weight_val,
            random_state=42,
            n_jobs=-1,
            eval_metric="logloss",
        ),
    }

    results = []
    trained_models = {}

    for model_name, model in models.items():
        logger.info(f"Training {model_name}...")

        # 1. Training Time
        start_time = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start_time

        trained_models[model_name] = model

        # 2. Batch Inference (Evaluation Metrics)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        pr_auc = average_precision_score(y_test, y_prob)
        recall = recall_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        # 3. Real-Time (Online) Inference Simulation
        sample_for_online_test = X_test.head(100).values

        online_start_time = time.time()
        for row in sample_for_online_test:
            _ = model.predict(row.reshape(1, -1))
        online_inference_time = (time.time() - online_start_time) / 100 * 1000

        results.append(
            {
                "Model": model_name,
                "PR-AUC": round(pr_auc, 4),
                "Recall": round(recall, 4),
                "Precision": round(precision, 4),
                "F1-Score": round(f1, 4),
                "Train Time (s)": round(train_time, 2),
                "Real-Time Latency (ms/row)": round(online_inference_time, 4),
            }
        )

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by="PR-AUC", ascending=False).reset_index(
        drop=True
    )

    print("\n" + "=" * 80)
    print(" " * 22 + "REAL-TIME BENCHMARK RESULTS")
    print("=" * 80)
    print(results_df.to_string(index=False))
    print("=" * 80)

    # Automatically export the best model to ONNX
    best_model_name = results_df.iloc[0]["Model"]
    best_model_instance = trained_models[best_model_name]
    logger.info(
        f"\nWinner Algorithm: {best_model_name}. Initiating ONNX export pipeline."
    )

    export_model_to_onnx(
        model=best_model_instance,
        model_name=best_model_name,
        input_feature_count=X_train.shape[1],
        output_dir=MODEL_DIR,
    )

    return results_df


if __name__ == "__main__":
    X_train, X_test, y_train, y_test = load_split_data(PROCESSED_DATA_DIR)
    benchmark_results = run_model_benchmark(X_train, X_test, y_train, y_test)
