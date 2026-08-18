# Categorizing Bank Expenses

A personal data pipeline that parses RBC bank statement CSVs, categorises transactions by merchant, and visualises spending through bar and pie charts.

## What it does

- Loads a bank statement CSV export (RBC format)
- Cleans raw transaction descriptions to isolate merchant names
- Maps merchants to categories (Groceries, Coffees, Utilities, Rent, etc.) using a configurable keyword-matching system
- Splits transactions into Income, Expenses, Miscellaneous, and Internal Transfers (e.g. credit card payments, savings transfers)
- Filters by custom date ranges, or slices a statement into weekly/monthly periods
- Generates:
  - Bar charts summarising transaction types
  - Grouped bar charts showing transaction types across periods (month-over-month comparison)
  - Pie charts for each transaction type, broken down by category
  - Income vs. Expenses balance charts (pie or bar), with net balance highlighted

## Project structure

```
src/
  data/
    read_data.py             # Load and prepare the raw CSV
    clean_description.py     # Strip known prefixes from transaction descriptions
    date_utils.py            # Date parsing, range filtering, period slicing
  categorise/ 
    group_in_categories.py   # Keyword-based category matching
    categories.py            # Definition of all the categories that can be found in the bank statements -- not committed (.gitignore)         
  visualise/
    data_shaping.py          # Group and sum transactions into chart-ready data
    generate_graphs.py       # Chart generation (matplotlib)
    generate_graph_helper.py # Convenience wrappers tying the pipeline together
  pipeline.py                # End-to-end pipeline entry point
data/                        # Bank statement CSVs (gitignored — not included in repo)
```

## How it works

1. **Read** — `read_bank_statements()` loads the CSV and parses transaction dates.
2. **Filter** (optional) — `filter_by_date_range()` restricts the data to a chosen window.
3. **Clean** — `clean_all_descriptions()` strips known prefixes from raw descriptions to isolate merchant names (the "Sub-Category").
4. **Categorise** — `rename_description()` matches each merchant against a keyword dictionary to assign a Category.
5. **Visualise** — the resulting data can be summarised and charted in several ways: totals, per-period comparisons, category breakdowns, and income/expense balance.

## Bank statements format

This project was designed to help me visualise my personal bank statement, so the format is taken from my personal data.
CSV files with this format:
```Account Type,Account Number,Transaction Date,Cheque Number,Description 1,Description 2,CAD$,USD$```

## Categories

Category definitions (which merchant keywords map to which category) are kept out of this repository, since they contain personal transaction data. See `categorise/group_in_categories.py` for the matching logic.

## Status

This project is under active development. Planned next steps include:

- A month-over-month spending trend/line graph
- A summary totals table
- A web application (CSV upload, date range selection, category selection, and a "Generate" button to produce charts on demand)

## Requirements

- Python 3
- pandas
- matplotlib
- numpy

## Disclaimer

This project processes personal financial data for demonstration purposes. Sample data and category mappings are excluded from version control.

## Acknowledgements

This project was built with guidance from Claude (Anthropic) as a pair-programming and learning tool — used for code review, debugging, and design discussion throughout development.