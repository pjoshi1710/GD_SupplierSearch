import pandas as pd
import requests
import time
import logging
import numpy as np
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv("GLOBALDB_API_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_file(input_file_path, output_folder, sheet_name=None):
    try:
        # Detect file type
        file_ext = os.path.splitext(input_file_path)[1].lower()

        if file_ext == '.csv':
            df = pd.read_csv(input_file_path)
        elif file_ext in ['.xls', '.xlsx']:
            df = pd.read_excel(input_file_path, sheet_name=sheet_name)
        else:
            raise ValueError("Unsupported file format. Please use CSV or Excel (.xls/.xlsx) files.")

        df.columns = df.columns.str.strip()

        # Clean up common missing values
        df.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Fill or drop basic required columns
        required_columns = ["Supplier Name", "Region (ONS Definition)"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise KeyError(f"Missing required columns: {missing_columns}")

        # Print missing value counts
        postcode_missing = df['Postcode'].isna().sum() if 'Postcode' in df.columns else 0
        employees_missing = df['Number of Employees (Detailed Range)'].isna().sum() if 'Number of Employees (Detailed Range)' in df.columns else 0

        logging.info(f"Missing Postcodes: {postcode_missing}")
        logging.info(f"Missing Number of Employees (Detailed Range): {employees_missing}")

        # Country code mapping based on Region (ONS Definition)
        region_to_country_code = {
        "United Kingdom": "GB", "England": "GB","Scotland": "GB","Wales": "GB","Northern Ireland": "GB",
        "North East": "GB", "North West": "GB", "East of England": "GB", "South East": "GB", "South West": "GB",
        "Yorkshire and The Humber": "GB", "London": "GB", "West Midlands": "GB","East Midlands": "GB","Isle of Man": "GB",
        "France": "FR", "Germany": "DE","Italy": "IT", "Spain": "ES"
        # Extend as needed
        }

        df['country_code'] = df['Region (ONS Definition)'].map(region_to_country_code)
        df['country_code'].fillna('Unknown', inplace=True)

        # Filter only suppliers where postcode or employees are missing
        condition = (df['Postcode'].isna() if 'Postcode' in df.columns else False) | \
                    (df['Number of Employees (Detailed Range)'].isna() if 'Number of Employees (Detailed Range)' in df.columns else False)
        filtered_df = df[condition].copy()

        # If empty, skip API call
        if filtered_df.empty:
            messagebox.showinfo("Info", "No missing data to process.")
            return

        headers = {
            "Authorization": f"Token {API_TOKEN}"
        }

        parsed_results = []
        for _, record in filtered_df.iterrows():
            payload = {
                "name": record["Supplier Name"],
                "country_code": record["country_code"],
                "page": 1
            }

            try:
                r = requests.post("https://api.globaldatabase.com/v2/overview", json=payload, headers=headers)
                r.raise_for_status()
                response_data = r.json()
                filtered_data = response_data.get("data", [])

                for entry in filtered_data:
                    parsed_results.append({
                        "Registered Name": record['Supplier Name'],
                        "id": entry.get('id'),
                        "registration_number": entry.get('registration_number'),
                        "name": entry.get('name'),
                        "status": entry.get('status'),
                        "country_code": entry.get('country_code')
                    })

            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching data for {record['Supplier Name']}: {e}")
                continue

            time.sleep(1)

        result_df = pd.DataFrame(parsed_results)
        detailed_results = []

        for _, record in result_df.iterrows():
            company_id = record["id"]
            try:
                r = requests.get(f"https://api.globaldatabase.com/v2/companies/{company_id}", headers=headers)
                r.raise_for_status()
                company_data = r.json()

                detailed_results.append({
                    "id": company_id,
                    "Registered Name": record["Registered Name"],
                    "name": company_data.get("name"),
                    "registration_number": company_data.get("registration_number"),
                    "status": company_data.get("status"),
                    "company_legal_form": company_data.get("company_legal_form"),
                    "size": company_data.get("size"),
                    "country_code": company_data.get("country_code"),
                    "address_street": company_data.get("address_street"),
                    "address_location": company_data.get("address_location"),
                    "address_city": company_data.get("address_city"),
                    "country_region": company_data.get("country_region"),
                    "Postcode": company_data.get("zip_code"),
                    "country_name": company_data.get("country_name"),
                    "company_phone": company_data.get("company_phone"),
                    "company_email": company_data.get("company_email"),
                    "company_fax": company_data.get("company_fax"),
                    "company_website": company_data.get("company_website"),
                    "brands": company_data.get("brands"),
                    "vat_number": company_data.get("vat_number"),
                    "founding_date": company_data.get("founding_date"),
                    "industry": company_data.get("industry"),
                    "sic": company_data.get("sic"),
                    "twitter": company_data.get("twitter"),
                    "linkedin": company_data.get("linkedin"),
                    "facebook": company_data.get("facebook")
                })

            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching detailed data for company ID {company_id}: {e}")
                continue

            time.sleep(1)

        detailed_df = pd.DataFrame(detailed_results)

        merged_df = pd.merge(df, detailed_df, left_on="Supplier Name", right_on="Registered Name", how="left")

        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_path = os.path.join(output_folder, f"results_construction_{timestamp}.xlsx")
        merged_df.to_excel(output_file_path, index=False)

        logging.info(f"Processing complete. File saved to {output_file_path}")
        messagebox.showinfo("Success", f"Processing complete.\nFile saved to:\n{output_file_path}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        messagebox.showerror("Error", str(e))



def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel or CSV files", "*.xlsx *.xls *.csv")])
    if file_path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, file_path)


def select_output_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, folder_path)


def run_app():
    input_path = input_entry.get()
    output_path = output_entry.get()

    if not input_path or not output_path:
        messagebox.showwarning("Missing info", "Please select both input file and output folder.")
        return

    ext = os.path.splitext(input_path)[1].lower()
    sheet_name = None
    if ext in ['.xls', '.xlsx']:
        sheet_name = simpledialog.askstring("Sheet Name", "Enter the Excel sheet name to read:")

    run_button.config(state="disabled", text="Processing...", bg="gray")
    root.update()

    try:
        process_file(input_path, output_path, sheet_name)
    finally:
        run_button.config(state="normal", text="Run Process", bg="green")
        root.update()


# GUI setup
root = tk.Tk()
root.title("Supplier Data Processor")

tk.Label(root, text="Select Input File (.csv or .xlsx):").grid(row=0, column=0, padx=10, pady=5, sticky='w')
input_entry = tk.Entry(root, width=60)
input_entry.grid(row=0, column=1, padx=10)
tk.Button(root, text="Browse", command=select_input_file).grid(row=0, column=2, padx=5)

tk.Label(root, text="Select Output Folder:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
output_entry = tk.Entry(root, width=60)
output_entry.grid(row=1, column=1, padx=10)
tk.Button(root, text="Browse", command=select_output_folder).grid(row=1, column=2, padx=5)

run_button = tk.Button(root, text="Run Process", command=run_app, bg="green", fg="white", width=20)
run_button.grid(row=2, column=1, pady=20)

root.mainloop()