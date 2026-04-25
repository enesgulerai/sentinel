import hashlib
import logging
import os
import zipfile
from pathlib import Path

import gdown
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure standard logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
CSV_PATH = RAW_DATA_DIR / "creditcard.csv"
ZIP_PATH = RAW_DATA_DIR / "creditcard.zip"

# Fetch configurations from environment variables
DRIVE_FILE_ID = os.getenv("DRIVE_FILE_ID")
EXPECTED_ZIP_HASH = os.getenv("EXPECTED_ZIP_HASH")


def verify_file_hash(file_path: Path, expected_hash: str) -> bool:
    """
    Verifies the SHA-256 hash of a file efficiently by reading it in chunks.
    """
    if not expected_hash or expected_hash == "replace_this_with_actual_sha256_hash_string":
        logger.warning("No valid expected hash provided in .env. Skipping integrity check.")
        return True

    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    calculated_hash = sha256_hash.hexdigest()
    if calculated_hash != expected_hash:
        logger.error(f"Hash mismatch! Expected: {expected_hash}, Got: {calculated_hash}")
        return False

    logger.info("File integrity verified successfully via SHA-256.")
    return True


def download_and_extract_data():
    if not DRIVE_FILE_ID:
        raise ValueError("DRIVE_FILE_ID environment variable is missing.")

    logger.info(f"Checking for raw data at: {CSV_PATH}")

    # 1. Idempotency Check
    if CSV_PATH.exists():
        logger.info("Data already exists. Skipping download process.")
        return

    logger.info("Data not found. Initiating download from remote storage...")
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Download with basic error handling
    url = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"
    try:
        gdown.download(url, str(ZIP_PATH), quiet=False)
    except Exception as e:
        logger.error(f"Network or remote server error during download: {e}")
        raise

    if not ZIP_PATH.exists():
        raise FileNotFoundError("Download process completed but zip file is missing.")

    # 3. Integrity Check (SHA-256)
    if not verify_file_hash(ZIP_PATH, EXPECTED_ZIP_HASH):
        ZIP_PATH.unlink()
        raise ValueError("Data integrity compromised. Downloaded file hash does not match.")

    # 4. Extraction
    logger.info("Extracting data archive...")
    try:
        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(RAW_DATA_DIR)
    except zipfile.BadZipFile:
        logger.error("The downloaded file is not a valid zip archive.")
        raise
    finally:
        # 5. Clean up
        if ZIP_PATH.exists():
            ZIP_PATH.unlink()
            logger.info("Temporary zip file deleted.")

    # 6. Final Verification
    if CSV_PATH.exists():
        logger.info("SUCCESS: Data ingestion completed normally.")
    else:
        raise FileNotFoundError("Extraction failed. Target CSV file not found.")


if __name__ == "__main__":
    download_and_extract_data()
