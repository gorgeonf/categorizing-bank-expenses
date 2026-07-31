from datetime import datetime
from pathlib import Path

from pandas.core.interchange.dataframe_protocol import DataFrame

from categorise.group_in_categories import rename_description
from data.clean_description import clean_all_descriptions
from data.date_utils import parse_date, filter_by_date_range, slice_by_period, Period
from data.read_data import read_bank_statements
from visualise.data_shaping import build_transaction_types_dicts


def run_pipeline(data_statements: DataFrame, start_date: datetime = None, end_date: datetime = None):
    if not start_date or not end_date:
        start_date, end_date = get_full_date_range(data_statements)
    statement = filter_by_date_range(start_date, end_date, data_statements)

    cleaned_statements = clean_all_descriptions(statement)
    categorized_statements = rename_description(cleaned_statements)
    return categorized_statements


def get_full_date_range(statement: DataFrame) -> tuple:
    return statement['Transaction Date'].min(), statement['Transaction Date'].max()


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent
    bank_statement_path = script_dir / "data" / "RBC_download-transactions.csv"
    raw_statements = read_bank_statements(bank_statement_path)

    selected_start = parse_date("11/04/2026")
    selected_end = parse_date("24/08/2026")

    categorised_statements = run_pipeline(raw_statements, selected_start, selected_end)
    transaction_dicts = build_transaction_types_dicts(categorised_statements)

    period_statements = slice_by_period(categorised_statements, Period.MONTHS)
    for period in period_statements:
        print(f"From {period['Transaction Date'].iloc[0]} to {period['Transaction Date'].iloc[-1]}")
