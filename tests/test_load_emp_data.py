import pytest
from unittest.mock import MagicMock, patch

from services.load_emp_data import load_emp_data


class TestLoadEmpData:

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_database_exception_handling(self, mock_critical):
        """Test database exception handling."""
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception, match="Database connection failed"):
            load_emp_data(mock_conn)
        
        mock_critical.assert_called_once()

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_no_employee_records(self, mock_critical):
        """Test no employee records returns empty list."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert result == []

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_successful_data_loading(self, mock_critical):
        """Test successful data loading with basic employee data."""
        mock_emp_row = ("E001", "Alice Johnson")
        emp_tags_rows = [("E001", f"{i:03d}") for i in range(1, 26)]
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            emp_tags_rows,
            [],
            [mock_emp_row],
            []
        ]
        mock_cursor.fetchone.side_effect = [(100, 500.0), (0, 0)]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["employee_number"] == "E001"
        assert emp_data["employee_name"] == "Alice Johnson"
        assert emp_data["total_tags"] == 25
        assert emp_data["total_quantity"] == 100
        assert emp_data["total_price"] == 500.0
        assert emp_data["total_discrepancy_dollars"] == 0
        assert emp_data["discrepancy_percent"] == 0

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_discrepancy_calculation(self, mock_critical):
        """Test discrepancy calculation business logic."""
        mock_emp_row = ("E001", "Alice Johnson")
        emp_tags_rows = [("E001", "001")]
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            emp_tags_rows,
            [],
            [mock_emp_row],
            [(1, "001", "111111111", 10.0, 5, 15, 100.0)]
        ]
        mock_cursor.fetchone.side_effect = [(100, 500.0), (100.0, 1)]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_discrepancy_dollars"] == 100.0
        assert emp_data["discrepancy_percent"] == 20.0  # 100/500 * 100
        assert len(emp_data["discrepancies"]) == 1

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_duplicate_tags_handling(self, mock_critical):
        """Test duplicate tags handling business logic."""
        mock_emp_row = ("E001", "Alice Johnson")
        emp_tags_rows = [("E001", "001")]
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            emp_tags_rows,
            [("E001", "001")],  # Duplicate tag exists
            [mock_emp_row],
            [(1, "001", "111111111", 10.0, 5, 15, 100.0)]
        ]
        mock_cursor.fetchone.side_effect = [
            (100, 500.0),
            ("E001",),
            (100.0, 1)
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_discrepancy_dollars"] == 100.0
        assert len(emp_data["discrepancies"]) == 1

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_zero_division_handling(self, mock_critical):
        """Test zero division handling in discrepancy percent calculation."""
        mock_emp_row = ("E001", "Alice Johnson")
        emp_tags_rows = [("E001", "001")]
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            emp_tags_rows,
            [],
            [mock_emp_row],
            [(1, "001", "111111111", 10.0, 5, 15, 100.0)]
        ]
        mock_cursor.fetchone.side_effect = [(0, 0), (100.0, 1)]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["discrepancy_percent"] == 0

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_business_rule_discrepancy_threshold(self, mock_critical):
        """Test business rule: Only discrepancies >$50 with reason='SERVICE_MISCOUNTED' are counted."""
        mock_emp_row = ("E001", "Alice Johnson")
        emp_tags_rows = [("E001", "001"), ("E001", "002")]
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            emp_tags_rows,
            [],
            [mock_emp_row],
            [
                (1, "002", "222222222", 20.0, 3, 8, 100.0)
            ]
        ]
        mock_cursor.fetchone.side_effect = [(100, 500.0), (100.0, 1)]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_discrepancy_dollars"] == 100.0
        assert len(emp_data["discrepancies"]) == 1