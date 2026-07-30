import re
from pathlib import Path

from pandas import DataFrame

from data.clean_description import clean_all_descriptions
from data.read_data import read_bank_statements

# Placeholder in case I need this category
RECURRING_PAYMENTS = {"E-TRANSFER SENT KEN WONG",
                      "MISC PAYMENT SUN LIFE",
                      "TAX REFUND CANADA",
                      "ATM WITHDRAWAL",
                      }

RENT = {"KEN WONG"}

UTILITIES = {"PUBLIC MOBILE", "HYDRO", "OXIO", "INSURANCE AVIVA-HOME", "MONTHLY FEE"}

INCOME = {"EI CANADA", "PAYROLL DEPOSIT", "SERVICE DE GARDE LES COPAINS", "MOBILE CHEQUE DEPOSIT", }

CAR = {"PETRO-CANADA", "ICBC", "CHV", }

TRANSPORT = {"COMPASS", "UBER CANADA/UBE", }

IMMIGRATION_AUSTRALIA = {"GURULLY", "PEARSON", "LINKEDIN", "INTERNATIONAL REMITTANCE", "EVENTBRITE", }

DA_LEISURES = {"DENMAN ATHLETIC", "VANCOUVER PB RE", "POPEYES SUPPLEM"}

ALCOHOL = {"BC LIQUOR", }

YOGACOACHING = {"YOGACOACHING", "SYSTEME.IO", "NANCY GIRARD"}

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

MISC = {"VANCOUVER PUBLI", }

ALL_CATEGORIES = {
    "UTILITIES": UTILITIES,
    "CAR": CAR,
    "TRANSPORT": TRANSPORT,
    "IMMIGRATION AUSTRALIA": IMMIGRATION_AUSTRALIA,
    "DA & LEISURES": DA_LEISURES,
    "ALCOHOL": ALCOHOL,
    "YOGACOACHING": YOGACOACHING,
    "COFFEES": COFFEES,
    "RESTAURANTS": RESTAURANTS,
    "GROCERIES": GROCERIES,
    "COSTCO": COSTCO,
    "HOUSE & CLOTHING": HOUSE_CLOTHING,
    "HEALTH": HEALTH,
    "TRAVELS": TRAVELS,
    "RENT": RENT,
}


def determine_category(text: str) -> str:
    for category, category_pattern in ALL_CATEGORIES.items():
        pattern = '|'.join(re.escape(word) for word in category_pattern)
        if re.search(pattern, text, re.IGNORECASE):
            return category
        elif "SERV" in text.upper():
            return "PAYROLL DEPOSIT SERVICE DE GARDE"
        # Outgoing and Incoming Transfers will be differentiated when preparing the data for the graphs
        elif any(word in text for word in ONLINE_TRANSFER):
            return "BANKING TRANSFER"
        elif "MOBILE CHEQUE DEPOSIT" in text.upper():
            return "CHEQUE DEPOSIT"
    return text


def rename_description(data_statements: DataFrame) -> DataFrame:
    data_statements['Description 2'] = data_statements['Description 2'].apply(determine_category)
    return data_statements


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent
    bank_statement_path = script_dir / "data" / "RBC_download-transactions.csv"
    raw_statements = read_bank_statements(bank_statement_path)

    cleaned_statements = clean_all_descriptions(raw_statements)
    categorized_statements = rename_description(cleaned_statements)
    categorized_statements_path = script_dir / "data" / "categorized_statements.csv"
    categorized_statements.to_csv(categorized_statements_path)
