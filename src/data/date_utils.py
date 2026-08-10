from datetime import datetime
from enum import Enum

import pandas as pd
from pandas import DataFrame


class Period(Enum):
    WEEKS = 1
    MONTHS = 2


def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, '%d/%m/%Y')


def filter_by_date_range(start_date: datetime, end_date: datetime, data_statement: DataFrame) -> DataFrame:
    time_range_mask = (data_statement['Transaction Date'] >= start_date) & (
            data_statement['Transaction Date'] <= end_date)
    return data_statement.loc[time_range_mask]


def slice_by_period(data_statement: DataFrame, period=Period.MONTHS) -> list:
    if data_statement.empty:
        return []

    period_statements = []

    if period == Period.MONTHS:
        step = pd.offsets.MonthBegin()
    elif period == Period.WEEKS:
        step = pd.offsets.Week(weekday=0)
    else:
        raise ValueError("Unsupported period type")

    start = data_statement['Transaction Date'].iloc[0]
    end = data_statement['Transaction Date'].iloc[-1]

    # Init for the loop
    first_date = start
    current_date = start + step

    while current_date < end:
        mask = (data_statement['Transaction Date'] >= first_date) & (data_statement['Transaction Date'] < current_date)
        chunk = data_statement.loc[mask]
        if not chunk.empty:
            period_statements.append(chunk)
        first_date = current_date
        current_date += step

    mask = (data_statement['Transaction Date'] >= first_date) & (data_statement['Transaction Date'] <= end)
    chunk = data_statement.loc[mask]
    if not chunk.empty:
        period_statements.append(chunk)

    return period_statements
