"""Manual database loading dialog with file browser."""
from PyQt6 import QtWidgets, uic

from utils import resource_path
from utils import center_on_screen


class StatsSourceDialog(QtWidgets.QDialog):
    """Dialog for selecting stats source."""
    btnHistorical: QtWidgets.QPushButton
    btnCurrent: QtWidgets.QPushButton
    btnAggregate: QtWidgets.QPushButton

    source: str

    def __init__(self) -> None:
        """Initialize the dialog and connect UI elements."""
        super().__init__()
        ui_path = resource_path("assets/ui/stats_source_dialog.ui")
        uic.loadUi(ui_path, self)

        self.btnHistorical.clicked.connect(lambda: (setattr(self, "source", "historical"), self.accept()))
        self.btnCurrent.clicked.connect(lambda: (setattr(self, "source", "current"), self.accept()))
        self.btnAggregate.clicked.connect(lambda: (setattr(self, "source", "aggregate"), self.accept()))

        center_on_screen(widget=self)