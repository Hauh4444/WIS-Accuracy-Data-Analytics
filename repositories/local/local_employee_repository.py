from repositories.base_repository import BaseRepository


class LocalEmployeeRepository(BaseRepository):

    def get_emp_data(self, store_number):
        return self._read("""
            SELECT DISTINCT
                EmpNo,
                EmpName,
                TotalTags,
                TotalQty,
                TotalEXTPRICE,
                DiscrepancyDollars,
                DiscrepancyTags,
                Hours
            FROM tblEmps
            WHERE StoreNo = ?
        """, [store_number])

    def get_aggregate_emp_data(self, date_range):
        return self._read("""
            SELECT
                e.EmpNo,
                MAX(e.EmpName) AS EmployeeName,
                AVG(e.TotalTags) AS AverageTags,
                AVG(e.TotalQty) AS AverageQty,
                AVG(e.TotalEXTPRICE) AS AveragePrice,
                AVG(e.DiscrepancyDollars) AS AverageZoneErrorTotal,
                AVG(e.DiscrepancyTags) AS AverageZoneErrorTags,
                AVG(e.Hours) AS AverageHours,
                COUNT(*) AS TotalStores
            FROM tblEmps AS e
            INNER JOIN tblInventory AS i
                ON e.StoreNo = i.StoreNo
            WHERE i.JobDateTime BETWEEN ? AND ?
            GROUP BY e.EmpNo
        """, [date_range[0], date_range[1]])

    def employee_exists(self, store_number, emp_number):
        return self._exists("""
            SELECT TOP 1 1
            FROM tblEmps
            WHERE StoreNo = ?
              AND EmpNo = ?
        """, [store_number, emp_number])

    def insert_employee(self, store_number, emp_data):
        self._execute("""
            INSERT INTO tblEmps (
                StoreNo,
                EmpNo,
                EmpName,
                TotalTags,
                TotalQty,
                TotalEXTPRICE,
                DiscrepancyDollars,
                DiscrepancyTags,
                Hours
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            store_number,
            emp_data.emp_id,
            emp_data.emp_name,
            emp_data.total_tags,
            emp_data.total_qty,
            emp_data.total_price,
            emp_data.zone_error_total,
            emp_data.zone_error_tags,
            emp_data.hours
        ])

    def update_employee(self, store_number, emp_data):
        self._execute("""
            UPDATE tblEmps
            SET
                TotalTags = ?,
                TotalQty = ?,
                TotalEXTPRICE = ?,
                DiscrepancyDollars = ?,
                DiscrepancyTags = ?,
                Hours = ?
            WHERE StoreNo = ?
              AND EmpNo = ?
        """, [
            emp_data.total_tags,
            emp_data.total_qty,
            emp_data.total_price,
            emp_data.zone_error_total,
            emp_data.zone_error_tags,
            emp_data.hours,
            store_number,
            emp_data.emp_id
        ])