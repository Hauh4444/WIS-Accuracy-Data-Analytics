import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from services.load_store_data import load_store_data


class TestLoadStoreData:

    def make_mock_row(self, **kwargs):
        row = MagicMock()
        for k, v in kwargs.items():
            setattr(row, k, v)
        return row

    @patch("services.load_store_data.QtWidgets.QMessageBox.critical")
    def test_database_exception_handling(self, mock_critical):
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception, match="Database connection failed"):
            load_store_data(mock_conn)
        
        mock_critical.assert_called_once()
        assert "An unexpected error occurred" in mock_critical.call_args[0][2]

    @patch("services.load_store_data.QtWidgets.QMessageBox.critical")
    def test_cursor_execute_exception(self, mock_critical):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("SQL execution failed")
        
        with pytest.raises(Exception, match="SQL execution failed"):
            load_store_data(mock_conn)
        
        mock_critical.assert_called_once()
        assert "SQL execution failed" in mock_critical.call_args[0][2]

    @patch("services.load_store_data.QtWidgets.QMessageBox.critical")
    def test_fetchone_exception(self, mock_critical):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = Exception("Fetch failed")
        
        with pytest.raises(Exception, match="Fetch failed"):
            load_store_data(mock_conn)
        
        mock_critical.assert_called_once()
        assert "Fetch failed" in mock_critical.call_args[0][2]

    @patch("services.load_store_data.QtWidgets.QMessageBox.critical")
    def test_successful_data_loading(self, mock_critical):
        mock_wise_row = (
            datetime(2024, 1, 15, 10, 30, 0),
            "Test Store #123",
            "123 Test Street, Test City, TS 12345"
        )
        
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_wise_row
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        with patch("services.load_store_data.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 15, 14, 30, 45)
            mock_datetime.now.return_value = mock_now
            
            result = load_store_data(mock_conn)
        
        assert isinstance(result, dict)
        assert result["inventory_datetime"] == datetime(2024, 1, 15, 10, 30, 0)
        assert result["store"] == "Test Store #123"
        assert result["store_address"] == "123 Test Street, Test City, TS 12345"
        assert result["print_date"] == "1/15/2024"
        assert result["print_time"] == "02:30:45PM"

    def test_successful_data_loading_with_none_values(self):
        mock_wise_row = (None, "Test Store", None)
        
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_wise_row
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        with patch("services.load_store_data.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 15, 14, 30, 45)
            mock_datetime.now.return_value = mock_now
            
            result = load_store_data(mock_conn)
        
        assert isinstance(result, dict)
        assert result["inventory_datetime"] == ""
        assert result["store"] == "Test Store"
        assert result["store_address"] == ""
        assert result["print_date"] == "1/15/2024"
        assert result["print_time"] == "02:30:45PM"

    @patch("services.load_store_data.QtWidgets.QMessageBox.critical")
    def test_no_data_found(self, mock_critical):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        with patch("services.load_store_data.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 15, 14, 30, 45)
            mock_datetime.now.return_value = mock_now
            
            with pytest.raises(RuntimeError, match="Unexpected WISE data structure"):
                load_store_data(mock_conn)

    def test_print_date_formatting(self):
        mock_wise_row = (
            datetime(2024, 1, 15, 10, 30, 0),
            "Test Store",
            "Test Address"
        )
        
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_wise_row
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        test_cases = [
            (datetime(2024, 1, 1, 12, 0, 0), "1/1/2024"),
            (datetime(2024, 12, 31, 12, 0, 0), "12/31/2024"),
            (datetime(2024, 6, 15, 12, 0, 0), "6/15/2024"),
        ]
        
        for mock_now, expected_date in test_cases:
            with patch("services.load_store_data.datetime") as mock_datetime:
                mock_datetime.now.return_value = mock_now
                
                result = load_store_data(mock_conn)
                
                assert result["print_date"] == expected_date

    def test_print_time_formatting(self):
        mock_wise_row = (
            datetime(2024, 1, 15, 10, 30, 0),
            "Test Store",
            "Test Address"
        )
        
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_wise_row
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        test_cases = [
            (datetime(2024, 1, 15, 14, 30, 45), "02:30:45PM"),
            (datetime(2024, 1, 15, 1, 5, 10), "01:05:10AM"),
            (datetime(2024, 1, 15, 12, 0, 0), "12:00:00PM"),
            (datetime(2024, 1, 15, 0, 0, 0), "12:00:00AM"),
        ]
        
        for mock_now, expected_time in test_cases:
            with patch("services.load_store_data.datetime") as mock_datetime:
                mock_datetime.now.return_value = mock_now
                
                result = load_store_data(mock_conn)
                
                assert result["print_time"] == expected_time

    def test_cursor_execute_called_with_correct_query(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (datetime.now(), "Test Store", "Test Address")
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        load_store_data(mock_conn)
        
        assert mock_cursor.execute.called
        call_args = mock_cursor.execute.call_args[0][0]
        assert "tblWISEInfo" in call_args
        assert "JobDateTime" in call_args
        assert "Name" in call_args
        assert "Address" in call_args
        assert "SELECT" in call_args

    def test_return_structure_consistency(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            datetime(2024, 1, 15, 10, 30, 0),
            "Test Store",
            "Test Address"
        )
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        with patch("services.load_store_data.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 15, 14, 30, 45)
            mock_datetime.now.return_value = mock_now
            
            result = load_store_data(mock_conn)
        
        expected_keys = {
            "inventory_datetime", 
            "print_date", 
            "store", 
            "print_time", 
            "store_address"
        }
        assert set(result.keys()) == expected_keys
        
        assert isinstance(result["inventory_datetime"], datetime)
        assert isinstance(result["print_date"], str)
        assert isinstance(result["store"], str)
        assert isinstance(result["print_time"], str)
        assert isinstance(result["store_address"], str)

    @patch("services.load_store_data.QtWidgets.QMessageBox.critical")
    def test_error_handling_with_default_values(self, mock_critical):
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("Test error")
        
        with patch("services.load_store_data.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 15, 14, 30, 45)
            mock_datetime.now.return_value = mock_now
            
            with pytest.raises(Exception, match="Test error"):
                load_store_data(mock_conn)
        
        mock_critical.assert_called_once()
        assert "An unexpected error occurred" in mock_critical.call_args[0][2]

    def test_partial_data_handling(self):
        mock_wise_row = (
            datetime(2024, 1, 15, 10, 30, 0),
            "Test Store",
            "123 Test Street, Test City, TS 12345"
        )
        
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_wise_row
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        with patch("services.load_store_data.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 15, 14, 30, 45)
            mock_datetime.now.return_value = mock_now
            
            result = load_store_data(mock_conn)
        
        assert result["inventory_datetime"] == datetime(2024, 1, 15, 10, 30, 0)
        assert result["store"] == "Test Store"
        assert result["store_address"] == "123 Test Street, Test City, TS 12345"

    def test_wisemodel_table_structure(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (datetime.now(), "Test", "Test")
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        load_store_data(mock_conn)
        
        call_args = mock_cursor.execute.call_args[0][0]
        assert "tblWISEInfo" in call_args
        assert "JobDateTime" in call_args
        assert "Name" in call_args
        assert "Address" in call_args
