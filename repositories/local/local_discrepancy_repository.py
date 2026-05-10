from repositories.base_repository import BaseRepository


class LocalDiscrepancyRepository(BaseRepository):

    def get_discrepancy_data(self, store_number):
        return self._read("""
            SELECT DISTINCT
                EmpNo,
                ZoneID,
                TagNo,
                UPC,
                EXTPRICE,
                OrigQty,
                NewQty,
                DiscrepancyDollars
            FROM tblDiscrepancies
            WHERE StoreNo = ?
        """, [store_number])

    def delete_employee_discrepancies(self, store_number, emp_number):
        self._execute("""
            DELETE FROM tblDiscrepancies
            WHERE StoreNo = ?
              AND EmpNo = ?
        """, [store_number, emp_number])

    def insert_discrepancy_data(self, store_number, emp_number, emp_data):
        query = """
            INSERT INTO tblDiscrepancies (
                StoreNo,
                EmpNo,
                ZoneID,
                TagNo,
                UPC,
                EXTPRICE,
                OrigQty,
                NewQty,
                DiscrepancyDollars
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = [
            [
                store_number,
                emp_number,
                d["ZoneID"],
                d["Tag"],
                d["UPC"],
                d["Price"],
                d["CountedQty"],
                d["NewQty"],
                d["LineError"]
            ]
            for d in emp_data.zone_errors
        ]

        self._executemany(query, params)

    def replace_employee_discrepancies(self, store_number, emp_number, emp_data):
        self.delete_employee_discrepancies(store_number, emp_number)
        if emp_data.zone_errors:
            self.insert_discrepancy_data(store_number, emp_number, emp_data)