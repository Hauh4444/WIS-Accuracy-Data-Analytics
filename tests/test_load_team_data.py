"""Tests for team data loading service."""
import pytest
from unittest.mock import Mock, patch
import pyodbc
from PyQt6 import QtWidgets

from services import load_source_team_data


class TestLoadTeamData:
    """Test load_team_data function."""
    
    def test_successful_load(self, mock_database_connection, mock_pyodbc_row):
        """Test successful team data loading."""
        with patch('services.load_team_data.fetch_zone_data') as mock_fetch_zone, \
             patch('services.load_team_data.fetch_zone_totals_data') as mock_fetch_zone_totals, \
             patch('services.load_team_data.fetch_zone_discrepancy_totals_data') as mock_fetch_zone_discrepancy:
            
            # Setup mock data
            mock_fetch_zone.return_value = [
                mock_pyodbc_row((1, "Electronics")),
                mock_pyodbc_row((2, "Clothing"))
            ]
            mock_fetch_zone_totals.return_value = mock_pyodbc_row((25, 250, 2500.0))
            mock_fetch_zone_discrepancy.return_value = mock_pyodbc_row((125.0, 5))
            
            result = load_source_team_data(mock_database_connection)
            
            assert len(result) == 2
            assert result[0]['zone_number'] == 1
            assert result[0]['zone_name'] == "Electronics"
            assert result[0]['total_tags'] == 25
            assert result[0]['total_quantity'] == 250
            assert result[0]['total_price'] == 2500.0
            assert result[0]['total_discrepancy_dollars'] == 125.0
            assert result[0]['total_discrepancy_tags'] == 5
            assert result[0]['discrepancy_percent'] == 5.0
    
    def test_none_connection(self):
        """Test ValueError when connection is None."""
        with pytest.raises(ValueError, match="Database connection cannot be None"):
            load_source_team_data(None)
    
    def test_invalid_connection(self):
        """Test ValueError when connection lacks cursor method."""
        invalid_conn = Mock()
        del invalid_conn.cursor
        
        with pytest.raises(ValueError, match="Invalid database connection object"):
            load_source_team_data(invalid_conn)
    
    def test_zone_data_invalid_structure(self, mock_database_connection, mock_pyodbc_row):
        """Test RuntimeError when zone data has invalid structure."""
        with patch('services.load_team_data.fetch_zone_data') as mock_fetch_zone:
            mock_fetch_zone.return_value = [mock_pyodbc_row((1,))]  # Wrong number of columns
            
            with pytest.raises(RuntimeError, match="Invalid zone query result structure"):
                load_source_team_data(mock_database_connection)
    
    def test_zone_totals_invalid_structure(self, mock_database_connection, mock_pyodbc_row):
        """Test RuntimeError when zone totals has invalid structure."""
        with patch('services.load_team_data.fetch_zone_data') as mock_fetch_zone, \
             patch('services.load_team_data.fetch_zone_totals_data') as mock_fetch_zone_totals:
            
            mock_fetch_zone.return_value = [mock_pyodbc_row((1, "Electronics"))]
            mock_fetch_zone_totals.return_value = mock_pyodbc_row((25, 250))  # Wrong number of columns
            
            with pytest.raises(RuntimeError, match="Invalid zone_totals query result"):
                load_source_team_data(mock_database_connection)
    
    def test_zone_discrepancy_totals_invalid_structure(self, mock_database_connection, mock_pyodbc_row):
        """Test RuntimeError when zone discrepancy totals has invalid structure."""
        with patch('services.load_team_data.fetch_zone_data') as mock_fetch_zone, \
             patch('services.load_team_data.fetch_zone_totals_data') as mock_fetch_zone_totals, \
             patch('services.load_team_data.fetch_zone_discrepancy_totals_data') as mock_fetch_zone_discrepancy:
            
            mock_fetch_zone.return_value = [mock_pyodbc_row((1, "Electronics"))]
            mock_fetch_zone_totals.return_value = mock_pyodbc_row((25, 250, 2500.0))
            mock_fetch_zone_discrepancy.return_value = mock_pyodbc_row((125.0,))  # Wrong number of columns
            
            with pytest.raises(RuntimeError, match="Invalid zone_discrepancy_totals query result"):
                load_source_team_data(mock_database_connection)
    
    def test_discrepancy_percent_calculation(self, mock_database_connection, mock_pyodbc_row):
        """Test discrepancy percent calculation."""
        with patch('services.load_team_data.fetch_zone_data') as mock_fetch_zone, \
             patch('services.load_team_data.fetch_zone_totals_data') as mock_fetch_zone_totals, \
             patch('services.load_team_data.fetch_zone_discrepancy_totals_data') as mock_fetch_zone_discrepancy:
            
            mock_fetch_zone.return_value = [mock_pyodbc_row((1, "Electronics"))]
            mock_fetch_zone_totals.return_value = mock_pyodbc_row((25, 250, 1000.0))  # Total price 1000
            mock_fetch_zone_discrepancy.return_value = mock_pyodbc_row((50.0, 2))  # Discrepancy 50
            
            result = load_source_team_data(mock_database_connection)
            
            assert result[0]['discrepancy_percent'] == 5.0  # 50/1000 * 100
    
    def test_zero_total_price_discrepancy_percent(self, mock_database_connection, mock_pyodbc_row):
        """Test discrepancy percent when total price is zero."""
        with patch('services.load_team_data.fetch_zone_data') as mock_fetch_zone, \
             patch('services.load_team_data.fetch_zone_totals_data') as mock_fetch_zone_totals, \
             patch('services.load_team_data.fetch_zone_discrepancy_totals_data') as mock_fetch_zone_discrepancy:
            
            mock_fetch_zone.return_value = [mock_pyodbc_row((1, "Electronics"))]
            mock_fetch_zone_totals.return_value = mock_pyodbc_row((25, 250, 0.0))  # Zero total price
            mock_fetch_zone_discrepancy.return_value = mock_pyodbc_row((50.0, 2))
            
            result = load_source_team_data(mock_database_connection)
            
            assert result[0]['discrepancy_percent'] == 0.0
    
    def test_none_values_handling(self, mock_database_connection, mock_pyodbc_row):
        """Test handling of None values in data."""
        with patch('services.load_team_data.fetch_zone_data') as mock_fetch_zone, \
             patch('services.load_team_data.fetch_zone_totals_data') as mock_fetch_zone_totals, \
             patch('services.load_team_data.fetch_zone_discrepancy_totals_data') as mock_fetch_zone_discrepancy:
            
            mock_fetch_zone.return_value = [mock_pyodbc_row((None, None))]
            mock_fetch_zone_totals.return_value = mock_pyodbc_row((None, None, None))
            mock_fetch_zone_discrepancy.return_value = mock_pyodbc_row((None, None))
            
            result = load_source_team_data(mock_database_connection)
            
            assert result[0]['zone_number'] == ""
            assert result[0]['zone_name'] == ""
            assert result[0]['total_tags'] == 0
            assert result[0]['total_quantity'] == 0
            assert result[0]['total_price'] == 0
            assert result[0]['total_discrepancy_dollars'] == 0
            assert result[0]['total_discrepancy_tags'] == 0
            assert result[0]['discrepancy_percent'] == 0.0
    
    def test_pyodbc_error_handling(self, mock_database_connection):
        """Test pyodbc error handling."""
        with patch('services.load_team_data.fetch_zone_data', side_effect=pyodbc.Error("Database error")):
            with patch('services.load_team_data.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(pyodbc.Error):
                    load_source_team_data(mock_database_connection)
                mock_msgbox.assert_called_once()
    
    def test_value_error_handling(self, mock_database_connection):
        """Test ValueError handling."""
        with patch('services.load_team_data.fetch_zone_data', side_effect=ValueError("Value error")):
            with patch('services.load_team_data.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(ValueError):
                    load_source_team_data(mock_database_connection)
                mock_msgbox.assert_called_once()
    
    def test_runtime_error_handling(self, mock_database_connection):
        """Test RuntimeError handling."""
        with patch('services.load_team_data.fetch_zone_data', side_effect=RuntimeError("Runtime error")):
            with patch('services.load_team_data.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(RuntimeError):
                    load_source_team_data(mock_database_connection)
                mock_msgbox.assert_called_once()
    
    def test_generic_exception_handling(self, mock_database_connection):
        """Test generic Exception handling."""
        with patch('services.load_team_data.fetch_zone_data', side_effect=Exception("Generic error")):
            with patch('services.load_team_data.QtWidgets.QMessageBox.critical') as mock_msgbox:
                with pytest.raises(Exception):
                    load_source_team_data(mock_database_connection)
                mock_msgbox.assert_called_once()
    
    def test_empty_zone_data(self, mock_database_connection):
        """Test handling of empty zone data."""
        with patch('services.load_team_data.fetch_zone_data') as mock_fetch_zone:
            mock_fetch_zone.return_value = []
            
            result = load_source_team_data(mock_database_connection)
            
            assert result == []
    
    def test_multiple_zones(self, mock_database_connection, mock_pyodbc_row):
        """Test handling of multiple zones."""
        with patch('services.load_team_data.fetch_zone_data') as mock_fetch_zone, \
             patch('services.load_team_data.fetch_zone_totals_data') as mock_fetch_zone_totals, \
             patch('services.load_team_data.fetch_zone_discrepancy_totals_data') as mock_fetch_zone_discrepancy:
            
            mock_fetch_zone.return_value = [
                mock_pyodbc_row((1, "Electronics")),
                mock_pyodbc_row((2, "Clothing")),
                mock_pyodbc_row((3, "Books"))
            ]
            
            def mock_zone_totals(conn, zone_id):
                totals_map = {
                    "1": mock_pyodbc_row((25, 250, 2500.0)),
                    "2": mock_pyodbc_row((30, 300, 3000.0)),
                    "3": mock_pyodbc_row((20, 200, 2000.0))
                }
                return totals_map.get(zone_id)
            
            def mock_zone_discrepancy(conn, zone_id):
                discrepancy_map = {
                    "1": mock_pyodbc_row((125.0, 5)),
                    "2": mock_pyodbc_row((150.0, 6)),
                    "3": mock_pyodbc_row((100.0, 4))
                }
                return discrepancy_map.get(zone_id)
            
            mock_fetch_zone_totals.side_effect = mock_zone_totals
            mock_fetch_zone_discrepancy.side_effect = mock_zone_discrepancy
            
            result = load_source_team_data(mock_database_connection)
            
            assert len(result) == 3
            assert result[0]['zone_number'] == 1
            assert result[1]['zone_number'] == 2
            assert result[2]['zone_number'] == 3
