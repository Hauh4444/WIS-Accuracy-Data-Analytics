from domain.dto.report_data import StoreReportData


class LocalDataSaveService:

    def __init__(self, store_repo, emp_repo, zone_repo, disc_repo, schema_repo):
        self.store_repo = store_repo
        self.emp_repo = emp_repo
        self.zone_repo = zone_repo
        self.disc_repo = disc_repo
        self.schema_repo = schema_repo

    def save_all(self, report_data: StoreReportData):
        store_number = report_data.context.store_name.strip().split()[-1]

        self.schema_repo.create_tables_if_not_exists()

        if self.store_repo.store_exists(store_number):
            is_update = True

        else:
            self.store_repo.insert_store(store_number, report_data.context)
            is_update = False

        for emp in report_data.employees:
            if is_update:
                self.emp_repo.update_employee(store_number, emp)

            else:
                self.emp_repo.insert_employee(store_number, emp)

            self.disc_repo.replace_employee_discrepancies(store_number, emp.emp_id, emp)

        for zone in report_data.zones:
            if is_update:
                self.zone_repo.update_zone(store_number, zone)

            else:
                self.zone_repo.insert_zone(store_number, zone)