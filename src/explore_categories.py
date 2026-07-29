import re
from pathlib import Path

from pandas import DataFrame

from data.read_data import read_bank_statements

COMMON_PREFIXES = ["E-TRANSFER SENT ",
                   r".*INTERAC PURCHASE - \d{4}$",
                   # "^CONTACTLESS INTERAC PURCHASE - \d{4}$",
                   r"^VISA DEBIT PURCHASE - \d{4}$ ",
                   "PAYROLL DEPOSIT ",
                   "E-TRANSFER RECEIVED ",
                   ]

STATEMENT_KEYWORDS = ["MONTHLY FEE",
                      "HYDRO BILL",
                      "ONLINE TRANSFER",
                      "ONLINE BANKING TRANSFER",
                      "MISC PAYMENT SUN LIFE",
                      "MOBILE CHEQUE DEPOSIT",
                      "AUTO INSURANCE ICBC",
                      "TAX REFUND",
                      "INSURANCE AVIVA-HOME/AUTO",
                      "EI CANADA",
                      "INTERNATIONAL REMITTANCE",
                      "ATM WITHDRAWAL",
                      "AUTO INSURANCE ICBC",
                      ]

COFFEES = ["SQ *CHEZ NOUS B",
           "BLENZ ON DENMAN",
           "SQ *ANALOG COFF",
           "STARBUCKS COFFE",
           "SQ *WICKED CAFE",
           "SQ *TURF KITSIL",
           "SQ *FEAST & FAL",
           "SQ *FUNK. COFFE",
           "APHRODITE'S ORG",
           "SQ *FABLES & FO",
           "SQ *OAKBERRY AC",
           "SQ *OIDE COFFEE",
           "BONUS BAKERY",
           "BREKA BAKERY &",
           "MARCHE MON PITO",
           "LS TOFINO SEA K",
           ]

RESTAURANTS = ["HOUSE OF DOSAS",
               "SQ *NIDHI'S CUI",
               "SQ *HEALY?S",
               "SQ *LOCAL PIZZA",
               "SQ *CA CROUSTIL",
               "SQ *MODERN HAND",
               "TST-SAZON MEXIC",
               "TST-SHELTER RES",
               "SQ *ADRIANA?S",
               "SQ *WITCH?S BRE",
               "SQ *TOFITIAN CA",
               "TST-TACOFINO TO",
               "WHITE RABBIT CO",
               ]

""" 
TRICKY BITS:
    SOCIETE DU SERV == SERVICE DE GARDE LES COPAINS = SDG
    COSTCO WHOLESAL == COSTCO CA == COSTCO
    LONDON DRUGS xx == LONDON DRUGS 
    BRANDON & JOANN == NO FRILLS
"""


def group_by_transcation_types(statement: DataFrame) -> dict:
    # {'Visa Debit': DataFrame, 'Interact Purchase': DataFrame}
    transcation_types = {}
    categories = ["E-TRANSFER", "INTERAC PURCHASE", "VISA DEBIT PURCHASE", "CONTACTLESS INTERAC PURCHASE",
                  "ONLINE BANKING TRANSFER"]
    for type in categories:
        transcation_types[type] = pd.DataFrame(columns=statement.columns)
        for _, row in statement.iterrows():
            if type in row['Description 1']:
                transcation_types[type].loc[len(transcation_types[type])] = row
    return transcation_types


def clean_description(text, pattern: str) -> DataFrame:
    match = re.match(pattern, text)
    if match:
        subtext = match.group(0)
        new_text = text.replace(subtext, "")
        return new_text.split('#', 1)[0]
    else:
        return text


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent
    bank_statement_path = script_dir / "data" / "RBC_download-transactions.csv"
    bank_statements = read_bank_statements(bank_statement_path)

    # Split each description into words
    types = bank_statements['Description 1'].str.split()

    # categories = [' '.join(text[:2]) for text in types]
    # c = collections.Counter(categories)
    # for prefix, counts in c.items():
    #     print(f"{prefix}: {counts}")

    pattern = r".*INTERAC PURCHASE - \d{4}"
    bank_statements['Description 1'] = bank_statements['Description 1'].apply(clean_description, args=(pattern,))
    print(bank_statements)
