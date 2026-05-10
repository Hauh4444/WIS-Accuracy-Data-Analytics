import pandas as pd
from typing import List

from mappers.base_mapper import BaseMapper
from domain.dto.zone import Zone, AggregateZone
from domain.constants.local.required_columns import REQUIRED_LOCAL_ZONE_COLUMNS, REQUIRED_AGGREGATE_ZONE_COLUMNS
from domain.constants.local.rename_map import LOCAL_ZONE_RENAME_MAP, LOCAL_AGGREGATE_ZONE_RENAME_MAP, ZONE_RENAME_MAP, AGGREGATE_ZONE_RENAME_MAP


class LocalZoneMapper(BaseMapper):

    def to_zone_models(self, df: pd.DataFrame) -> List[Zone]:
        df = self._prepare(df, required_columns=REQUIRED_LOCAL_ZONE_COLUMNS, rename_map=LOCAL_ZONE_RENAME_MAP)
        df = self._fill(df, ["ZoneID", "ZoneDesc", "TotalPrice", "TotalTags", "TotalQty", "ZoneErrorTotal", "ZoneErrorTags"], 0)

        df["ZoneErrorPercent"] = df["ZoneErrorTotal"].div(df["TotalPrice"].replace(0, pd.NA)).fillna(0) * 100

        df = df.sort_values("ZoneID", ascending=True)

        return self._map_dataframe(df, Zone, ZONE_RENAME_MAP)

    def to_aggregate_zone_models(self, df: pd.DataFrame) -> List[AggregateZone]:
        df = self._prepare(df, required_columns=REQUIRED_AGGREGATE_ZONE_COLUMNS, rename_map=LOCAL_AGGREGATE_ZONE_RENAME_MAP)
        df = self._fill(df, ["TotalStores"], 0)

        df["ZoneErrorPercent"] = df["ZoneErrorTotal"].div(df["TotalPrice"].replace(0, pd.NA)).fillna(0) * 100

        df = df.sort_values("ZoneID", ascending=True)

        return self._map_dataframe(df, AggregateZone, AGGREGATE_ZONE_RENAME_MAP)