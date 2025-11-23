import pytest
from unittest.mock import patch, MagicMock
import pyodbc
from datetime import datetime

import services.load_source_store_data as loader


@pytest.fixture
def mock_conn():
    """Return a dummy pyodbc connection-like object."""
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = MagicMock()
    return conn


def test_load_source_store_data_basic(mock_conn):
    wise_row = ("2025-11-23 10:00:00", "123", "123 Main St")
    with patch("repositories.source_store_repository.fetch_wise_data", return_value=wise_row):
        result = loader.load_source_store_data(mock_conn)
        assert result["inventory_datetime"] == "2025-11-23 10:00:00"
        assert result["store"] == "123"
        assert result["store_address"] == "123 Main St"
        # verify print date and time fields exist
        now = datetime.now()
        assert result["print_date"] == f"{now.month}/{now.day}/{now.year}"
        assert "print_time" in result


def test_load_source_store_data_none_row(mock_conn):
    with patch("repositories.source_store_repository.fetch_wise_data", return_value=None):
        with pytest.raises(RuntimeError):
            loader.load_source_store_data(mock_conn)


def test_load_source_store_data_invalid_row_length(mock_conn):
    wise_row = ("only_one_column",)
    with patch("repositories.source_store_repository.fetch_wise_data", return_value=wise_row):
        with pytest.raises(RuntimeError):
            loader.load_source_store_data(mock_conn)


def test_load_source_store_data_invalid_connection():
    import PyQt6.QtWidgets as qt
    with patch.object(qt.QMessageBox, "warning") as mock_warning:
        with pytest.raises(ValueError):
            loader.load_source_store_data(None)
        with pytest.raises(ValueError):
            loader.load_source_store_data(object())
        assert mock_warning.called
