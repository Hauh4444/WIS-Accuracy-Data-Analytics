import pytest
import pyodbc
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from services.load_source_emp_data import load_source_emp_data


@pytest.fixture
def mock_conn():
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = MagicMock()
    return conn


def test_load_source_emp_data_basic(mock_conn):
    emp_tags_rows = [("E001", "T001"), ("E001", "T002")]
    duplicate_tags_rows = [("T002",)]
    emp_rows = [("E001", "Alice")]
    emp_totals_row = (5, 100.0)
    emp_line_totals_row = (2, 40.0)
    emp_discrepancies_rows = [("Z01", "T001", "UPC1", 1, 2, 10.0, 10.0),
                              ("Z01", "T002", "UPC2", 2, 3, 20.0, 20.0)]

    with patch("services.load_source_emp_data.fetch_emp_tags_data", return_value=emp_tags_rows), \
         patch("services.load_source_emp_data.fetch_duplicate_tags_data", return_value=duplicate_tags_rows), \
         patch("services.load_source_emp_data.fetch_emp_data", return_value=emp_rows), \
         patch("services.load_source_emp_data.fetch_emp_totals_data", return_value=emp_totals_row), \
         patch("services.load_source_emp_data.fetch_emp_line_totals_data", return_value=emp_line_totals_row), \
         patch("services.load_source_emp_data.fetch_emp_discrepancies_data", return_value=emp_discrepancies_rows), \
         patch("services.load_source_emp_data.fetch_line_data", return_value=("E001",)):

        result = load_source_emp_data(mock_conn)
        assert len(result) == 1
        emp = result[0]
        assert emp["emp_number"] == "E001"
        assert emp["emp_name"] == "Alice"
        assert emp["total_quantity"] == 7
        assert emp["total_price"] == 140.0
        assert emp["discrepancy_dollars"] == 30.0
        assert emp["discrepancy_tags"] == 2
        assert len(emp["discrepancies"]) == 2
        assert emp["discrepancy_percent"] == pytest.approx(21.42857, 0.0001)


def test_load_source_emp_data_empty_data(mock_conn):
    with patch("services.load_source_emp_data.fetch_emp_tags_data", return_value=[]), \
         patch("services.load_source_emp_data.fetch_duplicate_tags_data", return_value=[]), \
         patch("services.load_source_emp_data.fetch_emp_data", return_value=[]):
        result = load_source_emp_data(mock_conn)
        assert result == []


def test_load_source_emp_data_zero_totals(mock_conn):
    emp_tags_rows = [("E001", "T001")]
    duplicate_tags_rows = []
    emp_rows = [("E001", "Alice")]
    emp_totals_row = (0, 0.0)
    emp_line_totals_row = (0, 0.0)
    emp_discrepancies_rows = []

    with patch("services.load_source_emp_data.fetch_emp_tags_data", return_value=emp_tags_rows), \
         patch("services.load_source_emp_data.fetch_duplicate_tags_data", return_value=duplicate_tags_rows), \
         patch("services.load_source_emp_data.fetch_emp_data", return_value=emp_rows), \
         patch("services.load_source_emp_data.fetch_emp_totals_data", return_value=emp_totals_row), \
         patch("services.load_source_emp_data.fetch_emp_line_totals_data", return_value=emp_line_totals_row), \
         patch("services.load_source_emp_data.fetch_emp_discrepancies_data", return_value=emp_discrepancies_rows):

        result = load_source_emp_data(mock_conn)
        emp = result[0]
        assert emp["total_quantity"] == 0
        assert emp["total_price"] == 0
        assert emp["discrepancy_percent"] == 0


def test_load_source_emp_data_invalid_connection():
    with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        with pytest.raises(ValueError):
            load_source_emp_data(None)
        with pytest.raises(ValueError):
            load_source_emp_data(object())
        assert mock_warning.called


def test_load_source_emp_data_invalid_row_length(mock_conn):
    with patch("services.load_source_emp_data.fetch_emp_tags_data", return_value=[("E001", "T001", "EXTRA")]), \
         patch("services.load_source_emp_data.fetch_duplicate_tags_data", return_value=[]), \
         patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        with pytest.raises(RuntimeError):
            load_source_emp_data(mock_conn)
        assert mock_warning.called


def test_load_source_emp_data_db_exception(mock_conn):
    with patch("services.load_source_emp_data.fetch_emp_tags_data", side_effect=pyodbc.Error("DB error")), \
         patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        with pytest.raises(pyodbc.Error):
            load_source_emp_data(mock_conn)
        assert mock_warning.called
