import sys
from PyQt6 import QtWidgets

from views.emp_hours_input_dialog import EmpHoursInputWindow

emp_data = [
    {
        "employee_id": "E001",
        "employee_name": "Alice Johnson",
        "total_discrepancy_tags": 5,
        "total_discrepancy_dollars": 320.75,
        "discrepancy_percent": 1.8,
        "total_tags": 150,
        "total_quantity": 3400,
    },
    {
        "employee_id": "E002",
        "employee_name": "Bob Smith",
        "total_discrepancy_tags": 2,
        "total_discrepancy_dollars": 120.00,
        "discrepancy_percent": 0.6,
        "total_tags": 200,
        "total_quantity": 4100,
    },
    {
        "employee_id": "E003",
        "employee_name": "Carla Diaz",
        "total_discrepancy_tags": 8,
        "total_discrepancy_dollars": 780.50,
        "discrepancy_percent": 2.9,
        "total_tags": 175,
        "total_quantity": 3650,
    },
    {
        "employee_id": "E004",
        "employee_name": "David Lee",
        "total_discrepancy_tags": 0,
        "total_discrepancy_dollars": 0.00,
        "discrepancy_percent": 0.0,
        "total_tags": 190,
        "total_quantity": 4000,
    },
]

team_data = [
    {
        "department_number": "001",
        "total_discrepancy_dollars": 1200.50,
        "total_discrepancy_tags": 15,
        "discrepancy_percent": 2.5,
        "total_tags": 600,
        "total_quantity": 12500,
    },
    {
        "department_number": "002",
        "total_discrepancy_dollars": 850.75,
        "total_discrepancy_tags": 9,
        "discrepancy_percent": 1.3,
        "total_tags": 700,
        "total_quantity": 14000,
    },
    {
        "department_number": "003",
        "total_discrepancy_dollars": 2150.00,
        "total_discrepancy_tags": 22,
        "discrepancy_percent": 3.1,
        "total_tags": 710,
        "total_quantity": 13200,
    },
    {
        "department_number": "004",
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