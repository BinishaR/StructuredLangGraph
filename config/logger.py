# config/logger.py
"""
Centralized logging setup.

Import `logger` from this module anywhere in the project instead of using
print(). Built on Python's standard `logging` module, so no extra
dependency is required.

Usage:
    from config.logger import logger
    logger.info("Something happened")
    logger.warning("Something looks off")
    logger.error("Something failed")
"""

import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _build_logger(name: str = "laxmi_bank") -> logging.Logger:
    log = logging.getLogger(name)

    # Avoid attaching duplicate handlers if this module gets imported
    # more than once (e.g. via multiple entry points).
    if log.handlers:
        return log

    log.setLevel(logging.INFO)

    formatter = logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT)

    # Console handler — what you see while developing
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    # File handler — persisted logs for debugging later
    file_handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    log.propagate = False
    return log


logger = _build_logger()