from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler

from src.utils.logger import get_logger

logger = get_logger(__name__)


class FeatureEngineer:
    """
    Handles data loading, train/test splitting, feature scaling using RobustScaler,
    and artifact generation while strictly preventing data leakage.
    """

    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.default_raw_csv = self.project_root / "data" / "raw" / "creditcard.csv"
        self.processed_data_dir = self.project_root / "data" / "processed"
        self.scaler_artifact_path = self.project_root / "models" / "robust_scaler.joblib"

        self.target_col = "Class"
        self.cols_to_scale = ["Time", "Amount"]
        self.test_size = 0.20
        self.random_state = 42

    def _load_and_inspect(self, filepath: Path) -> pd.DataFrame:
        """Loads the raw dataset and logs basic distribution metrics."""
        logger.info(f"Loading dataset from: {filepath}")
        if not filepath.exists():
            raise FileNotFoundError(f"Dataset not found at: {filepath}")

        df = pd.read_csv(filepath)
        logger.info(f"Dataset Shape: {df.shape}")

        # Ensure no existing nulls before processing
        assert df.isnull().sum().max() == 0, "Missing values detected in raw data!"

        fraud_count = df[self.target_col].sum()
        total_count = len(df)
        fraud_ratio = (fraud_count / total_count) * 100.0

        logger.info("--- Class Distribution ---")
        logger.info(f"Normal Transactions: {total_count - fraud_count}")
        logger.info(f"Fraud Transactions: {fraud_count}")
        logger.info(f"Fraud Ratio: {fraud_ratio:.3f}%")

        return df

    def _split_and_scale(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Splits data to prevent leakage, then applies RobustScaler."""
        logger.info("Splitting data into train and test sets...")

        X = df.drop(columns=[self.target_col])
        y = df[self.target_col]

        # Stratified split to maintain the fraud ratio in both sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
        )

        logger.info("Applying RobustScaler to configure training distributions...")
        scaler = RobustScaler()

        X_train_scaled = X_train.copy()
        X_test_scaled = X_test.copy()

        # Fit strictly on TRAIN data, transform BOTH
        X_train_scaled[self.cols_to_scale] = scaler.fit_transform(X_train[self.cols_to_scale])
        X_test_scaled[self.cols_to_scale] = scaler.transform(X_test[self.cols_to_scale])

        logger.info(f"Saving RobustScaler artifact to: {self.scaler_artifact_path}")
        self.scaler_artifact_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(scaler, self.scaler_artifact_path)

        train_df = pd.concat([X_train_scaled, y_train], axis=1)
        test_df = pd.concat([X_test_scaled, y_test], axis=1)

        return train_df, test_df

    def execute(self, raw_data_path: Path | None = None) -> tuple[Path, Path]:
        """
        Executes the feature engineering pipeline.

        Args:
            raw_data_path (Path, optional): Path to the ingested CSV. Defaults to the standard path.

        Returns:
            tuple[Path, Path]: Paths to the scaled train and test CSV files.
        """
        target_path = raw_data_path if raw_data_path else self.default_raw_csv

        df = self._load_and_inspect(target_path)
        train_df, test_df = self._split_and_scale(df)

        logger.info(f"Saving processed data to directory: {self.processed_data_dir}")
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)

        train_csv_path = self.processed_data_dir / "train_scaled.csv"
        test_csv_path = self.processed_data_dir / "test_scaled.csv"

        train_df.to_csv(train_csv_path, index=False)
        test_df.to_csv(test_csv_path, index=False)

        logger.info("SUCCESS: Feature engineering pipeline completed successfully.")
        return train_csv_path, test_csv_path


if __name__ == "__main__":
    engineer = FeatureEngineer()
    engineer.execute()
