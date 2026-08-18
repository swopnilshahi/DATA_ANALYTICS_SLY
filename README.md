 #DATA_ANALYTICS_SLY

```text
DATA_ANALYTICS/
│
├── 01_DATA/
│   ├── raw/
│   ├── cleaned/
│   └── processed/
│
├── 02_NOTEBOOKS/
│   ├── exploration/
│   ├── analysis/
│   └── reports/
│
├── 03_SCRIPTS/
│   ├── data_cleaning/
│   ├── analysis/
│   └── visualization/
│
├── 04_VISUALIZATIONS/
│
├── 05_REPORTS/
│
├── 06_PROJECTS/
│
├── 07_RESOURCES/
│
├── 08_OUTPUT/
│
└── README.md
```

### Core tools

Since you already have Python/Django experience, I'd use a **Python-first analytics stack**:

| Area               | Tool                 |
| ------------------ | -------------------- |
| Programming        | Python               |
| Environment        | `venv`               |
| IDE                | VS Code              |
| Data manipulation  | pandas               |
| Numerical analysis | NumPy                |
| Visualization      | Matplotlib + Seaborn |
| Statistics         | SciPy                |
| Excel              | openpyxl / pandas    |
| Database           | PostgreSQL           |
| SQL                | PostgreSQL SQL       |
| Notebooks          | Jupyter              |
| BI                 | Power BI             |
| Version control    | Git + GitHub         |

### Step 1 — Create the project

On Windows:

```powershell
mkdir DATA_ANALYTICS
cd DATA_ANALYTICS

python -m venv .venv
.venv\Scripts\activate
```

Then:

```powershell
python -m pip install --upgrade pip

pip install pandas numpy matplotlib seaborn scipy
pip install openpyxl jupyterlab
pip install sqlalchemy psycopg2-binary
```

Check:

```powershell
python --version
pip --version
jupyter --version
```

### Step 2 — Create the folders

```powershell
mkdir 01_DATA
mkdir 01_DATA\raw
mkdir 01_DATA\cleaned
mkdir 01_DATA\processed

mkdir 02_NOTEBOOKS
mkdir 02_NOTEBOOKS\exploration
mkdir 02_NOTEBOOKS\analysis
mkdir 02_NOTEBOOKS\reports

mkdir 03_SCRIPTS
mkdir 03_SCRIPTS\data_cleaning
mkdir 03_SCRIPTS\analysis
mkdir 03_SCRIPTS\visualization

mkdir 04_VISUALIZATIONS
mkdir 05_REPORTS
mkdir 06_PROJECTS
mkdir 07_RESOURCES
mkdir 08_OUTPUT
```

### Step 3 — VS Code

Open the workspace:

```powershell
code .
```

Install these VS Code extensions:

* **Python**
* **Jupyter**
* **Pylance**
* **Python Debugger**
* **Excel Viewer**
* **GitLens** — optional

Then select:

**Ctrl + Shift + P → Python: Select Interpreter → `.venv`**

### Step 4 — First analytics workflow

We'll follow this pipeline for every project:

```text
RAW DATA
   ↓
Data Understanding
   ↓
Data Cleaning
   ↓
Exploratory Data Analysis
   ↓
Statistical Analysis
   ↓
Visualization
   ↓
Insights
   ↓
Report / Dashboard
   ↓
Business Decision
```

For example:

```text
sales.csv
   ↓
pandas
   ↓
clean_sales.csv
   ↓
EDA
   ↓
Matplotlib / Seaborn
   ↓
Power BI Dashboard
   ↓
Sales Insights
```

### Step 5 — Your learning/project path

I recommend we build the workspace progressively:

**Phase 1 — Python for Data Analytics**

* Python fundamentals
* NumPy
* pandas
* data types
* missing values
* filtering
* grouping
* merging
* aggregation

**Phase 2 — Statistics**

* mean/median/mode
* variance & standard deviation
* distributions
* correlation
* probability
* hypothesis testing
* regression

**Phase 3 — Data Visualization**

* Matplotlib
* Seaborn
* dashboards
* storytelling with data

**Phase 4 — SQL**

* SELECT
* WHERE
* GROUP BY
* JOIN
* subqueries
* CTE
* window functions

**Phase 5 — Excel**

* Pivot Tables
* XLOOKUP
* Power Query
* dashboards

**Phase 6 — Power BI**

* Power Query
* data modeling
* DAX
* dashboards
* publishing

**Phase 7 — Real Projects**

* Sales Analytics
* Customer Analytics
* HR Analytics
* Financial Analytics
* Marketing Analytics
* Nepal-focused datasets


----

