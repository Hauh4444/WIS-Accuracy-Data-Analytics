"""Manual database loading dialog with file browser."""
from functools import partial
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

        self.btnSeason.clicked.connect(partial(self.select_source, "season"))
        self.btnOld.clicked.connect(partial(self.select_source, "local"))
        self.btnNew.clicked.connect(partial(self.select_source, "source"))

        center_on_screen(widget=self)

    def select_source(self, source_type: str) -> None:
        """Handle the selection of a data source when a button is clicked.

        Args:
            source_type: One of 'season', 'local', or 'source'.
        """
        self.source = source_type
        self.accept()