"""WIS Accuracy Data Analytics - Inventory accuracy reporting tool."""
import sys
import logging
from PyQt6 import QtWidgets

from utils import generate_accuracy_report, setup_logging
from views import (
    EmpHoursInputWindow,
    StatsSourceDialog,
    LoadLocalDataDialog,
    LoadSourceDataDynamicDialog,
    LoadSourceDataManualDialog,
    LoadRangeDataDialog
)


def handle_dialog(dialog: QtWidgets.QDialog) -> str | tuple[dict, list[dict], list[dict]] | None:
    """Run a dialog and return its result.

    Args:
        dialog: The QDialog to execute.

    Returns:
        'local' or 'source' if a source is selected,
        tuple containing store_data, emp_data, and zone_data if data is loaded,
        or None if cancelled or failed.
    """
    if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
        return None

    if hasattr(dialog, "source"):
        source = dialog.source
        if source in ("local", "source", "season"):
            return source

    if hasattr(dialog, "store_data") and hasattr(dialog, "emp_data") and hasattr(dialog, "zone_data"):
        data = dialog.store_data, dialog.emp_data, dialog.zone_data
        if all(data):
            return data

    return None


if __name__ == "__main__":
    setup_logging()

    try:
        app = QtWidgets.QApplication(sys.argv)

        stats_source = handle_dialog(StatsSourceDialog())

        if stats_source == "local":
            result = handle_dialog(LoadLocalDataDialog())
            if not result:
                raise Exception("Failed to load local data.")

            store_data, emp_data, zone_data = result
            generate_accuracy_report(store_data, emp_data, zone_data, is_date_range=False)

        elif stats_source == "source":
            result = handle_dialog(LoadSourceDataDynamicDialog())
            if not result:
                result = handle_dialog(LoadSourceDataManualDialog())
            if not result:
                raise Exception("Failed to load source data.")

            store_data, emp_data, zone_data = result
            window = EmpHoursInputWindow(store_data, emp_data, zone_data)
            app.exec()

        elif stats_source == "season":
            result = handle_dialog(LoadRangeDataDialog())
            if not result:
                raise Exception("Failed to load range data.")

            store_data, emp_data, zone_data = result
            generate_accuracy_report(store_data, emp_data, zone_data, is_date_range=True)

    except Exception as e:
        logging.exception("Unhandled application error")
        QtWidgets.QMessageBox.critical(
            None,
            "Application Error",
            f"An unexpected error occurred:\n{e}"
        )