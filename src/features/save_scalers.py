from pathlib import Path

import joblib
import pandas as pd
from sklearn.preprocessing import RobustScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "creditcard.csv"
MODEL_DIR = PROJECT_ROOT / "models"


def export_scalers():
    print("Generating and saving RobustScalers from raw data...")
    df = pd.read_csv(RAW_DATA_PATH)

    rob_scaler_amount = RobustScaler()
    rob_scaler_time = RobustScaler()

    # Fit the scalers on the raw data
    rob_scaler_amount.fit(df["Amount"].values.reshape(-1, 1))
    rob_scaler_time.fit(df["Time"].values.reshape(-1, 1))

    # Save them for the consumer to use
    joblib.dump(rob_scaler_amount, MODEL_DIR / "scaler_amount.joblib")
    joblib.dump(rob_scaler_time, MODEL_DIR / "scaler_time.joblib")

    print("SUCCESS: Scalers saved to models/ directory!")


if __name__ == "__main__":
    export_scalers()
