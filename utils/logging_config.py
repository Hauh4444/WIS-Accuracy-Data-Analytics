import sys
import logging
from logging.handlers import RotatingFileHandler

from .paths import get_log_path


def setup_logging(level: int = logging.INFO) -> None:
    """Set up logging to a rotating file and the console.

    Args:
        level: Logging level (default is INFO).
    """
    log_path = get_log_path()
    handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

    if sys.stdout:
        root.addHandler(logging.StreamHandler())