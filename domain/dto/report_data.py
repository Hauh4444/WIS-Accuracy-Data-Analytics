from dataclasses import dataclass
from typing import List

from domain.dto.employee import Employee, AggregateEmployee
from domain.dto.zone import Zone, AggregateZone
from domain.dto.report_context import StoreReportContext, AggregateReportContext


@dataclass
class StoreReportData:
    context: StoreReportContext
    employees: List[Employee]
    zones: List[Zone]


@dataclass
class AggregateReportData:
    context: AggregateReportContext
    employees: List[AggregateEmployee]
    zones: List[AggregateZone]