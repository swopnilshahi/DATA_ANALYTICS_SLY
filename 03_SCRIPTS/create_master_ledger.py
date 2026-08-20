from pathlib import Path
import pandas as pd
import numpy as np

CLEANED_FOLDER = Path("01_DATA/CLEANED")
OUTPUT_FOLDER = Path("04_OUTPUT")

OUTPUT_FOLDER.mkdir(exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

expenses = pd.read_csv(
    CLEANED_FOLDER / "expenses_clean.csv"
)

receipts = pd.read_csv(
    CLEANED_FOLDER / "receipts_clean.csv"
)

bank = pd.read_csv(
    CLEANED_FOLDER / "bank_clean.csv"
)


# ============================================================
# STANDARDIZE EXPENSES
# ============================================================

expense_master = pd.DataFrame()

expense_master["transaction_id"] = (
    "EXP-" + expenses["expense_id"].astype(str)
)

expense_master["date_ad"] = pd.to_datetime(
    expenses["date_ad"],
    errors="coerce"
)

expense_master["date_bs"] = expenses["date_bs"]

expense_master["transaction_type"] = "EXPENSE"

expense_master["payment_method"] = expenses[
    "payment_type"
].fillna("UNKNOWN")

expense_master["description"] = expenses[
    "particular"
]

expense_master["amount"] = pd.to_numeric(
    expenses["amount"],
    errors="coerce"
)

expense_master["money_flow"] = "OUT"

expense_master["source"] = "EXPENSE_BOOK"

expense_master["source_id"] = expenses[
    "expense_id"
]


# ============================================================
# STANDARDIZE RECEIPTS
# ============================================================

receipt_master = pd.DataFrame()

receipt_master["transaction_id"] = (
    "REC-" + receipts["receipt_id"].astype(str)
)

receipt_master["date_ad"] = pd.to_datetime(
    receipts["date_ad"],
    errors="coerce"
)

receipt_master["date_bs"] = receipts["date_bs"]

receipt_master["transaction_type"] = "RECEIPT"

receipt_master["payment_method"] = receipts[
    "payment_type"
].fillna("UNKNOWN")

# Combine useful receipt information
receipt_master["description"] = (
    receipts["name"].fillna("")
    + " | "
    + receipts["reason"].fillna("")
)

receipt_master["amount"] = pd.to_numeric(
    receipts["amount"],
    errors="coerce"
)

receipt_master["money_flow"] = "IN"

receipt_master["source"] = "RECEIPT_BOOK"

receipt_master["source_id"] = receipts[
    "receipt_id"
]


# ============================================================
# STANDARDIZE BANK TRANSACTIONS
# ============================================================

bank_master = pd.DataFrame()

bank_master["transaction_id"] = (
    "BANK-" +
    bank["bank_transaction_id"].astype(str)
)

bank_master["date_ad"] = pd.to_datetime(
    bank["date"],
    errors="coerce"
)

bank_master["date_bs"] = pd.NA

# Determine bank transaction direction
bank_master["transaction_type"] = np.where(
    bank["withdraw"].notna(),
    "BANK_WITHDRAW",
    "BANK_DEPOSIT"
)

bank_master["payment_method"] = "BANK"

bank_master["description"] = bank[
    "description"
]

# Amount = withdraw or deposit
bank_master["amount"] = (
    bank["withdraw"]
    .fillna(
        bank["deposit"]
    )
)

bank_master["amount"] = pd.to_numeric(
    bank_master["amount"],
    errors="coerce"
)

bank_master["money_flow"] = np.where(
    bank["withdraw"].notna(),
    "OUT",
    "IN"
)

bank_master["source"] = "BANK_STATEMENT"

bank_master["source_id"] = bank[
    "bank_transaction_id"
]


# ============================================================
# COMBINE
# ============================================================

master = pd.concat(
    [
        expense_master,
        receipt_master,
        bank_master
    ],
    ignore_index=True
)


# ============================================================
# CLEAN
# ============================================================

master["description"] = (
    master["description"]
    .fillna("")
    .astype(str)
    .str.strip()
)

master["amount"] = pd.to_numeric(
    master["amount"],
    errors="coerce"
)

master = master.sort_values(
    by=["date_ad", "transaction_id"],
    na_position="last"
)


# ============================================================
# SAVE
# ============================================================

output_file = (
    OUTPUT_FOLDER /
    "master_transactions.csv"
)

master.to_csv(
    output_file,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("MASTER TRANSACTION LEDGER CREATED")
print("=" * 70)

print(f"\nTotal transactions: {len(master)}")

print("\nTransactions by source:")
print(
    master["source"]
    .value_counts()
)

print("\nTransactions by money flow:")
print(
    master.groupby("money_flow")["amount"]
    .agg(["count", "sum"])
)

print("\nDate range:")
print(
    master["date_ad"]
    .min(),
    "to",
    master["date_ad"]
    .max()
)

print(f"\nSaved to: {output_file}")

print("\nFirst 10 records:")
print(
    master.head(10).to_string(
        index=False
    )
)