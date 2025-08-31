# """
# [Module Number: 5] LLM Decision Module for Bitcoin Trading Agent

# Purpose: Uses Moonshot via Groq API to generate dynamic trading suggestions.

# Inputs:
# - Market data from 01_data_collection (technical indicators, price data)
# - Configuration from 02_config_manager

# Outputs:
# - Trading suggestions (e.g., buy/sell with rationale)
# - Confidence scores for decisions

# Dependencies: groq, pandas, 01_data_collection
# """

# import os
# from groq import Groq
# from dotenv import load_dotenv
# import pandas as pd
# import asyncio
# from data_collection import collect_yahoo_async

# def initialize_groq_client():
#     """Initialize Groq client with API key."""
#     # Load environment variables for secure API access
#     load_dotenv()
#     api_key = os.getenv('GROQ_API_KEY')
#     if not api_key:
#         raise Exception("Groq API key missing in .env")
#     # Return initialized Groq client
#     return Groq(api_key=api_key)

# def generate_llm_prompt(yahoo_df, current_price, indicators):
#     """Generate prompt for Moonshot based on market data."""
#     # Construct detailed prompt with market data for LLM analysis
#     prompt = f"""
#     You are a Bitcoin trading assistant. Analyze the following market data and suggest a trading action (BUY, SELL, or HOLD) with a confidence score (0-100). Provide a brief rationale.

#     Current Price: ${current_price:,.2f}
#     ATR (14): ${indicators['atr_14']:,.2f}
#     RSI (14): {indicators['rsi_14']:.1f}
#     SMA 20: ${indicators['sma_20']:,.2f}
#     SMA 50: ${indicators['sma_50']:,.2f}
#     MACD: {indicators['macd']:.2f}
#     MACD Signal: {indicators['macd_signal']:.2f}
#     Recent Volume: {yahoo_df['volume'].iloc[-1]:,}
#     Price Change (24h): {(yahoo_df['close'].iloc[-1] - yahoo_df['close'].iloc[-2]) / yahoo_df['close'].iloc[-2] * 100:.2f}%

#     Suggest an action and confidence score. Format response as JSON:
#     ```json
#     {
#         "action": "BUY|SELL|HOLD",
#         "confidence": <0-100>,
#         "rationale": "<brief explanation>"
#     }
#     ```
#     """
#     return prompt

# def get_llm_decision(yahoo_df, current_price, indicators):
#     """Get trading decision from Moonshot via Groq API."""
#     try:
#         # Initialize Groq client
#         client = initialize_groq_client()
#         # Generate prompt with market data
#         prompt = generate_llm_prompt(yahoo_df, current_price, indicators)
#         # Query Moonshot model for trading decision
#         response = client.chat.completions.create(
#             model="llama3-8b-8192",  # Moonshot-compatible model
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=200
#         )
#         # Parse JSON response from LLM
#         decision = eval(response.choices[0].message.content.strip('```json\n```'))
#         print(f"[LLM] Decision: {decision['action']} ({decision['confidence']}%) - {decision['rationale']}")
#         return decision
#     except Exception as e:
#         # Handle LLM query errors
#         print(f"[ERROR] LLM decision failed: {e}")
#         return None

# if __name__ == "__main__":
#     """Test 05_llm_decision module with real market data."""
#     print("Testing 05_llm_decision module with real data...")
#     try:
#         # Fetch real market data
#         yahoo_df, current_price, indicators = asyncio.run(collect_yahoo_async())
#         if yahoo_df is None or current_price is None:
#             raise Exception("Failed to fetch market data")
        
#         # Get real LLM decision
#         decision = get_llm_decision(yahoo_df, current_price, indicators)
#         print(f"[TEST] LLM Decision: {decision}")
#     except Exception as e:
#         print(f"[TEST ERROR] {e}")


# ------------- V2 Takes all data from complete bitcoin data file and current status of portfolio as well --------------------------------------
"""
[Module Number: 5] LLM Decision Module for Bitcoin Trading Agent

Purpose: Uses Moonshot via Groq API to generate dynamic trading suggestions.

Inputs:
- Full market data from complete_bitcoin_data.md (all sources)
- Current portfolio status (from trade_executor_03.py Binance API)
- Recent trade history (from trade_log.csv and/or Google Sheet)

Outputs:
- Trading suggestions (e.g., buy/sell with rationale)
- Confidence scores for decisions

Dependencies: groq, dotenv, pandas, gspread, google-auth
"""

import os  # For environment variables and file paths
import pandas as pd  # For reading trade logs from CSV
import json  # For formatting and parsing JSON
import gspread  # For Google Sheets API
import re  # Import regex for extracting JSON
import sys
from groq import Groq  # Groq API client for LLM interaction
from dotenv import load_dotenv  # Loads environment variables from .env file
from google.oauth2.service_account import Credentials  # For Google Sheets authentication
from trade_executor_03 import get_portfolio, initialize_binance_client  # Import portfolio functions

# Add the modules directory to sys.path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))

def initialize_groq_client():
    load_dotenv()  # Load environment variables from .env
    api_key = os.getenv('GROQ_API_KEY')  # Get Groq API key
    if not api_key:
        raise Exception("Groq API key missing in .env")  # Error if key is missing
    return Groq(api_key=api_key)  # Return Groq client

def read_md_market_data(md_path="complete_bitcoin_data.md"):
    try:
        with open(md_path, "r", encoding="utf-8") as f:  # Open markdown file
            content = f.read()  # Read all contents
        return content  # Return file content
    except Exception as e:
        print(f"[ERROR] Failed to read markdown data: {e}")  # Print error if file can't be read
        return None  # Return None on error

def read_trade_log_csv(csv_path="../data/trade_log.csv", n=10):
    try:
        df = pd.read_csv(csv_path)  # Read trade log CSV into DataFrame
        return df.tail(n).to_dict(orient="records")  # Return last n trades as list of dicts
    except Exception as e:
        print(f"[WARNING] Could not read trade_log.csv: {e}")  # Warn if file can't be read
        return []  # Return empty list on error

def read_trade_log_google_sheet(n=10):
    try:
        load_dotenv()  # Load environment variables
        sheet_id = os.getenv('GOOGLE_SHEETS_ID')  # Get Google Sheets ID
        creds_path = os.getenv('GOOGLE_SHEETS_API_KEY')  # Get service account path
        scopes_url = os.getenv('GOOGLE_SHEETS_SCOPE')  # Get Google Sheets scope
        if not creds_path or not sheet_id or not scopes_url:
            print("[WARNING] Google Sheets logging skipped: missing credentials, sheet ID, or scope in .env")
            return []  # Return empty list if any credential is missing
        scopes = [scopes_url]  # Set scopes for authentication
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)  # Authenticate
        gc = gspread.authorize(creds)  # Authorize gspread client
        sh = gc.open_by_key(sheet_id)  # Open Google Sheet by ID
        worksheet = sh.worksheet("Trade Logs")  # Select 'Trade Logs' worksheet
        rows = worksheet.get_all_records()  # Get all records as list of dicts
        return rows[-n:] if len(rows) >= n else rows  # Return last n trades
    except Exception as e:
        print(f"[WARNING] Could not read Google Sheet: {e}")  # Warn if can't read sheet
        return []  # Return empty list on error

def extract_json_from_response(response_text): # To parse json from LLM Response
    
    response_text = response_text.strip()  # Remove leading/trailing whitespace
    response_text = response_text.replace('```json', '').replace('```', '').strip()  # Remove markdown code block markers
    try:
        return json.loads(response_text)  # Try parsing entire response as JSON
    except Exception:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)  # Find first JSON object in response
        if match:
            try:
                return json.loads(match.group(0))  # Parse found JSON object
            except Exception as e:
                print(f"[ERROR] Failed to parse JSON: {e}")  # Print error if parsing fails
                print(f"[RAW RESPONSE] {response_text}")  # Print raw response for debugging
                return None  # Return None on error
        else:
            print("[ERROR] LLM response did not contain valid JSON.")  # Warn if no JSON found
            print(f"[RAW RESPONSE] {response_text}")  # Print raw response for debugging
            return None  # Return None if no JSON found

# def get_llm_decision(md_path="complete_bitcoin_data.md", use_google_sheet=False):
#     try:
#         client = initialize_groq_client()  # Initialize Groq client for LLM
#         md_content = read_md_market_data(md_path)  # Read full market data from markdown
#         binance_client = initialize_binance_client()  # Initialize Binance client
#         portfolio = get_portfolio(binance_client)  # Get current Binance portfolio
#         trade_history = read_trade_log_google_sheet() if use_google_sheet else read_trade_log_csv()  # Get recent trade history

#         # # Print out all data being fed to the LLM
#         # print("\n========== LLM INPUT DATA ==========")
#         # print("----- MARKET DATA REPORT -----")
#         # print(md_content)
#         # print("\n----- BINANCE PORTFOLIO STATUS -----")
        
#         # print(json.dumps(portfolio, indent=2))
#         # print(f"\n----- RECENT TRADE HISTORY (last {len(trade_history)} trades) -----")
#         # print(json.dumps(trade_history, indent=2))
#         # print("====================================\n")

#         if not md_content:
#             raise Exception("No market data found in markdown file.")  # Error if no market data

#         # Compose everything into the system prompt for LLM
#         system_prompt = f"""
# You are a Bitcoin trading assistant. Analyze the following comprehensive market data report, current Binance portfolio status, and recent trade history. Suggest a trading action (BUY, SELL, or HOLD) with a confidence score (0-100). Provide a brief rationale.

# MARKET DATA REPORT:
# {md_content}

# BINANCE PORTFOLIO STATUS:
# {json.dumps(portfolio, indent=2)}

# RECENT TRADE HISTORY (last {len(trade_history)} trades):
# {json.dumps(trade_history, indent=2)}

# Respond ONLY with valid JSON (no markdown, no explanation, no code block markers):

# {{
#     "action": "BUY|SELL|HOLD",
#     "confidence": <0-100>,
#     "rationale": "<brief explanation>"
# }}
# """

#         response = client.chat.completions.create(
#             model="openai/gpt-oss-120b",  # Specify LLM model
#             messages=[
#                 {"role": "system", "content": system_prompt}  # Send system prompt to LLM
#             ],
#             #max_tokens=350  # Limit response length
#         )
#         response_text = response.choices[0].message.content.strip()  # Get LLM response text
#         #print(f"[LLM RAW RESPONSE] {response_text}")  # Print raw LLM response for debugging
#         decision = extract_json_from_response(response_text)  # Extract JSON decision from response
#         if decision:
#             print(f"[LLM] Decision: {decision['action']} ({decision['confidence']}%) - {decision['rationale']}")  # Print decision
#             return decision  # Return parsed decision
#         else:
#             # Fallback: return neutral decision if parsing fails
#             return {
#                 "action": "HOLD",
#                 "confidence": 50,
#                 "rationale": "LLM response parsing failed, defaulting to HOLD."
#             }
#     except Exception as e:
#         print(f"[ERROR] LLM decision failed: {e}")  # Print error if LLM call fails
#         return {
#             "action": "HOLD",
#             "confidence": 50,
#             "rationale": "LLM decision failed, defaulting to HOLD."
#         }
def get_llm_decision(
    md_path="complete_bitcoin_data.md",
    portfolio=None,
    trade_history=None,
    use_google_sheet=False
):
    """
    Get trading decision from LLM using market data, portfolio, and trade history.
    For backtest, pass in portfolio and trade_history directly.
    """
    count = 0  # ------ setting to only print data passed into llm once
    if portfolio is None:
        portfolio = get_portfolio(binance_client)  # Get current Binance portfolio

    try:
        client = initialize_groq_client()  # Initialize Groq client for LLM
        md_content = read_md_market_data(md_path)  # Read full market data from markdown

        # Use provided portfolio/trade_history, or fallback to reading from APIs
        if portfolio is None:
            if use_google_sheet:
                # Optionally fetch from Google Sheet if desired
                portfolio = {}  # Replace with Google Sheet fetch if needed
            else:
                portfolio = {}
        if trade_history is None:
            if use_google_sheet:
                trade_history = read_trade_log_google_sheet()
            else:
                trade_history = []

        if not md_content:
            raise Exception("No market data found in markdown file.")

        system_prompt = f"""
You are a Bitcoin trading assistant. Analyze the following comprehensive market data report, current portfolio status, and recent trade history. Suggest a trading action (BUY, SELL, or HOLD) with a confidence score (0-100). Provide a brief rationale.

MARKET DATA REPORT:
{md_content}

PORTFOLIO STATUS:
{json.dumps(portfolio, indent=2)}

RECENT TRADE HISTORY (last {len(trade_history)} trades):
{json.dumps(trade_history, indent=2)}

Respond ONLY with valid JSON (no markdown, no explanation, no code block markers):

{{
    "action": "BUY|SELL|HOLD",
    "confidence": <0-100>,
    "rationale": "<brief explanation>"
}}
"""
        if count == 0:
                    # Print out all data being fed to the LLM
            print("\n========== LLM INPUT DATA ==========")
            print("----- MARKET DATA REPORT -----")
            print(md_content)
            print("\n----- BINANCE PORTFOLIO STATUS -----")
            
            print(json.dumps(portfolio, indent=2))
            print(f"\n----- RECENT TRADE HISTORY (last {len(trade_history)} trades) -----")
            print(json.dumps(trade_history, indent=2))
            print("====================================\n")
            print(f"System Prompt : {system_prompt}")
            print(f"LLM Input Data Count: {count}")
            count+=1

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
        )
        response_text = response.choices[0].message.content.strip()
        decision = extract_json_from_response(response_text)
        if decision:
            print(f"[LLM] Decision: {decision['action']} ({decision['confidence']}%) - {decision['rationale']}")
            return decision
        else:
            return {
                "action": "HOLD",
                "confidence": 50,
                "rationale": "LLM response parsing failed, defaulting to HOLD."
            }
    except Exception as e:
        print(f"[ERROR] LLM decision failed: {e}")
        return {
            "action": "HOLD",
            "confidence": 50,
            "rationale": "LLM decision failed, defaulting to HOLD."
        }
if __name__ == "__main__":
    print("Testing 05_llm_decision module with full context...")  # Indicate test start
    decision = get_llm_decision(use_google_sheet=True)  # Run decision function with Google Sheet
    print(f"[TEST] LLM Decision: {decision}")  # Print test