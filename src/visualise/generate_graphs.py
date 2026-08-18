import numpy as np
import pandas as pd
from matplotlib.widgets import CheckButtons
from pandas.core.interchange.dataframe_protocol import DataFrame

from visualise.data_shaping import build_transaction_types_dicts

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


def generate_line_graph_account_flows_per_period(period_statements, account_flows):
    """
    Interactive line chart comparing Income, Transfers from Savings, Expenses,
    Savings/Investments, and Net Change across periods, with toggleable lines
    via checkboxes.

    :param period_statements: list of DataFrames, one per period (e.g. from slice_by_period).
    :param account_flows: list of label, DataFrame, color and marker for the account flows:
        income, transfers_from_savings, expenses, essential_expenses, savings_investments, net_change
    """
    x_ticks = [statement.iloc[0]['Transaction Date'].strftime('%B - %Y').upper() for statement in period_statements]
    x_coord = np.arange(len(account_flows[0][1]))

    # Initialize the plot
    fig = plt.figure(figsize=(14, 7))
    n = len(account_flows)
    gs = fig.add_gridspec(2, 2, width_ratios=[3, 2], height_ratios=[n, 1])

    ax = fig.add_subplot(gs[:, 0])  # graph takes the full left column
    rax = fig.add_subplot(gs[0, 1])  # checkboxes: top-right
    box_ax = fig.add_subplot(gs[1, 1])  # info box: bottom-right
    box_ax.axis('off')  # no ticks/frame, just a text area

    # Maps each flow's name (e.g. "INCOME") to its Line2D object,
    # so toggle_line can look up and show/hide the correct line when its checkbox is clicked.
    lines = {}

    # Maps each flow's name to its annotation (the $ value text shown at non-zero points).
    # Not every flow has one — a flow with all-zero values across every period never gets an entry here,
    # so toggle_line checks membership before accessing it.
    annotations = {}

    flow_totals = []
    for flow in account_flows:
        # Convert to a numpy array for consistent array operations
        flow_array = np.array(flow[1])

        total_flow = flow_array.sum()
        label_flow = f"{flow[0]}: {total_flow:,.2f}$".replace(",", " ")
        line_flow = ax.plot(x_coord, flow_array, marker=flow[3], markersize=4, color=flow[2], linewidth=1.5,
                            ls='solid', label=label_flow)
        lines[flow[0]] = line_flow[0]
        flow_totals.append((flow[0], line_flow[0], total_flow))

        annotations[flow[0]] = []
        for xi, yi in zip(x_coord, flow_array):
            if yi != 0:
                ann = ax.annotate(f"{yi:,.2f}$".replace(",", " "),
                                  (xi, yi), textcoords="offset points", xytext=(0, 8),
                                  ha='center', fontsize=8, weight='bold', color=flow[2])
                annotations[flow[0]].append(ann)

    colors = [flow[2] for flow in account_flows]

    check = CheckButtons(
        rax,
        list(lines.keys()),
        [True for _ in account_flows],
        label_props={'fontsize': [10] * len(account_flows), 'color': colors},  # Text size and colors
        frame_props={'edgecolor': 'gray', 's': 100},  # checkbox frame (size 's', edge color)
        check_props={'facecolor': colors},  # checkmark color per item
    )

    def toggle_line(label):
        line = lines[label]
        line.set_visible(not line.get_visible())
        for ann in annotations.get(label, []):
            ann.set_visible(not ann.get_visible())
        fig.canvas.draw_idle()

    check.on_clicked(toggle_line)

    # Delimit time period with separation lines
    for i in range(len(x_coord) - 1):
        midpoint = (x_coord[i] + x_coord[i + 1]) / 2
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

    ax.set_xticks(x_coord)
    ax.set_xticklabels(x_ticks)
    ax.tick_params(axis='x', which='both', length=0, pad=10)

    ax.set_xlabel("Time Period", fontsize=12, labelpad=10)
    ax.set_ylabel("CAD$", fontsize=12)

    plt.margins(y=0.2)

    # To sort the legend by the highest CAD$
    flow_totals_sorted = sorted(flow_totals, key=lambda x: x[2], reverse=False)
    sorted_handles = [item[1] for item in flow_totals_sorted]
    # Display the legend in a second, standalone window
    legend_fig = plt.figure(figsize=(4, len(account_flows) * 0.3))
    legend_fig.legend(handles=sorted_handles, loc='center')

    start_period = period_statements[0].iloc[0]['Transaction Date'].strftime("%d %B %Y")
    end_period = period_statements[-1].iloc[-1]['Transaction Date'].strftime("%d %B %Y")
    ax.set_title(f"Checking account transactions\n"
                 f"From {start_period} to {end_period}", fontsize=16, weight='bold', pad=25)
    plt.tight_layout()
    plt.show()


def generate_line_graph_account_flows_categories_per_period(period_statements):
    set_categories = set()
    for df in period_statements:
        tmp_set = set(list(df['Category']))
        set_categories = set_categories.union(tmp_set)

    account_flows = []
    import random
    import colorsys
    for category in set_categories:
        df_totals = []
        for df in period_statements:
            df_totals.append(df.loc[df['Category'] == category, 'CAD$'].sum())
        color = colorsys.hsv_to_rgb(
            random.random(),  # hue
            0.7,  # saturation
            0.7  # brightness
        )
        account_flows.append((category, df_totals, color, 'o'))

    generate_line_graph_account_flows_per_period(period_statements, account_flows)