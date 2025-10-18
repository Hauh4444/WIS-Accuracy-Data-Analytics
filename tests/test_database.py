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
    def test_file_not_found_error(self, mock_msg, mock_exists, app):
        """Test file not found error handling."""
        with pytest.raises(ValueError, match="Database file not found"):
            get_db_connection(db_path="nonexistent.accdb")
        mock_msg.assert_called_once()

    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_invalid_path_errors(self, mock_msg, app):
        """Test various invalid path error conditions."""
        with pytest.raises(ValueError, match="Database path cannot be None"):
            get_db_connection(db_path=None)
        
        with pytest.raises(ValueError, match="Database path must be a string"):
            get_db_connection(db_path=123)
        
        with pytest.raises(ValueError, match="Database path cannot be empty"):
            get_db_connection(db_path="")
        
        assert mock_msg.call_count == 3

    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.Path.is_file", return_value=False)
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_path_not_file_error(self, mock_msg, mock_is_file, mock_exists, app):
        """Test path is not a file error."""
        with pytest.raises(ValueError, match="Database path is not a file"):
            get_db_connection(db_path="directory_path")
        mock_msg.assert_called_once()

    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.Path.is_file", return_value=True)
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_invalid_file_extension_error(self, mock_msg, mock_is_file, mock_exists, app):
        """Test invalid file extension error."""
        with pytest.raises(ValueError, match="Invalid database file extension"):
            get_db_connection(db_path="test.txt")
        mock_msg.assert_called_once()

    @patch("services.database.platform.system", return_value="Linux")
    @patch("services.database.Path.is_file", return_value=True)
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_linux_platform_error(self, mock_msg, mock_exists, mock_is_file, mock_platform, app):
        """Test Linux platform error."""
        with pytest.raises(ValueError, match="Windows platform required"):
            get_db_connection(db_path="test.accdb")
        mock_msg.assert_called_once()

    @patch("services.database.platform.system", return_value="Windows")
    @patch("services.database.Path.is_file", return_value=True)
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.pyodbc.connect", side_effect=Exception("Connection failed"))
    @patch("services.database.QtWidgets.QMessageBox.critical")
    def test_connection_error(self, mock_msg, mock_connect, mock_exists, mock_is_file, mock_platform, app):
        """Test database connection error."""
        with pytest.raises(Exception, match="Connection failed"):
            get_db_connection(db_path="valid_path.accdb")
        mock_msg.assert_called_once()

    @patch("services.database.platform.system", return_value="Windows")
    @patch("services.database.Path.is_file", return_value=True)
    @patch("services.database.Path.exists", return_value=True)
    @patch("services.database.pyodbc.connect")
    def test_successful_connection(self, mock_connect, mock_exists, mock_is_file, mock_platform, app):
        """Test successful database connection."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        result = get_db_connection(db_path="valid_path.accdb")
        
        assert result == mock_conn
        mock_connect.assert_called_once()
        connection_string = mock_connect.call_args[0][0]
        assert "Microsoft Access Driver" in connection_string
        assert "valid_path.accdb" in connection_string