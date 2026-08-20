from pathlib import Path
import pandas as pd

RAW_FOLDER = Path("01_DATA/RAW")

files = list(RAW_FOLDER.glob("*.xlsx"))

for file in files:
    print("\n" + "=" * 70)
    print(f"FILE: {file.name}")
    print("=" * 70)

    excel_file = pd.ExcelFile(file)

    print("\nSHEETS:")
    print(excel_file.sheet_names)

    for sheet in excel_file.sheet_names:
        print("\n" + "-" * 50)
        print(f"SHEET: {sheet}")
        print("-" * 50)

        df = pd.read_excel(file, sheet_name=sheet)

        print(f"\nRows: {len(df)}")
        print(f"Columns: {len(df.columns)}")

        print("\nCOLUMN NAMES:")
        for col in df.columns:
            print(f" - {col}")

        print("\nDATA TYPES:")
        print(df.dtypes)

        print("\nMISSING VALUES:")
        print(df.isnull().sum())

        print("\nEXACT DUPLICATE ROWS:")
        print(df.duplicated().sum())

        print("\nFIRST 5 ROWS:")
        print(df.head())