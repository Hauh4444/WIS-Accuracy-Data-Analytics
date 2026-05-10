from typing import List

from domain.dto.employee import Employee


class WisdomEmployeeService:

    def __init__(self, repo, mapper):
        self.repo = repo
        self.mapper = mapper

    def fetch_employee_data(self) -> List[Employee]:
        df_term = self.repo.get_terminals()
        df_emp = self.repo.get_employees()
        df_details = self.repo.get_details()
        df_zone_errors = self.repo.get_zone_errors()
        df_manual_adjustments = self.repo.get_manual_adjustments()

        return self.mapper.to_employee_models(df_term, df_emp, df_details, df_zone_errors, df_manual_adjustments)