import pytest
import pyodbc
from dataclasses import fields
from unittest.mock import MagicMock

import repositories.local_zone_repository as repo
import models.local_models as models


@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        ('Z001', 'Zone A', 10, 5, 100.0, 0.0, 0)
    ]
    return cursor


@pytest.fixture
def mock_conn(mock_cursor):
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = mock_cursor
    return conn


def test_fetch_old_zone_data_returns_rows(mock_conn, mock_cursor):
    result = repo.fetch_old_zone_data(mock_conn, "001")
    mock_conn.cursor.assert_called_once()
    mock_cursor.close.assert_called_once()
    assert mock_cursor.execute.call_args[0][1] == ("001",)
    assert result == mock_cursor.fetchall.return_value


def test_fetch_old_zone_data_no_rows(mock_conn, mock_cursor):
    mock_cursor.fetchall.return_value = []
    result = repo.fetch_old_zone_data(mock_conn, "002")
    assert result == []


def test_fetch_season_zone_data_returns_rows(mock_conn, mock_cursor):
    result = repo.fetch_season_zone_data(mock_conn)
    mock_conn.cursor.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_cursor.execute.assert_called_once()
    assert result == mock_cursor.fetchall.return_value


def test_fetch_season_zone_data_no_rows(mock_conn, mock_cursor):
    mock_cursor.fetchall.return_value = []
    result = repo.fetch_season_zone_data(mock_conn)
    assert result == []


def test_fetch_old_zone_data_executes_correct_query(mock_conn, mock_cursor):
    repo.fetch_old_zone_data(mock_conn, "001")
    executed_sql = mock_cursor.execute.call_args[0][0]

    zone = models.ZoneTable()
    for field in fields(zone):
        if field.name != "table":
            assert getattr(zone, field.name) in executed_sql
    assert zone.table in executed_sql


def test_fetch_season_zone_data_executes_correct_query(mock_conn, mock_cursor):
    repo.fetch_season_zone_data(mock_conn)
    executed_sql = mock_cursor.execute.call_args[0][0]

    zone_totals = models.ZoneTotalsTable()
    for field in fields(zone_totals):
        if field.name != "table":
            assert getattr(zone_totals, field.name) in executed_sql
    assert zone_totals.table in executed_sql
