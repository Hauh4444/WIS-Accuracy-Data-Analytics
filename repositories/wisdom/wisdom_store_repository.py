from repositories.base_repository import BaseRepository


class WisdomStoreRepository(BaseRepository):

    def get_wise_info(self):
        return self._read("""
            SELECT 
                JobDateTime,
                Name,
                Address 
            FROM tblWISEInfo
        """)