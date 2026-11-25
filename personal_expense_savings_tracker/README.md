# Personal Expense & Savings Tracker

Python + pandas + SQLite. Track cash-basis income and spending from a CSV snapshot, validate records, and generate monthly savings and category spending reports. Includes a Colab notebook, synthetic sample data, six SQL reports, and automated tests. This is a CSV-based tracker, not a bank-connected app or a live dashboard.

## Quick start: Colab (no local installation)
1. Open Google Colab and choose File > Upload notebook.
2. Upload Expense_Tracker_Colab.ipynb from this project ZIP.
3. Run each notebook cell in order. Upload this project ZIP when prompted.
4. The notebook runs synthetic sample data, displays the reports, and downloads the outputs.
Do not upload confidential data to public GitHub repositories. Google Colab is cloud-hosted: only upload personal records if comfortable with that environment.

## Local setup
Use Python 3.10+. Run these inside the extracted project folder:
```sh
pip install -r requirements.txt
python tracker.py --input data/sample_transactions.csv --output artifacts_demo
python -m unittest discover -s tests -v
```
Use a fresh output directory for each run. Existing nonempty directories are not overwritten.

## Your own records
Copy data/transactions_template.csv to private_data/my_transactions.csv. Add rows then run:
```sh
python tracker.py --input private_data/my_transactions.csv --output artifacts_my_run
```
The CSV is the editable source of truth. Add/update records there and rerun a COMPLETE snapshot into a new output directory. No incremental imports or interactive transaction entry are implemented.

## Input contract
- transaction_id: nonempty and unique across the complete file. All rows sharing a repeated ID are quarantined, not arbitrarily retained.
- transaction_date: YYYY-MM-DD, a valid calendar date.
- type: income, expense, refund, or transfer (normalized to lowercase).
- category: nonempty; use consistent spelling/case, e.g. Groceries.
- amount: positive INR decimal, max two decimal places, no currency symbols/commas/scientific notation. Ceiling INR 1 trillion per transaction to catch extreme inputs.
- account: a label, e.g. Bank, Card, Cash. Never put account/card numbers here.
- description: optional text.
All data is INR. Money is parsed using Decimal and stored as integer paise; SQL outputs use rupees for display. Extremely large aggregate imports still require checking SQLite integer-sum bounds.

## Accounting scope and anti-double-counting rules
Income = external earned/received income. Expenses = purchases, recognized on the recorded date. Refunds reduce expenses in the month received, under the original expense category. All entered amounts remain positive; type determines treatment.

Monthly savings = income - (expenses - refunds). Savings rate = savings / income * 100; zero-income months have a blank rate. Refund-heavy months may have negative net spending or rates over 100%; savings can be negative. This is observed cash-basis surplus, not verified bank savings, net worth, or investment return.

Transfers between your own accounts are excluded from income and spending. A savings-account transfer is not a new expense. Record card purchases as expenses; card bill principal payments as transfers to avoid counting spending twice. Fees/interest are separate expenses. Loans, investments, and complex reimbursements are outside this starter scope; do not classify loan proceeds as earned income or security purchases as consumption without defining a broader policy. This ledger does not compute account balances or match transfer pairs.

## Six reports
1. Monthly income, net expenses, savings, savings rate.
2. Category spending by month.
3. Category totals with gross expenses and refunds separately.
4. Income sources.
5. Ten largest expense transactions.
6. Monthly activity counts/amounts by transaction type (including transfers for audit).

Only months with accepted records appear. Missing months do not mean zero activity. No partial-month normalization or completeness claim is made. Category labels are not auto-guessed. Report totals describe supplied records only.

## Audit and outputs
expenses.db; clean_transactions.csv; rejected_transactions.csv with source row/reason; quality_report.json; reports/ with six CSVs. Invalid data is quarantined, never silently dropped. Input row count reconciles to accepted + rejected; SQLite counts and integer monetary totals reconcile to Python. Exported free text may contain spreadsheet formulas if inputs are untrusted: review/sanitize before opening CSVs in Excel.

## Sample expected results (SYNTHETIC ONLY)
January: income 50000, net expenses 19500, savings 30500, savings rate 61%.
February: income 60000, net expenses 20500, savings 39500, savings rate 65.83%.
March: income 52000, net expenses 20800, savings 31200, savings rate 60%.
22 source rows: 20 accepted, 2 intentionally invalid rows rejected.

## Portfolio presentation
State explicitly that demonstration records are synthetic. Include the notebook, SQL, sample data, and tests. For a stronger version, add a real-data report only after anonymization, plus budgets, charts, or a local UI as separately implemented features. Do not claim features that are not implemented.

## Privacy
Keep real data in private_data/ and generated outputs in artifacts*/. .gitignore only helps with Git workflows; browser uploads still require manual review. Clear notebook outputs before publishing if you later run personal data. The distributed sample notebook has no saved personal outputs.
