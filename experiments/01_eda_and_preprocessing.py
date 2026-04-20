import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "creditcard.csv"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
SCALER_ARTIFACT_PATH = PROJECT_ROOT / "models" / "robust_scaler.joblib"

# Pipeline Configurations
TARGET_COL = "Class"
COLS_TO_SCALE = ["Time", "Amount"]
TEST_SIZE = 0.20
RANDOM_STATE = 42


def load_and_inspect_data(filepath: Path) -> pd.DataFrame:
    logger.info(f"Loading dataset from: {filepath}")
    if not filepath.exists():
        raise FileNotFoundError(f"Dataset not found at: {filepath}")

    df = pd.read_csv(filepath)
    logger.info(f"Dataset Shape: {df.shape}")

    fraud_count = df[TARGET_COL].sum()
    total_count = len(df)
    fraud_ratio = (fraud_count / total_count) * 100.0

    logger.info("--- Class Distribution ---")
    logger.info(f"Normal Transactions: {total_count - fraud_count}")
    logger.info(f"Fraud Transactions: {fraud_count}")
    logger.info(f"Fraud Ratio: {fraud_ratio:.3f}%")

    return df


def split_and_scale_data(
    df: pd.DataFrame, scaler_out_path: Path
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits the data into train/test sets FIRST, then applies scaling
    to prevent data leakage.
    """
    logger.info("Splitting data into train and test sets...")

    # Separate features and target
    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    # Stratified split to maintain the 0.17% fraud ratio in both sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    logger.info("Applying RobustScaler to configure training distributions...")
    scaler = RobustScaler()

    # Fit strictly on TRAIN data, transform BOTH
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()

    X_train_scaled[COLS_TO_SCALE] = scaler.fit_transform(X_train[COLS_TO_SCALE])
    X_test_scaled[COLS_TO_SCALE] = scaler.transform(X_test[COLS_TO_SCALE])

    # Save the fitted scaler artifact
    logger.info(f"Saving RobustScaler artifact to: {scaler_out_path}")
    scaler_out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, scaler_out_path)

    # Recombine X and y for saving (optional, depends on downstream pipeline preference)
    train_df = pd.concat([X_train_scaled, y_train], axis=1)
    test_df = pd.concat([X_test_scaled, y_test], axis=1)

    logger.info("Preprocessing and split completed.")
    return train_df, test_df


def save_processed_data(
    train_df: pd.DataFrame, test_df: pd.DataFrame, output_dir: Path
) -> None:
    logger.info(f"Saving processed data to directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(output_dir / "train_scaled.csv", index=False)
    test_df.to_csv(output_dir / "test_scaled.csv", index=False)

    logger.info("Data export complete.")


if __name__ == "__main__":
    raw_df = load_and_inspect_data(RAW_DATA_PATH)

    # Ensure no existing nulls before processing
    assert raw_df.isnull().sum().max() == 0, "Missing values detected in raw data!"

    train_data, test_data = split_and_scale_data(raw_df, SCALER_ARTIFACT_PATH)
    save_processed_data(train_data, test_data, PROCESSED_DATA_DIR)
