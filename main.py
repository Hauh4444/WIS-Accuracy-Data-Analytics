import sys
from PyQt6 import QtWidgets
from views.load_data_dialog import LoadDataDialog


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        dialog = LoadDataDialog()
        dialog.exec()
    except Exception as e:
        QtWidgets.QMessageBox.critical(
            None,
            "Application Error",
            f"An unexpected error occurred:\n{e}"
        )