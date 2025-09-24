import sys
from PyQt6 import QtWidgets

from views.emp_hours_input_window import EmpHoursInputWindow

emp_data = [
    {
        "employee_id": "XXXXXX",
        "employee_name": "PRESTON FOX",
        "total_discrepancy_tags": 5,
        "total_discrepancy_dollars": 320.75,
        "discrepancy_percent": 1.8,
        "total_tags": 378,
        "total_quantity": 52187,
    },
    {
        "employee_id": "XXXXXX",
        "employee_name": "COLIN FOX",
        "total_discrepancy_tags": 2,
        "total_discrepancy_dollars": 120.00,
        "discrepancy_percent": 0.6,
        "total_tags": 350,
        "total_quantity": 73254,
    },
    {
        "employee_id": "XXXXXX",
        "employee_name": "CHRISTOPHER HOLLANDSWORTH",
        "total_discrepancy_tags": 8,
        "total_discrepancy_dollars": 780.50,
        "discrepancy_percent": 2.9,
        "total_tags": 297,
        "total_quantity": 47562,
    },
    {
        "employee_id": "XXXXXX",
        "employee_name": "JABBA DA JAKE",
        "total_discrepancy_tags": 0,
        "total_discrepancy_dollars": 0.00,
        "discrepancy_percent": 0.0,
        "total_tags": 100,
        "total_quantity": 10000,
    },
]

team_data = [
    {
        "department_number": "01",
        "department_name": "ENTERTAINMENT",
        "total_discrepancy_dollars": 1200.50,
        "total_discrepancy_tags": 15,
        "discrepancy_percent": 2.5,
        "total_tags": 600,
        "total_quantity": 12500,
    },
    {
        "department_number": "02",
        "department_name": "GROCERY",
        "total_discrepancy_dollars": 850.75,
        "total_discrepancy_tags": 9,
        "discrepancy_percent": 1.3,
        "total_tags": 700,
        "total_quantity": 14000,
    },
    {
        "department_number": "03",
        "department_name": "GM SEASONAL",
        "total_discrepancy_dollars": 2150.00,
        "total_discrepancy_tags": 22,
        "discrepancy_percent": 3.1,
        "total_tags": 710,
        "total_quantity": 13200,
    },
    {
        "department_number": "04",
        "department_name": "HOME",
        "total_discrepancy_dollars": 430.20,
        "total_discrepancy_tags": 4,
        "discrepancy_percent": 0.7,
        "total_tags": 590,
        "total_quantity": 11000,
    },
]

app = QtWidgets.QApplication(sys.argv)
window = EmpHoursInputWindow(emp_data, team_data)
window.show()
app.exec()