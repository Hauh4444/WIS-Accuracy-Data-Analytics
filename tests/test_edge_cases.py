import pytest
from unittest.mock import MagicMock, patch
from PyQt6 import QtWidgets

from services.load_emp_data import load_emp_data
from services.load_team_data import load_team_data
from services.load_store_data import load_store_data


class TestDataLoadingEdgeCases:

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_load_emp_data_malformed_query_results(self, mock_critical):
        """Test handling of malformed database query results."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [("E001", "001", "EXTRA_COLUMN")],
            [],
            [],
            []
        ]
        mock_cursor.fetchone.side_effect = [(100, 500.0)]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        with pytest.raises(RuntimeError, match="Invalid emp_tags query result structure"):
            load_emp_data(mock_conn)

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_load_emp_data_large_dataset(self, mock_critical):
        """Test handling of large datasets (performance considerations)."""
        large_emp_tags = [("E001", f"{i:03d}") for i in range(1, 1001)]
        large_emp_rows = [("E001", "Alice Johnson")]
        large_discrepancies = [(1, f"{i:03d}", "123456789", 10.0, 5, 15, 100.0) for i in range(1, 501)]
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            large_emp_tags,
            [],
            large_emp_rows,
            large_discrepancies
        ]
        mock_cursor.fetchone.side_effect = [
            (10000, 50000.0),
            (50000.0, 500)
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_tags"] == 1000
        assert emp_data["total_discrepancy_tags"] == 500
        assert emp_data["total_discrepancy_dollars"] == 50000.0

    @patch("services.load_team_data.QtWidgets.QMessageBox.critical")
    def test_load_team_data_malformed_zone_data(self, mock_critical):
        """Test handling of malformed zone data."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [(101, "Finance", "EXTRA_COLUMN")],
        ]
        mock_cursor.fetchone.side_effect = [(50, 100, 500.0), (25.0, 1)]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        with pytest.raises(RuntimeError):
            load_team_data(mock_conn)

    @patch("services.load_store_data.QtWidgets.QMessageBox.critical")
    def test_load_store_data_malformed_wise_data(self, mock_critical):
        """Test handling of malformed WISE data structure."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("2024-01-15", "Test Store")
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        with pytest.raises(RuntimeError, match="Unexpected WISE data structure"):
            load_store_data(mock_conn)

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_load_emp_data_negative_values(self, mock_critical):
        """Test handling of negative values in database (edge case)."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [("E001", "001")],
            [],
            [("E001", "Alice Johnson")],
            []
        ]
        mock_cursor.fetchone.side_effect = [
            (-100, -500.0),
            (0, 0)
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_quantity"] == -100
        assert emp_data["total_price"] == -500.0
        assert emp_data["discrepancy_percent"] == 0