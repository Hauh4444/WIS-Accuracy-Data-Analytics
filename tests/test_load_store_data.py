import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from services.load_store_data import load_store_data


class TestLoadStoreData:

    @patch("services.load_store_data.QtWidgets.QMessageBox.critical")
    def test_database_exception_handling(self, mock_critical):
        """Test database exception handling."""
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception, match="Database connection failed"):
            load_store_data(mock_conn)
        
        mock_critical.assert_called_once()

    @patch("services.load_store_data.QtWidgets.QMessageBox.critical")
    def test_successful_data_loading(self, mock_critical):
        """Test successful store data loading."""
        mock_wise_row = ("2024-01-15 10:00:00", "Test Store #123", "123 Test Street, Test City, TS 12345")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_wise_row
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_store_data(mock_conn)
        
        assert result["store"] == "Test Store #123"
        assert result["store_address"] == "123 Test Street, Test City, TS 12345"
        assert result["inventory_datetime"] == "2024-01-15 10:00:00"
        assert "print_date" in result
        assert "print_time" in result

    @patch("services.load_store_data.QtWidgets.QMessageBox.critical")
    def test_malformed_wise_data_structure(self, mock_critical):
        """Test handling of malformed WISE data structure."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("2024-01-15", "Test Store")
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        with pytest.raises(RuntimeError, match="Unexpected WISE data structure"):
            load_store_data(mock_conn)
        
        mock_critical.assert_called_once()

    @patch("services.load_store_data.QtWidgets.QMessageBox.critical")
    def test_empty_store_name_validation(self, mock_critical):
        """Test validation of empty store name."""
        mock_wise_row = ("2024-01-15 10:00:00", "", "123 Test Street")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_wise_row
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        with pytest.raises(RuntimeError, match="Store name is missing or empty"):
            load_store_data(mock_conn)
        
        mock_critical.assert_called_once()

    @patch("services.load_store_data.QtWidgets.QMessageBox.critical")
    def test_future_inventory_datetime_validation(self, mock_critical):
        """Test validation of future inventory datetime."""
        future_date = datetime(2030, 1, 15, 10, 0, 0)
        mock_wise_row = (future_date, "Test Store", "123 Test Street")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_wise_row
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        with pytest.raises(RuntimeError, match="Invalid inventory datetime"):
            load_store_data(mock_conn)
        
        mock_critical.assert_called_once()