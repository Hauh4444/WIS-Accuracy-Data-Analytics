"""Database table schema definitions for the stored Accuracy Report data.

- Immutable dataclass mappings for database table and column names.
- All table models are frozen to prevent accidental modification.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class InventoryTable:
    table: str = "tblInventory"
    store_number: str = "StoreNo"
    store_name: str = "StoreName"
    job_datetime: str = "JobDateTime"
    store_address: str = "Address"


@dataclass(frozen=True)
class EmployeeTable:
    table: str = "tblEmps"
    store_number: str = "StoreNo"
    emp_number: str = "EmpNo"
    emp_name: str = "EmpName"
    total_tags: str = "TotalTags"
    total_quantity: str = "TotalQty"
    total_price: str = "TotalEXTPRICE"
    discrepancy_dollars: str = "DiscrepancyDollars"
    discrepancy_tags: str = "DiscrepancyTags"
    hours: str = "Hours"


@dataclass(frozen=True)
class EmployeeTotalsTable:
    # Totals table used for efficiency in retrieving season accuracy statistics
    table: str = "tblEmpTotals"
    emp_number: str = "EmpNo"
    emp_name: str = "EmpName"
    total_tags: str = "TotalTags"
    total_quantity: str = "TotalQty"
    total_price: str = "TotalEXTPRICE"
    discrepancy_dollars: str = "DiscrepancyDollars"
    discrepancy_tags: str = "DiscrepancyTags"
    stores: str = "TotalStores"
    hours: str = "TotalHours"


@dataclass(frozen=True)
class ZoneTable:
    table: str = "tblZones"
    store_number: str = "StoreNo"
    zone_id: str = "ZoneID"
    zone_description: str = "ZoneDesc"
    total_tags: str = "TotalTags"
    total_quantity: str = "TotalQty"
    total_price: str = "TotalEXTPRICE"
    discrepancy_dollars: str = "DiscrepancyDollars"
    discrepancy_tags: str = "DiscrepancyTags"


@dataclass(frozen=True)
class ZoneTotalsTable:
    # Totals table used for efficiency in retrieving season accuracy statistics
    table: str = "tblZoneTotals"
    zone_id: str = "ZoneID"
    zone_description: str = "ZoneDesc"
    total_tags: str = "TotalTags"
    total_quantity: str = "TotalQty"
    total_price: str = "TotalEXTPRICE"
    discrepancy_dollars: str = "DiscrepancyDollars"
    discrepancy_tags: str = "DiscrepancyTags"
    stores: str = "TotalStores"