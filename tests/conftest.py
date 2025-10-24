"""Pytest configuration and shared fixtures."""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock
from PyQt6 import QtWidgets
import pyodbc


@pytest.fixture
def mock_qt_app():
    """Mock QApplication for testing."""
    app = Mock(spec=QtWidgets.QApplication)
    app.primaryScreen.return_value = Mock()
    app.primaryScreen.return_value.availableGeometry.return_value = Mock()
    app.primaryScreen.return_value.availableGeometry.return_value.width.return_value = 1920
    app.primaryScreen.return_value.availableGeometry.return_value.height.return_value = 1080
    return app


@pytest.fixture
def mock_database_connection():
    """Mock database connection for testing."""
    conn = Mock(spec=pyodbc.Connection)
    cursor = Mock(spec=pyodbc.Cursor)
    conn.cursor.return_value = cursor
    return conn


@pytest.fixture
def mock_cursor():
    """Mock database cursor for testing."""
    cursor = Mock(spec=pyodbc.Cursor)
    return cursor


@pytest.fixture
def sample_emp_data():
    """Sample employee data for testing."""
    return [
        {
            'emp_number': '12345',
            'emp_name': 'John Doe',
            'total_tags': 10,
            'total_quantity': 100,
            'total_price': 1000.0,
            'total_discrepancy_dollars': 50.0,
            'total_discrepancy_tags': 2,
            'discrepancy_percent': 5.0,
            'hours': 8.0,
            'uph': 12.5,
            'discrepancies': [
                {
                    'zone_id': 1,
                    'tag_number': 'T001',
                    'upc': '123456789',
                    'price': 10.0,
                    'counted_quantity': 5,
                    'new_quantity': 4,
                    'discrepancy_dollars': 10.0
                }
            ]
        },
        {
            'emp_number': '67890',
            'emp_name': 'Jane Smith',
            'total_tags': 15,
            'total_quantity': 150,
            'total_price': 1500.0,
            'total_discrepancy_dollars': 75.0,
            'total_discrepancy_tags': 3,
            'discrepancy_percent': 5.0,
            'hours': 7.5,
            'uph': 20.0,
            'discrepancies': []
        }
    ]


@pytest.fixture
def sample_team_data():
    """Sample team data for testing."""
    return [
        {
            'zone_number': 1,
            'zone_name': 'Electronics',
            'total_tags': 25,
            'total_quantity': 250,
            'total_price': 2500.0,
            'total_discrepancy_dollars': 125.0,
            'total_discrepancy_tags': 5,
            'discrepancy_percent': 5.0
        },
        {
            'zone_number': 2,
            'zone_name': 'Clothing',
            'total_tags': 30,
            'total_quantity': 300,
            'total_price': 3000.0,
            'total_discrepancy_dollars': 150.0,
            'total_discrepancy_tags': 6,
            'discrepancy_percent': 5.0
        }
    ]


@pytest.fixture
def sample_store_data():
    """Sample store data for testing."""
    return {
        'inventory_datetime': '2024-01-15 10:00:00',
        'print_date': '1/15/2024',
        'store': 'Test Store',
        'print_time': '10:30:00AM',
        'store_address': '123 Test St, Test City, TC 12345'
    }


@pytest.fixture
def temp_database_file():
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.mdb', delete=False) as tmp:
        tmp_path = tmp.name
    yield tmp_path
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def mock_pyodbc_row():
    """Mock pyodbc.Row for testing."""
    def create_row(values):
        row = Mock()
        row.__getitem__ = Mock(side_effect=lambda i: values[i])
        row.__len__ = Mock(return_value=len(values))
        # Don't set __iter__ as it's not supported by Mock
        return row
    return create_row


@pytest.fixture
def mock_file_dialog():
    """Mock QFileDialog for testing."""
    with pytest.Mock() as mock_dialog:
        mock_dialog.getOpenFileName.return_value = ("/path/to/test.mdb", "Access Databases (*.mdb *.accdb)")
        yield mock_dialog


@pytest.fixture
def mock_webbrowser():
    """Mock webbrowser module for testing."""
    with pytest.Mock() as mock_browser:
        mock_browser.open = Mock()
        yield mock_browser


@pytest.fixture
def mock_pisa():
    """Mock xhtml2pdf.pisa for testing."""
    with pytest.Mock() as mock_pisa_module:
        mock_pisa_module.CreatePDF = Mock()
        mock_pisa_module.CreatePDF.return_value.err = False
        yield mock_pisa_module


@pytest.fixture
def mock_jinja2_env():
    """Mock Jinja2 Environment for testing."""
    with pytest.Mock() as mock_env:
        mock_template = Mock()
        mock_template.render = Mock(return_value="<html>Test HTML</html>")
        mock_env.get_template = Mock(return_value=mock_template)
        yield mock_env


@pytest.fixture
def mock_tempfile():
    """Mock tempfile module for testing."""
    with pytest.Mock() as mock_temp:
        mock_file = Mock()
        mock_file.name = "/tmp/test.pdf"
        mock_file.write = Mock()
        mock_file.flush = Mock()
        mock_temp.NamedTemporaryFile.return_value.__enter__ = Mock(return_value=mock_file)
        mock_temp.NamedTemporaryFile.return_value.__exit__ = Mock(return_value=None)
        yield mock_temp
