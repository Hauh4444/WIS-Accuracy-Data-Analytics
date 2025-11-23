"""WIS Accuracy Data Analytics - Inventory accuracy reporting tool."""
import sys

from PyQt6 import QtWidgets

from utils import generate_accuracy_report
from views import StatsSourceDialog, LoadSourceDataDynamicDialog, LoadSourceDataManualDialog, EmpHoursInputWindow, LoadLocalDataDialog


def select_stats_source() -> str | None:
    """Show the stats source dialog and return the selected source.

    Returns:
        'local' if the 'old' button was clicked,
        'source' if the 'new' button was clicked,
        None if the dialog was canceled or 'season' was selected.
    """
    source_dialog = StatsSourceDialog()
    if source_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        source = source_dialog.get_result()
        if source in ('local', 'source'):
            return source

    return None


def load_data_with_fallback() -> tuple[dict, list[dict], list[dict]] | None:
    """Load store, employee, and zone data using dynamic dialog with a manual dialog fallback from source database for new inventory.

    Returns:
        Tuple containing (store_data, emp_data, zone_data) if successful, or None if data could not be loaded.
    """
    dynamic_dialog = LoadSourceDataDynamicDialog()
    if dynamic_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        data = dynamic_dialog.get_data()
        if all(data):
            return data

    manual_dialog = LoadSourceDataManualDialog()
    if manual_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        data = manual_dialog.get_data()
        if all(data):
            return data

    return None


def load_old_inventory_data() -> tuple[dict, list[dict], list[dict]] | None:
    """Load store, employee, and zone data from local database for previous inventory.

    Returns:
        Tuple containing (store_data, emp_data, zone_data) if successful, or None if data could not be loaded.
    """
    local_dialog = LoadLocalDataDialog()
    if local_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        data = local_dialog.get_data()
        if all(data):
            return data

    return None


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)

        stats_source = select_stats_source()
        if stats_source == "local":
            store_data, emp_data, zone_data = load_old_inventory_data()
            if store_data and emp_data and zone_data:
                generate_accuracy_report(store_data, emp_data, zone_data, season=False)
        elif stats_source == "source":
            store_data, emp_data, zone_data = load_data_with_fallback()

            if not store_data:
                raise Exception("Failed to load store data.")
            if not emp_data:
                raise Exception("Failed to load employee data.")
            if not zone_data:
                raise Exception("Failed to load zone data.")

            window = EmpHoursInputWindow(store_data, emp_data, zone_data)
            window.setWindowTitle("WIS Accuracy Data Analytics")
            window.show()
            window.raise_()
            window.activateWindow()
            app.exec()

    except Exception as e:
        QtWidgets.QMessageBox.critical(
            None,
            "Application Error",
            f"An unexpected error occurred:\n{e}"
        )