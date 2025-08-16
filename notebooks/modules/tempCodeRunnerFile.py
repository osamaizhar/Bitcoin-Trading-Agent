import os
import requests
from dotenv import load_dotenv

# === Step 1: Load .env ===
load_dotenv()
SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
API_KEY = os.getenv("GOOGLE_SHEETS_API_KEY")

# === Step 2: Fetch from correct sheet ===
SHEET_NAME = "Config"
url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{SHEET_NAME}?key={API_KEY}"
response = requests.get(url).json()

values = response.get("values", [])
if not values:
    raise Exception("No data found in sheet!")

rows = values[1:]  # skip header row ("Parameter", "Value")

# === Step 3: Write as .env style config ===
with open("config.cfg", "w") as f:
    for row in rows:
        if len(row) >= 2:   # Parameter + Value
            key, value = row[0].strip(), row[1].strip()
            f.write(f"{key}={value}\n")
        elif len(row) == 1: # Parameter only, no value
            key = row[0].strip()
            f.write(f"{key}=\n")

print("✅ Config file generated with key=value pairs!")
