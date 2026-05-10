from typing import List

from domain.dto.employee import Employee, AggregateEmployee
from domain.dto.zone import Zone, AggregateZone


class ReportDataService:

    @staticmethod
    def prepare_emp_data(emp_data: List[Employee | AggregateEmployee]):
        for e in emp_data:
            hours = float(e.hours or 0)
            qty = e.total_qty or 0

            e.uph = (qty / hours) if hours > 0 else 0

        return sorted(emp_data, key=lambda x: (-x.uph, -x.total_qty))

    @staticmethod
    def prepare_zone_data(zone_data: List[Zone | AggregateZone]):
        return sorted(zone_data, key=lambda x: int(x.zone_id))