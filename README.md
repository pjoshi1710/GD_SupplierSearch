## Supplier Data Processor

A desktop tool to clean and enrich supplier data files (CSV/Excel) using the GlobalDatabase API.

## 📦 Setup (If You’re a Developer)

1. Clone/download this repository.
2. Install Python 3.9 or later.
3. Install dependencies:

```bash
pip install -r requirements.txt


Run the app:
```bash
python main.py

🔍 Features
Supports .csv and .xlsx
Accepts sheet name input at runtime
Identifies missing values in:
  Postcodes
  Number of Employees
Uses Region (ONS Definition) to generate country_code
Fetches supplier details using the GlobalDatabase API
Exports enriched results as Excel
