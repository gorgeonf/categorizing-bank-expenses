from pandas import DataFrame
from pandas.io.stata import stata_epoch

from categorise.group_in_categories import ALL_CATEGORIES


def sum_categories(statement: DataFrame, categories: set) -> dict:
    dict_expenses = {}
    for category in categories:
        total = statement.loc[statement['Category'] == category, 'CAD$'].sum()
        dict_expenses[category] = float(round(total, 2))
    return dict_expenses


def build_transaction_types_dicts(statement: DataFrame) -> tuple:
    income_mask = statement['CAD$'] > 0
    expenses_mask = (statement['CAD$'] < 0) & (statement['Category'].isin(ALL_CATEGORIES.keys()))
    misc_mask = (statement['CAD$'] < 0) & (~statement['Category'].isin(ALL_CATEGORIES.keys())) & (
            statement['Category'] != "BANKING TRANSFER")
    internal_transfer_mask = statement['Category'] == "BANKING TRANSFER"

    expenses = sum_categories(statement.loc[expenses_mask], set(statement.loc[expenses_mask]['Category']))
    income = sum_categories(statement.loc[income_mask], set(statement.loc[income_mask]['Category']))
    misc = sum_categories(statement.loc[misc_mask], set(statement.loc[misc_mask]['Category']))
    internal_transfer = dict(zip(list(statement.loc[internal_transfer_mask]['Transaction Date']),
                                 list(statement.loc[internal_transfer_mask]['CAD$'])))

    incoming_transfers = {x: y for x, y in internal_transfer.items() if y > 0}
    outgoing_transfers = {x: y for x, y in internal_transfer.items() if y < 0}

    return (dict(expenses.items()), dict(sorted(income.items())), dict(sorted(misc.items())),
            dict(sorted(incoming_transfers.items())), dict(sorted(outgoing_transfers.items())))

def build_sub_category_dicts(statement: DataFrame) -> tuple:
    label = list(set(statement['Sub-Category']))
    values = []
    return label, values
