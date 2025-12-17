import pytest
import pyodbc
from unittest.mock import patch, MagicMock
from datetime import datetime
from PyQt6 import QtWidgets

from services.load_source_store_data import load_source_store_data


@pytest.fixture
def mock_conn():
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = MagicMock()
    return conn


def test_load_source_store_data_basic(mock_conn):
    wise_row = ("2025-11-23 10:00:00", "123", "123 Main St")
    with patch("services.load_source_store_data.fetch_wise_data", return_value=wise_row):
        result = load_source_store_data(mock_conn)
        assert result["inventory_datetime"] == "2025-11-23 10:00:00"
        assert result["store"] == "123"
        assert result["store_address"] == "123 Main St"
        now = datetime.now()
        assert result["print_date"] == f"{now.month}/{now.day}/{now.year}"
        assert "print_time" in result


def test_load_source_store_data_none_row(mock_conn):
    with patch("services.load_source_store_data.fetch_wise_data", return_value=None), \
         patch("services.load_source_store_data.QtWidgets.QMessageBox.warning") as mock_warning:
        with pytest.raises(RuntimeError):
            load_source_store_data(mock_conn)
        assert mock_warning.called


def test_load_source_store_data_invalid_row_length(mock_conn):
    wise_row = ("only_one_column",)
    with patch("services.load_source_store_data.fetch_wise_data", return_value=wise_row), \
         patch("services.load_source_store_data.QtWidgets.QMessageBox.warning") as mock_warning:
        with pytest.raises(RuntimeError):
            load_source_store_data(mock_conn)
        assert mock_warning.called


def test_load_source_store_data_invalid_connection():
    with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        with pytest.raises(ValueError):
            load_source_store_data(None)
        with pytest.raises(ValueError):
            load_source_store_data(object())
        assert mock_warning.called
