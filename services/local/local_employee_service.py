from typing import List

from domain.dto.employee import Employee, AggregateEmployee


class LocalEmployeeService:

    def __init__(self, emp_repo, zone_err_repo, mapper):
        self.emp_repo = emp_repo
        self.zone_err_repo = zone_err_repo
        self.mapper = mapper

    def fetch_employee_data(self, store_number) -> List[Employee]:
        df_emp = self.emp_repo.get_emp_data(store_number)
        df_zone_errors = self.zone_err_repo.get_discrepancy_data(store_number)

        return self.mapper.to_employee_models(df_emp, df_zone_errors)

    def fetch_aggregate_employee_data(self, date_range) -> List[AggregateEmployee]:
        df = self.emp_repo.get_aggregate_emp_data(date_range)

        return self.mapper.to_aggregate_employee_models(df)