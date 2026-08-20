import numpy as np
import pandas as pd
from matplotlib.widgets import CheckButtons

from visualise.data_shaping import AccountFlow

pd.set_option('display.max_columns', None)
import matplotlib.pyplot as plt


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
    # plt.legend(loc="lower right")

    # Display the legend in a second, standalone window
    legend_fig = plt.figure(figsize=(4, len(labels) * 0.3))
    handles, labels = ax.get_legend_handles_labels()
    legend_fig.legend(handles, labels, loc='center')

    start_period = sliced_statements[0].iloc[0]['Transaction Date'].strftime("%d %B %Y")
    end_period = sliced_statements[-1].iloc[-1]['Transaction Date'].strftime("%d %B %Y")
    ax.set_title(
        f"Sub Category Trend by Period\n"
        f"From {start_period} to {end_period}",
        fontsize=16,
        weight='bold',
        pad=25
    )
    plt.tight_layout()
    plt.show()


def generate_category_line_graph_per_period(sliced_statements: list, category: list):
    """
    Line chart of one or several sub-categories across periods.

    :param sliced_statements: list of DataFrames, one per period (e.g. from slice_by_period).
    :param category: list of ategory names to plot.
    """
    labels = np.array(category)
    y = []
    xticks = []
    for data in sliced_statements:
        xticks.append(data.iloc[0]['Transaction Date'].strftime('%B - %Y').upper())
        tmp_array = []
        for sub in category:
            sub_mask = data['Category'] == sub
            tmp_array.append(data.loc[sub_mask, 'CAD$'].sum())
        y.append(np.array(tmp_array))

    y_matrix = np.array(y)

    fig, ax = plt.subplots(figsize=(12, 7))

    x = np.arange(len(y))

    cmap = plt.get_cmap('tab10')
    colors_categories = [cmap(i) for i in range(len(labels))]

    for i in range(len(category)):
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
    # plt.legend(loc="lower right")

    # Display the legend in a second, standalone window
    legend_fig = plt.figure(figsize=(4, len(labels) * 0.3))
    handles, labels = ax.get_legend_handles_labels()
    legend_fig.legend(handles, labels, loc='center')

    start_period = sliced_statements[0].iloc[0]['Transaction Date'].strftime("%d %B %Y")
    end_period = sliced_statements[-1].iloc[-1]['Transaction Date'].strftime("%d %B %Y")
    ax.set_title(
        f"Category Trend by Period\n"
        f"From {start_period} to {end_period}",
        fontsize=16,
        weight='bold',
        pad=25
    )
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

    # To sort the legend by the highest CAD$ and put NET CHANGE at the end
    net_change = ()
    for type in flow_totals:
        if AccountFlow.NET_CHANGE.value in type:
            flow_totals.remove(type)
            net_change = type
            break
    flow_totals_sorted = sorted(flow_totals, key=lambda x: x[2], reverse=False)
    sorted_handles = [item[1] for item in flow_totals_sorted]
    # Add a space before NET CHANGE and a description
    if net_change:
        import matplotlib.patches as mpatches
        spacer_handle = mpatches.Rectangle((0, 0), 1, 1, fill=False, edgecolor='none', linewidth=0, label='')
        formula_handle = mpatches.Rectangle((0, 0), 1, 1, fill=False, edgecolor='none', linewidth=0,
                                            label="NET CHANGE = Income + Expenses")
        sorted_handles.append(spacer_handle)
        sorted_handles.append(formula_handle)
        sorted_handles.append(net_change[1])

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
