"""WIS Accuracy Data Analytics - Inventory accuracy reporting tool."""
import sys
from PyQt6 import QtWidgets

from views.load_data_manual_dialog import LoadDataManualDialog
from views.load_data_dynamic_dialog import LoadDataDynamicDialog
from views.emp_hours_input_window import EmpHoursInputWindow


def load_data_with_fallback():
    """Load data using dynamic dialog first (job_number), fallback to manual dialog if needed."""
    dynamic_dialog = LoadDataDynamicDialog()
    if dynamic_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        if hasattr(dynamic_dialog, 'store_data') and hasattr(dynamic_dialog, 'emp_data') and hasattr(dynamic_dialog, 'team_data'):
            return dynamic_dialog.store_data, dynamic_dialog.emp_data, dynamic_dialog.team_data
    
    manual_dialog = LoadDataManualDialog()
    if manual_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        if hasattr(manual_dialog, 'store_data') and hasattr(manual_dialog, 'emp_data') and hasattr(manual_dialog, 'team_data'):
            return manual_dialog.store_data,  manual_dialog.emp_data, manual_dialog.team_data
    
    return None, None, None


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        store_data, emp_data, team_data = load_data_with_fallback()
        
        if store_data is not None and emp_data is not None and team_data is not None:
            window = EmpHoursInputWindow(store_data=store_data, emp_data=emp_data, team_data=team_data)
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