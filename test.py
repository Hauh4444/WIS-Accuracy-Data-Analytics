import sys
from PyQt6 import QtWidgets

from views.emp_hours_input_window import EmpHoursInputWindow

page_headers = {
    "inventory_datetime": "10/1/2025 6:48:00AM",
    "print_date": "10/3/2025",
    "store": "WM - APP - SC - 5499",
    "print_time": "12:34:38PM",
    "store_address": "201 CHAMBER DR"
}

emp_data = [
    {
        "employee_id": "70FP60",
        "employee_name": "FOX, PRESTON",
        "total_discrepancy_dollars": 3782.51,
        "total_discrepancy_tags": 5,
        "discrepancy_percent": 0.58,
        "total_price": 651324.48,
        "total_tags": 376,
        "total_quantity": 72421,
        "discrepancies": [
            {
                'zone_id': 'Z001',
                'upc': '0123456789012',
                'price': 5.99,
                'counted_qty': 8,
                'new_quantity': 3,
                'discrepancy_dollars': abs((5.99 * 3) - (5.99 * 8))
            },
            {
                'zone_id': 'Z001',
                'upc': '0123456789012',
                'price': 5.99,
                'counted_qty': 8,
                'new_quantity': 3,
                'discrepancy_dollars': abs((5.99 * 3) - (5.99 * 8))
            },
            {
                'zone_id': 'Z001',
                'upc': '0123456789012',
                'price': 5.99,
                'counted_qty': 8,
                'new_quantity': 3,
                'discrepancy_dollars': abs((5.99 * 3) - (5.99 * 8))
            }
        ]
    },
    {
        "employee_id": "71FC62",
        "employee_name": "FOX, COLIN",
        "total_discrepancy_dollars": 2831.25,
        "total_discrepancy_tags": 3,
        "discrepancy_percent": 0.51,
        "total_price": 552361.12,
        "total_tags": 342,
        "total_quantity": 75231,
    },
    {
        "employee_id": "62HC15",
        "employee_name": "HOLLANDSWORTH, CHRISTOPHER",
        "total_discrepancy_dollars": 5321.23,
        "total_discrepancy_tags": 10,
        "discrepancy_percent": 1.63,
        "total_price": 327216.21,
        "total_tags": 271,
        "total_quantity": 45326,
    },
]

team_data = [
    {
        "department_number": 1,
        "department_name": "Entertainment",
        "total_discrepancy_dollars": 4532.13,
        "total_discrepancy_tags": 5,
        "discrepancy_percent": 0.70,
        "total_price": 651324.25,
        "total_tags": 87,
        "total_quantity": 52000
    },
    {
        "department_number": 2,
        "department_name": "Home",
        "total_discrepancy_dollars": 2731.62,
        "total_discrepancy_tags": 15,
        "discrepancy_percent": 0.52,
        "total_price": 521352.16,
        "total_tags": 375,
        "total_quantity": 43000
    },
]

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = EmpHoursInputWindow(page_headers, emp_data, team_data)
    window.setWindowTitle("WIS Accuracy Data Analytics")
    window.show()
    window.raise_()
    window.activateWindow()

    app.exec()
