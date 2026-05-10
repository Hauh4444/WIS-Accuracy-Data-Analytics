from typing import List

from domain.dto.zone import Zone


class WisdomZoneService:

    def __init__(self, repo, mapper):
        self.repo = repo
        self.mapper = mapper

    def fetch_zone_data(self) -> List[Zone]:
        df_zone = self.repo.get_zones()
        df_totals = self.repo.get_totals()
        df_zone_errors = self.repo.get_zone_errors()

        return self.mapper.to_zone_models(df_zone, df_totals, df_zone_errors)