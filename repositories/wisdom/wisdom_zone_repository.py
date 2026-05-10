from repositories.base_repository import BaseRepository


class WisdomZoneRepository(BaseRepository):

    def get_zones(self):
        return self._read("""
            SELECT DISTINCT
                ZoneID,
                ZoneDesc
            FROM tblZone
        """)

    def get_totals(self):
        return self._read("""
            SELECT 
                ZoneID,
                SUM(TagValTo - TagValFrom + 1) AS TotalTags,
                SUM(TotalEXTPRICE) AS TotalPrice,
                SUM(TotalQty) AS TotalQuantity
            FROM tblTagRange
            GROUP BY ZoneID
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