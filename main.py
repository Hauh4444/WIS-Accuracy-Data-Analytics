"""WIS Accuracy Data Analytics - Inventory accuracy reporting tool."""
import sys

from PyQt6 import QtWidgets

from utils.report_generator import generate_accuracy_report
from views import StatsSourceDialog, LoadDataDynamicDialog, LoadDataManualDialog, EmpHoursInputWindow, LoadLocalDataDialog


def select_stats_source() -> bool | None:
    """Show the stats source dialog and return the selected source.

    Returns:
        'new' if the 'new' button was clicked,
        'old' if the 'old' button was clicked,
        None if the dialog was canceled or 'season' was selected.
    """
    source_dialog = StatsSourceDialog()
    if source_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        source = source_dialog.get_result()
        if source in ('source', 'local'):
            return source

    return None


def load_data_with_fallback() -> tuple[dict, list[dict], list[dict]] | None:
    """Load store, employee, and team data using dynamic dialog with a manual dialog fallback from source database for new inventory.

    Returns:
        Tuple containing (store_data, emp_data, team_data) if successful, or None if data could not be loaded.
    """
    dynamic_dialog = LoadDataDynamicDialog()
    if dynamic_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        data = dynamic_dialog.get_data()
        if all(data):
            return data

    manual_dialog = LoadDataManualDialog()
    if manual_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        data = manual_dialog.get_data()
        if all(data):
            return data

    return None


def load_old_inventory_data() -> tuple[dict, list[dict], list[dict]] | None:
    """Load store, employee, and team data from local database for previous inventory.

    Returns:
        Tuple containing (store_data, emp_data, team_data) if successful, or None if data could not be loaded.
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
        if stats_source == "source":
            store_data, emp_data, team_data = load_data_with_fallback()
            if store_data and emp_data and team_data:
                window = EmpHoursInputWindow(store_data=store_data, emp_data=emp_data, team_data=team_data)
                window.setWindowTitle("WIS Accuracy Data Analytics")
                window.show()
                window.raise_()
                window.activateWindow()
                app.exec()

        elif stats_source == "local":
            store_data, emp_data, team_data = load_old_inventory_data()
            if store_data and emp_data and team_data:
                generate_accuracy_report(store_data=store_data, emp_data=emp_data, team_data=team_data)

    except Exception as e:
        QtWidgets.QMessageBox.critical(
            None,
            "Application Error",
            f"An unexpected error occurred:\n{e}"
        )