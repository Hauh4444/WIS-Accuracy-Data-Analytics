import pytest
from unittest.mock import MagicMock, patch

from services.load_emp_data import load_emp_data


class TestLoadEmpData:
    """Test cases for employee data loading."""

    def make_mock_row(self, **kwargs):
        """Helper to create mock database row."""
        row = MagicMock()
        for k, v in kwargs.items():
            setattr(row, k, v)
        return row

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_database_exception_handling(self, mock_critical):
        """Test error handling when database connection fails."""
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("Database connection failed")
        
        result = load_emp_data(mock_conn)
        
        assert result == []
        mock_critical.assert_called_once()
        assert "Database connection failed" in mock_critical.call_args[0][2]

    def test_no_employee_records(self):
        """Test handling when no employee records are found."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert result == []

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_successful_data_loading(self, mock_critical):
        """Test successful loading of employee data."""
        mock_emp_row = ("E001", "Alice Johnson", 25)
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_emp_row],
            [("TAG001",)],
            []  # no discrepancies
        ]
        mock_cursor.fetchone.side_effect = [
            (100, 500.0),  # tag totals
            (0,),          # discrepancy dollars
            (0,)           # discrepancy tags
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["employee_name"] == "Alice Johnson"
        assert result[0]["employee_id"] == "E001"
        assert result[0]["total_tags"] == 25
        assert result[0]["total_quantity"] == 100
        assert result[0]["total_price"] == 500.0
        assert result[0]["total_discrepancy_dollars"] == 0
        assert result[0]["total_discrepancy_tags"] == 0
        assert result[0]["discrepancy_percent"] == 0
        assert result[0]["discrepancies"] == []

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_multiple_employees_loading(self, mock_critical):
        """Test loading multiple employee records."""
        mock_row1 = ("E001", "Alice Johnson", 20)
        mock_row2 = ("E002", "Bob Smith", 15)
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_row1, mock_row2],
            [("TAG001",)],
            [],  # no discrepancies for employee 1
            [("TAG002",)],
            []   # no discrepancies for employee 2
        ]
        mock_cursor.fetchone.side_effect = [
            (100, 500.0),  # tag totals for employee 1
            (0,),          # discrepancy dollars for employee 1
            (0,),          # discrepancy tags for employee 1
            (100, 500.0),  # tag totals for employee 2
            (0,),          # discrepancy dollars for employee 2
            (0,)           # discrepancy tags for employee 2
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 2
        assert result[0]["employee_name"] == "Alice Johnson"
        assert result[1]["employee_name"] == "Bob Smith"
        
        # Verify all expected fields are present for both employees
        for emp_data in result:
            assert "employee_id" in emp_data
            assert "employee_name" in emp_data
            assert "total_tags" in emp_data
            assert "total_quantity" in emp_data
            assert "total_price" in emp_data
            assert "total_discrepancy_dollars" in emp_data
            assert "total_discrepancy_tags" in emp_data
            assert "discrepancy_percent" in emp_data

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_cursor_execute_called(self, mock_critical):
        """Test that cursor execute is called properly."""
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = [
            [("E001", "Test Employee", 5)],
            [("TAG001",)]
        ]
        mock_cursor.fetchone.return_value = None
        
        load_emp_data(mock_conn)
        
        assert mock_cursor.execute.called

    def test_zero_discrepancy_calculation(self):
        """Test calculation when discrepancy values are zero."""
        mock_emp_row = ("E001", "Alice Johnson", 25)
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_emp_row],
            [("TAG001",)],
            []  # no discrepancies
        ]
        mock_cursor.fetchone.side_effect = [
            (100, 500.0),  # tag totals
            (0,),          # discrepancy dollars = 0
            (0,)           # discrepancy tags = 0
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_discrepancy_dollars"] == 0
        assert emp_data["total_discrepancy_tags"] == 0
        assert emp_data["discrepancy_percent"] == 0
        assert emp_data["discrepancies"] == []

    def test_high_discrepancy_calculation(self):
        """Test calculation with high discrepancy values."""
        mock_emp_row = ("E001", "Alice Johnson", 25)
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_emp_row],
            [("TAG001",)],
            [(100.0, 5, 10, 10.0, "E001", "111111111", 1), (150.0, 3, 8, 18.75, "E001", "222222222", 2)]  # high discrepancies
        ]
        mock_cursor.fetchone.side_effect = [
            (100, 500.0),  # tag totals
            (250.0,),      # high discrepancy dollars
            (5,)           # high discrepancy tags
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_discrepancy_dollars"] == 250.0
        assert emp_data["total_discrepancy_tags"] == 5
        assert emp_data["discrepancy_percent"] == 50.0  # 250/500 * 100
        
        # Check discrepancies data
        assert len(emp_data["discrepancies"]) == 2
        assert emp_data["discrepancies"][0]["discrepancy_dollars"] == 100.0
        assert emp_data["discrepancies"][1]["discrepancy_dollars"] == 150.0

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_discrepancy_calculation_with_data(self, mock_critical):
        """Test discrepancy calculation when discrepancy data exists."""
        mock_emp_row = ("E001", "Alice Johnson", 25)
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_emp_row],
            [("TAG001",)],
            [(50.0, 10, 5, 10.0, "E001", "123456789", 1), (25.0, 8, 3, 8.33, "E001", "987654321", 2)]  # discrepancies
        ]
        mock_cursor.fetchone.side_effect = [
            (100, 500.0),  # tag totals
            (75.0,),       # discrepancy dollars
            (2,)           # discrepancy tags
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_discrepancy_dollars"] == 75.0
        assert emp_data["total_discrepancy_tags"] == 2
        assert emp_data["discrepancy_percent"] == 15.0  # 75/500 * 100
        
        # Check discrepancies data
        assert len(emp_data["discrepancies"]) == 2
        assert emp_data["discrepancies"][0]["discrepancy_dollars"] == 50.0
        assert emp_data["discrepancies"][0]["counted_qty"] == 10
        assert emp_data["discrepancies"][0]["quantity"] == 5
        assert emp_data["discrepancies"][0]["price"] == 10.0
        assert emp_data["discrepancies"][0]["emp_no"] == "E001"
        assert emp_data["discrepancies"][0]["upc"] == "123456789"
        assert emp_data["discrepancies"][0]["zone_id"] == 1

    def test_discrepancy_percent_zero_division(self):
        """Test that discrepancy percent is 0 when total_price is 0."""
        mock_emp_row = ("E001", "Alice Johnson", 25)
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_emp_row],
            [("TAG001",)],
            [(50.0, 5, 3, 16.67, "E001", "333333333", 1)]  # discrepancies
        ]
        mock_cursor.fetchone.side_effect = [
            (100, 0.0),    # tag totals with 0 price
            (50.0,),       # discrepancy dollars
            (1,)           # discrepancy tags
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_price"] == 0.0
        assert emp_data["discrepancy_percent"] == 0  # Should be 0, not cause division by zero

    def test_null_values_handling(self):
        """Test handling of None values from database."""
        mock_emp_row = ("E001", "Alice Johnson", 25)
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_emp_row],
            [("TAG001",)]
        ]
        mock_cursor.fetchone.side_effect = [
            (None, None),  # tag totals are None
            (None,),       # discrepancy dollars is None
            (None,)        # discrepancy tags is None
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_quantity"] == 0  # Should handle None as 0
        assert emp_data["total_price"] == 0     # Should handle None as 0
        assert emp_data["total_discrepancy_dollars"] == 0  # Should handle None as 0
        assert emp_data["total_discrepancy_tags"] == 0     # Should handle None as 0