from pathlib import Path

import numpy as np
import pandas as pd

from data.date_utils import parse_date, filter_by_date_range, slice_by_period, Period
from visualise.data_shaping import build_transaction_types_dicts, build_sub_category_dicts

pd.set_option('display.max_columns', None)
import matplotlib.pyplot as plt

from data.clean_description import clean_all_descriptions
from categorise.group_in_categories import rename_description
from data.read_data import read_bank_statements


def generate_bar_graph_summary(data: tuple):
    labels = np.array(['Expenses', 'Income', 'Miscellaneous', 'Incoming Transfers', 'Outgoing Transfers'])
    values = np.array([sum(data[0].values()), sum(data[1].values()), sum(data[2].values()), sum(data[3].values()),
                       sum(data[4].values())])

    cmap = plt.get_cmap('viridis')
    colors_categories = [cmap(i / len(labels)) for i in range(len(labels))]

    fig, ax = plt.subplots()
    bars = ax.bar(labels, values, color=colors_categories)
    ax.bar_label(bars, labels=[f"{v:,.2f}$".replace(",", " ") for v in values], padding=3, fontsize=10)
    plt.show()


def generate_period_bar_graph(sliced_statements: list):
    labels = np.array(['Expenses', 'Income', 'Miscellaneous', 'Incoming Transfers', 'Outgoing Transfers'])
    y = []
    xticks = []
    for data in sliced_statements:
        xticks.append(data.iloc[0]['Transaction Date'].strftime('%B - %Y').upper())
        transaction_dicts = build_transaction_types_dicts(data)
        y.append(np.array(
            [sum(transaction_dicts[0].values()), sum(transaction_dicts[1].values()), sum(transaction_dicts[2].values()),
             sum(transaction_dicts[3].values()), sum(transaction_dicts[4].values())]))

    # Convert y from a list of N arrays into a 2D NumPy array of shape (N, 5)
    y_matrix = np.array(y)

    fig, ax = plt.subplots(figsize=(12, 7))

    width = 0.15
    x = np.arange(len(y))

    # plot data in grouped manner of bar type
    ax.bar(x - 2 * width, y_matrix[:, 0], width, color='red', label=labels[0])
    ax.bar(x - width, y_matrix[:, 1], width, color='blue', label=labels[1])
    ax.bar(x, y_matrix[:, 2], width, color='yellow', label=labels[2])
    ax.bar(x + width, y_matrix[:, 3], width, color='cyan', label=labels[3])
    ax.bar(x + 2 * width, y_matrix[:, 4], width, color='orange', label=labels[4])

    for container in ax.containers:
        ax.bar_label(
            container,
            labels=[f"{val:,.2f}".replace(",", " ") + "$" if val != 0 else "" for val in container.datavalues],
            # Formats numbers as flat currency strings
            padding=3,  # Space in points between the top of the bar and the label text
            fontsize=9,  # Adjust text size to keep it neat
            weight='bold'  # Makes the numbers crisp and highly readable
        )

    ax.grid(axis='y', linestyle=':', linewidth=1, color='gray', alpha=0.4)

    # Delimit time period with separation lines
    for i in range(len(x) - 1):
        midpoint = (x[i] + x[i + 1]) / 2
        ax.axvline(
            x=midpoint,
            color='grey',  # Strong color to make boundaries obvious
            linestyle='-',  # Solid line style to distinguish from the dotted grid
            linewidth=1.2,  # Thickness of the separation lines
            alpha=0.2  # Semi-transparent so it stays in the background
        )

    # Basic layout settings
    ax.set_xticks(x)
    ax.set_xticklabels(xticks)
    ax.tick_params(axis='x', which='both', length=0, pad=10)

    plt.xlabel("Time Period", fontsize=12, labelpad=10)
    plt.ylabel("CAD$", fontsize=12)

    plt.margins(y=0.2)
    plt.legend(loc="upper right")
    start_period = sliced_statements[0].iloc[0]['Transaction Date'].strftime("%d %B %Y")
    end_period = sliced_statements[-1].iloc[-1]['Transaction Date'].strftime("%d %B %Y")
    plt.title(f"Financial Statement Summary by Period\n"
              f"From {start_period} to {end_period}", fontsize=16, weight='bold', pad=25)
    plt.tight_layout()
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
    start_date = parse_date("10/04/2026")
    end_date = parse_date("01/08/2026")
    bank_statements = filter_by_date_range(start_date, end_date, read_bank_statements(bank_statement_path))

    cleaned_statements = clean_all_descriptions(bank_statements)
    categorized_statements = rename_description(cleaned_statements)

    build_sub_category_dicts(categorized_statements)


    transaction_dicts = build_transaction_types_dicts(categorized_statements)
    # generate_pie_graph_categories(transaction_dicts)
    # generate_bar_graph_summary(transaction_dicts)
    period_statements = slice_by_period(categorized_statements, Period.MONTHS)
    generate_period_bar_graph(period_statements)
