import re
from pathlib import Path

from pandas import DataFrame

from clean_description import clean_all_descriptions
from read_data import read_bank_statements

# Placeholder in case I need this category
RECURRING_PAYMENTS = {"E-TRANSFER SENT KEN WONG",
                      "ONLINE TRANSFER",
                      "ONLINE BANKING TRANSFER",
                      "MISC PAYMENT SUN LIFE",
                      "MOBILE CHEQUE DEPOSIT",
                      "TAX REFUND CANADA",
                      "ATM WITHDRAWAL",
                      }

RENT = {"KEN WONG"}

UTILITIES = {"PUBLIC MOBILE", "HYDRO", "OXIO", "INSURANCE AVIVA-HOME", "MONTHLY FEE"}

PAYROLL = {"EI CANADA", "PAYROLL DEPOSIT", "SERVICE DE GARDE LES COPAINS", }

CAR = {"PETRO-CANADA", "ICBC", "CHV", }

TRANSPORT = {"COMPASS", "UBER CANADA/UBE", }

IMMIGRATION_AUSTRALIA = {"GURULLY", "PEARSON", "INTERNATIONAL REMITTANCE"}

DA_GYM = {"DENMAN ATHLETIC"}

ALCOHOL = {"BC LIQUOR", }

YOGACOACHING = {"YOGACOACHING", "SYSTEME.IO", }

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
           "ORGANIC BITES C"
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
               "VEGAIN"
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
             "BERRYMOBILE",
             ]

COSTCO = {"COSTCO WHOLESAL", "COSTCO CA"}

HOUSE = ["THE SOAP DISPEN",
         "CANADIAN TIRE",
         "THE GOURMET WAR",
         "DOLLORAMA",
         "BANYEN BOOKS",
         "THE CROSS",
         "MARSHALLS",
         "STEVE WEST END RECYCLING",
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
          "SABAI THAI",
          "TOETOSOUL",
          "MSK HEALTH",
          "TUNE UP",
          ]

TRAVELS = {"AIRBNB", "BEST WESTERN", "BCF", "PACIFIC RIM", }


def determine_category(text: str) -> str:
    all_categories = {
        "UTILITIES": UTILITIES,
        "PAYROLL": PAYROLL,
        "CAR": CAR,
        "TRANSPORT": TRANSPORT,
        "IMMIGRATION_AUSTRALIA": IMMIGRATION_AUSTRALIA,
        "DA_GYM": DA_GYM,
        "ALCOHOL": ALCOHOL,
        "YOGACOACHING": YOGACOACHING,
        "COFFEES": COFFEES,
        "RESTAURANTS": RESTAURANTS,
        "GROCERIES": GROCERIES,
        "COSTCO": COSTCO,
        "HOUSE": HOUSE,
        "HEALTH": HEALTH,
        "TRAVELS": TRAVELS,
        "RENT": RENT,
    }

    new_description = text

    for category, category_pattern in all_categories.items():
        pattern = '|'.join(re.escape(word) for word in category_pattern)
        if re.search(pattern, text, re.IGNORECASE):
            new_description = category

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

    categorized_statements_path = script_dir / "data" / "categorized_statements.csv"
    categorized_statements.to_csv(categorized_statements_path)
