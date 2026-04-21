import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """
    A standardized, formatted logging service for the entire project.
    Usage: logger = get_logger(__name__)
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers if get_logger is called multiple times
    if not logger.handlers:
        # 1. Dynamic Log Level from Environment (Default to INFO)
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        logger.setLevel(log_level)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 2. Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 3. File Handler with Rotation (Production Standard)
        # Keeps log size managed. Max 5MB per file, keeps last 5 backup files.
        log_filename = LOGS_DIR / "sentinel.log"
        file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=5 * 1024 * 1024,  # 5 MB limit
            backupCount=5,  # Keep up to 5 older files (sentinel.log.1, sentinel.log.2...)
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
