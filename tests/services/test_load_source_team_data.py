import pytest
from unittest.mock import patch, MagicMock
import pyodbc

import services.load_source_zone_data as loader


@pytest.fixture
def mock_conn():
    """Return a dummy pyodbc connection-like object."""
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = MagicMock()
    return conn


def test_load_source_zone_data_basic(mock_conn):
    zone_rows = [("Z001", "Electronics")]
    zone_totals_row = (100, 200, 5000.0)
    zone_discrepancy_totals_row = (150.0, 3)

    with patch("repositories.source_zone_repository.fetch_zone_data", return_value=zone_rows), \
         patch("repositories.source_zone_repository.fetch_zone_totals_data", return_value=zone_totals_row), \
         patch("repositories.source_zone_repository.fetch_zone_discrepancy_totals_data", return_value=zone_discrepancy_totals_row):

        result = loader.load_source_zone_data(mock_conn)
        assert len(result) == 1
        row = result[0]
        assert row["zone_id"] == "Z001"
        assert row["zone_description"] == "Electronics"
        assert row["total_tags"] == 100
        assert row["total_quantity"] == 200
        assert row["total_price"] == 5000.0
        assert row["discrepancy_dollars"] == 150.0
        assert row["discrepancy_tags"] == 3
        assert row["discrepancy_percent"] == (150.0 / 5000.0 * 100)


def test_load_source_zone_data_invalid_zone_row(mock_conn):
    with patch("repositories.source_zone_repository.fetch_zone_data", return_value=[("only_one_column",)]):
        with pytest.raises(RuntimeError):
            loader.load_source_zone_data(mock_conn)


def test_load_source_zone_data_invalid_totals_row(mock_conn):
    zone_rows = [("Z001", "Electronics")]
    with patch("repositories.source_zone_repository.fetch_zone_data", return_value=zone_rows), \
         patch("repositories.source_zone_repository.fetch_zone_totals_data", return_value=None):
        with pytest.raises(RuntimeError):
            loader.load_source_zone_data(mock_conn)


def test_load_source_zone_data_invalid_discrepancy_row(mock_conn):
    zone_rows = [("Z001", "Electronics")]
    zone_totals_row = (100, 200, 5000.0)
    with patch("repositories.source_zone_repository.fetch_zone_data", return_value=zone_rows), \
         patch("repositories.source_zone_repository.fetch_zone_totals_data", return_value=zone_totals_row), \
         patch("repositories.source_zone_repository.fetch_zone_discrepancy_totals_data", return_value=None):
        with pytest.raises(RuntimeError):
            loader.load_source_zone_data(mock_conn)


def test_load_source_zone_data_invalid_connection():
    import PyQt6.QtWidgets as qt
    with patch.object(qt.QMessageBox, "warning") as mock_warning:
        with pytest.raises(ValueError):
            loader.load_source_zone_data(None)
        with pytest.raises(ValueError):
            loader.load_source_zone_data(object())
        assert mock_warning.called
