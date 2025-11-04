"""Tests for database connection functionality."""
import pytest
from unittest.mock import Mock, patch
import pyodbc
from PyQt6 import QtWidgets

from database.connection import get_db_connection

pytestmark = pytest.mark.database


class TestGetDbConnection:
    """Test get_db_connection function."""
    
    def test_successful_connection(self, mock_database_connection, temp_database_file):
        """Test successful database connection."""
        with patch('database.connection.pyodbc.connect', return_value=mock_database_connection) as mock_connect, \
             patch('database.connection.platform.system', return_value="Windows"):
            result = get_db_connection(temp_database_file)
            assert result == mock_database_connection
            mock_connect.assert_called_once()
    
    def test_none_db_path(self):
        """Test ValueError when db_path is None."""
        with pytest.raises(ValueError, match="Database path cannot be None"):
            get_db_connection(None)
    
    def test_non_string_db_path(self):
        """Test ValueError when db_path is not a string."""
        with pytest.raises(ValueError, match="Database path must be a string"):
            get_db_connection(123)
    
    def test_empty_db_path(self):
        """Test ValueError when db_path is empty."""
        with pytest.raises(ValueError, match="Database path cannot be empty"):
            get_db_connection("")
    
    def test_whitespace_db_path(self):
        """Test ValueError when db_path is only whitespace."""
        with pytest.raises(ValueError, match="Database path cannot be empty"):
            get_db_connection("   ")
    
    def test_nonexistent_file(self):
        """Test ValueError when database file doesn't exist."""
        with pytest.raises(ValueError, match="Database file not found"):
            get_db_connection("/nonexistent/path.mdb")
    
    def test_directory_instead_of_file(self, tmp_path):
        """Test ValueError when path is a directory."""
        dir_path = tmp_path / "test_dir"
        dir_path.mkdir()
        with pytest.raises(ValueError, match="Database path is not a file"):
            get_db_connection(str(dir_path))
    
    def test_invalid_file_extension(self, tmp_path):
        """Test ValueError when file has invalid extension."""
        file_path = tmp_path / "test.txt"
        file_path.touch()
        with pytest.raises(ValueError, match="Invalid database file extension"):
            get_db_connection(str(file_path))
    
    def test_non_windows_platform(self, temp_database_file):
        """Test ValueError on non-Windows platform."""
        with patch('database.connection.platform.system', return_value="Linux"):
            with pytest.raises(ValueError, match="Windows platform required"):
                get_db_connection(temp_database_file)
    
    def test_pyodbc_error(self, temp_database_file):
        """Test handling of pyodbc.Error."""
        with patch('database.connection.pyodbc.connect', side_effect=pyodbc.Error("Connection failed")):
            with patch('database.connection.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(pyodbc.Error):
                    get_db_connection(temp_database_file)
                mock_msgbox.assert_called_once()
    
    def test_value_error_handling(self, temp_database_file):
        """Test handling of ValueError."""
        with patch('database.connection.pyodbc.connect', side_effect=ValueError("Invalid path")):
            with patch('database.connection.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(ValueError):
                    get_db_connection(temp_database_file)
                mock_msgbox.assert_called_once()
    
    def test_runtime_error_handling(self, temp_database_file):
        """Test handling of RuntimeError."""
        with patch('database.connection.pyodbc.connect', side_effect=RuntimeError("Runtime error")):
            with patch('database.connection.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(RuntimeError):
                    get_db_connection(temp_database_file)
                mock_msgbox.assert_called_once()
    
    def test_generic_exception_handling(self, temp_database_file):
        """Test handling of generic Exception."""
        with patch('database.connection.pyodbc.connect', side_effect=Exception("Unexpected error")):
            with patch('database.connection.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(Exception):
                    get_db_connection(temp_database_file)
                mock_msgbox.assert_called_once()
    
    def test_connection_string_format(self, temp_database_file):
        """Test that connection string is formatted correctly."""
        with patch('database.connection.pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            get_db_connection(temp_database_file)
            expected_conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={temp_database_file};"
            mock_connect.assert_called_once_with(expected_conn_str, autocommit=False)
    
    def test_autocommit_false(self, temp_database_file):
        """Test that autocommit is set to False."""
        with patch('database.connection.pyodbc.connect') as mock_connect:
            mock_connect.return_value = Mock()
            get_db_connection(temp_database_file)
            mock_connect.assert_called_once_with(
                f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={temp_database_file};",
                autocommit=False
            )
