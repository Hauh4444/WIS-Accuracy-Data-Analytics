from dataclasses import dataclass


@dataclass(frozen=True)
class DiscrepancyTable:
    table: str = "discrepancies"
    tag_number: str = "tag_number"
    dollar_change: str = "dollar_change"
    department_number: str = "department_number"
    department_name: str = "department_name"


@dataclass(frozen=True)
class TagTable:
    table: str = "tags"
    employee_id: str = "employee_id"
    employee_name: str = "employee_name"
    tag_number: str = "tag_number"
    dollars: str = "dollars"
    qty: str = "qty"


@dataclass(frozen=True)
class EmployeeTable:
    table: str = "employees"
    employee_id: str = "employee_id"
    employee_name: str = "employee_name"
