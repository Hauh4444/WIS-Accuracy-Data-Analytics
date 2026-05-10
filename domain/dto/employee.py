from dataclasses import dataclass
from typing import Any, Optional


@dataclass(kw_only=True)
class Employee:
    emp_id: str
    emp_name: str
    total_price: float
    total_tags: int
    total_qty: int
    zone_error_total: float
    zone_error_tags: int
    zone_error_percent: float
    zone_errors: list[Any]
    hours: float | None = None
    uph: float | None = None


@dataclass(kw_only=True)
class AggregateEmployee(Employee):
    total_stores: int