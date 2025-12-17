import pytest
import pyodbc
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from services.load_source_zone_data import load_source_zone_data


@pytest.fixture
def mock_conn():
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = MagicMock()
    return conn


def test_load_source_zone_data_basic(mock_conn):
    zone_rows = [("Z001", "Electronics")]
    zone_totals_row = (100, 200, 5000.0)
    zone_discrepancy_totals_row = (150.0, 3)

    with patch("services.load_source_zone_data.fetch_zone_data", return_value=zone_rows), \
         patch("services.load_source_zone_data.fetch_zone_totals_data", return_value=zone_totals_row), \
         patch("services.load_source_zone_data.fetch_zone_discrepancy_totals_data", return_value=zone_discrepancy_totals_row):

        result = load_source_zone_data(mock_conn)
        assert len(result) == 1
        row = result[0]
        assert row["zone_id"] == "Z001"
        assert row["zone_description"] == "Electronics"
        assert row["total_tags"] == 100
        assert row["total_quantity"] == 200
        assert row["total_price"] == 5000.0
        assert row["discrepancy_dollars"] == 150.0
        assert row["discrepancy_tags"] == 3
        assert row["discrepancy_percent"] == pytest.approx(150.0 / 5000.0 * 100)


def test_load_source_zone_data_empty_data(mock_conn):
    with patch("services.load_source_zone_data.fetch_zone_data", return_value=[]):
        result = load_source_zone_data(mock_conn)
        assert result == []


def test_load_source_zone_data_zero_totals(mock_conn):
    zone_rows = [("Z001", "Electronics")]
    zone_totals_row = (0, 0, 0.0)
    zone_discrepancy_totals_row = (0.0, 0)

    with patch("services.load_source_zone_data.fetch_zone_data", return_value=zone_rows), \
         patch("services.load_source_zone_data.fetch_zone_totals_data", return_value=zone_totals_row), \
         patch("services.load_source_zone_data.fetch_zone_discrepancy_totals_data", return_value=zone_discrepancy_totals_row):

        result = load_source_zone_data(mock_conn)
        row = result[0]
        assert row["total_tags"] == 0
        assert row["total_quantity"] == 0
        assert row["total_price"] == 0
        assert row["discrepancy_percent"] == 0


def test_load_source_zone_data_invalid_connection():
    with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        with pytest.raises(ValueError):
            load_source_zone_data(None)
        with pytest.raises(ValueError):
            load_source_zone_data(object())
        assert mock_warning.called


def test_load_source_zone_data_invalid_row_length(mock_conn):
    with patch("services.load_source_zone_data.fetch_zone_data", return_value=[("only_one_column",)]), \
         patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        with pytest.raises(RuntimeError):
            load_source_zone_data(mock_conn)
        assert mock_warning.called


def test_load_source_zone_data_invalid_totals_row(mock_conn):
    zone_rows = [("Z001", "Electronics")]
    with patch("services.load_source_zone_data.fetch_zone_data", return_value=zone_rows), \
         patch("services.load_source_zone_data.fetch_zone_totals_data", return_value=None), \
         patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        with pytest.raises(RuntimeError):
            load_source_zone_data(mock_conn)
        assert mock_warning.called


def test_load_source_zone_data_invalid_discrepancy_row(mock_conn):
    zone_rows = [("Z001", "Electronics")]
    zone_totals_row = (100, 200, 5000.0)
    with patch("services.load_source_zone_data.fetch_zone_data", return_value=zone_rows), \
         patch("services.load_source_zone_data.fetch_zone_totals_data", return_value=zone_totals_row), \
         patch("services.load_source_zone_data.fetch_zone_discrepancy_totals_data", return_value=None), \
         patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        with pytest.raises(RuntimeError):
            load_source_zone_data(mock_conn)
        assert mock_warning.called


def test_load_source_zone_data_db_exception(mock_conn):
    with patch("services.load_source_zone_data.fetch_zone_data", side_effect=pyodbc.Error("DB error")), \
         patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        with pytest.raises(pyodbc.Error):
            load_source_zone_data(mock_conn)
        assert mock_warning.called
