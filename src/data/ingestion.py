import hashlib
import os
import zipfile
from pathlib import Path

import gdown
from dotenv import load_dotenv

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataIngestor:
    """
    Handles the secure downloading, SHA-256 integrity verification,
    and extraction of raw datasets.
    """

    def __init__(self):
        load_dotenv()

        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.raw_data_dir = self.project_root / "data" / "raw"
        self.csv_path = self.raw_data_dir / "creditcard.csv"
        self.zip_path = self.raw_data_dir / "creditcard.zip"

        self.drive_file_id = os.getenv("DRIVE_FILE_ID")
        self.expected_hash = os.getenv("EXPECTED_ZIP_HASH")

    def _verify_file_hash(self, file_path: Path) -> bool:
        """
        Verifies the SHA-256 hash of a file by reading it in chunks.
        """
        if not self.expected_hash or self.expected_hash == "replace_this_with_actual_sha256_hash_string":
            logger.warning("No valid expected hash provided in .env. Skipping integrity check.")
            return True

        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        calculated_hash = sha256_hash.hexdigest()

        # Ensure comparison is case-insensitive
        if calculated_hash != self.expected_hash.lower():
            logger.error(f"Hash mismatch! Expected: {self.expected_hash.lower()}, Got: {calculated_hash}")
            return False

        logger.info("File integrity verified successfully via SHA-256.")
        return True

    def execute(self) -> Path:
        """
        Executes the data ingestion pipeline.

        Returns:
            Path: The absolute path to the extracted target CSV file.
        """
        if not self.drive_file_id:
            logger.error("DRIVE_FILE_ID environment variable is missing.")
            raise ValueError("DRIVE_FILE_ID environment variable is missing.")

        logger.info(f"Checking for raw data at: {self.csv_path}")

        # Idempotency Check
        if self.csv_path.exists():
            logger.info("Data already exists. Skipping download process.")
            return self.csv_path

        logger.info("Data not found. Initiating download from remote storage...")
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)

        # Download process
        url = f"https://drive.google.com/uc?id={self.drive_file_id}"
        try:
            gdown.download(url, str(self.zip_path), quiet=False)
        except Exception as e:
            logger.error(f"Network or remote server error during download: {e}")
            raise

        if not self.zip_path.exists():
            raise FileNotFoundError("Download process completed but zip file is missing.")

        # Integrity Check
        if not self._verify_file_hash(self.zip_path):
            self.zip_path.unlink()
            raise ValueError("Data integrity compromised. Downloaded file hash does not match.")

        # Extraction
        logger.info("Extracting data archive...")
        try:
            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                zip_ref.extractall(self.raw_data_dir)
        except zipfile.BadZipFile:
            logger.error("The downloaded file is not a valid zip archive.")
            raise
        finally:
            # Clean up temporary files
            if self.zip_path.exists():
                self.zip_path.unlink()
                logger.info("Temporary zip file deleted.")

        # Final Verification
        if self.csv_path.exists():
            logger.info("SUCCESS: Data ingestion completed normally.")
            return self.csv_path
        else:
            logger.error("Extraction failed. Target CSV file not found.")
            raise FileNotFoundError("Extraction failed. Target CSV file not found.")


if __name__ == "__main__":
    ingestor = DataIngestor()
    ingestor.execute()
