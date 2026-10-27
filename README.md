# Data Analytics Workspace — Step-by-Step Notes

> **Purpose:** Clean and analyze the expense book, receipt book, and bank statements; identify transactions represented in multiple sources; and prepare reliable data for reports and dashboards.
>
> These notes record the workflow and results shared so far. Treat matches as candidates until they have been checked against original records.

## 1. Workflow overview

1. Inspect source files.
2. Clean expenses, receipts, and bank statements.
3. Standardize payment types.
4. Convert Nepali Bikram Sambat (BS) dates to Gregorian/AD dates where possible.
5. Review invalid dates.
6. Create a master transaction ledger.
7. Reconcile book entries against bank transactions.
8. Review confirmed and possible matches.
9. Improve matching logic and manually review exceptions.
10. Build financial reports and dashboards after data quality checks.

**Current stage:** Initial reconciliation is complete, but matching logic and unresolved records need further review before final financial totals can be trusted.

## 2. Suggested folder structure

```text
project/
├── 01_DATA/
│   ├── RAW/                         # Original files; do not overwrite
│   └── CLEANED/
│       ├── expenses_clean.csv
│       ├── receipts_clean.csv
│       ├── bank_clean.csv
│       └── bank_duplicates_review.csv
├── 03_SCRIPTS/
│   ├── inspect_data.py
│   ├── clean_data.py
│   ├── normalize_payment_types.py
│   ├── convert_dates.py
│   ├── review_invalid_dates.py
│   ├── create_master_ledger.py
│   ├── reconcile_transactions.py
│   └── review_matches.py
├── 04_OUTPUT/
│   ├── master_transactions.csv
│   ├── reconciliation_results.csv
│   ├── bank_only_transactions.csv
│   ├── all_match_candidates.csv
│   ├── confirmed_matches.csv
│   ├── possible_matches.csv
│   ├── expenses_date_review.csv
│   └── receipts_date_review.csv
└── README.md
```

Folder names in earlier runs varied: some date-review outputs were saved under `08_OUTPUT`, others under `04_OUTPUT`. Use the path printed by the current script.

## 3. Step 1 — Inspect source data

Run from the project root in PowerShell:

```powershell
python .\03_SCRIPTS\inspect_data.py
```

### Sources inspected

- Four bank statement Excel files.
- `EXPENSES.xlsx`, with `Sheet1` and `Copy of Sheet1`.
- `RECEIPT.xlsx`.

### Findings from the inspection run

| Source | Rows reported | Notes |
|---|---:|---|
| `1783949751132..xlsx` | 331 | Includes an opening-balance row |
| `1783949831793..xlsx` | 43 | Includes an opening-balance row |
| `1786279425444..xlsx` | 120 | Overlaps another statement |
| `20260101_20260714.xlsx` | 230 | Earlier statement period |
| `EXPENSES.xlsx` — `Sheet1` | 961 | Unused `Unnamed` columns; 6 missing amounts |
| `EXPENSES.xlsx` — `Copy of Sheet1` | 887 | May be a copy/overlap; verify before combining |
| `RECEIPT.xlsx` | 103 | Contains blank/template rows |

No exact duplicate rows were found within each individual file/sheet during this inspection. This does not rule out overlapping bank statements or the same transaction appearing in different books.

### Checks

- Confirm which expense sheet is authoritative.
- Keep original files unchanged.
- Check that opening-balance rows are excluded from transaction records.
- Investigate missing amounts and blank rows instead of guessing values.

## 4. Step 2 — Clean the data

Run:

```powershell
python .\03_SCRIPTS\clean_data.py
```

### Results from the cleaning run

| Dataset | Clean records | Amount total reported |
|---|---:|---:|
| Expenses | 954 | NPR 2,699,743.00 |
| Receipts | 65 | NPR 1,760,900.00 |
| Bank transactions after overlap removal | 675 | Withdrawals: NPR 3,138,726.69; deposits: NPR 3,146,700.00 |

Outputs reported:

- `01_DATA\CLEANED\expenses_clean.csv`
- `01_DATA\CLEANED\receipts_clean.csv`
- `01_DATA\CLEANED\bank_clean.csv`
- `01_DATA\CLEANED\bank_duplicates_review.csv`

The four bank statements initially produced 716 transaction rows. The script flagged 41 overlapping/duplicate transactions and retained 675 unique bank transactions.

**Important:** The 41 flagged records came from `1786279425444..xlsx`. Review `bank_duplicates_review.csv` and compare dates, descriptions, balances, and statement coverage before accepting all removals. Legitimate transactions can share amounts, so amount alone is not enough to establish a duplicate.

## 5. Step 3 — Standardize payment types

Run:

```powershell
python .\03_SCRIPTS\normalize_payment_types.py
```

The working convention is to group **ONLINE, BANK, and QR** into one broad non-cash category for high-level analysis. If possible, preserve the original method in a separate column for detailed reconciliation.

### Results reported

**Expenses**

| Standardized type | Rows |
|---|---:|
| UNKNOWN | 539 |
| ONLINE | 233 |
| CASH | 182 |

**Receipts**

| Standardized type | Rows |
|---|---:|
| CASH | 46 |
| ONLINE | 15 |
| UNKNOWN | 2 |
| CHEQUE | 2 |

`UNKNOWN` means the source does not provide enough evidence to classify the payment. Do not automatically treat it as cash or online.

## 6. Step 4 — Convert BS dates to AD dates

Run:

```powershell
python .\03_SCRIPTS\convert_dates.py
```

The expense and receipt books use Bikram Sambat dates, while bank statements use Gregorian/AD dates. Convert dates so records can be compared across sources.

### Latest reported conversion results

| Dataset | Total records | Converted | Unresolved |
|---|---:|---:|---:|
| Expenses | 954 | 914 | 40 |
| Receipts | 65 | 61 | 4 |
| **Total** | **1,019** | **975** | **44** |

Reported AD ranges:

- Expenses: 2026-04-14 through 2026-08-17.
- Receipts: 2026-04-18 through 2026-08-16.

An earlier run reported more failures. The latest run reported 40 expense and 4 receipt failures. Regenerate review files after corrections to keep counts consistent.

### Date-conversion rules

- Preserve both `date_bs` and `date_ad`.
- Do not silently replace invalid dates with guesses.
- Verify month/day ordering in ambiguous values such as `2/29/2083`.
- Do not validate BS dates using Gregorian month lengths; the calendars differ.
- Leave unresolved `date_ad` values blank until the original entry or a trusted calendar conversion confirms the intended date.

## 7. Step 5 — Review invalid dates

Run:

```powershell
python .\03_SCRIPTS\review_invalid_dates.py
```

An earlier review listed 47 invalid expense dates and 9 invalid receipt dates. A later conversion run reported 40 expense and 4 receipt failures. These outputs were produced at different stages or with different conversion logic. Regenerate the review from the latest cleaned data before relying on the final count.

Examples of suspicious values:

- `2/29/2083`
- `2/30/2083`
- `2/31/2083`
- `3/21/20083`
- `3/32/2083`
- `31/4/2083` / `31/04/2083`

These are review cases, not automatic corrections. Check the original workbook and nearby entries. For each manual correction, record the original value, corrected value, reason, and reviewer in an audit log.

## 8. Step 6 — Create the master ledger

Run:

```powershell
python .\03_SCRIPTS\create_master_ledger.py
```

Output:

```text
04_OUTPUT\master_transactions.csv
```

### Results reported

| Source | Transactions |
|---|---:|
| Expense book | 954 |
| Bank statements | 675 |
| Receipt book | 65 |
| **Total ledger rows** | **1,694** |

Reported date range: 2026-01-01 through 2026-08-17.

Expected traceability fields include:

- `transaction_id`
- `date_ad`
- `date_bs`
- `transaction_type`
- `payment_method`
- `description`
- `amount`
- `money_flow`
- `source`
- `source_id`

### Accounting caution

The master ledger combines records from all sources, so the same real-world movement may appear more than once. For example, a customer payment may be recorded in the receipt book and also appear as a bank deposit. **Do not sum all master-ledger rows as unique money movements.** Reconcile first to prevent double counting.

The initial output reported 155 inflow rows totaling NPR 4,907,600 and 1,539 outflow rows totaling NPR 5,838,469.69. These are raw ledger summaries, not verified revenue or expense totals.

## 9. Step 7 — Run initial reconciliation

Run:

```powershell
python .\03_SCRIPTS\reconcile_transactions.py
```

Outputs:

- `04_OUTPUT\reconciliation_results.csv`
- `04_OUTPUT\bank_only_transactions.csv`

### Initial results reported

| Book-entry status | Rows | Amount |
|---|---:|---:|
| MATCHED | 42 | NPR 343,139 |
| POSSIBLE_MATCH | 193 | NPR 709,115 |
| CASH_OR_CHEQUE | 230 | NPR 1,325,728 |
| UNMATCHED | 528 | NPR 2,000,693 |
| INVALID_DATE | 26 | NPR 81,968 |

- Bank transactions: 675
- Bank transactions reported as matched: 235
- Bank-only transactions: 179

These are outputs of the current matching rules, not an audited reconciliation.

### Interpret statuses carefully

- `MATCHED`: accepted by current rules; sample-check against source records.
- `POSSIBLE_MATCH`: needs manual review.
- `CASH_OR_CHEQUE`: use only when the book's payment method supports this classification. `UNKNOWN` should not automatically become cash.
- `UNMATCHED`: no match was found by the current rules; this does not prove an error.
- `INVALID_DATE`: matching may be blocked until the date is resolved.

## 10. Step 8 — Review match candidates

Run:

```powershell
python .\03_SCRIPTS\review_matches.py
```

Outputs:

- `04_OUTPUT\all_match_candidates.csv`
- `04_OUTPUT\confirmed_matches.csv`
- `04_OUTPUT\possible_matches.csv`

Latest run reported 42 confirmed matches and 193 possible matches. Average match scores were approximately 72.27 for `MATCHED` and 19.37 for `POSSIBLE_MATCH`.

### Issue found

Description similarity can under-rate a real match when the book says, for example, `CHANA GEDA, CHAUSER GGEDA` and the bank uses a merchant name or QR reference. Same amount and date can be strong evidence, but should not automatically confirm a match because multiple transactions can share an amount.

## 11. Next improvement — one-to-one reconciliation

Create an improved reconciliation script that:

1. Checks money-flow direction (in/out) before matching.
2. Compares exact amount.
3. Compares date: same day first, then ±1 day, then a wider review window.
4. Uses normalized description similarity as supporting evidence.
5. Prevents one bank transaction from matching multiple book entries.
6. Flags multiple candidates with the same amount/date.
7. Separates high-confidence candidates from manual-review cases.
8. Exports source IDs and a reason for each proposed match.

**Do not auto-confirm every exact-amount match.** Check direction, payment method, references, merchant/customer details, and source evidence.

## 12. Recommended next steps

- [ ] Confirm the authoritative expense sheet and handle copied/template rows.
- [ ] Regenerate date review files using the current conversion script.
- [ ] Resolve or document invalid BS dates.
- [ ] Review the 41 bank-statement overlap records.
- [ ] Improve reconciliation with one-to-one matching and amount/date/direction checks.
- [ ] Manually review `POSSIBLE_MATCH` candidates.
- [ ] Investigate unmatched non-cash book entries and bank-only transactions.
- [ ] Verify opening/closing balances and statement continuity.
- [ ] Produce monthly receipt and expense reports after reconciliation.
- [ ] Build dashboard charts after totals and matches are validated.
- [ ] Maintain an audit log of manual corrections.

## 13. Analytics to build after reconciliation

- Monthly expenses by category and payment method.
- Monthly receipts by service/reason.
- Cash vs. non-cash movements.
- Bank withdrawals and deposits.
- Receipt-book entries not found in bank deposits.
- Expense-book entries not found in bank withdrawals.
- Bank transactions not explained by the books.
- Refunds, loans, salaries, transfers, and bank fees separately from operating income/expenses.
- Month-end bank balance and reconciliation differences.

Do not classify every deposit as revenue or every withdrawal as an expense. Transfers, loan proceeds/repayments, refunds, owner movements, and bank fees may require separate accounting categories.

## 14. Reproducibility checklist

1. Open PowerShell in the project root.
2. Activate the project's virtual environment if one is used.
3. Back up original files.
4. Run scripts in sequence, using their actual filenames.
5. Check printed row counts, totals, and output paths.
6. Confirm downstream scripts use the latest outputs.
7. Save review outputs before manual corrections.
8. Never overwrite raw source data with cleaned or corrected data.

Example sequence:

```powershell
python .\03_SCRIPTS\inspect_data.py
python .\03_SCRIPTS\clean_data.py
python .\03_SCRIPTS\normalize_payment_types.py
python .\03_SCRIPTS\convert_dates.py
python .\03_SCRIPTS\review_invalid_dates.py
python .\03_SCRIPTS\create_master_ledger.py
python .\03_SCRIPTS\reconcile_transactions.py
python .\03_SCRIPTS\review_matches.py
```

After changing data or scripts, rerun all affected downstream steps so the ledger and reconciliation outputs stay consistent.

## 15. Current project status

**Completed:** source inspection, initial cleaning, payment-type normalization, initial BS-to-AD conversion, master ledger creation, initial reconciliation, and match-candidate exports.

**In progress:** invalid-date resolution, statement-overlap verification, and improved one-to-one reconciliation.

**Not ready to finalize:** audited income/expense totals or final dashboards. Existing figures are exploratory until dates, overlaps, and matches are reviewed.

## 16. Data privacy

Financial records may include names, addresses, bank references, and customer details. Keep raw files and detailed reconciliation outputs access-controlled. Share anonymized summaries when personal or bank details are not needed.
