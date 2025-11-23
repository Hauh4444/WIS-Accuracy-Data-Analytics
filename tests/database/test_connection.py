import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import database.connection as db_conn

@pytest.mark.parametrize(
    "db_path, expected_msg",
    [
        (None, "Database path cannot be None"),
        (123, "Database path must be a string"),
        ("   ", "Database path cannot be empty"),
        ("/non/existent/file.mdb", "Source database file not found"),
        ("/fake/path/file.txt", "Invalid database file extension. Expected .mdb or .accdb"),
    ],
)
@patch("platform.system", return_value="Windows")
def test_get_db_connection_invalid_paths(mock_platform, db_path, expected_msg):
    # Set up path mocking based on test case
    mock_path_instance = None
    if isinstance(db_path, str) and db_path.strip():
        mock_path_instance = MagicMock(spec=Path)
        if db_path.endswith(".txt"):
            # File exists but has wrong extension
            mock_path_instance.exists.return_value = True
            mock_path_instance.is_file.return_value = True
        elif db_path.endswith((".mdb", ".accdb")):
            # File doesn't exist
            mock_path_instance.exists.return_value = False
            mock_path_instance.is_file.return_value = False

    with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
        # Apply path patch if needed
        if mock_path_instance:
            with patch("database.connection.Path", return_value=mock_path_instance):
                result = db_conn.get_db_connection(db_path)
        else:
            result = db_conn.get_db_connection(db_path)
        
        assert result is None
        mock_warning.assert_called()
        assert expected_msg in mock_warning.call_args[0][2]


@patch("platform.system", return_value="Linux")
def test_get_db_connection_non_windows(mock_platform):
    mock_path_instance = MagicMock(spec=Path)
    mock_path_instance.exists.return_value = True
    mock_path_instance.is_file.return_value = True
    with patch("database.connection.Path", return_value=mock_path_instance), \
         patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
        result = db_conn.get_db_connection("/fake/file.mdb")
        assert result is None
        mock_warning.assert_called()
        assert "Windows platform required" in mock_warning.call_args[0][2]


@patch("pyodbc.connect")
@patch("platform.system", return_value="Windows")
def test_get_db_connection_success(mock_platform, mock_connect):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_path_instance = MagicMock(spec=Path)
    mock_path_instance.exists.return_value = True
    mock_path_instance.is_file.return_value = True
    with patch("database.connection.Path", return_value=mock_path_instance):
        result = db_conn.get_db_connection("/fake/file.mdb")
        assert result == mock_conn
        mock_connect.assert_called_once()


@patch("utils.paths.get_appdata_db_path")
@patch("pyodbc.connect")
@patch("platform.system", return_value="Windows")
def test_get_storage_db_connection_success(mock_platform, mock_connect, mock_get_appdata):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.is_file.return_value = True
    mock_get_appdata.return_value = mock_path

    result = db_conn.get_storage_db_connection()
    assert result == mock_conn
    mock_connect.assert_called_once()


def test_get_storage_db_connection_missing_file():
    fake_path = Path("/non/existent/storage.mdb")
    with patch("utils.paths.get_appdata_db_path", return_value=fake_path), \
         patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
        result = db_conn.get_storage_db_connection()
        assert result is None
        mock_warning.assert_called_once()
        assert "Storage database file not found" in mock_warning.call_args[0][2]


@patch("utils.paths.get_appdata_db_path")
def test_get_storage_db_connection_non_windows(mock_get_appdata):
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.is_file.return_value = True
    mock_get_appdata.return_value = mock_path

    with patch("platform.system", return_value="Linux"), \
         patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
        result = db_conn.get_storage_db_connection()
        assert result is None
        mock_warning.assert_called()
        assert "Windows platform required" in mock_warning.call_args[0][2]
