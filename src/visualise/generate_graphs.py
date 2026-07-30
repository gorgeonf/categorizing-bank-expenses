from pathlib import Path

import numpy as np
import pandas as pd

pd.set_option('display.max_columns', None)
import matplotlib.pyplot as plt
from pandas import DataFrame

from data.clean_description import clean_all_descriptions
from categorise.group_in_categories import rename_description, ALL_CATEGORIES
from data.read_data import read_bank_statements, filter_by_date_range


def sum_categories(statement: DataFrame, categories: set) -> dict:
    dict_expenses = {}
    for category in categories:
        total = statement.loc[statement['Description 2'] == category, 'CAD$'].sum()
        dict_expenses[category] = float(round(total, 2))
    return dict_expenses


def build_transaction_types_dicts(statement: DataFrame) -> tuple:
    income_mask = statement['CAD$'] > 0
    expenses_mask = (statement['CAD$'] < 0) & (statement['Description 2'].isin(ALL_CATEGORIES.keys()))
    misc_mask = (statement['CAD$'] < 0) & (~statement['Description 2'].isin(ALL_CATEGORIES.keys())) & (
            statement['Description 2'] != "BANKING TRANSFER")
    internal_transfer_mask = statement['Description 2'] == "BANKING TRANSFER"

    expenses = sum_categories(statement.loc[expenses_mask], set(statement.loc[expenses_mask]['Description 2']))
    income = sum_categories(statement.loc[income_mask], set(statement.loc[income_mask]['Description 2']))
    misc = sum_categories(statement.loc[misc_mask], set(statement.loc[misc_mask]['Description 2']))
    internal_transfer = dict(zip(list(statement.loc[internal_transfer_mask]['Transaction Date']),
                                 list(statement.loc[internal_transfer_mask]['CAD$'])))

    return expenses, income, misc, internal_transfer


def generate_bar_graph_summary(data: tuple):
    incoming_transfers = [x for x in data[3].values() if x > 0]
    outgoing_transfers = [x for x in data[3].values() if x < 0]

    labels = np.array(['Expenses', 'Income', 'Miscellaneous', 'Incoming Transfers', 'Outgoing Transfers'])
    values = np.array([sum(data[0].values()), sum(data[1].values()), sum(data[2].values()), sum(incoming_transfers),
                       sum(outgoing_transfers)])

    cmap = plt.get_cmap('viridis')
    colors_categories = [cmap(i / len(labels)) for i in range(len(labels))]

    fig, ax = plt.subplots()
    bars = ax.bar(labels, values, color=colors_categories)
    ax.bar_label(bars, labels=[f"{v:,.2f}$".replace(",", " ") for v in values], padding=3, fontsize=10)
    plt.show()


def generate_pie_graph_categories(data: tuple):
    expenses = {key: abs(value) for key, value in data[0].items()}
    income = data[1]
    misc = {key: abs(value) for key, value in data[2].items()}

    internal_transfer = {key.strftime('%d %b %Y'): value for key, value in data[3].items()}
    incoming_transfers = {key: value for key, value in internal_transfer.items() if value > 0}
    outgoing_transfers = {key: -value for key, value in internal_transfer.items() if value < 0}

    generate_pie_chart_helper(expenses, f"Expenses: -{sum(expenses.values()):,.2f}$".replace(",", " "))
    generate_pie_chart_helper(income, f"Income: +{sum(income.values()):,.2f}$".replace(",", " "))
    generate_pie_chart_helper(misc, f"Miscellaneous: -{sum(misc.values()):,.2f}$".replace(",", " "))
    generate_pie_chart_helper(incoming_transfers,
                              f"Incoming Transfers: +{sum(incoming_transfers.values()):,.2f}$".replace(",", " "))
    generate_pie_chart_helper(outgoing_transfers,
                              f"Outgoing Transfers: -{sum(outgoing_transfers.values()):,.2f}$".replace(",", " "))


def generate_pie_chart_helper(data: dict, title: str):
    plt.figure()
    plt.pie(data.values(), labels=[x + f"\n {str(y)}$" for x, y in data.items()], autopct='%1.1f%%')
    plt.suptitle(title)
    plt.show()


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent.parent
    bank_statement_path = script_dir / "data" / "RBC_download-transactions.csv"
    bank_statements = filter_by_date_range("01/06/2026", "24/07/2026", read_bank_statements(bank_statement_path))

    cleaned_statements = clean_all_descriptions(bank_statements)
    categorized_statements = rename_description(cleaned_statements)

    statement_data = build_transaction_types_dicts(categorized_statements)
    # generate_pie_graph_categories(statement_data)
    generate_bar_graph_summary(statement_data)
