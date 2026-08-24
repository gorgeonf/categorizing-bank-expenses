from pathlib import Path

from pandas.core.interchange.dataframe_protocol import DataFrame

from categorise.group_in_categories import rename_description
from data.categories import ALL_CATEGORIES
from data.clean_description import clean_all_descriptions
from data.date_utils import parse_date, filter_by_date_range, slice_by_period, Period
from data.read_data import read_all_bank_statements
from visualise.data_shaping import (build_transaction_types_dicts, get_account_flows,
                                    AccountFlow,
                                    get_account_flow_type_mask)
from visualise.generate_graphs import (generate_line_graph_account_flows_per_period,
                                       generate_line_graph_account_flows_categories_per_period,
                                       generate_sub_category_line_graph_per_period,
                                       generate_category_line_graph_per_period)


def get_categorise_statements(start_date: str, end_date: str, bank_statement_df: DataFrame):
    start_period = parse_date(start_date)
    end_period = parse_date(end_date)
    if end_period < start_period:
        raise ValueError("End date must be after start date.")
    filtered_bank_statements = filter_by_date_range(start_period, end_period, bank_statement_df)

    cleaned_statements = clean_all_descriptions(filtered_bank_statements)
    return rename_description(cleaned_statements)


def generate_income_sub_categories(sliced_statements: list, category: str) -> list:
    """
    Gets the list of sub categories for a given category
    """
    income_subs = set()
    for df in sliced_statements:
        sub_mask = df['Category'] == category
        income_subs.update(df.loc[sub_mask, 'Sub Category'])
    return sorted(income_subs)


def generate_expenses_categories(sliced_statements: list) -> list:
    """
    Gets the list of categories in Expenses
    """
    expenses_categories = set()
    for df in sliced_statements:
        sub_mask = (df["CAD$"] < 0) & (df["Category"].isin(ALL_CATEGORIES.keys()))
        expenses_categories.update(df.loc[sub_mask, 'Category'])
    return sorted(expenses_categories)


def get_monthly_statements(start_date: str, end_date: str, bank_statement_df: DataFrame):
    categorised_statements = get_categorise_statements(start_date, end_date, bank_statement_df)
    return slice_by_period(categorised_statements, Period.MONTHS)


def get_transaction_types_dict(start_date: str, end_date: str, bank_statement_df: DataFrame):
    categorised_statements = get_categorise_statements(start_date, end_date, bank_statement_df)
    return build_transaction_types_dicts(categorised_statements)


def generate_sub_category_line_graph_per_period_helper(start_date: str, end_date: str, bank_statement_df: DataFrame,
                                                       sub_category: list):
    """

    """
    period_statements = get_monthly_statements(start_date, end_date, bank_statement_df)
    generate_sub_category_line_graph_per_period(period_statements, sub_category)


def generate_category_line_graph_per_period_helper(start_date: str, end_date: str, bank_statement_df: DataFrame,
                                                   category: list):
    """

    """
    period_statements = get_monthly_statements(start_date, end_date, bank_statement_df)
    generate_category_line_graph_per_period(period_statements, category)


def generate_line_graph_account_flows_per_period_helper(start_date, end_date, bank_statement_df, expenses_excluded):
    period_statements = get_monthly_statements(start_date, end_date, bank_statement_df)
    account_flows = get_account_flows(period_statements, expenses_excluded)
    generate_line_graph_account_flows_per_period(period_statements, account_flows)


def generate_line_graph_account_flows_categories_per_period_helper(start_date, end_date, bank_statement_df: DataFrame,
                                                                   account_flow_type: AccountFlow, expenses_excluded):
    period_statements = get_monthly_statements(start_date, end_date, bank_statement_df)
    filtered_period_statements = []
    for statement in period_statements:
        statement_mask = get_account_flow_type_mask(statement, account_flow_type, expenses_excluded)
        filtered_period_statements.append(statement.loc[statement_mask])

    generate_line_graph_account_flows_categories_per_period(filtered_period_statements)


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent.parent
    bank_statement_path = script_dir / "data/bank_statements"

    bank_statement_df = read_all_bank_statements(bank_statement_path)

    start_date = "01/04/2026"
    end_date = "31/10/2026"

    expenses_excluded = {"HOUSE_CLOTHING", "TRAVELS", "VANCOUVER_COMMUNITY_CENTER", "IMMIGRATION_AUSTRALIA"}
    generate_line_graph_account_flows_categories_per_period_helper(start_date, end_date, bank_statement_df,
                                                                   AccountFlow.INCOME, expenses_excluded)
    generate_line_graph_account_flows_per_period_helper(start_date, end_date, bank_statement_df, expenses_excluded)
    # generate_sub_category_line_graph_per_period_helper(start_date, end_date, bank_statement_df,
    #                                                    ["AURELIE YOGACOACHING", "PAYROLL DEPOSIT SERVICE DE GARDE",
    #                                                     "CHEQUE DEPOSIT"])

    # generate_category_line_graph_per_period_helper(start_date, end_date, bank_statement_df,
    #                                                ["COFFEES", "RESTAURANTS", "COSTCO", "IMMIGRATION_AUSTRALIA"])
