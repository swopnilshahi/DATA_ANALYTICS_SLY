from pathlib import Path
import pandas as pd
import nepali_datetime

CLEANED_FOLDER = Path("01_DATA/CLEANED")


def bs_to_ad(date_value):
    """
    Convert BS date (2083-01-05)
    to AD date.
    """

    if pd.isna(date_value):
        return pd.NaT

    try:
        date_value = pd.to_datetime(date_value)

        bs_year = date_value.year
        bs_month = date_value.month
        bs_day = date_value.day

        bs_date = nepali_datetime.date(
            bs_year,
            bs_month,
            bs_day
        )

        ad_date = bs_date.to_datetime_date()

        return pd.Timestamp(ad_date)

    except Exception as e:
        print(f"Date conversion error: {date_value} -> {e}")
        return pd.NaT


def convert_file(filename, date_column):

    file_path = CLEANED_FOLDER / filename

    print("\n" + "=" * 70)
    print(f"CONVERTING: {filename}")
    print("=" * 70)

    df = pd.read_csv(file_path)

    print(f"Records before conversion: {len(df)}")

    df["date_ad"] = df[date_column].apply(
        bs_to_ad
    )

    print(
        f"Conversion failures: "
        f"{df['date_ad'].isna().sum()}"
    )

    print("\nFirst 10 conversions:")

    print(
        df[
            [
                date_column,
                "date_ad"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    # Save updated file
    df.to_csv(
        file_path,
        index=False
    )

    print(f"\nSaved: {file_path}")

    return df


expenses = convert_file(
    "expenses_clean.csv",
    "date_bs"
)

receipts = convert_file(
    "receipts_clean.csv",
    "date_bs"
)


print("\n" + "=" * 70)
print("DATE CONVERSION COMPLETE")
print("=" * 70)

print(
    f"\nExpense AD Range: "
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