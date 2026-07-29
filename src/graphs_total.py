from pathlib import Path

import pandas as pd

pd.set_option('display.max_columns', None)
import matplotlib.pyplot as plt
from pandas import DataFrame

from clean_description import clean_all_descriptions
from group_in_categories import rename_description, ALL_CATEGORIES
from read_data import read_bank_statements


def sum_categories(statement: DataFrame, categories: set) -> dict:
    dict_expenses = {}
    for category in categories:
        total = statement.loc[statement['Description 2'] == category, 'CAD$'].sum()
        dict_expenses[category] = float(round(total, 2))
    return dict_expenses


def generate_bar_graph_categories(statement: DataFrame):
    cmap = plt.get_cmap('viridis')
    colors_categories = [cmap(i / len(ALL_CATEGORIES)) for i in range(len(ALL_CATEGORIES))]

    income_mask = statement['CAD$'] > 0
    expenses_mask = (statement['CAD$'] < 0) & (statement['Description 2'].isin(ALL_CATEGORIES.keys()))
    misc_mask = (statement['CAD$'] < 0) & (~statement['Description 2'].isin(ALL_CATEGORIES.keys()))

    expenses = sum_categories(statement.loc[expenses_mask], ALL_CATEGORIES.keys())
    income = sum_categories(statement.loc[income_mask], set(statement.loc[income_mask]['Description 2']))
    misc = sum_categories(statement.loc[misc_mask], set(statement.loc[misc_mask]['Description 2']))

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 6))
    ax1.bar(expenses.keys(), expenses.values(), color=colors_categories, edgecolor='black')
    ax1.set_title('Expenses')
    ax2.bar(income.keys(), income.values(), color=colors_categories, edgecolor='black')
    ax2.set_title('Income')
    ax3.bar(misc.keys(), misc.values(), color=colors_categories, edgecolor='black')
    ax3.set_title('Miscellaneous')

    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')

    plt.show()


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent
    bank_statement_path = script_dir / "data" / "RBC_download-transactions.csv"
    bank_statements = read_bank_statements(bank_statement_path)

    cleaned_statements = clean_all_descriptions(bank_statements)
    categorized_statements = rename_description(cleaned_statements)

    generate_bar_graph_categories(categorized_statements)
