import os
import sys
import json
import re
import logging
from pathlib import Path

from exceptions.file_exceptions import FileLoadError, InvalidFileFormatError
from exceptions.wisdom_exceptions import WisdomDatabaseNotFoundError

APP_NAME = "Accuracy_Report"


def get_appdata_root() -> Path:
    try:
        root = Path(os.getenv("LOCALAPPDATA"))

        if not root:
            raise FileLoadError("LOCALAPPDATA environment variable not set")

        app_root = root / APP_NAME
        app_root.mkdir(parents=True, exist_ok=True)

        return app_root

    except Exception as e:
        logging.exception("Failed to resolve appdata root")
        raise FileLoadError("Failed to initialize application storage") from e


def read_config_file():
    try:
        config_path = os.path.join(get_appdata_root(), "config.json")

        if not os.path.exists(config_path):
            raise FileLoadError(f"Config file not found: {config_path}")

        with open(config_path, "r") as file:
            return json.load(file)

    except json.JSONDecodeError as e:
        logging.exception("Invalid config JSON")
        raise InvalidFileFormatError("Config file is not valid JSON") from e

    except Exception as e:
        logging.exception("Failed to read config file")
        raise FileLoadError("Failed to load configuration") from e


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)


def get_installed_image_path():
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)

    else:
        base_dir = os.path.dirname(__file__)

    return os.path.join(base_dir, "assets", "images", "checkmark.png").replace("\\", "/")


def get_db_path() -> Path:
    try:
        config = read_config_file()
        root = Path(os.path.expandvars(config["local_data_path"]))
        db_filename = config["database_filename"]
        db_path = root / db_filename

        if db_path.exists():
            return db_path

        template = Path(resource_path(f"assets/resources/{db_filename}"))

        if not template.exists():
            raise FileLoadError(f"Database template missing: {template}")

        db_path.write_bytes(template.read_bytes())

        return db_path

    except Exception as e:
        logging.exception("Failed to resolve database path")
        raise FileLoadError("Failed to initialize database file") from e


def get_log_path() -> Path:
    try:
        log_dir = get_appdata_root() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        config = read_config_file()
        log_filename = config["log_filename"]

        return log_dir / log_filename

    except Exception as e:
        logging.exception("Failed to resolve log path")
        raise FileLoadError("Failed to initialize logging path") from e


def build_wisdom_db_path(job_number):
    try:
        base_path = rf"C:\WISDOM\JOBS\{job_number}"

        if not os.path.exists(base_path):
            raise WisdomDatabaseNotFoundError(f"Job directory not found: {base_path}")

        wisdom_dirs = [
            d for d in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, d))
            and re.fullmatch(r"\d{5}", d)
        ]

        if not wisdom_dirs:
            raise WisdomDatabaseNotFoundError("No valid WISDOM directory found")

        wisdom_dir = wisdom_dirs[0]

        return os.path.join(base_path, wisdom_dir, f"{job_number}.MDB")

    except WisdomDatabaseNotFoundError:
        raise

    except Exception as e:
        logging.exception("Unexpected error building Wisdom DB path")
        raise WisdomDatabaseNotFoundError("Failed to resolve Wisdom database path") from e