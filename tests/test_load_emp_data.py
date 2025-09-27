"""Tests for employee data loading functionality."""

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

    @patch("services.load_emp_data.QtWidgets.QMessageBox.warning")
    def test_no_employee_records(self, mock_warning):
        """Test handling when no employee records are found."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert result == []
        mock_warning.assert_called_once()
        assert "No employee records" in mock_warning.call_args[0][2]

    def test_successful_data_loading(self):
        """Test successful loading of employee data."""
        mock_emp_row = self.make_mock_row(
            employee_id=1,
            employee_name="Alice Johnson",
            total_discrepancy_tags=2,
            total_discrepancy_dollars=150.0,
            discrepancy_percent=7.5,
            total_tags=25,
            total_quantity=100
        )
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [mock_emp_row]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["employee_name"] == "Alice Johnson"
        assert result[0]["total_discrepancy_tags"] == 2
        assert result[0]["total_discrepancy_dollars"] == 150.0
        assert result[0]["discrepancy_percent"] == 7.5
        mock_conn.close.assert_called_once()

    def test_multiple_employees_loading(self):
        """Test loading multiple employee records."""
        mock_row1 = self.make_mock_row(
            employee_id=1,
            employee_name="Alice Johnson",
            total_discrepancy_tags=2,
            total_discrepancy_dollars=100.0,
            discrepancy_percent=5.0,
            total_tags=20,
            total_quantity=50
        )
        mock_row2 = self.make_mock_row(
            employee_id=2,
            employee_name="Bob Smith",
            total_discrepancy_tags=0,
            total_discrepancy_dollars=0.0,
            discrepancy_percent=0.0,
            total_tags=15,
            total_quantity=75
        )
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [mock_row1, mock_row2]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert len(result) == 2
        assert result[0]["employee_name"] == "Alice Johnson"
        assert result[1]["employee_name"] == "Bob Smith"
        assert result[1]["total_discrepancy_tags"] == 0

    @patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
    def test_cursor_execute_called(self, mock_critical):
        """Test that cursor execute is called properly."""
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [self.make_mock_row(
            employee_id=1,
            employee_name="Test Employee",
            total_discrepancy_tags=1,
            total_discrepancy_dollars=50.0,
            discrepancy_percent=10.0,
            total_tags=5,
            total_quantity=10
        )]
        
        load_emp_data(mock_conn)
        
        assert mock_cursor.execute.called
        assert mock_conn.close.called
        mock_critical.assert_not_called()

    def test_zero_discrepancy_calculation(self):
        """Test calculation when discrepancy values are zero."""
        mock_row = self.make_mock_row(
            employee_id=1,
            employee_name="Perfect Employee",
            total_discrepancy_tags=0,
            total_discrepancy_dollars=0.0,
            discrepancy_percent=0.0,
            total_tags=10,
            total_quantity=25
        )
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [mock_row]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert result[0]["total_discrepancy_tags"] == 0
        assert result[0]["total_discrepancy_dollars"] == 0.0
        assert result[0]["discrepancy_percent"] == 0.0

    def test_high_discrepancy_calculation(self):
        """Test calculation with high discrepancy values."""
        mock_row = self.make_mock_row(
            employee_id=1,
            employee_name="Problematic Employee",
            total_discrepancy_tags=10,
            total_discrepancy_dollars=500.0,
            discrepancy_percent=25.0,
            total_tags=40,
            total_quantity=200
        )
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [mock_row]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_emp_data(mock_conn)
        
        assert result[0]["total_discrepancy_tags"] == 10
        assert result[0]["total_discrepancy_dollars"] == 500.0
        assert result[0]["discrepancy_percent"] == 25.0