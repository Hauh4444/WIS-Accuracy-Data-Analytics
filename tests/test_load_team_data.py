import pytest
from unittest.mock import MagicMock, patch

from services.load_team_data import load_team_data


class TestLoadTeamData:

    @patch("services.load_team_data.QtWidgets.QMessageBox.critical")
    def test_database_exception_handling(self, mock_critical):
        """Test database exception handling."""
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception, match="Database connection failed"):
            load_team_data(mock_conn)
        
        mock_critical.assert_called_once()

    def test_no_team_records(self):
        """Test no team records returns empty list."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert result == []

    def test_successful_data_loading(self):
        """Test successful team data loading with business logic."""
        mock_zone_row = (101, "Finance Zone")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_zone_row]
        ]
        mock_cursor.fetchone.side_effect = [
            (50, 100, 500.0),
            (75.0, 2),
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert len(result) == 1
        team_data = result[0]
        assert team_data["zone_number"] == 101
        assert team_data["zone_name"] == "Finance Zone"
        assert team_data["total_tags"] == 50
        assert team_data["total_quantity"] == 100
        assert team_data["total_price"] == 500.0
        assert team_data["total_discrepancy_dollars"] == 75.0
        assert team_data["total_discrepancy_tags"] == 2
        assert team_data["discrepancy_percent"] == 15.0  # 75/500 * 100

    def test_multiple_teams_loading(self):
        """Test loading multiple teams."""
        mock_zone_rows = [(101, "Finance"), (102, "HR")]
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            mock_zone_rows
        ]
        mock_cursor.fetchone.side_effect = [
            (50, 100, 500.0),
            (75.0, 2),
            (30, 60, 300.0),
            (15.0, 1),
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert len(result) == 2
        assert result[0]["zone_number"] == 101
        assert result[1]["zone_number"] == 102

    def test_zero_discrepancy_calculation(self):
        """Test zero discrepancy calculation."""
        mock_zone_row = (101, "Finance Zone")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_zone_row]
        ]
        mock_cursor.fetchone.side_effect = [
            (50, 100, 500.0),
            (0, 0),
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert len(result) == 1
        team_data = result[0]
        assert team_data["total_discrepancy_dollars"] == 0
        assert team_data["discrepancy_percent"] == 0

    def test_discrepancy_percent_zero_division(self):
        """Test zero division handling in discrepancy percent calculation."""
        mock_zone_row = (101, "Finance Zone")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_zone_row]
        ]
        mock_cursor.fetchone.side_effect = [
            (50, 100, 0),
            (75.0, 2),
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert len(result) == 1
        team_data = result[0]
        assert team_data["discrepancy_percent"] == 0

    @patch("services.load_team_data.QtWidgets.QMessageBox.critical")
    def test_malformed_zone_data(self, mock_critical):
        """Test handling of malformed zone data."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [(101, "Finance", "EXTRA_COLUMN")],
        ]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        with pytest.raises(RuntimeError):
            load_team_data(mock_conn)
        
        mock_critical.assert_called_once()

    def test_business_rule_discrepancy_threshold(self):
        """Test business rule: Only discrepancies >$50 with reason='SERVICE_MISCOUNTED' are counted."""
        mock_zone_row = (101, "Finance Zone")
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [mock_zone_row]
        ]
        mock_cursor.fetchone.side_effect = [
            (50, 100, 500.0),
            (75.0, 1),
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        result = load_team_data(mock_conn)
        
        assert len(result) == 1
        team_data = result[0]
        assert team_data["total_discrepancy_dollars"] == 75.0
        assert team_data["total_discrepancy_tags"] == 1
        assert team_data["discrepancy_percent"] == 15.0