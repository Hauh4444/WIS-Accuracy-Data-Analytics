import pytest
from unittest.mock import patch, MagicMock
import pyodbc

import services.load_source_emp_data as loader


@pytest.fixture
def mock_conn():
    """Return a dummy pyodbc connection-like object."""
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = MagicMock()
    return conn


def test_load_source_emp_data_basic(mock_conn):
    # Mocks
    emp_tags_rows = [("E001", "T001"), ("E001", "T002")]
    duplicate_tags_rows = [("T002",)]
    emp_rows = [("E001", "Alice")]
    emp_totals_row = (5, 100.0)  # total_quantity, total_price
    emp_line_totals_row = (2, 40.0)
    emp_discrepancies_rows = [("Z01", "T001", "UPC1", 1, 2, 10.0, 10.0),
                              ("Z01", "T002", "UPC2", 2, 3, 20.0, 20.0)]

    with patch("repositories.source_emp_repository.fetch_emp_tags_data", return_value=emp_tags_rows), \
         patch("repositories.source_emp_repository.fetch_duplicate_tags_data", return_value=duplicate_tags_rows), \
         patch("repositories.source_emp_repository.fetch_emp_data", return_value=emp_rows), \
         patch("repositories.source_emp_repository.fetch_emp_totals_data", return_value=emp_totals_row), \
         patch("repositories.source_emp_repository.fetch_emp_line_totals_data", return_value=emp_line_totals_row), \
         patch("repositories.source_emp_repository.fetch_emp_discrepancies_data", return_value=emp_discrepancies_rows), \
         patch("repositories.source_emp_repository.fetch_line_data", return_value=("E001",)):

        result = loader.load_source_emp_data(mock_conn)
        assert len(result) == 1
        emp = result[0]
        assert emp["emp_number"] == "E001"
        assert emp["emp_name"] == "Alice"
        # total_quantity = emp_totals_row + emp_line_totals_row
        assert emp["total_quantity"] == 5 + 2
        assert emp["total_price"] == 100.0 + 40.0
        # discrepancy dollars sum
        assert emp["discrepancy_dollars"] == 10.0 + 20.0
        # only 2 discrepancies for 2 tags
        assert emp["discrepancy_tags"] == 2
        assert len(emp["discrepancies"]) == 2
        # discrepancy percent
        assert emp["discrepancy_percent"] == (30.0 / 140.0 * 100)


def test_load_source_emp_data_empty_tags(mock_conn):
    # No tags, duplicates, or employees
    with patch("repositories.source_emp_repository.fetch_emp_tags_data", return_value=[]), \
         patch("repositories.source_emp_repository.fetch_duplicate_tags_data", return_value=[]), \
         patch("repositories.source_emp_repository.fetch_emp_data", return_value=[]):
        result = loader.load_source_emp_data(mock_conn)
        assert result == []


def test_load_source_emp_data_invalid_connection():
    import PyQt6.QtWidgets as qt
    with patch.object(qt.QMessageBox, "warning") as mock_warning:
        with pytest.raises(ValueError):
            loader.load_source_emp_data(None)
        with pytest.raises(ValueError):
            loader.load_source_emp_data(object())
        assert mock_warning.called


def test_load_source_emp_data_runtime_error_on_bad_emp_tags(mock_conn):
    # Emp tags row with wrong length
    with patch("repositories.source_emp_repository.fetch_emp_tags_data", return_value=[("E001", "T001", "EXTRA")]), \
         patch("repositories.source_emp_repository.fetch_duplicate_tags_data", return_value=[]):
        with pytest.raises(RuntimeError):
            loader.load_source_emp_data(mock_conn)
