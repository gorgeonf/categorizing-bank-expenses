import argparse

from pathlib import Path

from data.categories import DEFAULT_SUB_CATEGORIES, resolve_sub_categories
from data.read_data import read_all_bank_statements
from visualise.data_shaping import AccountFlow
from visualise.generate_graphs_helper import generate_line_graph_account_flows_per_period_helper, \
    generate_sub_category_line_graph_per_period_helper, generate_line_graph_account_flows_categories_per_period_helper

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("--start", "-s", required=True)
    parser.add_argument("--end", "-e", required=True)

    parser.add_argument("--sub_categories",
                        nargs="*",
                        default=None,
                        required=False)

    parser.add_argument("--category",
                        default=AccountFlow.EXPENSES,
                        required=False)

    args = parser.parse_args()

    sub_categories = (
        resolve_sub_categories(args.sub_categories)
        if args.sub_categories
        else DEFAULT_SUB_CATEGORIES
    )

    script_dir = Path(__file__).resolve().parent.parent
    bank_statement_path = script_dir / "data/bank_statements"

    bank_statement_df = read_all_bank_statements(bank_statement_path)

    if args.command == "graph":
        generate_line_graph_account_flows_per_period_helper(
            args.start,
            args.end,
            bank_statement_df
        )
    elif args.command == "category":
        args.category = AccountFlow(args.category.upper())
        generate_line_graph_account_flows_categories_per_period_helper(
            args.start,
            args.end,
            bank_statement_df,
            args.category
        )
    elif args.command == "sub_categories":
        generate_sub_category_line_graph_per_period_helper(
            args.start,
            args.end,
            bank_statement_df,
            sub_categories
        )
