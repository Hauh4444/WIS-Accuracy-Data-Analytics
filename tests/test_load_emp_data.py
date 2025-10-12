import pytest
from unittest.mock import MagicMock, patch

from services.load_emp_data import load_emp_data


class TestLoadEmpData:

    def make_mock_row(self, **kwargs):
        """Helper to create mock database row."""
        row = MagicMock()
        for k, v in kwargs.items():
            setattr(row, k, v)
        return row

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_database_exception_handling(self, mock_critical):
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("Database connection failed")
        
        result = load_emp_data(mock_conn)
        
        assert result == []
        mock_critical.assert_called_once()
        assert "Database connection failed" in mock_critical.call_args[0][2]

    def test_no_employee_records(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert result == []

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_successful_data_loading(self, mock_critical):
        mock_emp_row = ("E001", "Alice Johnson")
        
        # Tags query returns (emp_no, tag) pairs to build emp_tags_map
        tag_rows = [("E001", f"TAG{i:03d}") for i in range(1, 26)]
        
        mock_cursor = MagicMock()
        # First fetchall is tags query, second is emp query
        mock_cursor.fetchall.side_effect = [
            tag_rows,
            [mock_emp_row],
            []
        ]
        mock_cursor.fetchone.side_effect = [
            (2500, 12500.0),
            (0,),
            (0,)
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["employee_name"] == "Alice Johnson"
        assert result[0]["employee_id"] == "E001"
        assert result[0]["total_tags"] == 25
        assert result[0]["total_quantity"] == 2500
        assert result[0]["total_price"] == 12500.0
        assert result[0]["total_discrepancy_dollars"] == 0
        assert result[0]["total_discrepancy_tags"] == 0
        assert result[0]["discrepancy_percent"] == 0
        assert result[0]["discrepancies"] == []

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_multiple_employees_loading(self, mock_critical):
        mock_row1 = ("E001", "Alice Johnson")
        mock_row2 = ("E002", "Bob Smith")
        
        mock_cursor = MagicMock()
        # First fetchall is tags query, second is emp query
        mock_cursor.fetchall.side_effect = [
            [("E001", "TAG001"), ("E002", "TAG002")],
            [mock_row1, mock_row2],
            [],
            []
        ]
        mock_cursor.fetchone.side_effect = [
            (100, 500.0),
            (0,),
            (0,),
            (100, 500.0),
            (0,),
            (0,)
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 2
        assert result[0]["employee_name"] == "Alice Johnson"
        assert result[1]["employee_name"] == "Bob Smith"
        
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
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = [
            [("E001", "TAG001")],
            [("E001", "Test Employee")]
        ]
        mock_cursor.fetchone.return_value = None
        
        load_emp_data(mock_conn)
        
        assert mock_cursor.execute.called

    def test_zero_discrepancy_calculation(self):
        mock_emp_row = ("E001", "Alice Johnson")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [("E001", "TAG001")],
            [mock_emp_row],
            []
        ]
        mock_cursor.fetchone.side_effect = [
            (100, 500.0),
            (0,),
            (0,)
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
        mock_emp_row = ("E001", "Alice Johnson")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [("E001", "TAG001")],
            [mock_emp_row],
            [(1, "TAG001", "111111111", 10.0, 5, 15, 100.0),
             (2, "TAG001", "222222222", 18.75, 3, 11, 150.0)]
        ]
        mock_cursor.fetchone.side_effect = [
            (100, 500.0),
            (250.0,),
            (2,)
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_discrepancy_dollars"] == 250.0
        assert emp_data["total_discrepancy_tags"] == 2
        assert emp_data["discrepancy_percent"] == 50.0
        
        assert len(emp_data["discrepancies"]) == 2
        assert emp_data["discrepancies"][0]["zone_id"] == 1
        assert emp_data["discrepancies"][0]["tag"] == "TAG001"
        assert emp_data["discrepancies"][0]["upc"] == "111111111"
        assert emp_data["discrepancies"][0]["price"] == 10.0
        assert emp_data["discrepancies"][0]["counted_qty"] == 5
        assert emp_data["discrepancies"][0]["new_quantity"] == 15
        assert emp_data["discrepancies"][0]["discrepancy_dollars"] == 100.0
        assert emp_data["discrepancies"][1]["discrepancy_dollars"] == 150.0

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_discrepancy_calculation_with_data(self, mock_critical):
        mock_emp_row = ("E001", "Alice Johnson")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [("E001", "TAG001")],
            [mock_emp_row],
            [(1, "TAG001", "123456789", 10.0, 5, 10, 50.0),
             (2, "TAG001", "987654321", 8.33, 3, 6, 25.0)]
        ]
        mock_cursor.fetchone.side_effect = [
            (100, 500.0),
            (75.0,),
            (2,)
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_discrepancy_dollars"] == 75.0
        assert emp_data["total_discrepancy_tags"] == 2
        assert emp_data["discrepancy_percent"] == 15.0
        
        assert len(emp_data["discrepancies"]) == 2
        assert emp_data["discrepancies"][0]["zone_id"] == 1
        assert emp_data["discrepancies"][0]["tag"] == "TAG001"
        assert emp_data["discrepancies"][0]["upc"] == "123456789"
        assert emp_data["discrepancies"][0]["price"] == 10.0
        assert emp_data["discrepancies"][0]["counted_qty"] == 5
        assert emp_data["discrepancies"][0]["new_quantity"] == 10
        assert emp_data["discrepancies"][0]["discrepancy_dollars"] == 50.0

    def test_discrepancy_percent_zero_division(self):
        """Verify division by zero protection when total_price is 0."""
        mock_emp_row = ("E001", "Alice Johnson")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [("E001", "TAG001")],
            [mock_emp_row],
            [(50.0, 5, 3, 16.67, "E001", "333333333", 1)]
        ]
        mock_cursor.fetchone.side_effect = [
            (100, 0.0),
            (50.0,),
            (1,)
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_price"] == 0.0
        assert emp_data["discrepancy_percent"] == 0

    def test_null_values_handling(self):
        """Verify None values from database are converted to 0."""
        mock_emp_row = ("E001", "Alice Johnson")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [("E001", "TAG001")],
            [mock_emp_row],
            []
        ]
        mock_cursor.fetchone.side_effect = [
            (None, None),
            (None,),
            (None,)
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 1
        emp_data = result[0]
        assert emp_data["total_tags"] == 1
        assert emp_data["total_quantity"] == 0
        assert emp_data["total_price"] == 0
        assert emp_data["total_discrepancy_dollars"] == 0
        assert emp_data["total_discrepancy_tags"] == 0