from dataclasses import dataclass


@dataclass(frozen=True)
class WISEInfoTable:
    table: str = "tblWISEInfo"
    job_datetime: str = "JobDateTime"
    name: str = "Name"
    address: str = "Address"


@dataclass(frozen=True)
class UPHTable:
    table: str = "tblUPH"
    emp_no: str = "EmpNo"
    emp_name: str = "EmpName"
    tag_count: int = "TagCount"


@dataclass(frozen=True)
class DetailsTable:
    table: str = "tblDetailsOrg"
    emp_no: str = "empno"
    tag: str = "tag"


@dataclass(frozen=True)
class ZoneTable:
    table: str = "tblZone"
    zone_id: int = "ZoneID"
    zone_desc: str = "ZoneDesc"


@dataclass(frozen=True)
class ZoneChangeQueueTable:
    table: str = "tblZoneChangeQueue"
    zone_queue_id: int = "ZoneQueueID"
    zone_id: int = "ZoneID"
    tag: str = "Tag"
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