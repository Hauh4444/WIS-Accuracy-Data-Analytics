"""Manual database loading dialog with file browser."""
import traceback
import pyodbc
from datetime import datetime

from PyQt6 import QtWidgets, uic

from utils.paths import resource_path
from utils.ui_utils import center_on_screen
from utils.report_generator import generate_accuracy_report
from services import load_local_emp_data, load_local_team_data
from database.connection import get_storage_db_connection


class StatsSourceDialog(QtWidgets.QDialog):
    """Dialog for selecting stats source."""
    btnSeason: QtWidgets.QPushButton
    btnOld: QtWidgets.QPushButton
    btnNew: QtWidgets.QPushButton

    store_data: dict
    emp_data: list[dict]
    team_data: list[dict]
    source: str

    def __init__(self) -> None:
        """Initialize the dialog and connect UI elements."""
        super().__init__()
        ui_path = resource_path("ui/stats_source_dialog.ui")
        uic.loadUi(ui_path, self)

        self.btnSeason.clicked.connect(self.load_season_stats)
        self.btnOld.clicked.connect(self.load_old_stats)
        self.btnNew.clicked.connect(self.load_new_stats)

        center_on_screen(widget=self)

    def load_season_stats(self):
        conn = get_storage_db_connection()
        if not conn:
            self.reject()
            return

        try:
            now = datetime.now()
            store_data: dict = {
                "inventory_datetime": "",
                "print_date": f"{now.month}/{now.day}/{now.year}",
                "store": "",
                "print_time": now.strftime("%I:%M:%S%p"),
                "store_address": ""
            }
            emp_data = load_local_emp_data(conn=conn, store=None)
            team_data = load_local_team_data(conn=conn, store=None)
            if store_data and emp_data and team_data:
                generate_accuracy_report(store_data=store_data, emp_data=emp_data, team_data=team_data)

            self.accept()

        except (pyodbc.Error, pyodbc.DatabaseError) as e:
            QtWidgets.QMessageBox.critical(None, "Database Error", f"Database query failed: {str(e)}")
            traceback.print_exc()
            self.reject()
        except ValueError as e:
            QtWidgets.QMessageBox.critical(None, "Configuration Error", f"Invalid configuration: {str(e)}")
            traceback.print_exc()
            self.reject()
        except RuntimeError as e:
            QtWidgets.QMessageBox.critical(None, "Data Error", f"Data validation failed: {str(e)}")
            traceback.print_exc()
            self.reject()
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Unexpected Error", f"An unexpected error occurred: {str(e)}")
            traceback.print_exc()
            self.reject()

    def load_old_stats(self):
        self.source = "local"
        self.accept()

    def load_new_stats(self):
        self.source = "source"
        self.accept()

    def get_result(self):
        return self.source