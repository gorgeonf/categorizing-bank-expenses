from pathlib import Path

import pandas as pd
from pandas import DataFrame

from data.date_utils import parse_date, filter_by_date_range, slice_by_period

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


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent.parent
    bank_statement_path = script_dir / "data" / "RBC_download-transactions.csv"
    statements = read_bank_statements(bank_statement_path)

