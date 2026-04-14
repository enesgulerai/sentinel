import zipfile
from pathlib import Path

import gdown

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
CSV_PATH = RAW_DATA_DIR / "creditcard.csv"
ZIP_PATH = RAW_DATA_DIR / "creditcard.zip"

DRIVE_FILE_ID = "11KgVt4ebjSYDMswUuEXkGLXezHO0c0oc"


def download_and_extract_data():
    print(f"Checking for raw data at: {CSV_PATH}")

    # 1. Idempotency: Exit early if data already exists
    if CSV_PATH.exists():
        print("Data already exists! Skipping download.")
        return

    print("Data not found. Downloading dataset from Google Drive...")
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Download the zipped data
    url = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"
    gdown.download(url, str(ZIP_PATH), quiet=False)

    # 3. Extraction process
    if ZIP_PATH.exists():
        print("\nExtracting data...")
        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(RAW_DATA_DIR)

        # 4. Clean up: Delete the zip file to save disk space
        ZIP_PATH.unlink()

        if CSV_PATH.exists():
            print("=" * 50)
            print(f"SUCCESS: Data downloaded and extracted to {CSV_PATH}")
            print("=" * 50)
        else:
            raise FileNotFoundError(
                "Extraction failed. CSV file not found inside the zip."
            )
    else:
        raise FileNotFoundError(
            "ERROR: Download failed. Check your Google Drive ID or permissions."
        )


if __name__ == "__main__":
    download_and_extract_data()
