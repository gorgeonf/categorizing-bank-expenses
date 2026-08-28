import pandas as pd
import re
from data.categories import ALL_CATEGORIES, COLLAPSE_SUB_CATEGORY, KEYWORD_SUB_CATEGORY_OVERRIDE, ONLINE_TRANSFER
from data.clean_description import clean_all_descriptions
from data.read_data import read_all_bank_statements
from pandas import DataFrame
from pathlib import Path


def determine_category(text: str) -> tuple:
    """
    Maps a cleaned transaction description to (sub_category, category).

    Normal case: category is matched from ALL_CATEGORIES, sub_category stays
    as the original text (e.g. merchant name).
    Special cases (SERV, transfers, cheque deposits): sub_category and
    category are both set to the same override value.
    Fallback: both returned unchanged.
    """
    for category, category_pattern in ALL_CATEGORIES.items():
        pattern = '|'.join(re.escape(word) for word in category_pattern)
        if re.search(pattern, text, re.IGNORECASE):
            if category in COLLAPSE_SUB_CATEGORY:
                return category, category
            for keyword, override in KEYWORD_SUB_CATEGORY_OVERRIDE.items():
                if keyword in text.upper():
                    return override, category
            return text, category  # Sub Category stays as original cleaned text
    # Outgoing and Incoming Transfers will be differentiated when preparing the data for the graphs
    for sub_category in ONLINE_TRANSFER:
        if sub_category in text:
            return sub_category, "BANKING TRANSFER"

    return text, text


def apply_determine_category(text: str) -> pd.Series:
    return pd.Series(determine_category(text))


def rename_description(data_statements: DataFrame) -> DataFrame:
    data_statements[['Sub Category', 'Category']] = data_statements['Sub Category'].apply(apply_determine_category)
    return data_statements


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent.parent
    bank_statement_path = script_dir / "data/bank_statements"
    bank_statement_df = read_all_bank_statements(bank_statement_path)

    cleaned_statement = clean_all_descriptions(bank_statement_df)

    cleaned_statements = clean_all_descriptions(bank_statement_df)
    categorised_statements = rename_description(cleaned_statements)
    categorised_statements_path = script_dir / "data" / "categorised_statements.csv"
    categorised_statements.to_csv(categorised_statements_path)
