import pytest
import sys
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from services.database import get_db_connection


@pytest.fixture(scope="session")
def app():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    return app


class TestDatabaseConnection:

    @patch("services.database.Path.exists", return_value=False)
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_file_not_found_with_db_path(self, mock_msg, mock_exists, app):
        with pytest.raises(ValueError, match="Database file not found"):
            get_db_connection(db_path="nonexistent.accdb")
        
        mock_msg.assert_called_once()
        assert "Database file not found" in mock_msg.call_args[0][2]

    @patch("services.database.Path.exists", return_value=False)
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_file_not_found_with_constructed_path(self, mock_msg, mock_exists, app):
        job_number = "TEST123"
        db_path = rf"C:\WISDOM\JOBS\{job_number}\11355\{job_number}.MDB"
        with pytest.raises(ValueError, match="Database file not found"):
            get_db_connection(db_path=db_path)
        
        mock_msg.assert_called_once()
        assert "Database file not found" in mock_msg.call_args[0][2]

    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_none_path_error(self, mock_msg, app):
        with pytest.raises(ValueError, match="Database path cannot be None"):
            get_db_connection(db_path=None)
        
        mock_msg.assert_called_once()
        assert "Database path cannot be None" in mock_msg.call_args[0][2]

    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_non_string_path_error(self, mock_msg, app):
        with pytest.raises(ValueError, match="Database path must be a string"):
            get_db_connection(db_path=123)
        
        mock_msg.assert_called_once()
        assert "Database path must be a string" in mock_msg.call_args[0][2]

    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_empty_path_error(self, mock_msg, app):
        with pytest.raises(ValueError, match="Database path cannot be empty"):
            get_db_connection(db_path="")
        
        mock_msg.assert_called_once()
        assert "Database path cannot be empty" in mock_msg.call_args[0][2]

    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.Path.is_file", return_value=False)
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_path_not_file_error(self, mock_msg, mock_is_file, mock_exists, app):
        with pytest.raises(ValueError, match="Database path is not a file"):
            get_db_connection(db_path="directory_path")
        
        mock_msg.assert_called_once()
        assert "Database path is not a file" in mock_msg.call_args[0][2]

    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.Path.is_file", return_value=True)
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_invalid_file_extension_error(self, mock_msg, mock_is_file, mock_exists, app):
        with pytest.raises(ValueError, match="Invalid database file extension"):
            get_db_connection(db_path="test.txt")
        
        mock_msg.assert_called_once()
        assert "Invalid database file extension" in mock_msg.call_args[0][2]

    @patch("services.database.platform.system", return_value="Windows")
    @patch("services.database.Path.is_file", return_value=True)
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.pyodbc.connect", side_effect=Exception("Connection failed"))
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_connection_error(self, mock_msg, mock_connect, mock_exists, mock_is_file, mock_platform, app):
        with pytest.raises(Exception, match="Connection failed"):
            get_db_connection(db_path="valid_path.accdb")
        
        mock_msg.assert_called_once()
        assert "Unexpected error during database connection" in mock_msg.call_args[0][2]

    @patch("services.database.platform.system", return_value="Windows")
    @patch("services.database.Path.is_file", return_value=True)
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.pyodbc.connect")
    def test_connection_success_with_db_path(self, mock_connect, mock_exists, mock_is_file, mock_platform, app):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        result = get_db_connection(db_path="valid_path.accdb")
        
        assert result == mock_conn
        mock_connect.assert_called_once()
        connection_string = mock_connect.call_args[0][0]
        assert "valid_path.accdb" in connection_string

    @patch("services.database.platform.system", return_value="Windows")
    @patch("services.database.Path.is_file", return_value=True)
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.pyodbc.connect")
    def test_connection_success_with_constructed_path(self, mock_connect, mock_exists, mock_is_file, mock_platform, app):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        job_number = "TEST123"
        db_path = rf"C:\WISDOM\JOBS\{job_number}\11355\{job_number}.MDB"
        result = get_db_connection(db_path=db_path)
        
        assert result == mock_conn
        mock_connect.assert_called_once()
        connection_string = mock_connect.call_args[0][0]
        assert "TEST123" in connection_string

    @patch("services.database.platform.system", return_value="Windows")
    @patch("services.database.Path.is_file", return_value=True)
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.pyodbc.connect")
    def test_windows_driver_selection(self, mock_connect, mock_exists, mock_is_file, mock_platform, app):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        get_db_connection(db_path="test.accdb")
        
        connection_string = mock_connect.call_args[0][0]
        assert "Microsoft Access Driver" in connection_string

    @patch("services.database.platform.system", return_value="Linux")
    @patch("services.database.Path.is_file", return_value=True)
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_linux_platform_error(self, mock_msg, mock_exists, mock_is_file, mock_platform, app):
        with pytest.raises(ValueError, match="Windows platform required"):
            get_db_connection(db_path="test.accdb")
        
        mock_msg.assert_called_once()
        assert "Windows platform required" in mock_msg.call_args[0][2]

    @patch("services.database.platform.system", return_value="Linux")
    @patch("services.database.Path.is_file", return_value=True)
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_linux_connection_error_with_help_text(self, mock_msg, mock_exists, mock_is_file, mock_platform, app):
        with pytest.raises(ValueError, match="Windows platform required"):
            get_db_connection(db_path="test.accdb")
        
        error_message = mock_msg.call_args[0][2]
        assert "Windows platform required" in error_message