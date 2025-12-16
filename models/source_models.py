"""Database table schema definitions for the WIS inventory system.

- Immutable dataclass mappings for source database table and column names.
- All table models are frozen to prevent accidental modification.
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
    emp_number: str = "TerminalUser"


@dataclass(frozen=True)
class EmpNamesTable:
    table: str = "tblEmpNames"
    emp_number: str = "EmpNo"
    emp_name: str = "Name"


@dataclass(frozen=True)
class DetailsTable:
    """Stores every line counted, required to query since it's the only table that maps employee numbers to tags and lines"""
    table: str = "tblDetails"
    emp_number: str = "empno"
    tag_number: str = "tag"
    upc: str = "sku"
    price: str = "price"
    quantity: str = "qty"


@dataclass(frozen=True)
class DLoadErrorsTable:
    """Stores download errors including merged (duplicate) tags"""
    table: str = "tblDLoadErrors"
    error_msg: str = "ErrorMsg"
    tag_number: str = "tag"


@dataclass(frozen=True)
class ZonesTable:
    table: str = "tblZone"
    zone_id: str = "ZoneID"
    zone_description: str = "ZoneDesc"


@dataclass(frozen=True)
class ZoneChangeQueueTable:
    """Discrepancy queue stores the original counted quantities before corrections. Reason='SERVICE_MISCOUNTED' indicates counting errors blamed on WIS counters."""
    table: str = "tblZoneChangeQueue"
    zone_queue_id: str = "ZoneQueueID"
    zone_id: str = "ZoneID"
    tag_number: str = "Tag"
    upc: str = "UPC"
    price: str = "Price"
    quantity: str = "Quantity"
    reason: str = "Reason"


@dataclass(frozen=True)
class ZoneChangeInfoTable:
    """Stores the corrected quantities after corrections."""
    table: str = "tblZoneChangeInfo"
    zone_queue_id: str = "ZoneQueueID"
    quantity: str = "CountedQty"


@dataclass(frozen=True)
class TagTable:
    table: str = "tblTag"
    tag_number: str = "TagNo"
    total_quantity: str = "TotalQty"
    total_price: str = "TotalEXTPRICE"


@dataclass(frozen=True)
class TagRangeTable:
    table: str = "tblTagRange"
    tag_val_from: str = "TagValFrom"
    tag_val_to: str = "TagValTo"
    total_quantity: str = "TotalQty"
    total_price: str = "TotalEXTPRICE"
    zone_id: str = "ZoneID"