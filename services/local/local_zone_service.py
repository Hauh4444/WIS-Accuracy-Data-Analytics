from typing import List

from domain.dto.zone import Zone, AggregateZone


class LocalZoneService:

    def __init__(self, repo, mapper):
        self.repo = repo
        self.mapper = mapper

    def fetch_zone_data(self, store_number) -> List[Zone]:
        df = self.repo.get_zone_data(store_number)

        return self.mapper.to_zone_models(df)

    def fetch_aggregate_zone_data(self, date_range) -> List[AggregateZone]:
        df = self.repo.get_aggregate_zone_data(date_range)

        return self.mapper.to_aggregate_zone_models(df)