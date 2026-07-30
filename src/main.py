from pathlib import Path

from categorise.group_in_categories import rename_description
from data.clean_description import clean_all_descriptions
from data.read_data import read_bank_statements
from visualise.generate_graphs import build_transaction_types_dicts, generate_pie_graph_categories


def run_pipeline(csv_path: Path):
    bank_statements = read_bank_statements(csv_path)
    cleaned_statements = clean_all_descriptions(bank_statements)
    categorized_statements = rename_description(cleaned_statements)
    return categorized_statements


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent
    bank_statement_path = script_dir / "data" / "RBC_download-transactions.csv"

    categorised_statements = run_pipeline(bank_statement_path)
    statement_data = build_transaction_types_dicts(categorised_statements)

    generate_pie_graph_categories(statement_data)