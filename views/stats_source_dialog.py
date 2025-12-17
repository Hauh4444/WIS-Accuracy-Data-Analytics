"""Manual database loading dialog with file browser."""
from PyQt6 import QtWidgets, uic

from utils import resource_path
from utils import center_on_screen
from utils import generate_accuracy_report
from services import load_local_store_data, load_local_emp_data, load_local_zone_data
from database import get_storage_db_connection


class StatsSourceDialog(QtWidgets.QDialog):
    """Dialog for selecting stats source."""
    btnSeason: QtWidgets.QPushButton
    btnOld: QtWidgets.QPushButton
    btnNew: QtWidgets.QPushButton

    store_data: dict
    emp_data: list[dict]
    zone_data: list[dict]
    source: str

    def __init__(self) -> None:
        """Initialize the dialog and connect UI elements."""
        super().__init__()
        ui_path = resource_path("assets/ui/stats_source_dialog.ui")
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

        store_data = load_local_store_data(conn, store=None)
        emp_data = load_local_emp_data(conn, store=None)
        zone_data = load_local_zone_data(conn, store=None)
        if store_data and emp_data and zone_data:
            generate_accuracy_report(store_data, emp_data, zone_data, season=True)

        conn.close()
        self.accept()

    def load_old_stats(self):
        self.source = "local"
        self.accept()

    def load_new_stats(self):
        self.source = "source"
        self.accept()

    def get_result(self):
        return self.source