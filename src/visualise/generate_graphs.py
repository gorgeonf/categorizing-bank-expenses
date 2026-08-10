import numpy as np
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame

from visualise.data_shaping import build_transaction_types_dicts, get_balance_start_end_date_from_timestamps

pd.set_option('display.max_columns', None)
import matplotlib.pyplot as plt


def generate_transaction_types_bar_graph(data: tuple):
    """
        Bar chart showing total $ for each of the 5 transaction types
        (Expenses, Income, Misc, Incoming/Outgoing Transfers).

        :param data: tuple of 5 dicts (expenses, income, misc, incoming_transfers,
            outgoing_transfers), as returned by build_transaction_types_dicts.
        """
    labels = np.array(['Expenses', 'Income', 'Miscellaneous', 'Incoming Transfers', 'Outgoing Transfers'])
    values = np.array([sum(data[0].values()), sum(data[1].values()), sum(data[2].values()), sum(data[3].values()),
                       sum(data[4].values())])

    cmap = plt.get_cmap('viridis')
    colors_categories = [cmap(i / len(labels)) for i in range(len(labels))]

    fig, ax = plt.subplots()
    bars = ax.bar(labels, values, color=colors_categories)
    ax.bar_label(bars, labels=[f"{v:,.2f}$".replace(",", " ") for v in values], padding=3, fontsize=10)
    start_period = sorted(data[-1].keys())[0].strftime("%d %B %Y")
    end_period = sorted(data[-1].keys())[-1].strftime("%d %B %Y")
    plt.title(f"Financial Statement\n"
              f"From {start_period} to {end_period}", fontsize=16, weight='bold', pad=25)
    plt.show()


def generate_transaction_types_bar_graph_per_period(sliced_statements: list):
    """
        Grouped bar chart of the 5 transaction types (expenses, income, misc, incoming_transfers,
        outgoing_transfers) one cluster per period using build_transaction_types_dicts

        :param sliced_statements: list of DataFrames, one per period (e.g. from slice_by_period).
    """
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


def generate_balance_graph(statement: DataFrame, graph_type: str):
    """
        Income vs Expenses comparison, as a pie or bar chart. Net balance is shown
        below the chart, colored red if negative.

        :param statement: DataFrame of transactions to summarize.
        :param graph_type: "pie" or "bar".
    """
    income_mask = statement['CAD$'] > 0
    expenses_mask = statement['CAD$'] < 0

    income = statement.loc[income_mask, 'CAD$'].sum()
    expenses = statement.loc[expenses_mask, 'CAD$'].sum()
    balance = income + expenses

    title = (f"Income vs Expenses\n"
             f"From {statement.iloc[0]['Transaction Date'].strftime('%d %B %Y')} to "
             f"{statement.iloc[-1]['Transaction Date'].strftime('%d %B %Y')}")

    if graph_type == "pie":
        pie_data = {"Income": f"{income:,.2f}$".replace(",", " "),
                    "Expenses": f"{abs(expenses):,.2f}$".replace(",", " ")}

        plt.pie([income, abs(expenses)], labels=[f"Income\n{pie_data['Income']}", f"Expenses\n{pie_data['Expenses']}"],
                autopct='%1.1f%%')
    elif graph_type == "bar":
        fig, ax = plt.subplots()
        labels = ['Income', 'Expenses']
        values = [income, abs(expenses)]
        bars = ax.bar(labels, values, color=['blue', 'red'])
        ax.bar_label(bars, labels=[f"{v:,.2f}$".replace(",", " ") for v in values], padding=3, fontsize=10)
    else:
        raise ValueError("Graph type is not recognised")

    plt.suptitle(title)

    balance_color = 'red' if balance < 0 else 'black'
    plt.figtext(0.5, 0.02, f"Balance: {balance:,.2f}$".replace(",", " "),
                ha='center', fontsize=11, color=balance_color)

    plt.show()


def generate_balance_bar_graph_per_period(sliced_statements: list):
    """
    WARNING: this function was generated by CLAUDE

    Grouped bar chart of Income vs Expenses per period, with each period's
    balance labeled above its cluster (red if negative).

    :param sliced_statements: list of DataFrames, one per period (e.g. from slice_by_period).
    """
    labels = ['Income', 'Expenses']
    colors = ['blue', 'red']

    income_values = []
    expenses_values = []
    balances = []
    xticks = []

    for statement in sliced_statements:
        income_mask = statement['CAD$'] > 0
        expenses_mask = statement['CAD$'] < 0
        income = statement.loc[income_mask, 'CAD$'].sum()
        expenses = statement.loc[expenses_mask, 'CAD$'].sum()

        income_values.append(income)
        expenses_values.append(abs(expenses))
        balances.append(income + expenses)
        xticks.append(statement.iloc[0]['Transaction Date'].strftime('%B - %Y').upper())

    x = np.arange(len(sliced_statements))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.bar(x - width / 2, income_values, width, color=colors[0], label=labels[0])
    ax.bar(x + width / 2, expenses_values, width, color=colors[1], label=labels[1])

    for container in ax.containers:
        ax.bar_label(
            container,
            labels=[f"{v:,.2f}$".replace(",", " ") for v in container.datavalues],
            padding=3,
            fontsize=9,
            weight='bold'
        )

    # Balance label above each cluster, positioned above the taller of the two bars
    for i in range(len(sliced_statements)):
        cluster_max = max(income_values[i], expenses_values[i])
        balance_color = 'red' if balances[i] < 0 else 'green'
        ax.text(
            x[i], cluster_max + (cluster_max * 0.15),
            f"Balance: {balances[i]:,.2f}$".replace(",", " "),
            ha='center', fontsize=9, color=balance_color, weight='bold'
        )

    ax.grid(axis='y', linestyle=':', linewidth=1, color='gray', alpha=0.4)

    for i in range(len(x) - 1):
        midpoint = (x[i] + x[i + 1]) / 2
        ax.axvline(x=midpoint, color='grey', linestyle='-', linewidth=1.2, alpha=0.2)

    ax.set_xticks(x)
    ax.set_xticklabels(xticks)
    ax.tick_params(axis='x', which='both', length=0, pad=10)

    plt.xlabel("Time Period", fontsize=12)
    plt.ylabel("CAD$", fontsize=12)
    plt.margins(y=0.25)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.show()


def generate_pie_chart_helper(data: dict, title: str):
    """
        Renders a single pie chart.

        :param data: dict of {label: value} to plot as slices.
        :param title: chart title.
    """
    plt.figure()
    plt.pie(data.values(), labels=[x + f"\n {str(y)}$" for x, y in data.items()], autopct='%1.1f%%')
    plt.suptitle(title)
    plt.show()


def generate_grouped_bar_graph_per_period(sliced_statements: list, group: list, column: str):
    """
        Grouped bar chart of one or several Category or Sub Category values per period.

        :param sliced_statements: list of DataFrames, one per period (e.g. from slice_by_period).
        :param group: list of values (Category or Sub Category) we want to see on the graph.
        :param column: which column to group by — 'Category' or 'Sub Category'.
    """
    set_sub_category = set(group)
    all_sub_categories = set(pd.concat(sliced_statements, ignore_index=True)[column])
    for sub in set_sub_category:
        if sub not in all_sub_categories:
            raise ValueError(f"{column} {sub} does not exist in the statement.")

    labels = np.array(group)
    y = []
    xticks = []
    for data in sliced_statements:
        xticks.append(data.iloc[0]['Transaction Date'].strftime('%B - %Y').upper())
        tmp_array = []
        for sub in group:
            sub_mask = data[column] == sub
            tmp_array.append(data.loc[sub_mask, 'CAD$'].sum())
        y.append(np.array(tmp_array))

    # Convert y from a list of len(sliced_statements) arrays
    # into a 2D NumPy array of shape ( len(sliced_statements), len(sub_category) )
    y_matrix = np.array(y)

    fig, ax = plt.subplots(figsize=(12, 7))

    width = 0.15
    x = np.arange(len(y))

    cmap = plt.get_cmap('Set3')
    colors_categories = [cmap(i / len(labels)) for i in range(len(labels))]

    # plot data in grouped manner of bar type
    for i in range(len(group)):
        total = y_matrix[:, i].sum()
        label = f"{labels[i]}    Total: {total:,.2f}$".replace(",", " ")
        n = len(group)
        offset = (i - (n - 1) / 2) * width
        ax.bar(x + offset, y_matrix[:, i], width, color=colors_categories[i], label=label)

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
    plt.title(f"{column} Comparison by Period\n"
              f"From {start_period} to {end_period}", fontsize=16, weight='bold', pad=25)
    plt.tight_layout()
    plt.show()


def generate_sub_category_line_graph_per_period(sliced_statements: list, sub_category: list):
    """
    Line chart of one or several sub-categories across periods.

    :param sliced_statements: list of DataFrames, one per period (e.g. from slice_by_period).
    :param sub_category: list of Sub-Category names to plot.
    """
    labels = np.array(sub_category)
    y = []
    xticks = []
    for data in sliced_statements:
        xticks.append(data.iloc[0]['Transaction Date'].strftime('%B - %Y').upper())
        tmp_array = []
        for sub in sub_category:
            sub_mask = data['Sub Category'] == sub
            tmp_array.append(data.loc[sub_mask, 'CAD$'].sum())
        y.append(np.array(tmp_array))

    y_matrix = np.array(y)

    fig, ax = plt.subplots(figsize=(12, 7))

    x = np.arange(len(y))

    cmap = plt.get_cmap('tab10')
    colors_categories = [cmap(i) for i in range(len(labels))]

    for i in range(len(sub_category)):
        total = y_matrix[:, i].sum()
        label = f"{labels[i]}: {total:,.2f}$".replace(",", " ")
        ax.plot(x, y_matrix[:, i], marker='o', color=colors_categories[i], label=label)

        for xi, yi in zip(x, y_matrix[:, i]):
            if yi != 0:
                ax.annotate(f"{yi:,.2f}$".replace(",", " "),
                            (xi, yi), textcoords="offset points", xytext=(0, 8),
                            ha='center', fontsize=8, weight='bold')

    ax.grid(axis='y', linestyle=':', linewidth=1, color='gray', alpha=0.4)

    ax.set_xticks(x)
    ax.set_xticklabels(xticks)
    ax.tick_params(axis='x', which='both', length=0, pad=10)

    plt.xlabel("Time Period", fontsize=12, labelpad=10)
    plt.ylabel("CAD$", fontsize=12)

    plt.margins(y=0.2)
    plt.legend(loc="lower right")
    start_period = sliced_statements[0].iloc[0]['Transaction Date'].strftime("%d %B %Y")
    end_period = sliced_statements[-1].iloc[-1]['Transaction Date'].strftime("%d %B %Y")
    plt.title(f"Sub Category Trend by Period\n"
              f"From {start_period} to {end_period}", fontsize=16, weight='bold', pad=25)
    plt.tight_layout()
    plt.show()


def generate_line_graph_actual_balance_change_per_period(period_statements, balance_df):
    """
        actual_change = end_balance - start_balance
    """
    actual_change = []
    incoming_transfer = []
    outgoing_transfer = []
    income_values = []
    xticks = []

    for statement in period_statements:
        start_date = statement.iloc[0]['Transaction Date']
        end_date = statement.iloc[-1]['Transaction Date']
        balance_start, balance_end = get_balance_start_end_date_from_timestamps(start_date, end_date, balance_df)
        xticks.append(statement.iloc[0]['Transaction Date'].strftime('%B - %Y').upper())
        actual_change.append(balance_end - balance_start)

        # print(f"{statement.iloc[0]['Transaction Date'].strftime('%B - %Y').upper()}")
        # print(f"{balance_end}-{balance_start} = {balance_end - balance_start}\n")

        incoming_mask = (statement['CAD$'] > 0) & (statement['Category'] == "BANKING TRANSFER")
        incoming = statement.loc[incoming_mask, 'CAD$'].sum()
        incoming_transfer.append(incoming)

        outgoing_mask = (statement['CAD$'] < 0) & (statement['Category'] == "BANKING TRANSFER")
        outgoing = statement.loc[outgoing_mask, 'CAD$'].sum()
        outgoing_transfer.append(outgoing)

        income_mask = (statement['CAD$'] > 0) & (statement['Category'] != "BANKING TRANSFER")
        income = statement.loc[income_mask, 'CAD$'].sum()
        income_values.append(income)

    # Convert to a numpy array for consistent array operations
    actual_change = np.array(actual_change)
    incoming_transfer = np.array(incoming_transfer)
    outgoing_transfer = np.array(outgoing_transfer)
    income_values = np.array(income_values)

    x = np.arange(len(actual_change))

    # Initialize the plot
    fig, ax = plt.subplots(figsize=(12, 7))

    # --- LINE 1: ACTUAL BALANCE CHANGE ---
    total_change = actual_change.sum()
    label_change = f"Net Change: {total_change:,.2f}$".replace(",", " ")
    ax.plot(x, actual_change, marker='o', color='blue', linewidth=2.5, label=label_change)

    for xi, yi in zip(x, actual_change):
        if yi != 0:
            ax.annotate(f"{yi:,.2f}$".replace(",", " "),
                        (xi, yi), textcoords="offset points", xytext=(0, 8),
                        ha='center', fontsize=8, weight='bold', color='blue')

    # --- LINE 2: INCOMING TRANSFERS ---
    total_incoming = incoming_transfer.sum()
    label_incoming = f"Incoming Transfers: {total_incoming:,.2f}$".replace(",", " ")
    ax.plot(x, incoming_transfer, marker='s', color='cyan', linewidth=2.5, label=label_incoming)

    for xi, yi in zip(x, incoming_transfer):
        if yi != 0:
            ax.annotate(f"{yi:,.2f}$".replace(",", " "),
                        (xi, yi), textcoords="offset points", xytext=(0, 8),
                        ha='center', fontsize=8, weight='bold', color='cyan')

    # --- LINE 3: OUTGOING TRANSFERS ---
    total_outgoing = outgoing_transfer.sum()
    label_outgoing = f"Outgoing Transfers: {total_outgoing:,.2f}$".replace(",", " ")
    ax.plot(x, outgoing_transfer, marker='s', color='red', linewidth=2.5, label=label_outgoing)

    for xi, yi in zip(x, outgoing_transfer):
        if yi != 0:
            ax.annotate(f"{yi:,.2f}$".replace(",", " "),
                        (xi, yi), textcoords="offset points", xytext=(0, 8),
                        ha='center', fontsize=8, weight='bold', color='red')

    # --- LINE 4: INCOME RECEIVED ---
    total_income = income_values.sum()
    label_income = f"Income received: {total_income:,.2f}$".replace(",", " ")
    ax.plot(x, income_values, marker='s', color='green', linewidth=2.5, label=label_income)

    for xi, yi in zip(x, income_values):
        if yi != 0:
            ax.annotate(f"{yi:,.2f}$".replace(",", " "),
                        (xi, yi), textcoords="offset points", xytext=(0, 8),
                        ha='center', fontsize=8, weight='bold', color='green')

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

    # --- GRAPH FORMATTING ---
    ax.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.3)
    ax.grid(axis='y', linestyle=':', linewidth=1, color='gray', alpha=0.4)

    ax.set_xticks(x)
    ax.set_xticklabels(xticks)
    ax.tick_params(axis='x', which='both', length=0, pad=10)

    plt.xlabel("Time Period", fontsize=12, labelpad=10)
    plt.ylabel("CAD$", fontsize=12)

    plt.margins(y=0.2)
    plt.legend(loc="lower right")

    start_period = period_statements[0].iloc[0]['Transaction Date'].strftime("%d %B %Y")
    end_period = period_statements[-1].iloc[-1]['Transaction Date'].strftime("%d %B %Y")
    plt.title(f"Balance Change vs Other Indicators\n"
              f"From {start_period} to {end_period}", fontsize=16, weight='bold', pad=25)

    plt.tight_layout()
    plt.show()
