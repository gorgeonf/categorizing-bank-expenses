from pathlib import Path

from categorise.group_in_categories import rename_description
from data.clean_description import clean_all_descriptions
from data.date_utils import parse_date, filter_by_date_range, slice_by_period, Period
from data.read_data import read_bank_statements
from visualise.data_shaping import build_transaction_types_dicts
from visualise.generate_graphs import (generate_summary_period_bar_graph,
                                       generate_period_summary_balance_bar_graph,
                                       generate_summary_balance_graph,
                                       generate_summary_bar_graph)


def get_categorise_statements(start_date: str, end_date: str, bank_statement_path: Path):
    start_period = parse_date(start_date)
    end_period = parse_date(end_date)
    bank_statements = filter_by_date_range(start_period, end_period, read_bank_statements(bank_statement_path))

    cleaned_statements = clean_all_descriptions(bank_statements)
    return rename_description(cleaned_statements)

def get_monthly_statements(start_date:str, end_date:str, bank_statement_path:Path):
    categorised_statements = get_categorise_statements(start_date, end_date, bank_statement_path)
    return slice_by_period(categorised_statements, Period.MONTHS)

def get_transacation_types_dict(start_date:str, end_date:str, bank_statement_path:Path):
    categorised_statements = get_categorise_statements(start_date, end_date,bank_statement_path)
    return build_transaction_types_dicts(categorised_statements)


def generate_summary_period_bar_graph_helper(start_date:str, end_date:str, bank_statement_path:Path):
    period_statements = get_monthly_statements(start_date, end_date, bank_statement_path)
    generate_summary_period_bar_graph(period_statements)

def generate_period_summary_balance_bar_graph_helper(start_date:str, end_date:str, bank_statement_path:Path):
    period_statements = get_monthly_statements(start_date, end_date, bank_statement_path)
    generate_period_summary_balance_bar_graph(period_statements)

def generate_summary_balance_pie_graph_helper(start_date:str, end_date:str, bank_statement_path:Path):
    generate_summary_balance_graph(get_categorise_statements(start_date, end_date, bank_statement_path), "pie")

def generate_summary_balance_bar_graph_helper(start_date:str, end_date:str, bank_statement_path:Path):
    generate_summary_balance_graph(get_categorise_statements(start_date, end_date, bank_statement_path), "bar")

def generate_summary_bar_graph_helper(start_date:str, end_date:str, bank_statement_path:Path):
    transaction_dict = get_transacation_types_dict(start_date, end_date, bank_statement_path)
    generate_summary_bar_graph(transaction_dict)


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent.parent
    bank_statement_path = script_dir / "data" / "RBC_download-transactions.csv"

    generate_period_summary_balance_bar_graph_helper("01/04/2026", "01/08/2026", bank_statement_path)
    generate_summary_period_bar_graph_helper("01/04/2026", "01/08/2026", bank_statement_path)
    generate_summary_bar_graph_helper("01/04/2026", "01/08/2026", bank_statement_path)
    generate_summary_balance_pie_graph_helper("01/04/2026", "01/08/2026", bank_statement_path)
    generate_summary_balance_bar_graph_helper("01/04/2026", "01/08/2026", bank_statement_path)

