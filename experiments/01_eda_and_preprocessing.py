from pathlib import Path

import pandas as pd
from sklearn.preprocessing import RobustScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "creditcard.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "creditcard_scaled.csv"


def load_and_inspect_data(filepath: Path) -> pd.DataFrame:
    print(f"Loading dataset from: {filepath}")
    if not filepath.exists():
        raise FileNotFoundError(f"Dataset not found at: {filepath}")

    df = pd.read_csv(filepath)
    print(f"Dataset Shape: {df.shape}")

    fraud_count = df["Class"].sum()
    total_count = len(df)
    fraud_ratio = (fraud_count / total_count) * 100

    print("\n--- Class Distribution ---")
    print(f"Normal Transactions: {total_count - fraud_count}")
    print(f"Fraud Transactions: {fraud_count}")
    print(f"Fraud Ratio: {fraud_ratio:.3f}%")

    return df


def preprocess_features(df: pd.DataFrame) -> pd.DataFrame:
    print("\nApplying RobustScaler to 'Amount' and 'Time'...")
    df_processed = df.copy()
    rob_scaler = RobustScaler()

    df_processed["scaled_amount"] = rob_scaler.fit_transform(
        df_processed["Amount"].values.reshape(-1, 1)
    )
    df_processed["scaled_time"] = rob_scaler.fit_transform(
        df_processed["Time"].values.reshape(-1, 1)
    )

    df_processed.drop(["Time", "Amount"], axis=1, inplace=True)

    scaled_amount = df_processed["scaled_amount"]
    scaled_time = df_processed["scaled_time"]
    df_processed.drop(["scaled_amount", "scaled_time"], axis=1, inplace=True)

    df_processed.insert(0, "scaled_amount", scaled_amount)
    df_processed.insert(1, "scaled_time", scaled_time)

    print("Preprocessing completed.")
    return df_processed


def save_processed_data(df: pd.DataFrame, output_path: Path) -> None:
    print(f"\nSaving processed data to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print("Save complete.")


if __name__ == "__main__":
    raw_df = load_and_inspect_data(RAW_DATA_PATH)
    processed_df = preprocess_features(raw_df)

    assert processed_df.isnull().sum().max() == 0, "Missing values detected!"
    save_processed_data(processed_df, PROCESSED_DATA_PATH)
