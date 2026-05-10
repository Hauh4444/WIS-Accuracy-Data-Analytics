import logging
from PyQt6 import QtWidgets, uic

from controllers.wisdom_data_controller import WisdomDataController
from ui.dialogs.base_data_dialog import BaseDataDialog
from utils.paths import resource_path
from utils.ui import center_on_screen
from exceptions.file_exceptions import InvalidFileFormatError, FileLoadError
from exceptions.validation_exceptions import ValidationError
from exceptions.wisdom_exceptions import WisdomDataError


class LoadWisdomDataManualDialog(BaseDataDialog):

    def __init__(self, controller: WisdomDataController):
        super().__init__()

        self.controller = controller

        ui_path = resource_path("assets/ui/load_source_data_manual_dialog.ui")
        uic.loadUi(ui_path, self)

        self.btnBrowse.clicked.connect(self.browse_database)
        self.btnLoad.clicked.connect(self.load_database)

        center_on_screen(widget=self)

    def browse_database(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Database File",
            r"C:\WISDOM\JOBS",
            "Access Databases (*.mdb *.accdb)"
        )

        if file_path:
            self.txtDatabasePath.setText(file_path)

    def load_database(self):
        try:
            db_path = self.txtDatabasePath.text().strip()

            if not db_path:
                raise ValidationError("Database path is required")

            if not db_path.endswith((".mdb", ".MDB", ".accdb")):
                raise InvalidFileFormatError("Invalid database file format")

            data = self.controller.load_from_path(db_path)

            self._set_result_data(data)
            self.accept()

        except ValidationError:
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please provide a database path.")

        except InvalidFileFormatError:
            QtWidgets.QMessageBox.warning(self, "Invalid File", "Please select a valid Access database file (.mdb or .accdb).")

        except FileLoadError:
            QtWidgets.QMessageBox.critical(self, "File Error", "Failed to load the database file.")

        except WisdomDataError:
            QtWidgets.QMessageBox.critical(self, "Wisdom Error", "Failed to load wisdom data from the selected database.")

        except Exception:
            logging.exception("Unhandled error in LoadWisdomDataManualDialog.load_database")
            QtWidgets.QMessageBox.critical(self, "Unexpected Error", "An unexpected error occurred while loading data.")