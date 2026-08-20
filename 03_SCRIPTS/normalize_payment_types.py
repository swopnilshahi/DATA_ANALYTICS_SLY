from pathlib import Path
import pandas as pd

CLEANED_FOLDER = Path("01_DATA/CLEANED")


# ============================================================
# PAYMENT TYPE NORMALIZATION
# ============================================================

PAYMENT_TYPE_MAP = {
    "CASH": "CASH",

    "QR": "ONLINE",

    "ONLINE": "ONLINE",
    "ONLINE FORM PARABHU": "ONLINE",

    "BANK": "ONLINE",

    "CHECK": "CHEQUE",
    "CHEQUE": "CHEQUE",

    "UNKNOWN": "UNKNOWN",
    "": "UNKNOWN",
}


def normalize_payment_type(value):

    if pd.isna(value):
        return "UNKNOWN"

    value = str(value).strip().upper()

    return PAYMENT_TYPE_MAP.get(
        value,
        "UNKNOWN"
    )


# ============================================================
# NORMALIZE EXPENSES
# ============================================================

print("\n" + "=" * 70)
print("NORMALIZING EXPENSE PAYMENT TYPES")
print("=" * 70)

expenses_file = (
    CLEANED_FOLDER /
    "expenses_clean.csv"
)

expenses = pd.read_csv(
    expenses_file
)

# Preserve original value
expenses["payment_type_original"] = (
    expenses["payment_type"]
)

# Create standardized payment type
expenses["payment_type"] = (
    expenses["payment_type"]
    .apply(normalize_payment_type)
)

print("\nStandardized Expense Payment Types:")

print(
    expenses["payment_type"]
    .value_counts()
)

expenses.to_csv(
    expenses_file,
    index=False
)

print(
    "\nExpenses payment types normalized."
)


# ============================================================
# NORMALIZE RECEIPTS
# ============================================================

print("\n" + "=" * 70)
print("NORMALIZING RECEIPT PAYMENT TYPES")
print("=" * 70)

receipts_file = (
    CLEANED_FOLDER /
    "receipts_clean.csv"
)

receipts = pd.read_csv(
    receipts_file
)

# Preserve original value
receipts["payment_type_original"] = (
    receipts["payment_type"]
)

# Create standardized payment type
receipts["payment_type"] = (
    receipts["payment_type"]
    .apply(normalize_payment_type)
)

print("\nStandardized Receipt Payment Types:")

print(
    receipts["payment_type"]
    .value_counts()
)

receipts.to_csv(
    receipts_file,
    index=False
)

print(
    "\nReceipts payment types normalized."
)


# ============================================================
# FINAL CHECK
# ============================================================

print("\n" + "=" * 70)
print("NORMALIZATION COMPLETE")
print("=" * 70)