from pathlib import Path
import pandas as pd

CLEANED_FOLDER = Path("01_DATA/CLEANED")
OUTPUT_FOLDER = Path("08_OUTPUT")

OUTPUT_FOLDER.mkdir(exist_ok=True)


def review_invalid_dates(filename, transaction_type):

    file_path = CLEANED_FOLDER / filename

    df = pd.read_csv(file_path)

    # date_ad is empty = conversion failed
    invalid = df[
        df["date_ad"].isna()
    ].copy()

    print("\n" + "=" * 80)
    print(f"{transaction_type.upper()} - INVALID DATE REVIEW")
    print("=" * 80)

    print(f"Total invalid dates: {len(invalid)}")

    if len(invalid) > 0:

        columns_to_show = [
            col for col in df.columns
            if col in [
                "expense_id",
                "receipt_id",
                "date_bs",
                "date_ad",
                "particular",
                "name",
                "reason",
                "amount",
                "payment_type"
            ]
        ]

        print(
            "\nInvalid transactions:\n"
        )

        print(
            invalid[columns_to_show]
            .to_string(index=False)
        )

        output_file = (
            OUTPUT_FOLDER /
            f"{transaction_type}_invalid_dates.csv"
        )

        invalid.to_csv(
            output_file,
            index=False
        )

        print(f"\nSaved review file: {output_file}")

    return invalid


invalid_expenses = review_invalid_dates(
    "expenses_clean.csv",
    "expenses"
)

invalid_receipts = review_invalid_dates(
    "receipts_clean.csv",
    "receipts"
)


print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

print(f"Invalid expense dates : {len(invalid_expenses)}")
print(f"Invalid receipt dates : {len(invalid_receipts)}")

print(
    f"\nTotal transactions needing date review: "
    f"{len(invalid_expenses) + len(invalid_receipts)}"
)