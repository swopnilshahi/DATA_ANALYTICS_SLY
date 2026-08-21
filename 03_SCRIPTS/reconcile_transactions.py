from pathlib import Path
import pandas as pd
import re
from rapidfuzz.fuzz import token_set_ratio


INPUT_FILE = Path(
    "04_OUTPUT/master_transactions.csv"
)

OUTPUT_FOLDER = Path("04_OUTPUT")

OUTPUT_FOLDER.mkdir(exist_ok=True)


# ============================================================
# SETTINGS
# ============================================================

DATE_TOLERANCE_DAYS = 3

# Minimum description similarity
DESCRIPTION_SIMILARITY_THRESHOLD = 35


# ============================================================
# CLEAN DESCRIPTION
# ============================================================

def clean_text(text):

    if pd.isna(text):
        return ""

    text = str(text).upper()

    # Remove numbers and special characters
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"[^A-Z\s]", " ", text)

    # Remove repeated spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# LOAD MASTER DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

df["date_ad"] = pd.to_datetime(
    df["date_ad"],
    errors="coerce"
)

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="coerce"
)

df["clean_description"] = df[
    "description"
].apply(clean_text)


# ============================================================
# SEPARATE BANK AND BOOK RECORDS
# ============================================================

bank = df[
    df["source"] == "BANK_STATEMENT"
].copy()

book = df[
    df["source"] != "BANK_STATEMENT"
].copy()


# ============================================================
# PREPARE RESULT COLUMNS
# ============================================================

results = []

matched_bank_ids = set()


# ============================================================
# MATCH EACH BOOK TRANSACTION
# ============================================================

for _, transaction in book.iterrows():

    transaction_id = transaction["transaction_id"]

    # --------------------------------------------
    # CASH / CHEQUE transactions
    # --------------------------------------------

    if transaction["payment_method"] in [
        "CASH",
        "CHEQUE"
    ]:

        results.append({
            "transaction_id": transaction_id,
            "status": "CASH_OR_CHEQUE",
            "matched_bank_transaction_id": None,
            "date_difference_days": None,
            "amount": transaction["amount"],
            "match_score": None
        })

        continue


    # --------------------------------------------
    # Skip invalid dates
    # --------------------------------------------

    if pd.isna(transaction["date_ad"]):

        results.append({
            "transaction_id": transaction_id,
            "status": "INVALID_DATE",
            "matched_bank_transaction_id": None,
            "date_difference_days": None,
            "amount": transaction["amount"],
            "match_score": None
        })

        continue


    # --------------------------------------------
    # Find bank candidates
    # --------------------------------------------

    candidates = bank[
        (
            bank["money_flow"]
            == transaction["money_flow"]
        )
        &
        (
            bank["amount"]
            == transaction["amount"]
        )
        &
        (
            bank["date_ad"]
            >= transaction["date_ad"]
            - pd.Timedelta(
                days=DATE_TOLERANCE_DAYS
            )
        )
        &
        (
            bank["date_ad"]
            <= transaction["date_ad"]
            + pd.Timedelta(
                days=DATE_TOLERANCE_DAYS
            )
        )
        &
        (
            ~bank["transaction_id"]
            .isin(matched_bank_ids)
        )
    ].copy()


    # --------------------------------------------
    # No candidates
    # --------------------------------------------

    if len(candidates) == 0:

        results.append({
            "transaction_id": transaction_id,
            "status": "UNMATCHED",
            "matched_bank_transaction_id": None,
            "date_difference_days": None,
            "amount": transaction["amount"],
            "match_score": None
        })

        continue


    # --------------------------------------------
    # Calculate similarity
    # --------------------------------------------

    candidates["description_score"] = candidates[
        "clean_description"
    ].apply(
        lambda bank_description:
        token_set_ratio(
            transaction["clean_description"],
            bank_description
        )
    )

    candidates["date_difference_days"] = (
        candidates["date_ad"]
        - transaction["date_ad"]
    ).abs().dt.days


    # Prefer:
    # 1. Higher description similarity
    # 2. Smaller date difference

    candidates = candidates.sort_values(
        by=[
            "description_score",
            "date_difference_days"
        ],
        ascending=[
            False,
            True
        ]
    )

    best_match = candidates.iloc[0]

    score = best_match[
        "description_score"
    ]

    # --------------------------------------------
    # Determine status
    # --------------------------------------------

    if score >= DESCRIPTION_SIMILARITY_THRESHOLD:

        status = "MATCHED"

    else:

        status = "POSSIBLE_MATCH"


    # --------------------------------------------
    # Store match
    # --------------------------------------------

    results.append({
        "transaction_id": transaction_id,
        "status": status,
        "matched_bank_transaction_id":
            best_match["transaction_id"],
        "date_difference_days":
            best_match["date_difference_days"],
        "amount":
            transaction["amount"],
        "match_score":
            score
    })


    # Reserve bank transaction
    matched_bank_ids.add(
        best_match["transaction_id"]
    )


# ============================================================
# CREATE RESULTS DATAFRAME
# ============================================================

results_df = pd.DataFrame(results)


# ============================================================
# MERGE RESULTS WITH BOOK DATA
# ============================================================

reconciliation = book.merge(
    results_df,
    on="transaction_id",
    how="left",
    suffixes=("", "_result")
)


# ============================================================
# FIND BANK-ONLY TRANSACTIONS
# ============================================================

bank_only = bank[
    ~bank["transaction_id"]
    .isin(matched_bank_ids)
].copy()

bank_only["status"] = "BANK_ONLY"


# ============================================================
# SAVE FILES
# ============================================================

reconciliation_file = (
    OUTPUT_FOLDER /
    "reconciliation_results.csv"
)

bank_only_file = (
    OUTPUT_FOLDER /
    "bank_only_transactions.csv"
)


reconciliation.to_csv(
    reconciliation_file,
    index=False
)

bank_only.to_csv(
    bank_only_file,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("BANK RECONCILIATION COMPLETE")
print("=" * 70)

print("\nBOOK TRANSACTION STATUS:")

print(
    reconciliation["status"]
    .value_counts()
)


print("\nSTATUS AMOUNT SUMMARY:")

print(
    reconciliation.groupby("status")["amount"]
    .agg(
        ["count", "sum"]
    )
)


print("\nBANK TRANSACTIONS:")

print(f"Total bank transactions: {len(bank)}")

print(
    f"Matched bank transactions: "
    f"{len(matched_bank_ids)}"
)

print(
    f"Bank-only transactions: "
    f"{len(bank_only)}"
)


print("\nFILES CREATED:")

print(reconciliation_file)

print(bank_only_file)


print("\n" + "=" * 70)
print("RECONCILIATION FINISHED")
print("=" * 70)