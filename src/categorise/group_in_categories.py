import re
from pathlib import Path

import pandas as pd
from pandas import DataFrame

from data.clean_description import clean_all_descriptions
from data.read_data import read_bank_statements

# Placeholder in case I need this category
# RECURRING_PAYMENTS = {"E-TRANSFER SENT KEN WONG",
#                       "MISC PAYMENT SUN LIFE",
#                       "TAX REFUND CANADA",
#                       "ATM WITHDRAWAL",
#                       }

RENT = {"KEN WONG"}

UTILITIES = {"PUBLIC MOBILE", "HYDRO", "OXIO", "INSURANCE AVIVA-HOME", "MONTHLY FEE"}

INCOME = {"EI CANADA", "PAYROLL DEPOSIT", "SERVICE DE GARDE LES COPAINS", "MOBILE CHEQUE DEPOSIT", }

CAR = {"PETRO-CANADA", "ICBC", "CHV", }

TRANSPORT = {"COMPASS", "UBER CANADA/UBE", }

IMMIGRATION_AUSTRALIA = {"GURULLY", "PEARSON", "LINKEDIN", "INTERNATIONAL REMITTANCE", "EVENTBRITE", }

DENMAN_ATHLETICS = {"DENMAN ATHLETIC"}

VANCOUVER_COMMUNITY_CENTER = {"VANCOUVER PUBLI", "VANCOUVER PB RE"}

ALCOHOL = {"BC LIQUOR", "MARQUIS WINE CE", }

YOGA_AND_COACHING = {"YOGACOACHING", "SYSTEME.IO", "ZENSURANCE.COM", "NANCY GIRARD"}

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
           "ORGANIC BITES C",
           "VEGAIN"
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

ONLINE_TRANSFER = {"ONLINE TRANSFER", "ONLINE BANKING TRANSFER"}

GROCERIES = {"WHOLE FOODS MAR",
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
             "TOFINO CO-OP",
             }

COSTCO = {"COSTCO WHOLESAL", "COSTCO CA"}

HOUSE_CLOTHING = {"THE SOAP DISPEN",
                  "CANADIAN TIRE",
                  "THE GOURMET WAR",
                  "DOLLORAMA",
                  "BANYEN BOOKS",
                  "THE CROSS",
                  "MARSHALLS",
                  "STEVE WEST END RECYCLING",
                  "NICOLA DRYCLEAN",
                  }

HEALTH = {"SHOPPERS DRUG M",
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
          }

TRAVELS = {"AIRBNB", "BEST WESTERN", "BCF", "PACIFIC RIM", }

ALL_CATEGORIES = {key: value for key, value in globals().items() if
                  isinstance(value, set) and key not in ["ONLINE_TRANSFER"]}

COLLAPSE_SUB_CATEGORY = {"COSTCO", "DENMAN_ATHLETICS", "RENT", "ALCOHOL"}

# For Categories in ALL_CATEGORIES
KEYWORD_SUB_CATEGORY_OVERRIDE = {
    "HYDRO": "HYDRO",
    "LONDON DRUGS": "LONDON DRUGS",
    "PETRO-CANADA": "PETRO CANADA",
    "CHV": "PETROL CHEVRON CANADA",
    "AURELIE YOGACOACHING": "AURELIE YOGACOACHING",
    "COMPASS WEB": "COMPASS",
    "PUBLIC MOBILE S": "PUBLIC MOBILE",
    "OXIO": "OXIO",
    # future examples: "SOME KEYWORD": "FIXED SUB-CATEGORY NAME"
    "SERV": "PAYROLL DEPOSIT SERVICE DE GARDE",
    "PAYROLL DEPOSIT HP": "PAYROLL DEPOSIT HP",
    "MOBILE CHEQUE DEPOSIT": "CHEQUE DEPOSIT",
    "MISC PAYMENT SUN LIFE": "SUN LIFE REIMBURSEMENT",
    "ATM WITHDRAWAL": "ATM WITHDRAWAL",
    "BÉATRICE LAROUCHE": "AURELIE YOGACOACHING"
}


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
    if any(word in text for word in ONLINE_TRANSFER):
        return "BANKING TRANSFER", "BANKING TRANSFER"
    return text, text


def apply_determine_category(text: str) -> pd.Series:
    return pd.Series(determine_category(text))


def rename_description(data_statements: DataFrame) -> DataFrame:
    data_statements[['Sub Category', 'Category']] = data_statements['Sub Category'].apply(apply_determine_category)
    return data_statements


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent.parent
    bank_statement_path = script_dir / "data" / "RBC_download-transactions.csv"
    raw_statements = read_bank_statements(bank_statement_path)

    cleaned_statements = clean_all_descriptions(raw_statements)
    categorised_statements = rename_description(cleaned_statements)
    categorised_statements_path = script_dir / "data" / "categorised_statements.csv"
    categorised_statements.to_csv(categorised_statements_path)
