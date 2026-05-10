import pandas as pd
from typing import List

from mappers.base_mapper import BaseMapper
from domain.dto.zone import Zone
from domain.constants.wisdom.required_columns import REQUIRED_WISDOM_ZONE_COLUMNS
from domain.constants.wisdom.rename_map import WISDOM_ZONE_RENAME_MAP


class WisdomZoneMapper(BaseMapper):

    def to_zone_models(self, df_zone: pd.DataFrame, df_totals: pd.DataFrame, df_zone_errors_raw: pd.DataFrame) -> List[Zone]:
        self._validate(df_zone, required_columns=REQUIRED_WISDOM_ZONE_COLUMNS["df_zone"])
        self._validate(df_totals, required_columns=REQUIRED_WISDOM_ZONE_COLUMNS["df_totals"])
        self._validate(df_zone_errors_raw, required_columns=REQUIRED_WISDOM_ZONE_COLUMNS["df_zone_errors_raw"])

        df_totals = df_totals.rename(columns={"TotalQuantity": "TotalQty"})
        df_totals = df_totals.merge(df_zone, on="ZoneID", how="left")

        df_zone_deduped = df_zone_errors_raw.drop_duplicates(subset=['ZoneID', 'Tag', 'UPC', 'LineError'])
        df_zone_summary = df_zone_deduped.groupby("ZoneID").agg(ZoneErrorTotal=("LineError", "sum"), ZoneErrorTags=("Tag", "nunique")).reset_index()

        df_zone_errors = (
            df_zone_deduped.groupby("ZoneID")[['Tag', 'ZoneID', 'UPC', 'Price', 'Quantity', 'CountedQty', 'LineError']]
            .apply(lambda g: g.to_dict('records'))
            .reset_index(name='ZoneErrors')
        )

        df = df_totals.merge(df_zone_summary, on="ZoneID", how="left")
        df = df.merge(df_zone_errors, on="ZoneID", how="left")

        df['ZoneID'] = df['ZoneID'].fillna('')
        df['ZoneDesc'] = df['ZoneDesc'].fillna('')
        df['TotalPrice'] = df['TotalPrice'].fillna(0)
        df['TotalTags'] = df['TotalTags'].fillna(0)
        df['TotalQty'] = df['TotalQty'].fillna(0)
        df['ZoneErrorTotal'] = df['ZoneErrorTotal'].fillna(0)
        df['ZoneErrorTags'] = df['ZoneErrorTags'].fillna(0)
        df['ZoneErrorPercent'] = df['ZoneErrorTotal'].div(df['TotalPrice'].replace(0, pd.NA)).fillna(0) * 100

        df = df.sort_values("ZoneID", ascending=True)

        return self._map_dataframe(df, Zone, WISDOM_ZONE_RENAME_MAP)