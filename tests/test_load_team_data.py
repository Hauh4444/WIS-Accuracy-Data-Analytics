"""Tests for team data loading functionality."""

import pytest
from unittest.mock import MagicMock, patch

from services.load_team_data import load_team_data


class TestLoadTeamData:
    """Test cases for team data loading."""

    def make_mock_row(self, **kwargs):
        """Helper to create mock database row."""
        row = MagicMock()
        for k, v in kwargs.items():
            setattr(row, k, v)
        return row

    @patch("services.load_team_data.QtWidgets.QMessageBox.critical")
    def test_database_exception_handling(self, mock_critical):
        """Test error handling when database connection fails."""
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("Database connection failed")
        
        result = load_team_data(mock_conn)
        
        assert result == []
        mock_critical.assert_called_once()
        assert "Database connection failed" in mock_critical.call_args[0][2]

    @patch("services.load_team_data.QtWidgets.QMessageBox.warning")
    def test_no_team_records(self, mock_warning):
        """Test handling when no team records are found."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert result == []
        mock_warning.assert_called_once()
        assert "No team records" in mock_warning.call_args[0][2]

    def test_successful_data_loading(self):
        """Test successful loading of team data."""
        mock_team_row = self.make_mock_row(
            department_number=101,
            department_name="Human Resources",
            total_discrepancy_dollars=200.0,
            total_discrepancy_tags=3,
            discrepancy_percent=8.0,
            total_tags=30,
            total_quantity=150
        )
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [mock_team_row]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["department_name"] == "Human Resources"
        assert result[0]["department_number"] == 101
        assert result[0]["total_discrepancy_tags"] == 3
        assert result[0]["total_discrepancy_dollars"] == 200.0
        assert result[0]["discrepancy_percent"] == 8.0
        mock_conn.close.assert_called_once()

    def test_multiple_teams_loading(self):
        """Test loading multiple team records."""
        mock_row1 = self.make_mock_row(
            department_number=101,
            department_name="Finance",
            total_discrepancy_dollars=100.0,
            total_discrepancy_tags=2,
            discrepancy_percent=5.0,
            total_tags=20,
            total_quantity=100
        )
        mock_row2 = self.make_mock_row(
            department_number=102,
            department_name="Engineering",
            total_discrepancy_dollars=0.0,
            total_discrepancy_tags=0,
            discrepancy_percent=0.0,
            total_tags=15,
            total_quantity=75
        )
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [mock_row1, mock_row2]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert len(result) == 2
        assert result[0]["department_name"] == "Finance"
        assert result[1]["department_name"] == "Engineering"
        assert result[1]["total_discrepancy_tags"] == 0

    @patch("services.load_team_data.QtWidgets.QMessageBox.critical")
    def test_cursor_execute_called(self, mock_critical):
        """Test that cursor execute is called properly."""
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [self.make_mock_row(
            department_number=201,
            department_name="Test Department",
            total_discrepancy_dollars=50.0,
            total_discrepancy_tags=1,
            discrepancy_percent=10.0,
            total_tags=5,
            total_quantity=25
        )]
        
        load_team_data(mock_conn)
        
        assert mock_cursor.execute.called
        assert mock_conn.close.called
        mock_critical.assert_not_called()

    def test_zero_discrepancy_calculation(self):
        """Test calculation when discrepancy values are zero."""
        mock_row = self.make_mock_row(
            department_number=103,
            department_name="Perfect Team",
            total_discrepancy_dollars=0.0,
            total_discrepancy_tags=0,
            discrepancy_percent=0.0,
            total_tags=10,
            total_quantity=50
        )
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [mock_row]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert result[0]["total_discrepancy_tags"] == 0
        assert result[0]["total_discrepancy_dollars"] == 0.0
        assert result[0]["discrepancy_percent"] == 0.0

    def test_high_discrepancy_calculation(self):
        """Test calculation with high discrepancy values."""
        mock_row = self.make_mock_row(
            department_number=104,
            department_name="Problematic Team",
            total_discrepancy_dollars=750.0,
            total_discrepancy_tags=15,
            discrepancy_percent=30.0,
            total_tags=50,
            total_quantity=250
        )
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [mock_row]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert result[0]["total_discrepancy_tags"] == 15
        assert result[0]["total_discrepancy_dollars"] == 750.0
        assert result[0]["discrepancy_percent"] == 30.0

    def test_department_number_types(self):
        """Test handling of different department number types."""
        mock_row = self.make_mock_row(
            department_number="ABC123",
            department_name="Special Department",
            total_discrepancy_dollars=50.0,
            total_discrepancy_tags=1,
            discrepancy_percent=5.0,
            total_tags=10,
            total_quantity=25
        )
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [mock_row]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert result[0]["department_number"] == "ABC123"
        assert result[0]["department_name"] == "Special Department"