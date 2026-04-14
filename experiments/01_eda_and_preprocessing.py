from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "creditcard.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "creditcard_scaled.csv"
SCALER_ARTIFACT_PATH = PROJECT_ROOT / "models" / "robust_scaler.joblib"


def load_and_inspect_data(filepath: Path) -> pd.DataFrame:
    print(f"Loading dataset from: {filepath}")
    if not filepath.exists():
        raise FileNotFoundError(f"Dataset not found at: {filepath}")

    df = pd.read_csv(filepath)
    print(f"Dataset Shape: {df.shape}")

    fraud_count = df["Class"].sum()
    total_count = len(df)
    fraud_ratio = (fraud_count / total_count) * 100.0

    print("\n--- Class Distribution ---")
    print(f"Normal Transactions: {total_count - fraud_count}")
    print(f"Fraud Transactions: {fraud_count}")
    print(f"Fraud Ratio: {fraud_ratio:.3f}%")

    return df


def preprocess_features(df: pd.DataFrame, scaler_out_path: Path) -> pd.DataFrame:
    print("\nApplying RobustScaler to 'Amount' and 'Time'...")

    # Memory Optimization: Use pop() to extract and remove columns simultaneously O(1)
    # This prevents the need for df.copy() and df.drop()
    amount_vals = df.pop("Amount").values
    time_vals = df.pop("Time").values

    # Combine into a single 2D array to prevent scaler overwriting
    features_to_scale = np.column_stack((amount_vals, time_vals))

    scaler = RobustScaler()
    scaled_features = scaler.fit_transform(features_to_scale)

    # Insert scaled features back into the dataframe at the beginning
    df.insert(0, "scaled_amount", scaled_features[:, 0])
    df.insert(1, "scaled_time", scaled_features[:, 1])

    # Save the fitted scaler artifact for the production Inference Engine
    print(f"Saving RobustScaler artifact to: {scaler_out_path}")
    scaler_out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, scaler_out_path)

    print("Preprocessing completed.")
    return df


def save_processed_data(df: pd.DataFrame, output_path: Path) -> None:
    print(f"\nSaving processed data to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print("Save complete.")


if __name__ == "__main__":
    raw_df = load_and_inspect_data(RAW_DATA_PATH)
    processed_df = preprocess_features(raw_df, SCALER_ARTIFACT_PATH)

    assert processed_df.isnull().sum().max() == 0, (
        "Missing values detected in processed data!"
    )
    save_processed_data(processed_df, PROCESSED_DATA_PATH)
