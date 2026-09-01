from enum import Enum

import pandas as pd
from pandas import DataFrame, Timestamp

from data.categories import ALL_CATEGORIES
from data.date_utils import parse_date


class AccountFlow(Enum):
    INCOME = "INCOME"
    TRANSFERS_FROM_SAVINGS = "TRANSFERS FROM SAVINGS"
    EXPENSES = "EXPENSES"
    ESSENTIAL_EXPENSES = "ESSENTIAL EXPENSES"
    SAVINGS_AND_INVESTMENTS = "SAVINGS AND INVESTMENTS"
    NET_CHANGE = "NET CHANGE"


def sum_categories(statement: DataFrame, categories: set) -> dict:
    dict_expenses = {}
    for category in categories:
        total = statement.loc[statement['Category'] == category, 'CAD$'].sum()
        dict_expenses[category] = float(round(total, 2))
    return dict_expenses


def build_transaction_types_dicts(statement: DataFrame) -> tuple:
    income_mask = (statement['CAD$'] > 0) & (statement['Category'] != "BANKING TRANSFER")
    expenses_mask = (statement['CAD$'] < 0) & (statement['Category'].isin(ALL_CATEGORIES.keys()))
    misc_mask = (statement['CAD$'] < 0) & (~statement['Category'].isin(ALL_CATEGORIES.keys())) & (
            statement['Category'] != "BANKING TRANSFER")
    internal_transfer_mask = statement['Category'] == "BANKING TRANSFER"

    income = sum_categories(statement.loc[income_mask], set(statement.loc[income_mask]['Category']))
    expenses = sum_categories(statement.loc[expenses_mask], set(statement.loc[expenses_mask]['Category']))
    misc = sum_categories(statement.loc[misc_mask], set(statement.loc[misc_mask]['Category']))
    internal_transfer = dict(zip(list(statement.loc[internal_transfer_mask]['Transaction Date']),
                                 list(statement.loc[internal_transfer_mask]['CAD$'])))

    incoming_transfers = {x: y for x, y in internal_transfer.items() if y > 0}
    outgoing_transfers = {x: y for x, y in internal_transfer.items() if y < 0}

    return (dict(expenses.items()), dict(sorted(income.items())), dict(sorted(misc.items())),
            dict(sorted(incoming_transfers.items())), dict(sorted(outgoing_transfers.items())))


def build_sub_category_dicts(statement: DataFrame) -> tuple:
    label = list(set(statement['Sub Category']))
    values = []
    return label, values


def get_balance_start_end_date_from_strings(start_date: str, end_date: str, balance: DataFrame) -> tuple:
    targets = pd.DataFrame({'Date': [parse_date(start_date), parse_date(end_date)]})
    matched = pd.merge_asof(targets, balance, on='Date', direction='nearest')

    start_balance = matched.iloc[0]['Balance']
    end_balance = matched.iloc[1]['Balance']
    return start_balance, end_balance


def get_balance_start_end_date_from_timestamps(start_date: Timestamp, end_date: Timestamp, balance: DataFrame) -> tuple:
    targets = pd.DataFrame({'Date': [start_date, end_date]})
    matched = pd.merge_asof(targets, balance, on='Date', direction='nearest')

    start_balance = matched.iloc[0]['Balance']
    end_balance = matched.iloc[1]['Balance']
    return start_balance, end_balance


def get_account_flow_type_mask(statement, account_flow_type, expenses_excluded=None):
    if expenses_excluded is None:
        expenses_excluded = set()

    if account_flow_type == AccountFlow.INCOME:
        return ((statement['CAD$'] > 0) &
                (statement['Category'] != "INVESTMENTS") &
                (statement['Sub Category'] != "ONLINE BANKING TRANSFER") &
                ((statement['Category'] == "TAX REFUND CANADA") |
                 (~statement['Description 1'].str.contains("REFUND") &
                  ~statement['Description 1'].str.contains("CORRECTION"))))
    elif account_flow_type == AccountFlow.TRANSFERS_FROM_SAVINGS:
        return ((statement['CAD$'] > 0) &
                (statement['Sub Category'] == "ONLINE BANKING TRANSFER"))
    elif account_flow_type == AccountFlow.EXPENSES:
        is_expense = ((statement['CAD$'] < 0) &
                      (statement['Sub Category'] != "ONLINE TRANSFER TO DEPOSIT ACCOUNT") &
                      (statement['Category'] != "INVESTMENTS"))
        is_refund_or_correction = ((statement['Description 1'].str.contains("REFUND") |
                                   statement['Description 1'].str.contains("CORRECTION")) & (statement['Category'] != "TAX REFUND CANADA"))
        return is_expense | (is_refund_or_correction & (statement['CAD$'] > 0))

    elif account_flow_type == AccountFlow.ESSENTIAL_EXPENSES:
        return ((statement['CAD$'] < 0) &
                (statement['Sub Category'] != "ONLINE TRANSFER TO DEPOSIT ACCOUNT") &
                (statement['Category'] != "INVESTMENTS") &
                (~statement['Category'].isin(expenses_excluded)))
    elif account_flow_type == AccountFlow.SAVINGS_AND_INVESTMENTS:
        return (((statement['CAD$'] < 0) &
                 (statement['Sub Category'] == "ONLINE TRANSFER TO DEPOSIT ACCOUNT")) |
                ((statement['CAD$'] < 0) & (statement['Category'] == "INVESTMENTS")))
    else:
        return None


def get_all_account_flows_df_masks(statement, expenses_excluded=None):
    if expenses_excluded is None:
        expenses_excluded = set()

    income_mask = get_account_flow_type_mask(statement, AccountFlow.INCOME)
    transfers_from_savings_mask = get_account_flow_type_mask(statement, AccountFlow.TRANSFERS_FROM_SAVINGS)
    expenses_mask = get_account_flow_type_mask(statement, AccountFlow.EXPENSES)
    essential_expenses_mask =get_account_flow_type_mask(statement, AccountFlow.ESSENTIAL_EXPENSES, expenses_excluded)
    savings_investments_mask = get_account_flow_type_mask(statement, AccountFlow.SAVINGS_AND_INVESTMENTS)

    return [income_mask, transfers_from_savings_mask, expenses_mask, essential_expenses_mask, savings_investments_mask]


def get_account_flows(period_statements, expenses_excluded=None):
    """
    Returns a list of label, DataFrame, color and marker for the account flows:
        income, transfers_from_savings, expenses, essential_expenses, savings_investments, net_change
    """
    if expenses_excluded is None:
        expenses_excluded = set()
    transfers_from_savings = []
    savings_investments = []
    income = []
    expenses = []
    net_change = []
    essential_expenses = []

    for statement in period_statements:
        statement_masks = get_all_account_flows_df_masks(statement, expenses_excluded)

        # Income = positive CAD$ except "ONLINE BANKING TRANSFER" which are money transferred from Savings,
        #           and "INVESTMENTS" (Ex: withdrawal from RRSP overcontribution)
        income_mask = statement_masks[0]
        income_sum = statement.loc[income_mask, 'CAD$'].sum()
        income.append(income_sum)

        # Bank transfer coming from Savings
        transfers_from_savings_mask = statement_masks[1]
        transfers_from_savings_sum = statement.loc[transfers_from_savings_mask, 'CAD$'].sum()
        transfers_from_savings.append(transfers_from_savings_sum)

        # Expenses = negative CAD$ expect "ONLINE TRANSFER TO DEPOSIT ACCOUNT" which go into Savings
        # Need to take into account: negative CAD$ & "ONLINE BANKING TRANSFER" which are reimbursement of the Credit Card
        expenses_mask = statement_masks[2]
        expenses_sum = statement.loc[expenses_mask, 'CAD$'].sum()
        expenses.append(expenses_sum)

        # Essential expenses = Expenses - {set of categories to exclude}
        essential_expenses_mask = statement_masks[3]
        essential_expenses_sum = statement.loc[essential_expenses_mask, 'CAD$'].sum()
        essential_expenses.append(essential_expenses_sum)

        # Savings / Investments
        savings_investments_mask = statement_masks[4]
        savings_investments_sum = statement.loc[savings_investments_mask, 'CAD$'].sum()
        savings_investments.append(savings_investments_sum)

        # Net change: sum of all the above except savings and investments
        net_change.append(income_sum + expenses_sum)

    return [
        ("INCOME", income, 'blue', 's'),
        ("TRANSFERS FROM SAVINGS", transfers_from_savings, 'steelblue', 's'),
        ("EXPENSES", expenses, 'magenta', 's'),
        ("ESSENTIAL EXPENSES", essential_expenses, 'purple', 's'),
        ("SAVINGS AND INVESTMENTS", savings_investments, 'green', 's'),
        ("NET CHANGE", net_change, 'red', 'o'),
    ]
