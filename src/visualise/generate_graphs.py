from pathlib import Path

import pandas as pd

pd.set_option('display.max_columns', None)
import matplotlib.pyplot as plt
from pandas import DataFrame

from data.clean_description import clean_all_descriptions
from categorise.group_in_categories import rename_description, ALL_CATEGORIES
from data.read_data import read_bank_statements


def sum_categories(statement: DataFrame, categories: set) -> dict:
    dict_expenses = {}
    for category in categories:
        total = statement.loc[statement['Description 2'] == category, 'CAD$'].sum()
        dict_expenses[category] = float(round(total, 2))
    return dict_expenses


def build_category_dicts(statement: DataFrame) -> tuple:
    income_mask = statement['CAD$'] > 0
    expenses_mask = (statement['CAD$'] < 0) & (statement['Description 2'].isin(ALL_CATEGORIES.keys()))
    misc_mask = (statement['CAD$'] < 0) & (~statement['Description 2'].isin(ALL_CATEGORIES.keys())) & (
                statement['Description 2'] != "BANKING TRANSFER")
    internal_transfer_mask = statement['Description 2'] == "BANKING TRANSFER"

    expenses = sum_categories(statement.loc[expenses_mask], ALL_CATEGORIES.keys())
    income = sum_categories(statement.loc[income_mask], set(statement.loc[income_mask]['Description 2']))
    misc = sum_categories(statement.loc[misc_mask], set(statement.loc[misc_mask]['Description 2']))
    internal_transfer = dict(zip(list(statement.loc[internal_transfer_mask]['Transaction Date']),
                                 list(statement.loc[internal_transfer_mask]['CAD$'])))

    return expenses, income, misc, internal_transfer



def generate_bar_graph_categories(data: tuple):
    cmap = plt.get_cmap('viridis')
    colors_categories = [cmap(i / len(ALL_CATEGORIES)) for i in range(len(ALL_CATEGORIES))]

    expenses = data[0]
    income = data[1]
    misc = data[2]
    internal_transfer = data[3]

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(12, 6))
    ax1.bar(expenses.keys(), expenses.values(), color=colors_categories, edgecolor='black')
    ax1.set_title('Expenses')
    ax2.bar(income.keys(), income.values(), color=colors_categories, edgecolor='black')
    ax2.set_title('Income')
    ax3.bar(misc.keys(), misc.values(), color=colors_categories, edgecolor='black')
    ax3.set_title('Miscellaneous')
    ax4.bar(internal_transfer.keys(), internal_transfer.values(), color=colors_categories, edgecolor='black')
    ax4.set_title('Internal Transfers')

    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
    plt.setp(ax4.get_xticklabels(), rotation=45, ha='right')

    plt.show()


def generate_pie_graph_categories(data: tuple):
    expenses = {key: abs(value) for key, value in data[0].items()}
    income = data[1]
    misc = {key: abs(value) for key, value in data[2].items()}
    internal_transfer ={key: abs(value) for key, value in data[3].items()}

    plt.figure()
    plt.pie(expenses.values(), labels=expenses.keys(), autopct='%1.1f%%')
    plt.suptitle('Expenses')
    plt.show()

    plt.figure()
    plt.pie(income.values(), labels=income.keys(), autopct='%1.1f%%')
    plt.suptitle('Income')
    plt.show()

    plt.figure()
    plt.pie(misc.values(), labels=misc.keys(), autopct='%1.1f%%')
    plt.suptitle('Misc')
    plt.show()

    plt.figure()
    plt.pie(internal_transfer.values(), labels=internal_transfer.keys(), autopct='%1.1f%%')
    plt.suptitle('Internal Transfers')
    plt.show()


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent
    bank_statement_path = script_dir / "data" / "RBC_download-transactions.csv"
    bank_statements = read_bank_statements(bank_statement_path)

    cleaned_statements = clean_all_descriptions(bank_statements)
    categorized_statements = rename_description(cleaned_statements)

    statement_data = build_category_dicts(categorized_statements)
    generate_pie_graph_categories(statement_data)
