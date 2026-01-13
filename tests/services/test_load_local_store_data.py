import pytest
import pyodbc
from unittest.mock import patch, MagicMock

from services.load_local_store_data import load_local_store_data


@pytest.fixture
def mock_conn():
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = MagicMock()
    return conn


def test_load_local_store_data_store_specific(mock_conn):
    sample_row = ("01/01/2025 10:00:00 AM", "001", "123 Main St")
    with patch("services.load_local_store_data.fetch_old_inventory_data", return_value=sample_row) as mock_fetch:
        result = load_local_store_data(mock_conn, store="001")
        assert result["inventory_datetime"] == "01/01/2025 10:00:00 AM"
        assert result["store"] == "001"
        assert result["store_address"] == "123 Main St"
        assert "print_date" in result
        assert "print_time" in result
        mock_fetch.assert_called_once_with(mock_conn, "001")


def test_load_local_store_data_aggregate_specific(mock_conn):
    sample_rows = [
        ("01/01/2025 10:00:00 AM",),
        ("12/15/2025 03:00:00 PM",)
    ]
    with patch("services.load_local_store_data.fetch_aggregate_inventory_data", return_value=sample_rows) as mock_fetch:
        result = load_local_store_data(mock_conn, store=None)
        assert "aggregate_range" in result
        assert result["aggregate_range"] == "Dec 2025 - Jan 2025"
        mock_fetch.assert_called_once_with(mock_conn)


def test_load_local_store_data_invalid_conn(mock_conn):
    with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
        with pytest.raises(ValueError):
            load_local_store_data(None, store="001")
        assert mock_warning.called

        with pytest.raises(ValueError):
            load_local_store_data(object(), store="001")
        assert mock_warning.called


def test_load_local_store_data_invalid_inventory_structure(mock_conn):
    invalid_row = ("01/01/2025", "001")
    with patch("services.load_local_store_data.fetch_old_inventory_data", return_value=invalid_row):
        with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
            with pytest.raises(RuntimeError):
                load_local_store_data(mock_conn, store="001")
            assert mock_warning.called
