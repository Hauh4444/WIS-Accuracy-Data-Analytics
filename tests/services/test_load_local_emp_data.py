import pytest
import pyodbc
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from services.load_local_emp_data import load_local_emp_data


@pytest.fixture
def mock_conn():
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = MagicMock()
    return conn


def test_load_local_emp_data_store_calls_fetch_old_emp_data(mock_conn):
    sample_rows = [
        (123, "Alice", 10, 50, 500.0, 25.0, 1, 5),
        (124, "Bob", None, None, None, None, None, None),
    ]
    with patch("services.load_local_emp_data.fetch_old_emp_data", return_value=sample_rows) as mock_fetch:
        result = load_local_emp_data(mock_conn, store="001")
        assert len(result) == 2
        row1 = result[0]
        assert row1["emp_number"] == 123
        assert row1["emp_name"] == "Alice"
        row2 = result[1]
        assert row2["total_tags"] == 0
        mock_fetch.assert_called_once_with(mock_conn, "001")


def test_load_local_emp_data_aggregate_calls_fetch_aggregate_emp_data(mock_conn):
    sample_rows = [
        (201, "Charlie", 20, 100, 1000.0, 50.0, 2, 2, 10),
    ]
    with patch("services.load_local_emp_data.fetch_aggregate_emp_data", return_value=sample_rows) as mock_fetch:
        result = load_local_emp_data(mock_conn, store=None)
        assert len(result) == 1
        row = result[0]
        stores = 2
        assert row["total_tags"] == 20 / stores
        assert row["uph"] == (100 / stores) / (10 / stores)
        mock_fetch.assert_called_once_with(mock_conn)


@pytest.mark.parametrize(
    "conn, expected_exception, msg_substr",
    [
        (None, ValueError, "Database connection cannot be None"),
        (object(), ValueError, "Invalid database connection object"),
    ],
)
def test_load_local_emp_data_invalid_conn(conn, expected_exception, msg_substr):
    with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        with pytest.raises(expected_exception):
            load_local_emp_data(conn, store="001")
        mock_warning.assert_called()
        assert msg_substr in mock_warning.call_args[0][2]
