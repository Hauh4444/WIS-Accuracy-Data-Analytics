"""Tests for store repository functions."""
import pytest
from unittest.mock import Mock
import pyodbc

from repositories.source_store_repository import fetch_wise_data


class TestFetchWiseData:
    """Test fetch_wise_data function."""
    
    def test_successful_fetch(self, mock_database_connection, mock_pyodbc_row):
        """Test successful data fetch."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        
        sample_data = ("2024-01-15 10:00:00", "Test Store", "123 Test St")
        mock_row = mock_pyodbc_row(sample_data)
        mock_cursor.fetchone.return_value = mock_row
        
        result = fetch_wise_data(mock_database_connection)
        
        assert result == mock_row
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_empty_result(self, mock_database_connection):
        """Test when no data is returned."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = fetch_wise_data(mock_database_connection)
        
        assert result is None
        mock_cursor.close.assert_called_once()
    
    def test_sql_query_structure(self, mock_database_connection):
        """Test that SQL query has correct structure."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        fetch_wise_data(mock_database_connection)
        
        call_args = mock_cursor.execute.call_args[0][0]
        assert "SELECT" in call_args
        assert "tblWISEInfo" in call_args
        assert "JobDateTime" in call_args
        assert "Name" in call_args
        assert "Address" in call_args
    
    def test_cursor_management(self, mock_database_connection):
        """Test that cursor is properly closed after use."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        fetch_wise_data(mock_database_connection)
        
        mock_database_connection.cursor.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_database_connection_usage(self, mock_database_connection):
        """Test that database connection is used correctly."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        fetch_wise_data(mock_database_connection)
        
        mock_database_connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()
