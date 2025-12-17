from unittest.mock import patch
from pathlib import Path
import sys

import utils.paths as paths


def test_resource_path_dev_environment():
    if hasattr(sys, "_MEIPASS"):
        del sys._MEIPASS
    test_rel_path = "assets/resources/file.txt"
    abs_path = paths.resource_path(test_rel_path)
    assert test_rel_path in abs_path
    assert Path(abs_path).is_absolute()


def test_resource_path_pyinstaller_environment(monkeypatch):
    test_rel_path = "assets/resources/file.txt"
    monkeypatch.setattr(sys, "_MEIPASS", "/tmp/meipass", raising=False)
    abs_path = paths.resource_path(test_rel_path)
    assert abs_path.startswith("/tmp/meipass")
    assert abs_path.endswith(test_rel_path)


def test_get_appdata_db_path_creates_db():
    with patch("os.getenv", return_value="/fake/appdata") as mock_getenv, \
         patch("utils.paths.resource_path", return_value="/fake/resource/accuracy.mdb") as mock_resource_path, \
         patch("utils.paths.Path.read_bytes", return_value=b"DBDATA") as mock_read_bytes, \
         patch("utils.paths.Path.write_bytes") as mock_write_bytes, \
         patch("utils.paths.Path.exists", return_value=False) as mock_exists, \
         patch("utils.paths.Path.mkdir") as mock_mkdir:

        db_path = paths.get_appdata_db_path()
        expected_path = Path("/fake/appdata") / paths.APP_NAME / paths.DB_FILENAME
        assert db_path == expected_path
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_write_bytes.assert_called_once_with(b"DBDATA")
        mock_read_bytes.assert_called_once()


def test_get_appdata_db_path_existing_db():
    with patch("os.getenv", return_value="/fake/appdata") as mock_getenv, \
         patch("utils.paths.Path.exists", return_value=True) as mock_exists, \
         patch("utils.paths.Path.mkdir") as mock_mkdir:

        db_path = paths.get_appdata_db_path()
        assert db_path.name == paths.DB_FILENAME
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
