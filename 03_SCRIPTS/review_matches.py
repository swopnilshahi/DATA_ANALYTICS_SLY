from pathlib import Path
import pandas as pd

OUTPUT_FOLDER = Path("04_OUTPUT")

file_path = OUTPUT_FOLDER / "reconciliation_results.csv"

df = pd.read_csv(file_path)

# Only transactions that have a bank match candidate
matches = df[
    df["matched_bank_transaction_id"].notna()
].copy()

# Sort by confidence
matches = matches.sort_values(
    by=["status", "match_score", "date_difference_days"],
    ascending=[True, False, True]
)

columns = [
    "transaction_id",
    "transaction_type",
    "date_ad",
    "payment_method",
    "description",
    "amount",
    "status",
    "matched_bank_transaction_id",
    "date_difference_days",
    "match_score",
]

# Keep only columns that actually exist
columns = [col for col in columns if col in matches.columns]

# ------------------------------------------------------------
# SAVE ALL MATCHES
# ------------------------------------------------------------

matches.to_csv(
    OUTPUT_FOLDER / "all_match_candidates.csv",
    index=False
)

# ------------------------------------------------------------
# SAVE CONFIRMED MATCHES
# ------------------------------------------------------------

confirmed = matches[
    matches["status"] == "MATCHED"
].copy()

confirmed.to_csv(
    OUTPUT_FOLDER / "confirmed_matches.csv",
    index=False
)

# ------------------------------------------------------------
# SAVE POSSIBLE MATCHES
# ------------------------------------------------------------

possible = matches[
    matches["status"] == "POSSIBLE_MATCH"
].copy()

possible.to_csv(
    OUTPUT_FOLDER / "possible_matches.csv",
    index=False
)

# ------------------------------------------------------------
# PRINT SAMPLES
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("MATCH REVIEW")
print("=" * 80)

print(f"\nConfirmed matches: {len(confirmed)}")
print(f"Possible matches : {len(possible)}")

print("\nMATCH SCORE SUMMARY:")

print(
    matches.groupby("status")["match_score"]
    .agg(["count", "min", "max", "mean"])
)

print("\n" + "=" * 80)
print("TOP 20 CONFIRMED MATCHES")
print("=" * 80)

print(
    confirmed[columns]
    .head(20)
    .to_string(index=False)
)

print("\n" + "=" * 80)
print("TOP 20 POSSIBLE MATCHES")
print("=" * 80)

print(
    possible[columns]
    .sort_values("match_score", ascending=False)
    .head(20)
    .to_string(index=False)
)

print("\nFILES CREATED:")
print("04_OUTPUT/all_match_candidates.csv")
print("04_OUTPUT/confirmed_matches.csv")
print("04_OUTPUT/possible_matches.csv")