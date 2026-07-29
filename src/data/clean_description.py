import re
from pathlib import Path

from pandas import DataFrame

from data.read_data import read_bank_statements

COMMON_PREFIXES = [r".*E-TRANSFER SENT ",
                   r".*INTERAC PURCHASE - \d{4}",
                   r".*VISA DEBIT PURCHASE - \d{4} ",
                   r".*E-TRANSFER RECEIVED ",
                   ]


def clean_description(text, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.match(pattern, text)
        if match:
            subtext = match.group(0)
            new_text = text.replace(subtext, "")
            return new_text.split('#', 1)[0].strip()
    return text


def clean_all_descriptions(data_statements: DataFrame) -> DataFrame:
    patterns = COMMON_PREFIXES
    data_statements['Description 2'] = data_statements['Description 2'].apply(clean_description, args=(patterns,))
    return data_statements


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent
    bank_statement_path = script_dir / "data" / "RBC_download-transactions.csv"
    bank_statements = read_bank_statements(bank_statement_path)

    cleaned_statement = clean_all_descriptions(bank_statements)
    print(cleaned_statement)

    cleaned_statement.to_csv('clean_statement.csv')
