from datetime import datetime
from enum import Enum
from pathlib import Path

import pandas as pd
from pandas import DataFrame

class Period(Enum):
    WEEKS = 1
    MONTHS = 2


def read_bank_statements(file_path: Path) -> DataFrame:
    """
    Reads bank statements from a CSV file and returns a list of dictionaries.

    :param file_path: Path to the CSV file containing bank statements
    :return: List of dictionaries representing bank statements
    """
    # Columns: 'Account Type', 'Account Number', 'Transaction Date', 'Cheque Number', 'Description 1', 'Description 2', 'CAD$', 'USD$'
    bank_statements = pd.read_csv(file_path)

    # 'Description 2' currently empty will serve as working copy, while 'Description 1' will remain untouched
    bank_statements['Description 2'] = bank_statements['Description 1']

    # Convert dates from string to datetimes
    bank_statements['Transaction Date'] = pd.to_datetime(bank_statements['Transaction Date'], format='%m/%d/%Y')

    # Sort data by date to ensure iloc[0] and iloc[-1] are true start/end points
    bank_statements = bank_statements.sort_values('Transaction Date')

    # Only keep 'Transaction Date', 'Description 1', 'Description 2', 'CAD$'
    return bank_statements[['Transaction Date', 'Description 1', 'Description 2', 'CAD$']]


def filter_by_date_range(start_date: str, end_date: str, data_statement: DataFrame) -> DataFrame:
    start = datetime.strptime(start_date, '%d/%m/%Y')
    end = datetime.strptime(end_date, '%d/%m/%Y')
    time_range_mask = (data_statement['Transaction Date'] >= start) & (data_statement['Transaction Date'] <= end)
    return data_statement.loc[time_range_mask]


def slice_by_period(data_statement: DataFrame, period=Period.MONTHS) -> list:
    if data_statement.empty:
        return []

    sliced_statements = []

    if period == Period.MONTHS:
        step = pd.DateOffset(months=1)
    elif period == Period.WEEKS:
        step = pd.DateOffset(weeks=1)
    else:
        raise ValueError("Unsupported period type")

    start = data_statement['Transaction Date'].iloc[0]
    end = data_statement['Transaction Date'].iloc[-1]

    # Init for the loop
    first_date= start
    current_date = start + step

    while current_date < end:
        mask = (data_statement['Transaction Date'] >= first_date) & (data_statement['Transaction Date'] < current_date)
        chunk  =data_statement.loc[mask]
        # ONLY append if the slice actually contains data
        if not chunk.empty:
            sliced_statements.append(chunk)
        first_date = current_date
        current_date += step

    mask = (data_statement['Transaction Date'] >= first_date) & (data_statement['Transaction Date'] <= end)
    chunk = data_statement.loc[mask]
    if not chunk.empty:
        sliced_statements.append(chunk)

    return sliced_statements


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent.parent
    bank_statement_path = script_dir / "data" / "RBC_download-transactions.csv"
    statements = read_bank_statements(bank_statement_path)
    range_statements = filter_by_date_range("01/04/2026", "24/08/2026", statements)
    period_statements = slice_by_period(range_statements, Period.MONTHS)
