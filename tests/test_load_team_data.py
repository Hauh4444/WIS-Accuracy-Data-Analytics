import pytest
from unittest.mock import MagicMock, patch

from services.load_team_data import load_team_data


def make_row(**kwargs):
    row = MagicMock()
    for k, v in kwargs.items():
        setattr(row, k, v)
    return row


@patch("services.load_team_data.QtWidgets.QMessageBox.critical")
def test_load_team_data_exception(mock_critical):
    mock_conn = MagicMock()
    mock_conn.cursor.side_effect = Exception("DB error")
    result = load_team_data(mock_conn)
    assert result == []
    mock_critical.assert_called_once()
    assert "DB error" in mock_critical.call_args[0][2]


@patch("services.load_team_data.QtWidgets.QMessageBox.warning")
def test_load_team_data_no_rows(mock_warning):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    result = load_team_data(mock_conn)
    assert result == []
    mock_warning.assert_called_once()
    assert "No team records" in mock_warning.call_args[0][2]


def test_load_team_data_success():
    mock_row1 = make_row(
        department_number=101,
        department_name="HR",
        total_discrepancy_dollars=50.0,
        total_discrepancy_tags=2,
        discrepancy_percent=5.0,
        total_tags=20,
        total_quantity=100
    )
    mock_row2 = make_row(
        department_number=102,
        department_name="Finance",
        total_discrepancy_dollars=0.0,
        total_discrepancy_tags=0,
        discrepancy_percent=0.0,
        total_tags=10,
        total_quantity=50
    )
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [mock_row1, mock_row2]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    result = load_team_data(mock_conn)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["department_name"] == "HR"
    assert result[1]["total_discrepancy_tags"] == 0
    mock_conn.close.assert_called_once()


@patch("services.load_team_data.QtWidgets.QMessageBox.critical")
def test_cursor_execute_called(mock_critical):
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [make_row(
        department_number=201,
        department_name="IT",
        total_discrepancy_dollars=30.0,
        total_discrepancy_tags=1,
        discrepancy_percent=10.0,
        total_tags=5,
        total_quantity=25
    )]
    load_team_data(mock_conn)
    assert mock_cursor.execute.called
    assert mock_conn.close.called
    mock_critical.assert_not_called()
