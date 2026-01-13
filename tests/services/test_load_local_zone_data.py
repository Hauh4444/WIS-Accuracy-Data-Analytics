import pytest
import pyodbc
from unittest.mock import patch, MagicMock

from services.load_local_zone_data import load_local_zone_data


@pytest.fixture
def mock_conn():
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = MagicMock()
    return conn


def test_load_local_zone_data_store_specific(mock_conn):
    sample_row = ("001", "Electronics", 10, 50, 500.0, 20.0, 2)
    with patch("services.load_local_zone_data.fetch_old_zone_data", return_value=[sample_row]) as mock_fetch:
        result = load_local_zone_data(mock_conn, store="001")
        assert len(result) == 1
        row = result[0]
        assert row["zone_id"] == "001"
        assert row["zone_description"] == "Electronics"
        assert row["total_tags"] == 10
        assert row["total_quantity"] == 50
        assert row["total_price"] == 500.0
        assert row["discrepancy_dollars"] == 20.0
        assert row["discrepancy_tags"] == 2
        assert row["discrepancy_percent"] == 4.0
        mock_fetch.assert_called_once_with(mock_conn, "001")


def test_load_local_zone_data_aggregate_specific(mock_conn):
    sample_row = ("001", "Electronics", 10, 50, 500.0, 20.0, 2, 2)
    with patch("services.load_local_zone_data.fetch_aggregate_zone_data", return_value=[sample_row]) as mock_fetch:
        result = load_local_zone_data(mock_conn, store=None)
        assert len(result) == 1
        row = result[0]
        assert row["total_tags"] == 5
        assert row["total_quantity"] == 25
        assert row["total_price"] == 250.0
        assert row["discrepancy_dollars"] == 10.0
        assert row["discrepancy_tags"] == 1
        assert row["discrepancy_percent"] == 4.0
        mock_fetch.assert_called_once_with(mock_conn)


def test_load_local_zone_data_invalid_conn(mock_conn):
    with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
        with pytest.raises(ValueError):
            load_local_zone_data(None, store="001")
        with pytest.raises(ValueError):
            load_local_zone_data(object(), store="001")
        assert mock_warning.called


def test_load_local_zone_data_handles_empty_rows(mock_conn):
    with patch("services.load_local_zone_data.fetch_old_zone_data", return_value=[(None, None, None, None, None, None, None)]):
        result = load_local_zone_data(mock_conn, store="001")
        row = result[0]
        assert row["zone_id"] == ""
        assert row["zone_description"] == ""
        assert row["total_tags"] == 0
        assert row["total_quantity"] == 0
        assert row["total_price"] == 0.0
        assert row["discrepancy_dollars"] == 0.0
        assert row["discrepancy_tags"] == 0
        assert row["discrepancy_percent"] == 0
