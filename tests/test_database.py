import pytest
from unittest.mock import patch, MagicMock

from services.database import get_db_connection
from services.database import DEFAULT_DB_PATH


@patch("services.database.Path.exists", return_value=False)
@patch("services.database.QtWidgets.QMessageBox.critical")
def test_db_file_not_found(mock_msg, mock_exists):
    conn = get_db_connection("fake_path.accdb")
    assert conn is None
    mock_msg.assert_called_once()
    assert "Database file not found" in mock_msg.call_args[0][2]


@patch("services.database.Path.exists", return_value=True)
@patch("services.database.pyodbc.connect", side_effect=Exception("Connection failed"))
@patch("services.database.QtWidgets.QMessageBox.critical")
def test_db_connection_error(mock_msg, mock_connect, mock_exists):
    conn = get_db_connection("valid_path.accdb")
    assert conn is None
    mock_msg.assert_called_once()
    assert "Could not connect to database" in mock_msg.call_args[0][2]
    assert "Connection failed" in mock_msg.call_args[0][2]


@patch("services.database.Path.exists", return_value=True)
@patch("services.database.pyodbc.connect")
def test_db_connection_success(mock_connect, mock_exists):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    conn = get_db_connection("valid_path.accdb")
    assert conn == mock_conn
    mock_connect.assert_called_once()
    assert "valid_path.accdb" in mock_connect.call_args[0][0]


@patch("services.database.Path.exists", return_value=True)
@patch("services.database.pyodbc.connect")
def test_default_path_used(mock_connect, mock_exists):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    conn = get_db_connection(None)
    assert conn == mock_conn
    assert DEFAULT_DB_PATH in mock_connect.call_args[0][0]
