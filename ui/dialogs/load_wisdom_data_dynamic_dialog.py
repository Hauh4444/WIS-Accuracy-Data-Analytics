import logging
from PyQt6 import QtWidgets, uic

from controllers.wisdom_data_controller import WisdomDataController
from ui.dialogs.base_data_dialog import BaseDataDialog
from utils.paths import resource_path
from utils.ui import center_on_screen
from exceptions.validation_exceptions import ValidationError
from exceptions.wisdom_exceptions import WisdomDatabaseNotFoundError, WisdomDataError


class LoadWisdomDataDynamicDialog(BaseDataDialog):

    def __init__(self, controller: WisdomDataController):
        super().__init__()

        self.controller = controller

        ui_path = resource_path("assets/ui/load_source_data_dynamic_dialog.ui")
        uic.loadUi(ui_path, self)

        self.btnLoad.clicked.connect(self.load_database)

        center_on_screen(widget=self)

    def load_database(self):
        try:
            job_number = self.txtJobNumber.text().strip()

            if not job_number:
                raise ValidationError("Job number is required")

            data = self.controller.load_from_job_number(job_number)

            self._set_result_data(data)
            self.accept()

        except ValidationError:
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter a valid job number.")

        except WisdomDatabaseNotFoundError:
            QtWidgets.QMessageBox.critical(self, "Not Found", "No data found for the provided job number.")

        except WisdomDataError:
            QtWidgets.QMessageBox.critical(self, "Wisdom Data Error", "Failed to load wisdom data.")

        except Exception:
            logging.exception("Unhandled error in LoadWisdomDataDynamicDialog.load_database")
            QtWidgets.QMessageBox.critical(self, "Unexpected Error", "Failed to load data.")