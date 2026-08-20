from pathlib import Path
import pandas as pd

CLEANED_FOLDER = Path("01_DATA/CLEANED")


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

duplicates = pd.read_csv(
    CLEANED_FOLDER / "bank_duplicates_review.csv"
)


# ============================================================
# 1. EXPENSE DATE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("EXPENSE DATE ANALYSIS")
print("=" * 70)

expenses["date_bs"] = pd.to_datetime(
    expenses["date_bs"],
    errors="coerce"
)

print(f"First expense date: {expenses['date_bs'].min()}")
print(f"Last expense date : {expenses['date_bs'].max()}")

print("\nExpenses by BS month:")

expenses["bs_month"] = (
    expenses["date_bs"]
    .dt.to_period("M")
)

print(
    expenses
    .groupby("bs_month")["amount"]
    .agg(["count", "sum"])
)


# ============================================================
# 2. RECEIPT DATE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("RECEIPT DATE ANALYSIS")
print("=" * 70)

receipts["date_bs"] = pd.to_datetime(
    receipts["date_bs"],
    errors="coerce"
)

print(f"First receipt date: {receipts['date_bs'].min()}")
print(f"Last receipt date : {receipts['date_bs'].max()}")

print("\nReceipts by BS month:")

receipts["bs_month"] = (
    receipts["date_bs"]
    .dt.to_period("M")
)

print(
    receipts
    .groupby("bs_month")["amount"]
    .agg(["count", "sum"])
)


# ============================================================
# 3. PAYMENT TYPE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("EXPENSE PAYMENT TYPES")
print("=" * 70)

print(
    expenses
    .groupby("payment_type")["amount"]
    .agg(["count", "sum"])
    .sort_values("sum", ascending=False)
)


print("\n" + "=" * 70)
print("RECEIPT PAYMENT TYPES")
print("=" * 70)

print(
    receipts
    .groupby("payment_type")["amount"]
    .agg(["count", "sum"])
    .sort_values("sum", ascending=False)
)


# ============================================================
# 4. BANK DATE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("BANK DATE ANALYSIS")
print("=" * 70)

bank["date"] = pd.to_datetime(
    bank["date"],
    errors="coerce"
)

print(f"First bank transaction: {bank['date'].min()}")
print(f"Last bank transaction : {bank['date'].max()}")

print("\nTransactions by source file:")

print(
    bank
    .groupby("source_file")
    .agg(
        first_date=("date", "min"),
        last_date=("date", "max"),
        transactions=("bank_id", "count"),
        withdraw=("withdraw", "sum"),
        deposit=("deposit", "sum")
    )
)


# ============================================================
# 5. DUPLICATE BANK TRANSACTION ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("BANK OVERLAP / DUPLICATE ANALYSIS")
print("=" * 70)

print(f"Total duplicate transactions: {len(duplicates)}")

print("\nDuplicate transactions by source file:")

print(
    duplicates["source_file"]
    .value_counts()
)

print("\nFirst 20 duplicate records:")

columns = [
    "bank_transaction_id",
    "date",
    "description",
    "withdraw",
    "deposit",
    "balance",
    "source_file"
]

print(
    duplicates[columns]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 6. SAVE MONTHLY SUMMARIES
# ============================================================

expense_monthly = (
    expenses
    .groupby("bs_month", as_index=False)
    .agg(
        transaction_count=("expense_id", "count"),
        total_expense=("amount", "sum")
    )
)

receipt_monthly = (
    receipts
    .groupby("bs_month", as_index=False)
    .agg(
        receipt_count=("receipt_id", "count"),
        total_receipt=("amount", "sum")
    )
)

expense_monthly.to_csv(
    CLEANED_FOLDER / "expense_monthly_summary.csv",
    index=False
)

receipt_monthly.to_csv(
    CLEANED_FOLDER / "receipt_monthly_summary.csv",
    index=False
)


print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)