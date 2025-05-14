# 🏗️ GlobalDB Supplier Search App

A Python GUI application to clean, enrich, and validate supplier data using the [Global Database API](https://globaldatabase.com).  
No Python installation required for end users — just double-click the `.exe`.

---

## 📦 Features

- Input: Excel/CSV supplier data
- Cleans and finds missing postcodes or employee counts
- Maps "Region (ONS Definition)" to country codes
- Enriches data using Global Database API
- Outputs a new Excel file with matched details
- Built with `tkinter`, `pandas`, `requests`

---

## 🚀 Quick Start for Developers

```bash
git clone https://github.com/pjoshi1710/GD_SupplierSearch.git
cd GD_SupplierSearch
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

To run:
python main.py

📄 Files
main.py – GUI + logic
.env – API token (not tracked in Git)
requirements.txt – dependencies
README.md – this file

💬 Questions?
Feel free to raise an issue or email pjoshi@elcom.com.
