"""Tests for store data loading service."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import pyodbc
from PyQt6 import QtWidgets

from services.load_source_store_data import load_source_store_data


class TestLoadStoreData:
    """Test load_store_data function."""
    
    def test_successful_load(self, mock_database_connection, mock_pyodbc_row):
        """Test successful store data loading."""
        with patch('services.load_store_data.fetch_wise_data') as mock_fetch_wise:
            mock_fetch_wise.return_value = mock_pyodbc_row((
                datetime(2024, 1, 15, 10, 0, 0),
                "Test Store",
                "123 Test St, Test City, TC 12345"
            ))
            
            result = load_source_store_data(mock_database_connection)
            
            assert result['inventory_datetime'] == datetime(2024, 1, 15, 10, 0, 0)
            assert result['store'] == "Test Store"
            assert result['store_address'] == "123 Test St, Test City, TC 12345"
            assert 'print_date' in result
            assert 'print_time' in result
    
    def test_none_connection(self):
        """Test ValueError when connection is None."""
        with pytest.raises(ValueError, match="Database connection cannot be None"):
            load_source_store_data(None)
    
    def test_invalid_connection(self):
        """Test ValueError when connection lacks cursor method."""
        invalid_conn = Mock()
        del invalid_conn.cursor
        
        with pytest.raises(ValueError, match="Invalid database connection object"):
            load_source_store_data(invalid_conn)
    
    def test_wise_data_invalid_structure(self, mock_database_connection, mock_pyodbc_row):
        """Test RuntimeError when WISE data has invalid structure."""
        with patch('services.load_store_data.fetch_wise_data') as mock_fetch_wise:
            mock_fetch_wise.return_value = mock_pyodbc_row(("2024-01-15", "Test Store"))  # Wrong number of columns
            
            with pytest.raises(RuntimeError, match="Unexpected WISE data structure"):
                load_source_store_data(mock_database_connection)
    
    def test_none_wise_data(self, mock_database_connection):
        """Test RuntimeError when WISE data is None."""
        with patch('services.load_store_data.fetch_wise_data') as mock_fetch_wise:
            mock_fetch_wise.return_value = None
            
            with pytest.raises(RuntimeError, match="Unexpected WISE data structure"):
                load_source_store_data(mock_database_connection)
    
    def test_empty_store_name(self, mock_database_connection, mock_pyodbc_row):
        """Test RuntimeError when store name is empty."""
        with patch('services.load_store_data.fetch_wise_data') as mock_fetch_wise:
            mock_fetch_wise.return_value = mock_pyodbc_row((
                datetime(2024, 1, 15, 10, 0, 0),
                "",
                "123 Test St"
            ))
            
            with pytest.raises(RuntimeError, match="Store name is missing or empty"):
                load_source_store_data(mock_database_connection)
    
    def test_whitespace_store_name(self, mock_database_connection, mock_pyodbc_row):
        """Test RuntimeError when store name is only whitespace."""
        with patch('services.load_store_data.fetch_wise_data') as mock_fetch_wise:
            mock_fetch_wise.return_value = mock_pyodbc_row((
                datetime(2024, 1, 15, 10, 0, 0),
                "   ",
                "123 Test St"
            ))
            
            with pytest.raises(RuntimeError, match="Store name is missing or empty"):
                load_source_store_data(mock_database_connection)
    
    def test_future_inventory_datetime(self, mock_database_connection, mock_pyodbc_row):
        """Test RuntimeError when inventory datetime is in the future."""
        with patch('services.load_store_data.fetch_wise_data') as mock_fetch_wise:
            future_date = datetime(2030, 1, 15, 10, 0, 0)
            mock_fetch_wise.return_value = mock_pyodbc_row((
                future_date,
                "Test Store",
                "123 Test St"
            ))
            
            with pytest.raises(RuntimeError, match="Invalid inventory datetime"):
                load_source_store_data(mock_database_connection)
    
    def test_none_inventory_datetime(self, mock_database_connection, mock_pyodbc_row):
        """Test handling of None inventory datetime."""
        with patch('services.load_store_data.fetch_wise_data') as mock_fetch_wise:
            mock_fetch_wise.return_value = mock_pyodbc_row((
                None,
                "Test Store",
                "123 Test St"
            ))
            
            result = load_source_store_data(mock_database_connection)
            
            assert result['inventory_datetime'] == ""
            assert result['store'] == "Test Store"
    
    def test_none_store_name(self, mock_database_connection, mock_pyodbc_row):
        """Test handling of None store name."""
        with patch('services.load_store_data.fetch_wise_data') as mock_fetch_wise:
            mock_fetch_wise.return_value = mock_pyodbc_row((
                datetime(2024, 1, 15, 10, 0, 0),
                None,
                "123 Test St"
            ))
            
            result = load_source_store_data(mock_database_connection)
            
            assert result['store'] == ""
            assert result['store_address'] == "123 Test St"
    
    def test_none_store_address(self, mock_database_connection, mock_pyodbc_row):
        """Test handling of None store address."""
        with patch('services.load_store_data.fetch_wise_data') as mock_fetch_wise:
            mock_fetch_wise.return_value = mock_pyodbc_row((
                datetime(2024, 1, 15, 10, 0, 0),
                "Test Store",
                None
            ))
            
            result = load_source_store_data(mock_database_connection)
            
            assert result['store'] == "Test Store"
            assert result['store_address'] == ""
    
    def test_string_strip_handling(self, mock_database_connection, mock_pyodbc_row):
        """Test that string values are properly stripped."""
        with patch('services.load_store_data.fetch_wise_data') as mock_fetch_wise:
            mock_fetch_wise.return_value = mock_pyodbc_row((
                datetime(2024, 1, 15, 10, 0, 0),
                "  Test Store  ",
                "  123 Test St  "
            ))
            
            result = load_source_store_data(mock_database_connection)
            
            assert result['store'] == "Test Store"
            assert result['store_address'] == "123 Test St"
    
    def test_pyodbc_error_handling(self, mock_database_connection):
        """Test pyodbc error handling."""
        with patch('services.load_store_data.fetch_wise_data', side_effect=pyodbc.Error("Database error")):
            with patch('services.load_store_data.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(pyodbc.Error):
                    load_source_store_data(mock_database_connection)
                mock_msgbox.assert_called_once()
    
    def test_value_error_handling(self, mock_database_connection):
        """Test ValueError handling."""
        with patch('services.load_store_data.fetch_wise_data', side_effect=ValueError("Value error")):
            with patch('services.load_store_data.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(ValueError):
                    load_source_store_data(mock_database_connection)
                mock_msgbox.assert_called_once()
    
    def test_runtime_error_handling(self, mock_database_connection):
        """Test RuntimeError handling."""
        with patch('services.load_store_data.fetch_wise_data', side_effect=RuntimeError("Runtime error")):
            with patch('services.load_store_data.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(RuntimeError):
                    load_source_store_data(mock_database_connection)
                mock_msgbox.assert_called_once()
    
    def test_generic_exception_handling(self, mock_database_connection):
        """Test generic Exception handling."""
        with patch('services.load_store_data.fetch_wise_data', side_effect=Exception("Generic error")):
            with patch('services.load_store_data.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(Exception):
                    load_source_store_data(mock_database_connection)
                mock_msgbox.assert_called_once()
    
    def test_datetime_formatting(self, mock_database_connection, mock_pyodbc_row):
        """Test that datetime values are handled correctly."""
        with patch('services.load_store_data.fetch_wise_data') as mock_fetch_wise:
            test_datetime = datetime(2024, 1, 15, 10, 30, 45)
            mock_fetch_wise.return_value = mock_pyodbc_row((
                test_datetime,
                "Test Store",
                "123 Test St"
            ))
            
            result = load_source_store_data(mock_database_connection)
            
            assert result['inventory_datetime'] == test_datetime
            assert result['print_date'] == "1/15/2024"
            assert result['print_time'] == "10:30:45AM"
