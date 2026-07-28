import re
from pathlib import Path

from pandas import DataFrame

from clean_description import clean_all_descriptions
from read_data import read_bank_statements

# Placeholder in case I need this category
RECURRING_PAYMENTS = {"MONTHLY FEE",
                      "HYDRO BILL",
                      "ONLINE TRANSFER",
                      "ONLINE BANKING TRANSFER",
                      "MISC PAYMENT SUN LIFE",
                      "MOBILE CHEQUE DEPOSIT",
                      "AUTO INSURANCE ICBC",
                      "TAX REFUND CANADA",
                      "INSURANCE AVIVA-HOME/AUTO",
                      "EI CANADA",
                      "INTERNATIONAL REMITTANCE",
                      "ATM WITHDRAWAL",
                      "AUTO INSURANCE ICBC",
                      }

COFFEES = {"SQ *CHEZ NOUS B",
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
           "SOLLY'S BAGELRY",
           }

RESTAURANTS = {"HOUSE OF DOSAS",
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
               "SQ *EMPANADA GA",
               "TST-TACOFINO TO",
               "WHITE RABBIT CO",
               "YAYU CAFE & RES",
               }

GROCERIES = ["WHOLE FOODS MAR",
             "SAFEWAY",
             "DAVIE STREET YI",  # Independent grocer
             "BRANDON & JOANN",
             "KIN'S FARM",
             "DANIAL MARKET",
             "KONBINIYA",
             "KITSILANO NATUR",  # Kitsilano Natural Foods
             "LONDON DRUGS",
             "DOLLARAMA",
             "FRUITICANA",
             "QUALITY FOODS",
             ]

HOUSE = ["THE SOAP DISPEN",
         "CANADIAN TIRE",
         "THE GOURMET WAR",
         "DOLLORAMA",
         "BANYEN BOOKS",
         "THE CROSS",
         ]

HEALTH = ["SHOPPERS DRUG M",
          "FOOTBRIDGE PHYS",
          "LIFELABS",
          "LUXCEY",
          "DENTAL",
          "LUCILE DELORME",
          "OSTEOPATHY",
          "MY VIRTUAL SLP",
          "SILVER ORCH",
          "SABA THAI",
          "TOETOSOUL",
          "MSK HEALTH",
          ]


def determine_category(text: str) -> str:
    # Use regex pattern to identify the categories
    coffee_pattern = '|'.join(re.escape(word) for word in COFFEES)
    restaurant_pattern = '|'.join(re.escape(word) for word in RESTAURANTS)
    costco_pattern = '|'.join(re.escape(word) for word in ["COSTCO WHOLESAL", "COSTCO CA"])
    groceries_pattern = '|'.join(re.escape(word) for word in GROCERIES)
    sdg_pattern = r"^PAYROLL DEPOSIT .* SERV.*"

    new_description = text

    if re.search(coffee_pattern, text, re.IGNORECASE):
        new_description = "COFFEES"
    elif re.search(restaurant_pattern, text, re.IGNORECASE):
        new_description = "RESTAURANTS"
    elif re.search(groceries_pattern, text, re.IGNORECASE):
        new_description = "GROCERIES"
    elif re.search(costco_pattern, text, re.IGNORECASE):
        new_description = "COSTCO"
    elif re.search(sdg_pattern, text, re.IGNORECASE):
        new_description = re.sub("(DEPOSIT).*", f"DEPOSIT SDG LES COPAINS", text)

    return new_description


def rename_description(data_statements: DataFrame) -> DataFrame:
    data_statements['Description 2'] = data_statements['Description 2'].apply(determine_category)

    return data_statements


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent
    bank_statement_path = script_dir / "data" / "RBC_download-transactions.csv"
    bank_statements = read_bank_statements(bank_statement_path)

    cleaned_statements = clean_all_descriptions(bank_statements)
    categorized_statements = rename_description(cleaned_statements)
    categorized_statements.to_csv('categorized_statements.csv')
