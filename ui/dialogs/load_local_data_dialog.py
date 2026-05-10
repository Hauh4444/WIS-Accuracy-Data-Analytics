import logging
from PyQt6 import QtWidgets, uic

from controllers.local_store_data_controller import LocalStoreDataController
from ui.dialogs.base_data_dialog import BaseDataDialog
from utils.paths import resource_path
from utils.ui import center_on_screen
from exceptions.database_exceptions import DatabaseQueryError
from exceptions.validation_exceptions import ValidationError
from exceptions.wisdom_exceptions import WisdomDataError


class LoadLocalDataDialog(BaseDataDialog):

    def __init__(self, controller: LocalStoreDataController):
        super().__init__()

        self.controller = controller

        ui_path = resource_path("assets/ui/load_local_data_dialog.ui")
        uic.loadUi(ui_path, self)

        self.btnLoad.clicked.connect(self.load_database)

        center_on_screen(widget=self)

    def load_database(self):
        try:
            store_number = self.txtStoreNumber.text().strip()

            if not store_number:
                raise ValidationError("Store number is required")

            data = self.controller.load(store_number)

            self._set_result_data(data)
            self.accept()

        except ValidationError:
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter a valid store number.")

        except WisdomDataError:
            QtWidgets.QMessageBox.critical(self, "Data Error", "Failed to load store data.")

        except DatabaseQueryError:
            QtWidgets.QMessageBox.critical(self, "Database Error", "Database query failed.")

        except Exception:
            logging.exception("Unhandled error in LoadLocalDataDialog.load_database")
            QtWidgets.QMessageBox.critical(self, "Unexpected Error", "Failed to load data.")