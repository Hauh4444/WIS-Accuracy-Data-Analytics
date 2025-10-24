"""Tests for employee data loading service."""
import pytest
from unittest.mock import Mock, patch
import pyodbc
from PyQt6 import QtWidgets

from services.load_emp_data import load_emp_data
from repositories.emp_repository import (
    fetch_emp_tags_data, fetch_duplicate_tags_data, fetch_emp_data,
    fetch_emp_totals_data, fetch_emp_discrepancies_data, fetch_line_data
)


class TestLoadEmpData:
    """Test load_emp_data function."""
    
    def test_successful_load(self, mock_database_connection, mock_pyodbc_row):
        """Test successful employee data loading."""
        # Mock repository functions
        with patch('services.load_emp_data.fetch_emp_tags_data') as mock_emp_tags, \
             patch('services.load_emp_data.fetch_duplicate_tags_data') as mock_duplicate_tags, \
             patch('services.load_emp_data.fetch_emp_data') as mock_emp_data, \
             patch('services.load_emp_data.fetch_emp_totals_data') as mock_emp_totals, \
             patch('services.load_emp_data.fetch_emp_discrepancies_data') as mock_emp_discrepancies, \
             patch('services.load_emp_data.fetch_line_data') as mock_line_data:
            
            # Setup mock data
            mock_emp_tags.return_value = [mock_pyodbc_row(("12345", "T001")), mock_pyodbc_row(("12345", "T002"))]
            mock_duplicate_tags.return_value = []
            mock_emp_data.return_value = [mock_pyodbc_row(("12345", "John Doe"))]
            mock_emp_totals.return_value = mock_pyodbc_row((100, 1000.0))
            mock_emp_discrepancies.return_value = []
            
            result = load_emp_data(mock_database_connection)
            
            assert len(result) == 1
            assert result[0]['emp_number'] == '12345'
            assert result[0]['emp_name'] == 'John Doe'
            assert result[0]['total_tags'] == 2
            assert result[0]['total_quantity'] == 100
            assert result[0]['total_price'] == 1000.0
    
    def test_none_connection(self):
        """Test ValueError when connection is None."""
        with pytest.raises(ValueError, match="Database connection cannot be None"):
            load_emp_data(None)
    
    def test_invalid_connection(self):
        """Test ValueError when connection lacks cursor method."""
        invalid_conn = Mock()
        del invalid_conn.cursor
        
        with pytest.raises(ValueError, match="Invalid database connection object"):
            load_emp_data(invalid_conn)
    
    def test_emp_tags_invalid_structure(self, mock_database_connection, mock_pyodbc_row):
        """Test RuntimeError when emp_tags has invalid structure."""
        with patch('services.load_emp_data.fetch_emp_tags_data') as mock_emp_tags:
            mock_emp_tags.return_value = [mock_pyodbc_row(("12345",))]  # Wrong number of columns
            
            with pytest.raises(RuntimeError, match="Invalid emp_tags query result structure"):
                load_emp_data(mock_database_connection)
    
    def test_duplicate_tags_invalid_structure(self, mock_database_connection, mock_pyodbc_row):
        """Test RuntimeError when duplicate_tags has invalid structure."""
        with patch('services.load_emp_data.fetch_emp_tags_data') as mock_emp_tags, \
             patch('services.load_emp_data.fetch_duplicate_tags_data') as mock_duplicate_tags:
            
            mock_emp_tags.return_value = [mock_pyodbc_row(("12345", "T001"))]
            mock_duplicate_tags.return_value = [mock_pyodbc_row(("12345",))]  # Wrong number of columns
            
            with pytest.raises(RuntimeError, match="Invalid duplicate_tags query result structure"):
                load_emp_data(mock_database_connection)
    
    def test_emp_data_invalid_structure(self, mock_database_connection, mock_pyodbc_row):
        """Test RuntimeError when emp_data has invalid structure."""
        with patch('services.load_emp_data.fetch_emp_tags_data') as mock_emp_tags, \
             patch('services.load_emp_data.fetch_duplicate_tags_data') as mock_duplicate_tags, \
             patch('services.load_emp_data.fetch_emp_data') as mock_emp_data:
            
            mock_emp_tags.return_value = [mock_pyodbc_row(("12345", "T001"))]
            mock_duplicate_tags.return_value = []
            mock_emp_data.return_value = [mock_pyodbc_row(("12345",))]  # Wrong number of columns
            
            with pytest.raises(RuntimeError, match="Invalid emp query result structure"):
                load_emp_data(mock_database_connection)
    
    def test_emp_totals_invalid_structure(self, mock_database_connection, mock_pyodbc_row):
        """Test RuntimeError when emp_totals has invalid structure."""
        with patch('services.load_emp_data.fetch_emp_tags_data') as mock_emp_tags, \
             patch('services.load_emp_data.fetch_duplicate_tags_data') as mock_duplicate_tags, \
             patch('services.load_emp_data.fetch_emp_data') as mock_emp_data, \
             patch('services.load_emp_data.fetch_emp_totals_data') as mock_emp_totals:
            
            mock_emp_tags.return_value = [mock_pyodbc_row(("12345", "T001"))]
            mock_duplicate_tags.return_value = []
            mock_emp_data.return_value = [mock_pyodbc_row(("12345", "John Doe"))]
            mock_emp_totals.return_value = mock_pyodbc_row((100,))  # Wrong number of columns
            
            with pytest.raises(RuntimeError, match="Invalid emp_totals query result"):
                load_emp_data(mock_database_connection)
    
    def test_emp_discrepancies_invalid_structure(self, mock_database_connection, mock_pyodbc_row):
        """Test RuntimeError when emp_discrepancies has invalid structure."""
        with patch('services.load_emp_data.fetch_emp_tags_data') as mock_emp_tags, \
             patch('services.load_emp_data.fetch_duplicate_tags_data') as mock_duplicate_tags, \
             patch('services.load_emp_data.fetch_emp_data') as mock_emp_data, \
             patch('services.load_emp_data.fetch_emp_totals_data') as mock_emp_totals, \
             patch('services.load_emp_data.fetch_emp_discrepancies_data') as mock_emp_discrepancies:
            
            mock_emp_tags.return_value = [mock_pyodbc_row(("12345", "T001"))]
            mock_duplicate_tags.return_value = []
            mock_emp_data.return_value = [mock_pyodbc_row(("12345", "John Doe"))]
            mock_emp_totals.return_value = mock_pyodbc_row((100, 1000.0))
            mock_emp_discrepancies.return_value = [mock_pyodbc_row((1, 2, 3, 4, 5, 6))]  # Wrong number of columns
            
            with pytest.raises(RuntimeError, match="Invalid emp_discrepancies query result structure"):
                load_emp_data(mock_database_connection)
    
    def test_discrepancy_calculation(self, mock_database_connection, mock_pyodbc_row):
        """Test discrepancy calculation logic."""
        with patch('services.load_emp_data.fetch_emp_tags_data') as mock_emp_tags, \
             patch('services.load_emp_data.fetch_duplicate_tags_data') as mock_duplicate_tags, \
             patch('services.load_emp_data.fetch_emp_data') as mock_emp_data, \
             patch('services.load_emp_data.fetch_emp_totals_data') as mock_emp_totals, \
             patch('services.load_emp_data.fetch_emp_discrepancies_data') as mock_emp_discrepancies:
            
            mock_emp_tags.return_value = [mock_pyodbc_row(("12345", "T001"))]
            mock_duplicate_tags.return_value = []
            mock_emp_data.return_value = [mock_pyodbc_row(("12345", "John Doe"))]
            mock_emp_totals.return_value = mock_pyodbc_row((100, 1000.0))
            mock_emp_discrepancies.return_value = [
                mock_pyodbc_row((1, "T001", "123456789", 10.0, 5, 4, 10.0))
            ]
            
            result = load_emp_data(mock_database_connection)
            
            assert result[0]['total_discrepancy_dollars'] == 10.0
            assert result[0]['total_discrepancy_tags'] == 1
            assert result[0]['discrepancy_percent'] == 1.0
            assert len(result[0]['discrepancies']) == 1
    
    def test_duplicate_tag_verification(self, mock_database_connection, mock_pyodbc_row):
        """Test duplicate tag verification logic."""
        with patch('services.load_emp_data.fetch_emp_tags_data') as mock_emp_tags, \
             patch('services.load_emp_data.fetch_duplicate_tags_data') as mock_duplicate_tags, \
             patch('services.load_emp_data.fetch_emp_data') as mock_emp_data, \
             patch('services.load_emp_data.fetch_emp_totals_data') as mock_emp_totals, \
             patch('services.load_emp_data.fetch_emp_discrepancies_data') as mock_emp_discrepancies, \
             patch('services.load_emp_data.fetch_line_data') as mock_line_data:
            
            mock_emp_tags.return_value = [mock_pyodbc_row(("12345", "T001"))]
            mock_duplicate_tags.return_value = [mock_pyodbc_row(("12345", "T001"))]
            mock_emp_data.return_value = [mock_pyodbc_row(("12345", "John Doe"))]
            mock_emp_totals.return_value = mock_pyodbc_row((100, 1000.0))
            mock_emp_discrepancies.return_value = [
                mock_pyodbc_row((1, "T001", "123456789", 10.0, 5, 4, 10.0))
            ]
            mock_line_data.return_value = mock_pyodbc_row(("67890",))  # Different employee
            
            result = load_emp_data(mock_database_connection)
            
            # Discrepancy should be excluded because employee numbers don't match
            assert result[0]['total_discrepancy_dollars'] == 0.0
            assert result[0]['total_discrepancy_tags'] == 0
            assert len(result[0]['discrepancies']) == 0
    
    def test_pyodbc_error_handling(self, mock_database_connection):
        """Test pyodbc error handling."""
        with patch('services.load_emp_data.fetch_emp_tags_data', side_effect=pyodbc.Error("Database error")):
            with patch('services.load_emp_data.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(pyodbc.Error):
                    load_emp_data(mock_database_connection)
                mock_msgbox.assert_called_once()
    
    def test_value_error_handling(self, mock_database_connection):
        """Test ValueError handling."""
        with patch('services.load_emp_data.fetch_emp_tags_data', side_effect=ValueError("Value error")):
            with patch('services.load_emp_data.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(ValueError):
                    load_emp_data(mock_database_connection)
                mock_msgbox.assert_called_once()
    
    def test_runtime_error_handling(self, mock_database_connection):
        """Test RuntimeError handling."""
        with patch('services.load_emp_data.fetch_emp_tags_data', side_effect=RuntimeError("Runtime error")):
            with patch('services.load_emp_data.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(RuntimeError):
                    load_emp_data(mock_database_connection)
                mock_msgbox.assert_called_once()
    
    def test_generic_exception_handling(self, mock_database_connection):
        """Test generic Exception handling."""
        with patch('services.load_emp_data.fetch_emp_tags_data', side_effect=Exception("Generic error")):
            with patch('services.load_emp_data.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(Exception):
                    load_emp_data(mock_database_connection)
                mock_msgbox.assert_called_once()
    
    def test_empty_emp_tags_skips_employee(self, mock_database_connection, mock_pyodbc_row):
        """Test that employees with no tags are skipped."""
        with patch('services.load_emp_data.fetch_emp_tags_data') as mock_emp_tags, \
             patch('services.load_emp_data.fetch_duplicate_tags_data') as mock_duplicate_tags, \
             patch('services.load_emp_data.fetch_emp_data') as mock_emp_data:
            
            mock_emp_tags.return_value = []
            mock_duplicate_tags.return_value = []
            mock_emp_data.return_value = [mock_pyodbc_row(("12345", "John Doe"))]
            
            result = load_emp_data(mock_database_connection)
            
            assert result == []
    
    def test_zero_total_price_discrepancy_percent(self, mock_database_connection, mock_pyodbc_row):
        """Test discrepancy percent calculation when total_price is zero."""
        with patch('services.load_emp_data.fetch_emp_tags_data') as mock_emp_tags, \
             patch('services.load_emp_data.fetch_duplicate_tags_data') as mock_duplicate_tags, \
             patch('services.load_emp_data.fetch_emp_data') as mock_emp_data, \
             patch('services.load_emp_data.fetch_emp_totals_data') as mock_emp_totals, \
             patch('services.load_emp_data.fetch_emp_discrepancies_data') as mock_emp_discrepancies:
            
            mock_emp_tags.return_value = [mock_pyodbc_row(("12345", "T001"))]
            mock_duplicate_tags.return_value = []
            mock_emp_data.return_value = [mock_pyodbc_row(("12345", "John Doe"))]
            mock_emp_totals.return_value = mock_pyodbc_row((100, 0.0))  # Zero total price
            mock_emp_discrepancies.return_value = [
                mock_pyodbc_row((1, "T001", "123456789", 10.0, 5, 4, 10.0))
            ]
            
            result = load_emp_data(mock_database_connection)
            
            assert result[0]['discrepancy_percent'] == 0.0
