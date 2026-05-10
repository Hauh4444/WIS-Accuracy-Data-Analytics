import logging
from datetime import date

from PyQt6 import QtWidgets, QtCore, uic

from controllers.local_aggregate_data_controller import LocalAggregateDataController
from ui.dialogs.base_data_dialog import BaseDataDialog
from utils.paths import resource_path
from utils.ui import center_on_screen
from exceptions.database_exceptions import DatabaseQueryError
from exceptions.validation_exceptions import ValidationError
from exceptions.wisdom_exceptions import WisdomDataError


class LoadAggregateDataDialog(BaseDataDialog):

    def __init__(self, controller: LocalAggregateDataController):
        super().__init__()

        self.controller = controller

        ui_path = resource_path("assets/ui/load_aggregate_data_dialog.ui")
        uic.loadUi(ui_path, self)

        today = date.today()

        self.dateStart.setCalendarPopup(True)
        self.dateEnd.setCalendarPopup(True)
        self.dateStart.setDate(QtCore.QDate(today.year, 1, 1))
        self.dateEnd.setDate(QtCore.QDate(today.year, 12, 31))

        self.btnLoad.clicked.connect(self.load_database)

        center_on_screen(widget=self)

    def load_database(self):
        try:
            start = self.dateStart.date().toPyDate()
            end = self.dateEnd.date().toPyDate()

            data = self.controller.load(start, end)

            self._set_result_data(data)
            self.accept()

        except ValidationError:
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please select a valid date range.")

        except WisdomDataError:
            QtWidgets.QMessageBox.critical(self, "Data Error", "Failed to load aggregate data.")

        except DatabaseQueryError:
            QtWidgets.QMessageBox.critical(self, "Database Error", "Database query failed.")

        except Exception:
            logging.exception("Unhandled error in LoadAggregateDataDialog.load_database")
            QtWidgets.QMessageBox.critical(self, "Unexpected Error", "Failed to load data.")