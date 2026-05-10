from repositories.base_repository import BaseRepository


class WisdomEmployeeRepository(BaseRepository):

    def get_terminals(self):
        return self._read("""
            SELECT DISTINCT 
                TerminalUser 
            FROM tblTerminalControl 
            WHERE TerminalUser <> 'ZZ9999'
        """)

    def get_employees(self):
        return self._read("""
            SELECT 
                EmpNo, 
                Name 
            FROM tblEmpNames
        """)

    def get_details(self):
        return self._read("""
            SELECT 
                tag, 
                empno, 
                price, 
                qty
            FROM tblDetails
            WHERE empno <> 'ZZ9999'
        """)

    def get_zone_errors(self):
        return self._read("""
            SELECT
                zcq.Tag,
                zcq.ZoneID,
                zcq.UPC,
                zcq.Price,
                zcq.Quantity,
                zci.CountedQty,
                ABS(zcq.Price * (zci.CountedQty - zcq.Quantity)) AS LineError
            FROM tblZoneChangeQueue AS zcq
            INNER JOIN tblZoneChangeInfo AS zci
                ON zcq.ZoneQueueID = zci.ZoneQueueID
            WHERE
                zcq.Reason = 'SERVICE_MISCOUNTED'
                AND ABS(zcq.Price * (zci.CountedQty - zcq.Quantity)) > 50
        """)

    def get_manual_adjustments(self):
        return self._read("""
            SELECT
                t.tag AS Tag,
                d.ZoneID,
                t.sku AS UPC,
                t.price AS Price,
                t.qty AS Quantity,
                d.qty AS CountedQty,
                ABS(t.price * (d.qty - t.qty)) AS LineError
            FROM tblDetailsEdit AS t
            INNER JOIN tblDetailsOrg AS d
                ON t.DetailsID = d.DetailsID
            WHERE t.Errors = 6
                AND t.tag NOT IN (3999, 9999, 9996, 1999, 8500)
                AND t.AdjustmentTypeID = 3
                AND t.EditID = (
                    SELECT MAX(t2.EditID)
                    FROM tblDetailsEdit AS t2
                    WHERE t2.DetailsID = t.DetailsID
                        AND t2.Errors = 6
                        AND t2.tag NOT IN (3999, 9999, 9996, 1999, 8500)
                        AND t2.AdjustmentTypeID = 3
                )
        """)