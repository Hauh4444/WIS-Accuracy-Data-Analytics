"""Tests for team repository functions."""
import pytest
from unittest.mock import Mock
import pyodbc

from repositories.team_repository import (
    fetch_zone_data, fetch_zone_totals_data, fetch_zone_discrepancy_totals_data
)


class TestFetchZoneData:
    """Test fetch_zone_data function."""
    
    def test_successful_fetch(self, mock_database_connection, mock_pyodbc_row):
        """Test successful data fetch."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        
        sample_data = [(1, "Electronics"), (2, "Clothing")]
        mock_rows = [mock_pyodbc_row(row) for row in sample_data]
        mock_cursor.fetchall.return_value = mock_rows
        
        result = fetch_zone_data(mock_database_connection)
        
        assert result == mock_rows
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_empty_result(self, mock_database_connection):
        """Test when no data is returned."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        result = fetch_zone_data(mock_database_connection)
        
        assert result == []
        mock_cursor.close.assert_called_once()
    
    def test_sql_query_structure(self, mock_database_connection):
        """Test that SQL query has correct structure."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        fetch_zone_data(mock_database_connection)
        
        call_args = mock_cursor.execute.call_args[0][0]
        assert "SELECT DISTINCT" in call_args
        assert "tblZone" in call_args
        assert "ZoneID" in call_args
        assert "ZoneDesc" in call_args
        assert "ORDER BY" in call_args


class TestFetchZoneTotalsData:
    """Test fetch_zone_totals_data function."""
    
    def test_successful_fetch(self, mock_database_connection, mock_pyodbc_row):
        """Test successful data fetch."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        
        sample_data = (25, 250, 2500.0)
        mock_row = mock_pyodbc_row(sample_data)
        mock_cursor.fetchone.return_value = mock_row
        
        result = fetch_zone_totals_data(mock_database_connection, "1")
        
        assert result == mock_row
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_parameterized_query(self, mock_database_connection):
        """Test that query uses parameters correctly."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        fetch_zone_totals_data(mock_database_connection, "1")
        
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1] == ("1",)
    
    def test_sql_query_structure(self, mock_database_connection):
        """Test that SQL query has correct structure."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        fetch_zone_totals_data(mock_database_connection, "1")
        
        call_args = mock_cursor.execute.call_args[0][0]
        assert "SELECT" in call_args
        assert "Sum" in call_args
        assert "tblTagRange" in call_args
        assert "ZoneID" in call_args
        assert "WHERE" in call_args
    
    def test_empty_result(self, mock_database_connection):
        """Test when no data is returned."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = fetch_zone_totals_data(mock_database_connection, "1")
        
        assert result is None
        mock_cursor.close.assert_called_once()


class TestFetchZoneDiscrepancyTotalsData:
    """Test fetch_zone_discrepancy_totals_data function."""
    
    def test_successful_fetch(self, mock_database_connection, mock_pyodbc_row):
        """Test successful data fetch."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        
        sample_data = (125.0, 5)
        mock_row = mock_pyodbc_row(sample_data)
        mock_cursor.fetchone.return_value = mock_row
        
        result = fetch_zone_discrepancy_totals_data(mock_database_connection, "1")
        
        assert result == mock_row
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_parameterized_query(self, mock_database_connection):
        """Test that query uses parameters correctly."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        fetch_zone_discrepancy_totals_data(mock_database_connection, "1")
        
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1] == ("1", "1")
    
    def test_sql_query_structure(self, mock_database_connection):
        """Test that SQL query has correct structure."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        fetch_zone_discrepancy_totals_data(mock_database_connection, "1")
        
        call_args = mock_cursor.execute.call_args[0][0]
        assert "SELECT" in call_args
        assert "Sum" in call_args
        assert "tblZoneChangeQueue" in call_args
        assert "tblZoneChangeInfo" in call_args
        assert "INNER JOIN" in call_args
        assert "SERVICE_MISCOUNTED" in call_args
        assert "Abs" in call_args
        assert "Count" in call_args
    
    def test_empty_result(self, mock_database_connection):
        """Test when no data is returned."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = fetch_zone_discrepancy_totals_data(mock_database_connection, "1")
        
        assert result is None
        mock_cursor.close.assert_called_once()
    
    def test_cursor_management(self, mock_database_connection):
        """Test that cursor is properly closed after use."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        fetch_zone_discrepancy_totals_data(mock_database_connection, "1")
        
        mock_database_connection.cursor.assert_called_once()
        mock_cursor.close.assert_called_once()
