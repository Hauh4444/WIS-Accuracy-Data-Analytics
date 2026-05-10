import pandas as pd
from typing import List

from mappers.base_mapper import BaseMapper
from domain.dto.employee import Employee
from domain.constants.wisdom.required_columns import REQUIRED_WISDOM_EMP_COLUMNS
from domain.constants.wisdom.rename_map import WISDOM_EMP_RENAME_MAP


class WisdomEmployeeMapper(BaseMapper):

    def to_employee_models(self, df_term, df_emp, df_details, df_zone_errors_raw, df_manual_adjustments_raw) -> List[Employee]:
        self._validate(df_term, required_columns=REQUIRED_WISDOM_EMP_COLUMNS["df_term"])
        self._validate(df_emp, required_columns=REQUIRED_WISDOM_EMP_COLUMNS["df_emp"])
        self._validate(df_details, required_columns=REQUIRED_WISDOM_EMP_COLUMNS["df_details"])
        self._validate(df_zone_errors_raw, required_columns=REQUIRED_WISDOM_EMP_COLUMNS["df_zone_errors_raw"])
        self._validate(df_manual_adjustments_raw, required_columns=REQUIRED_WISDOM_EMP_COLUMNS["df_manual_adjustments_raw"])

        df_details_summary = df_details.groupby('empno').apply(
            lambda g: pd.Series({
                "TotalPrice": (g["price"] * g["qty"]).sum(),
                "TotalTags": g["tag"].nunique(),
                "TotalQty": g["qty"].sum()
            })
        ).reset_index()

        df_emp_zone_errors = df_zone_errors_raw.merge(
            df_details[df_details['empno'] != 'ZZ9999'][['tag', 'empno']].rename(columns={'tag': 'Tag', 'empno': 'TerminalUser'}),
            on='Tag',
            how='inner'
        )
        df_emp_zone_deduped = df_emp_zone_errors.drop_duplicates(subset=['TerminalUser', 'Tag', 'UPC', 'LineError'])
        df_emp_zone_summary = df_emp_zone_deduped.groupby('TerminalUser').agg(ZoneErrorTotal=('LineError', 'sum'), ZoneErrorTags=('Tag', 'nunique')).reset_index()
        df_emp_zone_errors_list = df_emp_zone_deduped.groupby('TerminalUser').apply(
            lambda x: x[['Tag', 'ZoneID', 'UPC', 'Price', 'Quantity', 'CountedQty', 'LineError']]
            .rename(columns={'Quantity': 'NewQty'})
            .to_dict('records')
        ).reset_index(name='ZoneErrors')

        df_emp_manual_adjustments = df_manual_adjustments_raw.merge(
            df_details[df_details['empno'] != 'ZZ9999'][['tag', 'empno']].rename(columns={'tag': 'Tag', 'empno': 'TerminalUser'}),
            on='Tag',
            how='inner'
        )
        df_emp_manual_deduped = df_emp_manual_adjustments.drop_duplicates(subset=['TerminalUser', 'Tag', 'UPC', 'LineError'])
        df_emp_manual_summary = df_emp_manual_deduped.groupby('TerminalUser').agg(ManualAdjustmentTotal=('LineError', 'sum'), ManualAdjustmentTags=('Tag', 'nunique')).reset_index()
        df_emp_manual_list = df_emp_manual_deduped.groupby('TerminalUser').apply(
            lambda x: x[['Tag', 'ZoneID', 'UPC', 'Price', 'Quantity', 'CountedQty', 'LineError']]
            .rename(columns={'Quantity': 'NewQty'})
            .to_dict('records')
        ).reset_index(name='ManualAdjustments')

        df_combined_error_tags = pd.concat([df_emp_zone_deduped[['TerminalUser', 'Tag']], df_emp_manual_deduped[['TerminalUser', 'Tag']]])
        df_combined_error_summary = (
            df_combined_error_tags
            .drop_duplicates(subset=['TerminalUser', 'Tag'])
            .groupby('TerminalUser')
            .agg(TotalErrorTags=('Tag', 'nunique'))
            .reset_index()
        )

        df = df_term.merge(df_emp, left_on='TerminalUser', right_on='EmpNo', how='inner')
        df = df.merge(df_details_summary, left_on='TerminalUser', right_on='empno', how='left').drop(columns=['empno'])
        df = df.merge(df_emp_zone_summary, on='TerminalUser', how='left')
        df = df.merge(df_emp_zone_errors_list, on='TerminalUser', how='left')
        df = df.merge(df_emp_manual_summary, on='TerminalUser', how='left')
        df = df.merge(df_emp_manual_list, on='TerminalUser', how='left')
        df = df.merge(df_combined_error_summary, on='TerminalUser', how='left')

        df['TerminalUser'] = df['TerminalUser'].fillna('')
        df['Name'] = df['Name'].fillna('')
        df['TotalPrice'] = df['TotalPrice'].fillna(0)
        df['TotalTags'] = df['TotalTags'].fillna(0)
        df['TotalQty'] = df['TotalQty'].fillna(0)
        df['ZoneErrorTotal'] = df['ZoneErrorTotal'].fillna(0)
        df['ZoneErrorTags'] = df['ZoneErrorTags'].fillna(0)
        df['ZoneErrorPercent'] = df['ZoneErrorTotal'].div(df['TotalPrice'].replace(0, pd.NA)).fillna(0) * 100
        df['ZoneErrors'] = df['ZoneErrors'].apply(lambda x: x if isinstance(x, list) else [])
        df['ManualAdjustmentTotal'] = df['ManualAdjustmentTotal'].fillna(0)
        df['ManualAdjustmentTags'] = df['ManualAdjustmentTags'].fillna(0)
        df['ManualAdjustmentPercent'] = df['ManualAdjustmentTotal'].div(df['TotalPrice'].replace(0, pd.NA)).fillna(0) * 100
        df['ManualAdjustments'] = df['ManualAdjustments'].apply(lambda x: x if isinstance(x, list) else [])
        df['TotalErrorTags'] = df['TotalErrorTags'].fillna(0)

        df = df.sort_values(["UPH", "TotalQty"], ascending=[False, False])

        return self._map_dataframe(df, Employee, WISDOM_EMP_RENAME_MAP)