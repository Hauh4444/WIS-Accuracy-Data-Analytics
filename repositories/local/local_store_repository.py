from repositories.base_repository import BaseRepository


class LocalStoreRepository(BaseRepository):

    def get_store_info(self, store_number):
        return self._read("""
            SELECT 
                JobDateTime,
                StoreName, 
                Address
            FROM tblInventory
            WHERE StoreNo = ?
        """, [store_number])

    def store_exists(self, store_number):
        return self._exists("""
            SELECT TOP 1 1
            FROM tblInventory
            WHERE StoreNo = ?
        """, [store_number])

    def insert_store(self, store_number, store_data):
        self._execute("""
            INSERT INTO tblInventory (
                StoreNo,
                StoreName,
                JobDateTime,
                Address
            )
            VALUES (?, ?, ?, ?)
        """, [
            store_number,
            store_data.store_name,
            store_data.job_datetime,
            store_data.store_address
        ])

    def update_store(self, store_number, store_data):
        self._execute("""
            UPDATE tblInventory
            SET
                StoreName = ?,
                JobDateTime = ?,
                Address = ?
            WHERE StoreNo = ?
        """, [
            store_data.store_name,
            store_data.job_datetime,
            store_data.store_address,
            store_number
        ])