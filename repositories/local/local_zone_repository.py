from repositories.base_repository import BaseRepository


class LocalZoneRepository(BaseRepository):

    def get_zone_data(self, store_number):
        return self._read("""
            SELECT DISTINCT
                ZoneID,
                ZoneDesc,
                TotalTags,
                TotalQty,
                TotalEXTPRICE,
                DiscrepancyDollars,
                DiscrepancyTags
            FROM tblZones
            WHERE StoreNo = ?
        """, [store_number])

    def get_aggregate_zone_data(self, date_range):
        return self._read("""
            SELECT 
                z.ZoneID,
                MAX(z.ZoneDesc) AS ZoneDescription,
                AVG(z.TotalTags) AS AverageTags,
                AVG(z.TotalQty) AS AverageQty,
                AVG(z.TotalEXTPRICE) AS AveragePrice,
                AVG(z.DiscrepancyDollars) AS AverageZoneErrorTotal,
                AVG(z.DiscrepancyTags) AS AverageZoneErrorTags,
                COUNT(*) as TotalStores
            FROM tblZones AS z
            INNER JOIN tblInventory AS i
                ON z.StoreNo = i.StoreNo
            WHERE i.JobDateTime BETWEEN ? AND ?
            GROUP BY z.ZoneID
        """, [date_range[0], date_range[1]])

    def zone_exists(self, store_number, zone_id):
        return self._exists("""
            SELECT TOP 1 1
            FROM tblZones
            WHERE StoreNo = ?
              AND ZoneID = ?
        """, [store_number, zone_id])

    def insert_zone(self, store_number, zone_data):
        self._execute("""
            INSERT INTO tblZones (
                StoreNo,
                ZoneID,
                ZoneDesc,
                TotalTags,
                TotalQty,
                TotalEXTPRICE,
                DiscrepancyDollars,
                DiscrepancyTags
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            store_number,
            zone_data.zone_id,
            zone_data.zone_desc,
            zone_data.total_tags,
            zone_data.total_qty,
            zone_data.total_price,
            zone_data.zone_error_total,
            zone_data.zone_error_tags
        ])

    def update_zone(self, store_number, zone_data):
        self._execute("""
            UPDATE tblZones
            SET
                ZoneDesc = ?,
                TotalTags = ?,
                TotalQty = ?,
                TotalEXTPRICE = ?,
                DiscrepancyDollars = ?,
                DiscrepancyTags = ?
            WHERE StoreNo = ?
              AND ZoneID = ?
        """, [
            zone_data.zone_desc,
            zone_data.total_tags,
            zone_data.total_qty,
            zone_data.total_price,
            zone_data.zone_error_total,
            zone_data.zone_error_tags,
            store_number,
            zone_data.zone_id
        ])