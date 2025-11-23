import pytest
from unittest.mock import patch, MagicMock
import pyodbc

import services.load_local_emp_data as loader


@pytest.fixture
def mock_conn():
    """Return a dummy pyodbc connection-like object."""
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = MagicMock()
    return conn


def test_load_local_emp_data_store_calls_fetch_emp_data(mock_conn):
    sample_rows = [
        (123, "Alice", 10, 50, 500.0, 25.0, 1, 5),  # all values present
        (124, "Bob", None, None, None, None, None, None),  # missing optional fields
    ]
    with patch("repositories.local_emp_repository.fetch_emp_data", return_value=sample_rows) as mock_fetch:
        result = loader.load_local_emp_data(mock_conn, store="001")
        assert len(result) == 2

        # First row calculations
        row1 = result[0]
        assert row1["emp_number"] == 123
        assert row1["emp_name"] == "Alice"
        assert row1["total_tags"] == 10
        assert row1["uph"] == 50 / 5
        assert row1["discrepancy_percent"] == 25.0 / 500.0 * 100

        # Second row missing values defaults
        row2 = result[1]
        assert row2["total_tags"] == 0
        assert row2["uph"] == 0
        assert row2["discrepancy_percent"] == 0

        mock_fetch.assert_called_once_with(conn=mock_conn, store="001")


def test_load_local_emp_data_season_calls_fetch_season_emp_data(mock_conn):
    sample_rows = [
        (201, "Charlie", 20, 100, 1000.0, 50.0, 2, 2, 10),  # stores=2
    ]
    with patch("repositories.local_emp_repository.fetch_season_emp_data", return_value=sample_rows) as mock_fetch:
        result = loader.load_local_emp_data(mock_conn, store=None)
        assert len(result) == 1
        row = result[0]

        # Values divided by stores
        assert row["total_tags"] == 20 / 2
        assert row["total_quantity"] == 100 / 2
        assert row["total_price"] == 1000.0 / 2
        assert row["discrepancy_dollars"] == 50.0 / 2
        assert row["hours"] == 10 / 2
        # UPH calculation
        assert row["uph"] == (100 / 2) / (10 / 2)
        # Discrepancy %
        assert row["discrepancy_percent"] == (25.0 / 500.0) * 100  # matches scaled values

        mock_fetch.assert_called_once_with(conn=mock_conn)


@pytest.mark.parametrize(
    "conn, expected_exception, msg_substr",
    [
        (None, ValueError, "Database connection cannot be None"),
        (object(), ValueError, "Invalid database connection object"),
    ],
)
def test_load_local_emp_data_invalid_conn(conn, expected_exception, msg_substr):
    with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
        with pytest.raises(expected_exception):
            loader.load_local_emp_data(conn, store="001")
        mock_warning.assert_called()
        assert msg_substr in mock_warning.call_args[0][2]
