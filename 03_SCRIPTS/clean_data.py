from pathlib import Path
import pandas as pd

RAW_FOLDER = Path("01_DATA/RAW")
CLEANED_FOLDER = Path("01_DATA/CLEANED")

CLEANED_FOLDER.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_amount(series):
    """
    Convert values like:
    '10,000.00' -> 10000.00
    '-'         -> NaN
    """
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("-", "", regex=False)
        .str.strip()
        .replace("", None),
        errors="coerce"
    )


# ============================================================
# 1. CLEAN EXPENSES
# ============================================================

print("\n" + "=" * 70)
print("1. CLEANING EXPENSES")
print("=" * 70)

expenses_file = RAW_FOLDER / "EXPENSES.xlsx"

expenses = pd.read_excel(
    expenses_file,
    sheet_name="Sheet1"
)

# Keep only actual columns we need
expenses = expenses[
    [
        "DATE",
        "PARTICULAR",
        "PAYMENT TYPE",
        "AMOUNTT"
    ]
].copy()

# Rename columns
expenses.columns = [
    "date_bs",
    "particular",
    "payment_type",
    "amount"
]

# Remove rows without a date OR amount
expenses = expenses.dropna(
    subset=["date_bs", "amount"],
    how="all"
)

# Clean text
expenses["particular"] = (
    expenses["particular"]
    .fillna("")
    .astype(str)
    .str.strip()
)

# Remove rows with empty particular
expenses = expenses[
    expenses["particular"] != ""
]

# Standardize payment type
expenses["payment_type"] = (
    expenses["payment_type"]
    .fillna("UNKNOWN")
    .astype(str)
    .str.strip()
    .str.upper()
)

# Clean amount
expenses["amount"] = pd.to_numeric(
    expenses["amount"],
    errors="coerce"
)

# Remove rows without valid amount
expenses = expenses.dropna(
    subset=["amount"]
)

# Create clean ID
expenses.insert(
    0,
    "expense_id",
    range(1, len(expenses) + 1)
)

# Remove exact duplicates based on meaningful fields
expenses = expenses.drop_duplicates(
    subset=[
        "date_bs",
        "particular",
        "payment_type",
        "amount"
    ]
)

# Save
expenses_output = CLEANED_FOLDER / "expenses_clean.csv"

expenses.to_csv(
    expenses_output,
    index=False
)

print(f"Total clean expenses: {len(expenses)}")
print(f"Total expense amount: Rs. {expenses['amount'].sum():,.2f}")

print("\nPayment Types:")
print(expenses["payment_type"].value_counts())

print(f"\nSaved: {expenses_output}")


# ============================================================
# 2. CLEAN RECEIPTS
# ============================================================

print("\n" + "=" * 70)
print("2. CLEANING RECEIPTS")
print("=" * 70)

receipt_file = RAW_FOLDER / "RECEIPT.xlsx"

receipts = pd.read_excel(
    receipt_file,
    sheet_name="RECEIPT"
)

# Rename columns
receipts = receipts.rename(
    columns={
        "Unnamed: 0": "receipt_id",
        "DATE": "date_bs",
        "NAME": "name",
        "ADDRESS": "address",
        "REASON": "reason",
        "AMOUNT": "amount",
        "REMARK": "remark",
        "TYPE": "payment_type"
    }
)

# Keep rows with actual transaction data
receipts = receipts.dropna(
    subset=["date_bs", "name", "amount"],
    how="all"
)

# Remove rows without amount
receipts = receipts.dropna(
    subset=["amount"]
)

# Clean ID
receipts["receipt_id"] = (
    pd.to_numeric(
        receipts["receipt_id"],
        errors="coerce"
    )
    .astype("Int64")
)

# Clean text columns
text_columns = [
    "name",
    "address",
    "reason",
    "remark"
]

for column in text_columns:

    receipts[column] = (
        receipts[column]
        .fillna("")
        .astype(str)
        .str.strip()
    )

# Standardize payment type
receipts["payment_type"] = (
    receipts["payment_type"]
    .fillna("UNKNOWN")
    .astype(str)
    .str.strip()
    .str.upper()
)

# Clean amount
receipts["amount"] = pd.to_numeric(
    receipts["amount"],
    errors="coerce"
)

# Remove invalid amounts
receipts = receipts.dropna(
    subset=["amount"]
)

# Remove duplicate receipts
receipts = receipts.drop_duplicates(
    subset=[
        "receipt_id",
        "date_bs",
        "name",
        "amount"
    ]
)

# Save
receipts_output = CLEANED_FOLDER / "receipts_clean.csv"

receipts.to_csv(
    receipts_output,
    index=False
)

print(f"Total clean receipts: {len(receipts)}")
print(f"Total receipt amount: Rs. {receipts['amount'].sum():,.2f}")

print("\nPayment Types:")
print(receipts["payment_type"].value_counts())

print(f"\nSaved: {receipts_output}")


# ============================================================
# 3. CLEAN BANK STATEMENTS
# ============================================================

print("\n" + "=" * 70)
print("3. CLEANING BANK STATEMENTS")
print("=" * 70)

bank_files = []

for file in RAW_FOLDER.glob("*.xlsx"):

    if file.name not in [
        "EXPENSES.xlsx",
        "RECEIPT.xlsx"
    ]:
        bank_files.append(file)


all_bank_data = []

for bank_file in bank_files:

    print(f"\nProcessing: {bank_file.name}")

    bank = pd.read_excel(
        bank_file,
        sheet_name="Statement"
    )

    # Standardize column names
    bank.columns = (
        bank.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Rename ID for clarity
    bank = bank.rename(
        columns={
            "id": "bank_transaction_id",
            "transaction_date": "date",
            "description": "description",
            "withdraw": "withdraw",
            "deposit": "deposit",
            "balance": "balance"
        }
    )

    # Remove opening/closing balance rows
    # Actual transactions have an ID
    bank = bank.dropna(
        subset=["bank_transaction_id"]
    )

    # Convert ID
    bank["bank_transaction_id"] = (
        pd.to_numeric(
            bank["bank_transaction_id"],
            errors="coerce"
        )
        .astype("Int64")
    )

    # Convert date
    bank["date"] = pd.to_datetime(
        bank["date"],
        errors="coerce"
    )

    # Clean text
    bank["description"] = (
        bank["description"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Convert money columns
    bank["withdraw"] = clean_amount(
        bank["withdraw"]
    )

    bank["deposit"] = clean_amount(
        bank["deposit"]
    )

    bank["balance"] = clean_amount(
        bank["balance"]
    )

    # Add source file
    bank["source_file"] = bank_file.name

    # Keep only valid transactions
    bank = bank.dropna(
        subset=["date"]
    )

    # Remove rows where both withdraw and deposit are empty
    bank = bank[
        ~(
            bank["withdraw"].isna()
            &
            bank["deposit"].isna()
        )
    ]

    all_bank_data.append(bank)

    print(f"Transactions found: {len(bank)}")


# Merge all bank statements
bank = pd.concat(
    all_bank_data,
    ignore_index=True
)

print(f"\nTotal bank rows before duplicate check: {len(bank)}")


# ============================================================
# 4. DETECT OVERLAPPING BANK STATEMENTS
# ============================================================

# Same transaction may appear in more than one bank statement.
# We keep the first occurrence.

duplicate_columns = [
    "date",
    "description",
    "withdraw",
    "deposit",
    "balance"
]

bank["is_duplicate"] = bank.duplicated(
    subset=duplicate_columns,
    keep="first"
)

duplicates = bank[
    bank["is_duplicate"]
].copy()

print(f"Duplicate/overlapping transactions found: {len(duplicates)}")

# Save duplicates separately for review
duplicates_output = (
    CLEANED_FOLDER
    / "bank_duplicates_review.csv"
)

duplicates.to_csv(
    duplicates_output,
    index=False
)


# Keep unique transactions
bank_clean = bank[
    ~bank["is_duplicate"]
].copy()

# Remove helper column
bank_clean = bank_clean.drop(
    columns=["is_duplicate"]
)

# Sort by date
bank_clean = bank_clean.sort_values(
    by="date"
).reset_index(drop=True)

# Create unique master bank ID
bank_clean.insert(
    0,
    "bank_id",
    range(1, len(bank_clean) + 1)
)

# Save clean bank statement
bank_output = CLEANED_FOLDER / "bank_clean.csv"

bank_clean.to_csv(
    bank_output,
    index=False
)

print(f"\nTotal unique bank transactions: {len(bank_clean)}")

print(
    f"Total Withdraw: Rs. "
    f"{bank_clean['withdraw'].sum():,.2f}"
)

print(
    f"Total Deposit: Rs. "
    f"{bank_clean['deposit'].sum():,.2f}"
)

print(f"\nSaved: {bank_output}")

print(f"Duplicates review saved: {duplicates_output}")


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CLEANING COMPLETE")
print("=" * 70)

print(f"Expenses: {len(expenses)}")
print(f"Receipts: {len(receipts)}")
print(f"Bank transactions: {len(bank_clean)}")