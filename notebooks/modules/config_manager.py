# import os
# import requests
# from dotenv import load_dotenv

# # === Load env ===
# load_dotenv()
# SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
# API_KEY = os.getenv("GOOGLE_SHEETS_API_KEY")

# SHEET_NAME = "Config"
# url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{SHEET_NAME}?key={API_KEY}"
# response = requests.get(url).json()

# values = response.get("values", [])
# if not values:
#     raise Exception("No data found in sheet!")

# rows = values[1:]  # skip header row (Parameter, Value, Description)

# # === Write config ===
# with open("config.cfg", "w") as f:
#     for row in rows:
#         if len(row) >= 2:   # Parameter + Value
#             key, value = row[0].strip(), row[1].strip()
#             f.write(f"{key}={value}\n")
#         elif len(row) == 1: # Only Parameter, no value
#             key = row[0].strip()
#             f.write(f"{key}=\n")

# print("✅ config.cfg updated with Parameter=Value pairs!")


# --------------------------------- Detailed code with error handling ----------------------------------

# import os
# import requests
# from dotenv import load_dotenv
# import time

# # === Load env ===
# load_dotenv()
# SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
# API_KEY = os.getenv("GOOGLE_SHEETS_API_KEY")

# # Debug environment variables
# if not SHEET_ID or not API_KEY:
#     raise Exception("Missing SHEET_ID or API_KEY in .env file")

# # === Fetch data from Google Sheets ===
# SHEET_NAME = "Config"
# timestamp = int(time.time())  # Cache-busting
# url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{SHEET_NAME}?key={API_KEY}&t={timestamp}"

# try:
#     response = requests.get(url).json()
# except requests.RequestException as e:
#     raise Exception(f"Failed to fetch data from Google Sheets: {e}")

# # Check for valid data
# values = response.get("values", [])
# if not values or len(values) < 2:
#     raise Exception("No valid data found in sheet! Ensure it has a header and at least one data row.")

# # Debug: Print fetched data
# print("Fetched values:", values)

# rows = values[1:]  # Skip header row (Parameter, Value, Description)

# # === Write config ===
# try:
#     with open("config.cfg", "w") as f:
#         for row in rows:
#             if len(row) >= 2:  # Parameter + Value
#                 key, value = row[0].strip(), row[1].strip()
#                 f.write(f"{key}={value}\n")
#             elif len(row) == 1:  # Only Parameter, no value
#                 key = row[0].strip()
#                 f.write(f"{key}=\n")
# except PermissionError:
#     raise Exception("Error: No permission to write to config.cfg")
# except Exception as e:
#     raise Exception(f"Error writing to file: {e}")

# print("✅ config.cfg updated with Parameter=Value pairs!")




# -------------------------- With Timestamp writing ------------------------------------------------
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# === Load env ===
load_dotenv()
SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
API_KEY = os.getenv("GOOGLE_SHEETS_API_KEY")

SHEET_NAME = "Config"
url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{SHEET_NAME}?key={API_KEY}"
response = requests.get(url).json()

values = response.get("values", [])
if not values:
    raise Exception("No data found in sheet!")

rows = values[1:]  # skip header row (Parameter, Value, Description)

# === Write config ===
with open("config.cfg", "w") as f:
    # Write timestamp as a comment
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    f.write(f"# Last updated: {timestamp}\n\n")
    for row in rows:
        if len(row) >= 2:   # Parameter + Value
            key, value = row[0].strip(), row[1].strip()
            f.write(f"{key}={value}\n")
        elif len(row) == 1: # Only Parameter, no value
            key = row[0].strip()
            f.write(f"{key}=\n")

print("✅ config.cfg updated with Parameter=Value pairs!")