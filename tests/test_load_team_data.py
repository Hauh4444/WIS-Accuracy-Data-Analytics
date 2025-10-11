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

    def test_no_team_records(self):
        """Test handling when no team records are found."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert result == []

    def test_successful_data_loading(self):
        """Test successful loading of team data."""
        mock_zone_row = (101, "Finance Department")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_zone_row],  # zones
            [("TAG001",), ("TAG002",)]  # 2 discrepancy tags
        ]
        mock_cursor.fetchone.side_effect = [
            (50, 100, 500.0),  # totals: tags, quantity, price
            (75.0,),           # discrepancy dollars
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["department_name"] == "Finance Department"
        assert result[0]["department_number"] == 101
        assert result[0]["total_tags"] == 50
        assert result[0]["total_quantity"] == 100
        assert result[0]["total_price"] == 500.0
        assert result[0]["total_discrepancy_dollars"] == 75.0
        assert result[0]["total_discrepancy_tags"] == 2
        assert result[0]["discrepancy_percent"] == 15.0  # 75/500 * 100

    def test_multiple_teams_loading(self):
        """Test loading multiple team records."""
        mock_zone_row1 = (101, "Finance Department")
        mock_zone_row2 = (102, "Human Resources")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_zone_row1, mock_zone_row2],  # zones
            [("TAG001",)],                      # discrepancy tags for zone 101 (1 tag)
            [("TAG002",)]                       # discrepancy tags for zone 102 (1 tag)
        ]
        mock_cursor.fetchone.side_effect = [
            (50, 100, 500.0),  # totals for zone 101
            (25.0,),           # discrepancy dollars for zone 101
            (30, 75, 300.0),   # totals for zone 102
            (15.0,),           # discrepancy dollars for zone 102
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert len(result) == 2
        assert result[0]["department_name"] == "Finance Department"
        assert result[0]["department_number"] == 101
        assert result[1]["department_name"] == "Human Resources"
        assert result[1]["department_number"] == 102
        
        # Verify all expected fields are present for both teams
        for team_data in result:
            assert "department_number" in team_data
            assert "department_name" in team_data
            assert "total_tags" in team_data
            assert "total_quantity" in team_data
            assert "total_price" in team_data
            assert "total_discrepancy_dollars" in team_data
            assert "total_discrepancy_tags" in team_data
            assert "discrepancy_percent" in team_data

    @patch("services.load_team_data.QtWidgets.QMessageBox.critical")
    def test_cursor_execute_called(self, mock_critical):
        """Test that cursor execute is called properly."""
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(201, "Test Department")]
        mock_cursor.fetchone.return_value = None
        
        load_team_data(mock_conn)
        
        assert mock_cursor.execute.called

    def test_zero_discrepancy_calculation(self):
        """Test calculation when discrepancy values are zero."""
        mock_zone_row = (101, "Finance Department")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_zone_row],  # zones
            []                # no discrepancy tags
        ]
        mock_cursor.fetchone.side_effect = [
            (50, 100, 500.0),  # totals: tags, quantity, price
            (0,),              # discrepancy dollars = 0
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert len(result) == 1
        team_data = result[0]
        assert team_data["total_discrepancy_dollars"] == 0
        assert team_data["total_discrepancy_tags"] == 0
        assert team_data["discrepancy_percent"] == 0

    def test_high_discrepancy_calculation(self):
        """Test calculation with high discrepancy values."""
        mock_zone_row = (101, "Finance Department")
        
        # Create 8 mock discrepancy tag rows
        discrepancy_tags = [(f"TAG{i:03d}",) for i in range(1, 9)]
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_zone_row],     # zones
            discrepancy_tags     # 8 discrepancy tags
        ]
        mock_cursor.fetchone.side_effect = [
            (50, 100, 500.0),  # totals: tags, quantity, price
            (300.0,),          # high discrepancy dollars
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert len(result) == 1
        team_data = result[0]
        assert team_data["total_discrepancy_dollars"] == 300.0
        assert team_data["total_discrepancy_tags"] == 8
        assert team_data["discrepancy_percent"] == 60.0  # 300/500 * 100

    def test_department_number_types(self):
        """Test handling of different department number types."""
        # Test with integer department numbers
        mock_zone_row1 = (101, "Finance Department")
        mock_zone_row2 = (102, "Human Resources")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_zone_row1, mock_zone_row2],  # zones
            [("TAG001",)],                      # discrepancy tags for zone 101
            [("TAG002",)]                       # discrepancy tags for zone 102
        ]
        mock_cursor.fetchone.side_effect = [
            (50, 100, 500.0),  # totals for zone 101
            (25.0,),           # discrepancy dollars for zone 101
            (30, 75, 300.0),   # totals for zone 102
            (15.0,),           # discrepancy dollars for zone 102
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert len(result) == 2
        # Verify department numbers are handled correctly as integers
        assert result[0]["department_number"] == 101
        assert result[1]["department_number"] == 102
        assert isinstance(result[0]["department_number"], int)
        assert isinstance(result[1]["department_number"], int)

    def test_discrepancy_percent_zero_division(self):
        """Test that discrepancy percent is 0 when total_price is 0."""
        mock_zone_row = (101, "Finance Department")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_zone_row],  # zones
            [("TAG001",)]     # discrepancy tags
        ]
        mock_cursor.fetchone.side_effect = [
            (50, 100, 0.0),   # totals with 0 price
            (25.0,),          # discrepancy dollars
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert len(result) == 1
        team_data = result[0]
        assert team_data["total_price"] == 0.0
        assert team_data["discrepancy_percent"] == 0  # Should be 0, not cause division by zero

    def test_null_values_handling(self):
        """Test handling of None values from database."""
        mock_zone_row = (101, "Finance Department")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_zone_row],  # zones
            []                # no discrepancy tags
        ]
        mock_cursor.fetchone.side_effect = [
            (None, None, None),  # totals are None
            (None,),             # discrepancy dollars is None
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert len(result) == 1
        team_data = result[0]
        assert team_data["total_tags"] == 0      # Should handle None as 0
        assert team_data["total_quantity"] == 0  # Should handle None as 0
        assert team_data["total_price"] == 0     # Should handle None as 0
        assert team_data["total_discrepancy_dollars"] == 0  # Should handle None as 0
        assert team_data["total_discrepancy_tags"] == 0     # Should handle None as 0

    def test_cursor_execute_query_structure(self):
        """Test that cursor execute is called with correct query structure."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = None
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        load_team_data(mock_conn)
        
        assert mock_cursor.execute.called
        # Verify the queries contain expected table and column references
        calls = mock_cursor.execute.call_args_list
        zone_query = calls[0][0][0]
        assert "tblZone" in zone_query
        assert "ZoneID" in zone_query
        assert "ZoneDesc" in zone_query
        assert "SELECT" in zone_query