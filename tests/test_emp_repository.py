"""Tests for employee repository functions."""
import pytest
from unittest.mock import Mock
import pyodbc

from repositories.source_emp_repository import (
    fetch_emp_tags_data, fetch_duplicate_tags_data, fetch_emp_data,
    fetch_emp_totals_data, fetch_emp_discrepancies_data, fetch_line_data
)


class TestFetchEmpTagsData:
    """Test fetch_emp_tags_data function."""
    
    def test_successful_fetch(self, mock_database_connection, mock_pyodbc_row):
        """Test successful data fetch."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        
        sample_data = [("12345", "T001"), ("12345", "T002"), ("67890", "T003")]
        mock_rows = [mock_pyodbc_row(row) for row in sample_data]
        mock_cursor.fetchall.return_value = mock_rows
        
        result = fetch_emp_tags_data(mock_database_connection)
        
        assert result == mock_rows
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_empty_result(self, mock_database_connection):
        """Test when no data is returned."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        result = fetch_emp_tags_data(mock_database_connection)
        
        assert result == []
        mock_cursor.close.assert_called_once()
    
    def test_sql_query_structure(self, mock_database_connection):
        """Test that SQL query has correct structure."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        fetch_emp_tags_data(mock_database_connection)
        
        call_args = mock_cursor.execute.call_args[0][0]
        assert "SELECT DISTINCT" in call_args
        assert "tblDetails" in call_args
        assert "empno" in call_args
        assert "tag" in call_args


class TestFetchDuplicateTagsData:
    """Test fetch_duplicate_tags_data function."""
    
    def test_successful_fetch(self, mock_database_connection, mock_pyodbc_row):
        """Test successful data fetch."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        
        sample_data = [("12345", "T001"), ("67890", "T002")]
        mock_rows = [mock_pyodbc_row(row) for row in sample_data]
        mock_cursor.fetchall.return_value = mock_rows
        
        result = fetch_duplicate_tags_data(mock_database_connection)
        
        assert result == mock_rows
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_sql_query_structure(self, mock_database_connection):
        """Test that SQL query has correct structure."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        fetch_duplicate_tags_data(mock_database_connection)
        
        call_args = mock_cursor.execute.call_args[0][0]
        assert "SELECT DISTINCT" in call_args
        assert "tblDLoadErrors" in call_args
        assert "Duplicate Tag" in call_args


class TestFetchEmpData:
    """Test fetch_emp_data function."""
    
    def test_successful_fetch(self, mock_database_connection, mock_pyodbc_row):
        """Test successful data fetch."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        
        sample_data = [("12345", "John Doe"), ("67890", "Jane Smith")]
        mock_rows = [mock_pyodbc_row(row) for row in sample_data]
        mock_cursor.fetchall.return_value = mock_rows
        
        result = fetch_emp_data(mock_database_connection)
        
        assert result == mock_rows
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_sql_query_structure(self, mock_database_connection):
        """Test that SQL query has correct structure."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        fetch_emp_data(mock_database_connection)
        
        call_args = mock_cursor.execute.call_args[0][0]
        assert "SELECT DISTINCT" in call_args
        assert "tblEmpNames" in call_args
        assert "tblTerminalControl" in call_args
        assert "INNER JOIN" in call_args


class TestFetchEmpTotalsData:
    """Test fetch_emp_totals_data function."""
    
    def test_successful_fetch(self, mock_database_connection, mock_pyodbc_row):
        """Test successful data fetch."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        
        sample_data = (100, 1000.0)
        mock_row = mock_pyodbc_row(sample_data)
        mock_cursor.fetchone.return_value = mock_row
        
        result = fetch_emp_totals_data(mock_database_connection, "T001,T002")
        
        assert result == mock_row
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_sql_query_structure(self, mock_database_connection):
        """Test that SQL query has correct structure."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        fetch_emp_totals_data(mock_database_connection, "T001,T002")
        
        call_args = mock_cursor.execute.call_args[0][0]
        assert "SELECT" in call_args
        assert "Sum" in call_args
        assert "tblTag" in call_args
        assert "CInt" in call_args
        assert "T001,T002" in call_args


class TestFetchEmpDiscrepanciesData:
    """Test fetch_emp_discrepancies_data function."""
    
    def test_successful_fetch(self, mock_database_connection, mock_pyodbc_row):
        """Test successful data fetch."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        
        sample_data = [(1, "T001", "123456789", 10.0, 5, 4, 10.0)]
        mock_rows = [mock_pyodbc_row(row) for row in sample_data]
        mock_cursor.fetchall.return_value = mock_rows
        
        result = fetch_emp_discrepancies_data(mock_database_connection, "T001,T002")
        
        assert result == mock_rows
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_sql_query_structure(self, mock_database_connection):
        """Test that SQL query has correct structure."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        fetch_emp_discrepancies_data(mock_database_connection, "T001,T002")
        
        call_args = mock_cursor.execute.call_args[0][0]
        assert "SELECT" in call_args
        assert "tblZoneChangeQueue" in call_args
        assert "tblZoneChangeInfo" in call_args
        assert "INNER JOIN" in call_args
        assert "SERVICE_MISCOUNTED" in call_args
        assert "Abs" in call_args
        assert "ORDER BY" in call_args


class TestFetchLineData:
    """Test fetch_line_data function."""
    
    def test_successful_fetch(self, mock_database_connection, mock_pyodbc_row):
        """Test successful data fetch."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        
        sample_data = ("12345",)
        mock_row = mock_pyodbc_row(sample_data)
        mock_cursor.fetchone.return_value = mock_row
        
        result = fetch_line_data(mock_database_connection, "T001", "123456789")
        
        assert result == mock_row
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_parameterized_query(self, mock_database_connection):
        """Test that query uses parameters correctly."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        fetch_line_data(mock_database_connection, "T001", "123456789")
        
        call_args = mock_cursor.execute.call_args
        # Check that the query contains the expected elements (accounting for formatting)
        query = call_args[0][0]
        assert "SELECT" in query
        assert "tblDetails.empno" in query
        assert "FROM tblDetails" in query
        assert "WHERE" in query
        assert "tblDetails.tag = ?" in query
        assert "tblDetails.sku = ?" in query
        assert call_args[0][1] == ("T001", "123456789")
    
    def test_sql_query_structure(self, mock_database_connection):
        """Test that SQL query has correct structure."""
        mock_cursor = Mock()
        mock_database_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        fetch_line_data(mock_database_connection, "T001", "123456789")
        
        call_args = mock_cursor.execute.call_args[0][0]
        assert "SELECT" in call_args
        assert "tblDetails" in call_args
        assert "empno" in call_args
        assert "WHERE" in call_args
        assert "?" in call_args
