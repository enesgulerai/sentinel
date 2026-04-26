import os
import warnings
from datetime import datetime
from pathlib import Path

import onnxmltools
import pandas as pd
from onnxmltools.convert.common.data_types import FloatTensorType
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score
from xgboost import XGBClassifier

from src.utils.logger import get_logger

warnings.filterwarnings("ignore")
logger = get_logger(__name__)


class ModelTrainer:
    """
    Production-grade model training module.
    Trains the champion model (XGBoost) using raw numpy arrays to prevent serving skew,
    and exports it to ONNX format with versioning.
    """

    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.processed_data_dir = self.project_root / "data" / "processed"
        self.model_dir = self.project_root / "models"

        self.train_path = self.processed_data_dir / "train_scaled.csv"
        self.test_path = self.processed_data_dir / "test_scaled.csv"
        self.target_col = "Class"

    def _load_data(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Loads the preprocessed train and test datasets."""
        logger.info(f"Loading split datasets from: {self.processed_data_dir}")
        if not self.train_path.exists() or not self.test_path.exists():
            raise FileNotFoundError("Processed datasets not found. Run preprocessing first.")

        train_df = pd.read_csv(self.train_path)
        test_df = pd.read_csv(self.test_path)

        y_train = train_df.pop(self.target_col)
        X_train = train_df

        y_test = test_df.pop(self.target_col)
        X_test = test_df

        return X_train, X_test, y_train, y_test

    def _train_and_evaluate(self, X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series):
        """Trains the XGBoost model and calculates production metrics."""
        neg_class_count = (y_train == 0).sum()
        pos_class_count = (y_train == 1).sum()
        scale_pos_weight_val = neg_class_count / pos_class_count

        logger.info(f"Training final XGBoost model on {len(X_train)} records...")
        logger.info(f"Final scale_pos_weight: {scale_pos_weight_val:.2f}")

        model = XGBClassifier(
            n_estimators=100,
            scale_pos_weight=scale_pos_weight_val,
            random_state=42,
            n_jobs=-1,
            eval_metric="logloss",
        )

        # Use .values to strip metadata and prevent serving skew in ONNX
        model.fit(X_train.values, y_train.values)

        # Evaluation (also using .values)
        y_pred = model.predict(X_test.values)
        y_prob = model.predict_proba(X_test.values)[:, 1]

        metrics = {
            "PR-AUC": average_precision_score(y_test, y_prob),
            "Recall": recall_score(y_test, y_pred),
            "Precision": precision_score(y_test, y_pred),
            "F1-Score": f1_score(y_test, y_pred),
        }

        logger.info("--- Model Evaluation Metrics ---")
        for metric_name, value in metrics.items():
            logger.info(f"{metric_name}: {value:.4f}")

        return model

    def _export_to_onnx(self, model, input_feature_count: int) -> Path:
        """Exports the trained model to ONNX format with timestamp versioning."""
        logger.info("Converting model to ONNX format...")
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # Versioning paths
        timestamp = datetime.now().strftime("%Y%m%d")
        versioned_path = self.model_dir / f"fraud_xgboost_{timestamp}.onnx"
        latest_path = self.model_dir / "fraud_xgboost.onnx"  # Expected by API and tests

        initial_type = [("float_input", FloatTensorType([None, input_feature_count]))]

        try:
            onnx_model = onnxmltools.convert_xgboost(model, initial_types=initial_type)

            # Save versioned and latest models
            onnxmltools.utils.save_model(onnx_model, str(versioned_path))
            onnxmltools.utils.save_model(onnx_model, str(latest_path))

            model_size_kb = os.path.getsize(latest_path) / 1024
            logger.info("=" * 50)
            logger.info(f"SUCCESS: Model exported to {versioned_path.name}")
            logger.info(f"FINAL ONNX MODEL SIZE: {model_size_kb:.2f} KB")
            logger.info("=" * 50)

            return latest_path
        except Exception as e:
            logger.error(f"ONNX export failed. Error: {e}")
            raise

    def execute(self) -> Path:
        """
        Executes the full training and export pipeline.

        Returns:
            Path: The absolute path to the exported 'latest' ONNX model artifact.
        """
        logger.info("Initiating model training pipeline...")

        X_train, X_test, y_train, y_test = self._load_data()
        model = self._train_and_evaluate(X_train, X_test, y_train, y_test)
        onnx_path = self._export_to_onnx(model, input_feature_count=X_train.shape[1])

        return onnx_path


if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.execute()
