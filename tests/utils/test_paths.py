from unittest.mock import patch
from pathlib import Path
import sys

import utils.paths as paths


def test_resource_path_dev_environment(monkeypatch):
    # Ensure sys._MEIPASS does not exist
    if hasattr(sys, "_MEIPASS"):
        del sys._MEIPASS
    test_rel_path = "assets/resources/file.txt"
    abs_path = paths.resource_path(test_rel_path)
    assert test_rel_path in abs_path
    assert Path(abs_path).is_absolute()


def test_resource_path_pyinstaller_environment(monkeypatch):
    test_rel_path = "assets/resources/file.txt"
    # Simulate PyInstaller environment
    monkeypatch.setattr(sys, "_MEIPASS", "/tmp/meipass")
    abs_path = paths.resource_path(test_rel_path)
    assert abs_path.startswith("/tmp/meipass")
    assert abs_path.endswith(test_rel_path)


@patch("paths.Path.mkdir")
@patch("paths.Path.exists")
@patch("paths.Path.write_bytes")
@patch("paths.Path.read_bytes")
@patch("paths.resource_path")
@patch("os.getenv")
def test_get_appdata_db_path_creates_db(mock_getenv, mock_resource_path, mock_read_bytes, mock_write_bytes, mock_exists, mock_mkdir):
    # Setup mocks
    mock_getenv.return_value = "/fake/appdata"
    mock_exists.return_value = False
    mock_resource_path.return_value = "/fake/resource/accuracy.mdb"
    mock_read_bytes.return_value = b"DBDATA"

    db_path = paths.get_appdata_db_path()
    expected_path = Path("/fake/appdata") / paths.APP_NAME / paths.DB_FILENAME
    assert db_path == expected_path
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_write_bytes.assert_called_once_with(b"DBDATA")
    mock_read_bytes.assert_called_once()


@patch("paths.Path.mkdir")
@patch("paths.Path.exists")
def test_get_appdata_db_path_existing_db(mock_exists, mock_mkdir):
    # Test when DB already exists
    mock_exists.return_value = True
    db_path = paths.get_appdata_db_path()
    assert db_path.name == paths.DB_FILENAME
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
