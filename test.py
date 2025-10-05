from services.report_generator import generate_accuracy_report

page_headers = {
    "inventory_datetime": "10/1/2025 6:48:00AM",
    "print_date": "10/3/2025",
    "store": "WM - APP - SC - 5499",
    "print_time": "12:34:38PM",
    "store_address": "201 CHAMBER DR"
}

emp_data = [
    {
        "employee_id": 101,
        "employee_name": "Alice Johnson",
        "total_discrepancy_dollars": 12.50,
        "total_discrepancy_tags": 5,
        "discrepancy_percent": 1.8,
        "total_price": 250.00,
        "total_tags": 120,
        "total_quantity": 100,
        "uph": 25
    },
    {
        "employee_id": 102,
        "employee_name": "Bob Smith",
        "total_discrepancy_dollars": 25.00,
        "total_discrepancy_tags": 10,
        "discrepancy_percent": 2.2,
        "total_price": 500.00,
        "total_tags": 200,
        "total_quantity": 150,
        "uph": 30
    },
    {
        "employee_id": 103,
        "employee_name": "Charlie Davis",
        "total_discrepancy_dollars": 5.00,
        "total_discrepancy_tags": 2,
        "discrepancy_percent": 1.2,
        "total_price": 100.00,
        "total_tags": 50,
        "total_quantity": 80,
        "uph": 20
    },
]

for i in range(42):
    emp_data.append({
        "employee_id": 103,
        "employee_name": "Charlie Davis",
        "total_discrepancy_dollars": 5.00,
        "total_discrepancy_tags": 2,
        "discrepancy_percent": 1.2,
        "total_price": 100.00,
        "total_tags": 50,
        "total_quantity": 80,
        "uph": 20
    })

team_data = [
    {
        "department_number": 1,
        "department_name": "Electronics",
        "total_discrepancy_dollars": 30.00,
        "total_discrepancy_tags": 12,
        "discrepancy_percent": 2.0,
        "total_price": 800.00,
        "total_tags": 250,
        "total_quantity": 200
    },
    {
        "department_number": 2,
        "department_name": "Home & Garden",
        "total_discrepancy_dollars": 15.00,
        "total_discrepancy_tags": 6,
        "discrepancy_percent": 1.5,
        "total_price": 400.00,
        "total_tags": 150,
        "total_quantity": 120
    },
]

if __name__ == "__main__":
    generate_accuracy_report(page_headers, emp_data, team_data)
