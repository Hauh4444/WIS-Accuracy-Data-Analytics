import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import database.connection as db_conn


@pytest.mark.parametrize(
    "db_path, exists, is_file, expected_msg",
    [
        (None, False, False, "Database path must be a non-empty string"),
        (123, False, False, "Database path must be a non-empty string"),
        ("   ", False, False, "Database path must be a non-empty string"),
        ("/non/existent/file.mdb", False, False, "Source database file not found"),
        ("/fake/path/file.txt", True, True, "Invalid database file extension"),
    ],
)
def test_get_db_connection_invalid_paths(db_path, exists, is_file, expected_msg):
    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = exists
    mock_path.is_file.return_value = is_file

    with patch("database.connection.Path", return_value=mock_path), \
         patch("database.connection.platform.system", return_value="Windows"), \
         patch("database.connection.QtWidgets.QMessageBox.warning") as mock_warning:

        result = db_conn.get_db_connection(db_path)
        assert result is None
        mock_warning.assert_called_once()
        assert expected_msg in mock_warning.call_args[0][2]



def test_get_db_connection_non_windows():
    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True
    mock_path.is_file.return_value = True

    with patch("database.connection.platform.system", return_value="Linux"), \
         patch("database.connection.Path", return_value=mock_path), \
         patch("database.connection.QtWidgets.QMessageBox.warning") as mock_warning:

        result = db_conn.get_db_connection("/fake/file.mdb")
        assert result is None
        mock_warning.assert_called_once()
        assert "Windows platform required" in mock_warning.call_args[0][2]


def test_get_db_connection_success():
    mock_conn = MagicMock()
    with patch("database.connection.platform.system", return_value="Windows"), \
         patch("database.connection.pyodbc.connect", return_value=mock_conn) as mock_connect, \
         patch("database.connection.Path.exists", return_value=True), \
         patch("database.connection.Path.is_file", return_value=True):

        result = db_conn.get_db_connection("/fake/file.mdb")
        assert result is mock_conn
        mock_connect.assert_called_once()


def test_get_storage_db_connection_success():
    mock_conn = MagicMock()
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.is_file.return_value = True

    with patch("database.connection.platform.system", return_value="Windows"), \
         patch("database.connection.pyodbc.connect", return_value=mock_conn) as mock_connect, \
         patch("database.connection.get_appdata_db_path", return_value=mock_path):

        result = db_conn.get_storage_db_connection()
        assert result is mock_conn
        mock_connect.assert_called_once()


def test_get_storage_db_connection_missing_file():
    mock_path = MagicMock()
    mock_path.exists.return_value = False
    mock_path.is_file.return_value = False

    with patch("database.connection.get_appdata_db_path", return_value=mock_path), \
         patch("database.connection.platform.system", return_value="Windows"), \
         patch("database.connection.QtWidgets.QMessageBox.warning") as mock_warning:

        result = db_conn.get_storage_db_connection()
        assert result is None
        mock_warning.assert_called_once()
        assert "Storage database file not found" in mock_warning.call_args[0][2]


def test_get_storage_db_connection_non_windows():
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.is_file.return_value = True

    with patch("database.connection.get_appdata_db_path", return_value=mock_path), \
         patch("database.connection.platform.system", return_value="Linux"), \
         patch("database.connection.QtWidgets.QMessageBox.warning") as mock_warning:

        result = db_conn.get_storage_db_connection()
        assert result is None
        mock_warning.assert_called_once()
        assert "Windows platform required" in mock_warning.call_args[0][2]
