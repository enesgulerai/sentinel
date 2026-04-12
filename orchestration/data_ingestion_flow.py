import time
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from prefect import flow, task

API_URL = "http://127.0.0.1:8000"


def generate_run_name():
    return datetime.now().strftime("%d-%m-%y_Data-Ingestion_%H-%M")


@task(retries=2, retry_delay_seconds=5)
def extract_data(source_url: str) -> pd.DataFrame:
    """Extracts raw data matching the FastAPI Transaction schema."""
    print(f"[EXTRACT] Pulling data from: {source_url}")
    time.sleep(1)

    data = []
    for i in range(5):
        row = {
            "Time": float(1000 + i),
            "Amount": round(np.random.uniform(1.5, 500.0), 2),
        }
        for v in range(1, 29):
            row[f"V{v}"] = np.random.normal(0, 1)

        data.append(row)

    raw_data = pd.DataFrame(data)
    print(f"[EXTRACT] Successfully pulled {len(raw_data)} records.")
    return raw_data


@task
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans data and prepares features for machine learning."""
    print("[TRANSFORM] Initiating data cleaning process...")

    df.fillna(0.0, inplace=True)

    print("[TRANSFORM] Data cleaned and structured for API.")
    return df


@task
def load_data(df: pd.DataFrame):
    """Sends processed data to the FastAPI endpoint (which routes to Redpanda)."""
    print(f"[LOAD] Pushing {len(df)} records to Sentinel API ({API_URL})...")

    success_count = 0
    error_count = 0

    for _, row in df.iterrows():
        payload = row.to_dict()

        try:
            response = requests.post(
                f"{API_URL}/api/v1/transactions", json=payload, timeout=5
            )

            if response.status_code == 202:
                success_count += 1
                print(f"  [+] SUCCESS: Record [Time: {payload['Time']}] -> Redpanda")
            elif response.status_code == 200:
                print(f"  [-] IGNORED (Duplicate): Record [Time: {payload['Time']}]")
            else:
                error_count += 1
                print(f"  [!] ERROR {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            error_count += 1
            print(f"  [!] CONNECTION FAILED: {str(e)}")

    print(f"[LOAD] Completed. Success: {success_count}, Errors: {error_count}")


@flow(name="Sentinel-Data-Ingestion", flow_run_name=generate_run_name)
def data_ingestion_pipeline():
    print("=== DATA INGESTION PIPELINE STARTED ===")

    raw_df = extract_data(source_url="https://s3-bucket/raw-transactions.csv")
    clean_df = transform_data(raw_df)
    load_data(clean_df)

    print("=== DATA INGESTION PIPELINE COMPLETED ===")


if __name__ == "__main__":
    data_ingestion_pipeline()
