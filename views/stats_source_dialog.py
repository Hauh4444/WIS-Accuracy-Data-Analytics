"""Manual database loading dialog with file browser."""
import traceback
import pyodbc

from PyQt6 import QtWidgets, uic

from utils.paths import resource_path
from utils.ui_utils import center_on_screen
from utils.season_report_generator import generate_season_accuracy_report
from services import load_local_store_data, load_local_emp_data, load_local_team_data
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
        self.source = "season"

        conn = get_storage_db_connection()
        if not conn:
            self.reject()
            return

        try:
            store_data = load_local_store_data(conn=conn, store=None)
            emp_data = load_local_emp_data(conn=conn, store=None)
            team_data = load_local_team_data(conn=conn, store=None)
            if store_data and emp_data and team_data:
                generate_season_accuracy_report(store_data=store_data, emp_data=emp_data, team_data=team_data)

            self.accept()

        except:
            traceback.print_exc()

    def load_old_stats(self):
        self.source = "local"
        self.accept()

    def load_new_stats(self):
        self.source = "source"
        self.accept()

    def get_result(self):
        return self.source