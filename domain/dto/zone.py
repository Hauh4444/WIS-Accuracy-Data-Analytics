from dataclasses import dataclass


@dataclass
class Zone:
    zone_id: str
    zone_desc: str
    total_tags: int
    total_price: float
    total_qty: int
    zone_error_total: float
    zone_error_tags: int
    zone_error_percent: float


@dataclass
class AggregateZone(Zone):
    total_stores: int