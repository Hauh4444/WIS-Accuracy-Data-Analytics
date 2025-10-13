"""Database table schema definitions for the WIS inventory system.

Immutable dataclass mappings for database table and column names.
All table models are frozen to prevent accidental modification.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class WISEInfoTable:
    table: str = "tblWISEInfo"
    job_datetime: str = "JobDateTime"
    name: str = "Name"
    address: str = "Address"


@dataclass(frozen=True)
class TerminalControlTable:
    table: str = "tblTerminalControl"
    emp_no: str = "TerminalUser"


@dataclass(frozen=True)
class EmpNamesTable:
    table: str = "tblEmpNames"
    emp_no: str = "EmpNo"
    emp_name: str = "Name"


@dataclass(frozen=True)
class DetailsTable:
    table: str = "tblDetails"
    emp_no: str = "empno"
    tag: str = "tag"


@dataclass(frozen=True)
class ZoneTable:
    table: str = "tblZone"
    zone_id: int = "ZoneID"
    zone_desc: str = "ZoneDesc"


@dataclass(frozen=True)
class ZoneChangeQueueTable:
    """Discrepancy queue. Reason='SERVICE_MISCOUNTED' indicates counting errors attributed to WIS counters."""
    table: str = "tblZoneChangeQueue"
    zone_queue_id: int = "ZoneQueueID"
    zone_id: int = "ZoneID"
    tag: str = "Tag"
    upc: str = "UPC"
    price: float = "Price"
    quantity: int = "Quantity"
    reason: str = "Reason"


@dataclass(frozen=True)
class ZoneChangeInfoTable:
    table: str = "tblZoneChangeInfo"
    zone_queue_id: int = "ZoneQueueID"
    counted_qty: int = "CountedQty"


@dataclass(frozen=True)
class TagTable:
    table: str = "tblTag"
    tag_no: int = "TagNo"
    total_qty: int = "TotalQty"
    total_ext: float = "TotalEXTPRICE"


@dataclass(frozen=True)
class TagRangeTable:
    table: str = "tblTagRange"
    tag_val_from: int = "TagValFrom"
    tag_val_to: int = "TagValTo"
    total_qty: int = "TotalQty"
    total_ext: float = "TotalEXTPRICE"
    zone_id: int = "ZoneID"