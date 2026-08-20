from pathlib import Path
import pandas as pd
import nepali_datetime
import re

CLEANED_FOLDER = Path("01_DATA/CLEANED")
OUTPUT_FOLDER = Path("04_OUTPUT")

OUTPUT_FOLDER.mkdir(exist_ok=True)


# ============================================================
# PARSE BS DATE
# ============================================================

def parse_bs_date(value):

    if pd.isna(value):
        return None

    value = str(value).strip()

    # Remove time portion if present
    value = value.split(" ")[0]

    # Fix obvious year typo
    value = value.replace("20083", "2083")

    # Normalize separators
    value = re.sub(r"[-.]", "/", value)

    parts = value.split("/")

    if len(parts) != 3:
        return None

    try:

        a = int(parts[0])
        b = int(parts[1])
        c = int(parts[2])

        # Case 1: YYYY/MM/DD
        if c < 100 and a >= 2000:
            year = a
            month = b
            day = c

        # More reliable: YYYY/MM/DD
        elif a >= 2000:
            year = a
            month = b
            day = c

        # Case 2: DD/MM/YYYY
        else:
            day = a
            month = b
            year = c

        return year, month, day

    except ValueError:
        return None


# ============================================================
# BS → AD CONVERSION
# ============================================================

def bs_to_ad(value):

    parsed = parse_bs_date(value)

    if parsed is None:
        return pd.NaT

    year, month, day = parsed

    try:

        bs_date = nepali_datetime.date(
            year,
            month,
            day
        )

        ad_date = bs_date.to_datetime_date()

        return pd.Timestamp(ad_date)

    except Exception:
        return pd.NaT


# ============================================================
# CONVERT FILE
# ============================================================

def convert_file(filename, date_column, transaction_type):

    file_path = CLEANED_FOLDER / filename

    print("\n" + "=" * 70)
    print(f"CONVERTING {transaction_type.upper()}")
    print("=" * 70)

    df = pd.read_csv(file_path)

    # Recalculate from original BS date
    df["date_ad"] = df[date_column].apply(
        bs_to_ad
    )

    failures = df[
        df["date_ad"].isna()
    ].copy()

    print(f"Total records: {len(df)}")
    print(f"Successfully converted: {len(df) - len(failures)}")
    print(f"Conversion failures: {len(failures)}")

    print("\nFirst 10 conversions:")

    print(
        df[
            [date_column, "date_ad"]
        ]
        .head(10)
        .to_string(index=False)
    )

    # Save unresolved dates separately
    if len(failures) > 0:

        review_file = (
            OUTPUT_FOLDER /
            f"{transaction_type}_date_review.csv"
        )

        failures.to_csv(
            review_file,
            index=False
        )

        print(
            f"\nUnresolved dates saved to: "
            f"{review_file}"
        )

    # Save corrected dataset
    df.to_csv(
        file_path,
        index=False
    )

    return df


# ============================================================
# RUN
# ============================================================

expenses = convert_file(
    "expenses_clean.csv",
    "date_bs",
    "expenses"
)

receipts = convert_file(
    "receipts_clean.csv",
    "date_bs",
    "receipts"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("DATE CONVERSION COMPLETE")
print("=" * 70)

print(
    f"Expense AD Range: "
    f"{expenses['date_ad'].min()} "
    f"to "
    f"{expenses['date_ad'].max()}"
)

print(
    f"Receipt AD Range: "
    f"{receipts['date_ad'].min()} "
    f"to "
    f"{receipts['date_ad'].max()}"
)