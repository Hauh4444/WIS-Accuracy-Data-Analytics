import sys
import logging
from logging.handlers import RotatingFileHandler

from utils.paths import get_log_path
from exceptions.file_exceptions import FileSaveError


def setup_logging(level=logging.INFO):
    try:
        log_path = get_log_path()

        handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5, encoding="utf-8")

        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        handler.setFormatter(formatter)

        root = logging.getLogger()
        root.setLevel(level)
        root.addHandler(handler)

        if sys.stdout:
            root.addHandler(logging.StreamHandler())

    except Exception as e:
        raise FileSaveError("Failed to initialize logging system") from e