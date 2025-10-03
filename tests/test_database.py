import pytest
import sys
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from services.database import get_db_connection


@pytest.fixture(scope="session")
def app():
    """Create QApplication instance for testing."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    return app


class TestDatabaseConnection:
    """Test cases for database connection management."""

    @patch("services.database.Path.exists", return_value=False)
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_file_not_found_with_db_path(self, mock_msg, mock_exists, app):
        """Test error handling when database file doesn't exist."""
        result = get_db_connection(db_path="nonexistent.accdb")
        
        assert result is None
        mock_msg.assert_called_once()
        assert "Database file not found" in mock_msg.call_args[0][2]

    @patch("services.database.Path.exists", return_value=False)
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_file_not_found_with_job_number(self, mock_msg, mock_exists, app):
        """Test error handling when job number database file doesn't exist."""
        result = get_db_connection(job_number="TEST123")
        
        assert result is None
        mock_msg.assert_called_once()
        assert "Database file not found" in mock_msg.call_args[0][2]

    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_no_parameters_provided(self, mock_msg, app):
        """Test error handling when neither db_path nor job_number is provided."""
        result = get_db_connection()
        
        assert result is None
        mock_msg.assert_called_once()
        assert "Database path or job number required for connection" in mock_msg.call_args[0][2]

    @patch("services.database.platform.system", return_value="Windows")
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.pyodbc.connect", side_effect=Exception("Connection failed"))
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_connection_error(self, mock_msg, mock_connect, mock_exists, mock_platform, app):
        """Test error handling when database connection fails."""
        result = get_db_connection(db_path="valid_path.accdb")
        
        assert result is None
        mock_msg.assert_called_once()
        assert "Database connection failed" in mock_msg.call_args[0][2]
        assert "Connection failed" in mock_msg.call_args[0][2]

    @patch("services.database.platform.system", return_value="Windows")
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.pyodbc.connect")
    def test_connection_success_with_db_path(self, mock_connect, mock_exists, mock_platform, app):
        """Test successful connection with direct database path."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        result = get_db_connection(db_path="valid_path.accdb")
        
        assert result == mock_conn
        mock_connect.assert_called_once()
        connection_string = mock_connect.call_args[0][0]
        assert "valid_path.accdb" in connection_string

    @patch("services.database.platform.system", return_value="Windows")
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.pyodbc.connect")
    def test_connection_success_with_job_number(self, mock_connect, mock_exists, mock_platform, app):
        """Test successful connection with job number."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        result = get_db_connection(job_number="TEST123")
        
        assert result == mock_conn
        mock_connect.assert_called_once()
        connection_string = mock_connect.call_args[0][0]
        assert "TEST123" in connection_string

    @patch("services.database.platform.system", return_value="Windows")
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.pyodbc.connect")
    def test_windows_driver_selection(self, mock_connect, mock_exists, mock_platform, app):
        """Test Windows-specific driver selection."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        get_db_connection(db_path="test.accdb")
        
        connection_string = mock_connect.call_args[0][0]
        assert "Microsoft Access Driver" in connection_string

    @patch("services.database.platform.system", return_value="Linux")
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.pyodbc.connect")
    def test_linux_platform_error(self, mock_connect, mock_exists, mock_platform, app):
        """Test Linux platform error handling."""
        with patch("services.database.QtWidgets.QMessageBox.critical") as mock_msg:
            result = get_db_connection(db_path="test.accdb")
            
            assert result is None
            mock_msg.assert_called_once()
            assert "Windows platform required" in mock_msg.call_args[0][2]

    @patch("services.database.platform.system", return_value="Linux")
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.pyodbc.connect", side_effect=Exception("Connection failed"))
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_linux_connection_error_with_help_text(self, mock_msg, mock_connect, mock_exists, mock_platform, app):
        """Test Linux platform error message."""
        get_db_connection(db_path="test.accdb")
        
        error_message = mock_msg.call_args[0][2]
        assert "Windows platform required" in error_message