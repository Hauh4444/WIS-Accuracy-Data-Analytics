"""Range data loading dialog."""
from PyQt6 import QtWidgets, QtCore, uic
from datetime import datetime, date, time

from database import get_storage_db_connection
from utils import resource_path
from utils import center_on_screen
from services import load_local_store_data, load_local_emp_data, load_local_zone_data


class LoadRangeDataDialog(QtWidgets.QDialog):
    """Dialog for loading range of data."""
    dateStart: QtWidgets.QDateEdit
    dateEnd: QtWidgets.QDateEdit
    btnLoad: QtWidgets.QPushButton

    store_data: dict
    emp_data: list[dict]
    zone_data: list[dict]

    def __init__(self) -> None:
        """Initialize the dialog and connect UI elements."""
        super().__init__()
        ui_path = resource_path("assets/ui/load_range_data_dialog.ui")
        uic.loadUi(ui_path, self)

        today = date.today()
        start_of_year = QtCore.QDate(today.year, 1, 1)
        end_of_year = QtCore.QDate(today.year, 12, 31)

        self.dateStart = QtWidgets.QDateEdit(self)
        self.dateStart.setCalendarPopup(True)
        self.dateStart.setDate(start_of_year)

        self.dateEnd = QtWidgets.QDateEdit(self)
        self.dateEnd.setCalendarPopup(True)
        self.dateEnd.setDate(end_of_year)

        self.btnLoad.clicked.connect(self.load_database)

        center_on_screen(widget=self)

    def load_database(self) -> None:
        """Load employee and zone data from selected database file."""
        conn = get_storage_db_connection()
        if not conn:
            self.reject()
            return

        start_datetime = datetime.combine(self.dateStart.date().toPyDate(), time.min)
        end_datetime = datetime.combine(self.dateEnd.date().toPyDate(), time.max)
        date_range = [start_datetime, end_datetime]

        self.store_data = load_local_store_data(conn, store=None, date_range=date_range)
        self.emp_data = load_local_emp_data(conn, store=None, date_range=date_range)
        self.zone_data = load_local_zone_data(conn, store=None, date_range=date_range)

        conn.close()
        self.accept()