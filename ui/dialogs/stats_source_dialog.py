import logging
from PyQt6 import QtWidgets, uic

from domain.enums.stats_source import StatsSource
from utils.paths import resource_path
from utils.ui import center_on_screen


class StatsSourceDialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        self.selected_source = None

        try:
            ui_path = resource_path("assets/ui/stats_source_dialog.ui")
            uic.loadUi(ui_path, self)

            self.btnHistorical.clicked.connect(lambda: self.select_source(StatsSource.HISTORICAL))
            self.btnCurrent.clicked.connect(lambda: self.select_source(StatsSource.CURRENT))
            self.btnAggregate.clicked.connect(lambda: self.select_source(StatsSource.AGGREGATE))

            center_on_screen(widget=self)

        except Exception:
            logging.exception("Failed to initialize StatsSourceDialog")
            QtWidgets.QMessageBox.critical(self, "Initialization Error", "Failed to load statistics source dialog")
            raise

    def select_source(self, source):
        try:
            self.selected_source = source
            self.accept()

        except Exception:
            logging.exception("Failed to select stats source")
            QtWidgets.QMessageBox.critical(self, "Selection Error", "Failed to select data source.")