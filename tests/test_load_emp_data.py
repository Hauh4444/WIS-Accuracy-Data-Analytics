import pytest
from unittest.mock import MagicMock, patch

from services.load_emp_data import load_emp_data


def make_row(**kwargs):
    row = MagicMock()
    for k, v in kwargs.items():
        setattr(row, k, v)
    return row


@patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
def test_load_emp_data_exception(mock_critical):
    mock_conn = MagicMock()
    mock_conn.cursor.side_effect = Exception("DB error")
    result = load_emp_data(mock_conn)
    assert result == []
    mock_critical.assert_called_once()
    assert "DB error" in mock_critical.call_args[0][2]


@patch("services.load_emp_data.QtWidgets.QMessageBox.warning")
def test_load_emp_data_no_rows(mock_warning):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    result = load_emp_data(mock_conn)
    assert result == []
    mock_warning.assert_called_once()
    assert "No employee records" in mock_warning.call_args[0][2]


def test_load_emp_data_success():
    mock_row1 = make_row(
        employee_id=1,
        employee_name="Alice",
        total_discrepancy_tags=2,
        total_discrepancy_dollars=100.0,
        discrepancy_percent=5.0,
        total_tags=20,
        total_quantity=50
    )
    mock_row2 = make_row(
        employee_id=2,
        employee_name="Bob",
        total_discrepancy_tags=0,
        total_discrepancy_dollars=0.0,
        discrepancy_percent=0.0,
        total_tags=10,
        total_quantity=30
    )
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [mock_row1, mock_row2]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    result = load_emp_data(mock_conn)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["employee_name"] == "Alice"
    assert result[1]["total_discrepancy_tags"] == 0
    mock_conn.close.assert_called_once()


@patch("services.load_emp_data.QtWidgets.QMessageBox.critical")
def test_cursor_execute_called(mock_critical):
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [make_row(
        employee_id=1,
        employee_name="Alice",
        total_discrepancy_tags=1,
        total_discrepancy_dollars=10.0,
        discrepancy_percent=50.0,
        total_tags=2,
        total_quantity=5
    )]
    load_emp_data(mock_conn)
    assert mock_cursor.execute.called
    assert mock_conn.close.called
    mock_critical.assert_not_called()
