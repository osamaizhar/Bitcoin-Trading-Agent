# -------------- With Binance server time sync fix ----------------------------

# """
# Module Number: 3 Trade Executor Module for Bitcoin Trading Agent

# Purpose: Manages trade execution and portfolio tracking using Binance API.

# Inputs:
# - Binance API credentials (from .env)
# - Trade parameters (amount, price, stop-loss) from strategy_manager
# - Configuration from config_manager

# Outputs:
# - Executed trades (buy/sell)
# - Portfolio status (BTC and USD balance)
# - Transaction logs saved to '../data/trade_log.csv'

# Dependencies: python-binance, pandas, dotenv
# """

# import os
# import pandas as pd
# from binance.client import Client
# from dotenv import load_dotenv
# import time
# from datetime import datetime

# def initialize_binance_client():
#     """Initialize Binance client with API credentials and sync time offset."""
#     load_dotenv()
#     api_key = os.getenv('BINANCE_API_KEY')
#     api_secret = os.getenv('BINANCE_SECRET_KEY')
#     if not api_key or not api_secret:
#         raise Exception("Binance API credentials missing in .env")
#     client = Client(api_key, api_secret)
#     # Sync time offset to avoid timestamp errors
#     try:
#         server_time = client.get_server_time()['serverTime']
#         local_time = int(time.time() * 1000)
#         client.time_offset = server_time - local_time
#     except Exception as e:
#         print(f"[WARNING] Could not sync time offset: {e}")
#     return client

# def get_portfolio(client):
#     """Get current portfolio balance (BTC and USD)."""
#     try:
#         account = client.get_account()
#         btc_balance = float([asset for asset in account['balances'] if asset['asset'] == 'BTC'][0]['free'])
#         usdt_balance = float([asset for asset in account['balances'] if asset['asset'] == 'USDT'][0]['free'])
#         return {'btc': btc_balance, 'usdt': usdt_balance}
#     except Exception as e:
#         print(f"[ERROR] Failed to get portfolio: {e}")
#         return {'btc': 0, 'usdt': 0}

# def execute_buy(client, amount_usd, current_price, trade_type="DCA"):
#     """Execute a buy order on Binance."""
#     try:
#         quantity = amount_usd / current_price
#         # Binance requires quantity to be rounded to 6 decimals for BTC
#         quantity = round(quantity, 6)
#         order = client.order_market_buy(symbol='BTCUSDT', quantity=quantity)
#         trade_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         trade_record = {
#             'timestamp': trade_time,
#             'type': 'BUY',
#             'trade_type': trade_type,
#             'price': current_price,
#             'quantity': quantity,
#             'amount_usd': amount_usd
#         }
#         log_trade(trade_record)
#         print(f"[OK] Buy executed: {quantity:.6f} BTC at ${current_price:,.2f} ({trade_type})")
#         return trade_record
#     except Exception as e:
#         print(f"[ERROR] Buy failed: {e}")
#         return None

# def execute_sell(client, quantity, current_price, trade_type="STOP_LOSS"):
#     """Execute a sell order on Binance."""
#     try:
#         quantity = round(quantity, 6)
#         order = client.order_market_sell(symbol='BTCUSDT', quantity=quantity)
#         trade_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         trade_record = {
#             'timestamp': trade_time,
#             'type': 'SELL',
#             'trade_type': trade_type,
#             'price': current_price,
#             'quantity': quantity,
#             'amount_usd': quantity * current_price
#         }
#         log_trade(trade_record)
#         print(f"[OK] Sell executed: {quantity:.6f} BTC at ${current_price:,.2f} ({trade_type})")
#         return trade_record
#     except Exception as e:
#         print(f"[ERROR] Sell failed: {e}")
#         return None

# def log_trade(trade_record):
#     """Log trade details to CSV."""
#     os.makedirs('../data', exist_ok=True)
#     trade_log_path = '../data/trade_log.csv'
#     df = pd.DataFrame([trade_record])
#     if os.path.exists(trade_log_path):
#         df.to_csv(trade_log_path, mode='a', header=False, index=False)
#     else:
#         df.to_csv(trade_log_path, index=False)

# if __name__ == "__main__":
#     """Test trade_executor module with a real small trade."""
#     print("Testing trade_executor module with real trade...")
#     try:
#         client = initialize_binance_client()
#         portfolio = get_portfolio(client)
#         print(f"[TEST] Portfolio: {portfolio['btc']:.6f} BTC, ${portfolio['usdt']:,.2f} USDT")
#         ticker = client.get_symbol_ticker(symbol='BTCUSDT')
#         current_price = float(ticker['price'])
#         print(f"[TEST] Current BTC price: ${current_price:,.2f}")
#         if portfolio['usdt'] >= 10:
#             trade_record = execute_buy(client, 10.0, current_price, trade_type="TEST_BUY")
#             if trade_record:
#                 print(f"[TEST] Real buy trade executed: {trade_record}")
#                 trade_log = pd.read_csv('../data/trade_log.csv')
#                 print(f"[TEST] Last trade in log: {trade_log.iloc[-1].to_dict()}")
#             else:
#                 print("[TEST] Buy trade failed")
#         else:
#             print("[TEST] Insufficient USDT balance for test trade")
#     except Exception as e:
#         print(f"[TEST ERROR] {e}")



# ---------------------------------- Test Net Mode added ------------------------------------
# """
# Module Number: 3 Trade Executor Module for Bitcoin Trading Agent

# Purpose: Manages trade execution and portfolio tracking using Binance API (supports testnet and live).

# Inputs:
# - Binance API credentials (from .env)
# - Trade parameters (amount, price, stop-loss) from strategy_manager
# - Configuration from config_manager

# Outputs:
# - Executed trades (buy/sell)
# - Portfolio status (BTC and USD balance)
# - Transaction logs saved to '../data/trade_log.csv'

# Dependencies: python-binance, pandas, dotenv
# """

# import os
# import pandas as pd
# from binance.client import Client
# from dotenv import load_dotenv
# import time
# from datetime import datetime

# # Global testnet mode variable
# testnet_mode = True  # Set to False for live trading

# def initialize_binance_client():
#     """Initialize Binance client with API credentials and endpoint based on mode."""
#     load_dotenv()
#     if testnet_mode:
#         api_key = os.getenv('BINANCE_TESTNET_API_KEY')
#         api_secret = os.getenv('BINANCE_TESTNET_SECRET_KEY')
#         base_url = os.getenv('TESTNET_BASE_URL', 'https://testnet.binance.vision/api')
#     else:
#         api_key = os.getenv('BINANCE_API_KEY')
#         api_secret = os.getenv('BINANCE_SECRET_KEY')
#         base_url = os.getenv('BINANCE_BASE_URL', 'https://api.binance.com/api')
#     if not api_key or not api_secret:
#         raise Exception("Binance API credentials missing in .env")
#     client = Client(api_key, api_secret)
#     client.API_URL = base_url
#     # Sync time offset to avoid timestamp errors
#     try:
#         server_time = client.get_server_time()['serverTime']
#         local_time = int(time.time() * 1000)
#         client.time_offset = server_time - local_time
#         print(f"[INFO] Time offset set to {client.time_offset} ms")
#     except Exception as e:
#         print(f"[WARNING] Could not sync time offset: {e}")
#     return client

# def get_portfolio(client):
#     """Get current portfolio balance (BTC and USDT)."""
#     try:
#         account = client.get_account()
#         btc_balance = float([asset for asset in account['balances'] if asset['asset'] == 'BTC'][0]['free'])
#         usdt_balance = float([asset for asset in account['balances'] if asset['asset'] == 'USDT'][0]['free'])
#         return {'btc': btc_balance, 'usdt': usdt_balance}
#     except Exception as e:
#         print(f"[ERROR] Failed to get portfolio: {e}")
#         return {'btc': 0, 'usdt': 0}

# def execute_buy(client, amount_usd, current_price, trade_type="DCA"):
#     """Execute a buy order on Binance."""
#     try:
#         quantity = round(amount_usd / current_price, 6)
#         quantity_str = format(quantity, 'f')  # Ensure plain decimal string
#         print(f"Quantity Str: {quantity_str}")
#         order = client.order_market_buy(symbol='BTCUSDT', quantity=quantity_str)
#         trade_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         trade_record = {
#             'timestamp': trade_time,
#             'type': 'BUY',
#             'trade_type': trade_type,
#             'price': current_price,
#             'quantity': quantity,
#             'amount_usd': amount_usd
#         }
#         log_trade(trade_record)
#         print(f"[OK] Buy executed: {quantity_str} BTC at ${current_price:,.2f} ({trade_type})")
#         return trade_record
#     except Exception as e:
#         print(f"[ERROR] Buy failed: {e}")
#         return None

# def execute_sell(client, quantity, current_price, trade_type="SELL"):
#     """Execute a sell order on Binance."""
#     try:
#         quantity = round(quantity, 6)
#         quantity_str = format(quantity, 'f')  # Ensure plain decimal string
#         order = client.order_market_sell(symbol='BTCUSDT', quantity=quantity_str)
#         trade_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         trade_record = {
#             'timestamp': trade_time,
#             'type': 'SELL',
#             'trade_type': trade_type,
#             'price': current_price,
#             'quantity': quantity,
#             'amount_usd': quantity * current_price
#         }
#         log_trade(trade_record)
#         print(f"[OK] Sell executed: {quantity_str} BTC at ${current_price:,.2f} ({trade_type})")
#         return trade_record
#     except Exception as e:
#         print(f"[ERROR] Sell failed: {e}")
#         return None

# def log_trade(trade_record):
#     """Log trade details to CSV."""
#     os.makedirs('../data', exist_ok=True)
#     trade_log_path = '../data/trade_log.csv'
#     df = pd.DataFrame([trade_record])
#     if os.path.exists(trade_log_path):
#         df.to_csv(trade_log_path, mode='a', header=False, index=False)
#     else:
#         df.to_csv(trade_log_path, index=False)

# if __name__ == "__main__":
#     print(f"Testing trade_executor module with {'Binance Spot Testnet' if testnet_mode else 'Binance Live'}...")
#     try:
#         client = initialize_binance_client()
#         # Get initial portfolio
#         portfolio = get_portfolio(client)
#         print(f"[TEST] Initial Portfolio: {portfolio['btc']:.6f} BTC, ${portfolio['usdt']:,.2f} USDT")
#         # Get current BTC price
#         ticker = client.get_symbol_ticker(symbol='BTCUSDT')
#         current_price = float(ticker['price'])
#         print(f"[TEST] Current BTC price: ${current_price:,.2f}")
#         # Perform a test buy trade ($10 USDT)
#         if portfolio['usdt'] >= 10:
#             trade_record = execute_buy(client, 10.0, current_price, trade_type="TEST_BUY")
#             if trade_record:
#                 print(f"[TEST] Buy trade executed: {trade_record}")
#             else:
#                 print("[TEST] Buy trade failed")
#         else:
#             print("[TEST] Insufficient USDT balance for test buy")
#         # Get updated portfolio after buy
#         portfolio = get_portfolio(client)
#         print(f"[TEST] Portfolio after buy: {portfolio['btc']:.6f} BTC, ${portfolio['usdt']:,.2f} USDT")
#         # Perform a test sell trade (sell 0.00005 BTC if available)
#         if portfolio['btc'] >= 0.00005:
#             trade_record = execute_sell(client, 0.00005, current_price, trade_type="TEST_SELL")
#             if trade_record:
#                 print(f"[TEST] Sell trade executed: {trade_record}")
#             else:
#                 print("[TEST] Sell trade failed")
#         else:
#             print("[TEST] Insufficient BTC balance for test sell")
#         # Get updated portfolio after sell
#         portfolio = get_portfolio(client)
#         print(f"[TEST] Portfolio after sell: {portfolio['btc']:.6f} BTC, ${portfolio['usdt']:,.2f} USDT")
#     except Exception as e:
#         print(f"[TEST ERROR] {e}")



# ----------------- Test Net + Logging + Async (local + Gsheet) -------------------------------------------

# """
# Module Number: 3 Trade Executor Module for Bitcoin Trading Agent

# Purpose: Manages trade execution and portfolio tracking using Binance API (supports testnet and live).
# Logs trades to local CSV and Google Sheet.

# Inputs:
# - Binance API credentials (from .env)
# - Trade parameters (amount, price, stop-loss) from strategy_manager
# - Configuration from config_manager

# Outputs:
# - Executed trades (buy/sell)
# - Portfolio status (BTC and USD balance)
# - Transaction logs saved to '../data/trade_log.csv' and Google Sheet 'Trade Logs'

# Dependencies: python-binance, pandas, dotenv, gspread, google-auth
# """

# import os
# import pandas as pd
# from binance.client import Client
# from dotenv import load_dotenv
# import time
# from datetime import datetime
# import asyncio
# import gspread
# from google.oauth2.service_account import Credentials

# # Global testnet mode variable
# testnet_mode = True  # Set to False for live trading

# def initialize_binance_client():
#     load_dotenv()
#     if testnet_mode:
#         api_key = os.getenv('BINANCE_TESTNET_API_KEY')
#         api_secret = os.getenv('BINANCE_TESTNET_SECRET_KEY')
#         base_url = os.getenv('TESTNET_BASE_URL')
#     else:
#         api_key = os.getenv('BINANCE_API_KEY')
#         api_secret = os.getenv('BINANCE_SECRET_KEY')
#         base_url = os.getenv('BINANCE_BASE_URL')
#     if not api_key or not api_secret or not base_url:
#         raise Exception("Binance API credentials or base URL missing in .env")
#     client = Client(api_key, api_secret)
#     client.API_URL = base_url
#     try:
#         server_time = client.get_server_time()['serverTime']
#         local_time = int(time.time() * 1000)
#         client.time_offset = server_time - local_time
#         print(f"[INFO] Time offset set to {client.time_offset} ms")
#     except Exception as e:
#         print(f"[WARNING] Could not sync time offset: {e}")
#     return client

# def get_portfolio(client):
#     try:
#         account = client.get_account()
#         btc_balance = float([asset for asset in account['balances'] if asset['asset'] == 'BTC'][0]['free'])
#         usdt_balance = float([asset for asset in account['balances'] if asset['asset'] == 'USDT'][0]['free'])
#         return {'btc': btc_balance, 'usdt': usdt_balance}
#     except Exception as e:
#         print(f"[ERROR] Failed to get portfolio: {e}")
#         return {'btc': 0, 'usdt': 0}

# async def log_trade(trade_record):
#     """Async log trade details to CSV and Google Sheet."""
#     os.makedirs('../data', exist_ok=True)
#     trade_log_path = '../data/trade_log.csv'
#     df = pd.DataFrame([trade_record])
#     loop = asyncio.get_event_loop()
#     if os.path.exists(trade_log_path):
#         await loop.run_in_executor(
#             None,
#             lambda: df.to_csv(trade_log_path, mode='a', header=False, index=False)
#         )
#     else:
#         await loop.run_in_executor(
#             None,
#             lambda: df.to_csv(trade_log_path, header=True, index=False)
#         )
#     await log_trade_to_google_sheet(trade_record)

# async def log_trade_to_google_sheet(trade_record):
#     """Async append trade record to Google Sheet 'Trade Logs'."""
#     try:
#         load_dotenv()
#         sheet_id = os.getenv('GOOGLE_SHEETS_ID')
#         creds_path = os.getenv('GOOGLE_SHEETS_API_KEY')
#         scopes_url = os.getenv('GOOGLE_SHEETS_SCOPE')
#         if not creds_path or not sheet_id or not scopes_url:
#             print("[WARNING] Google Sheets logging skipped: missing credentials, sheet ID, or scope in .env")
#             return
#         scopes = [scopes_url]
#         creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
#         gc = gspread.authorize(creds)
#         sh = gc.open_by_key(sheet_id)
#         worksheet = sh.worksheet("Trade Logs")
#         # Add header if sheet is empty
#         if worksheet.row_count == 0 or not worksheet.get_all_values():
#             header = [
#                 "Timestamp", "Type", "Trade Type", "Price BTC", "Quantity", "Value USD",
#                 "BTC Balance", "BTC Value USD", "Profit/Loss USD"
#             ]
#             worksheet.append_row(header, value_input_option='USER_ENTERED')
#         row = [
#             trade_record.get('timestamp', ''),
#             trade_record.get('type', ''),
#             trade_record.get('trade_type', ''),
#             trade_record.get('price', ''),
#             trade_record.get('quantity', ''),
#             trade_record.get('amount_usd', ''),
#             trade_record.get('btc_balance', ''),
#             trade_record.get('btc_value_usd', ''),
#             trade_record.get('profit_loss_usd', '')
#         ]
#         loop = asyncio.get_event_loop()
#         await loop.run_in_executor(None, worksheet.append_row, row, 'USER_ENTERED')
#         print("[OK] Trade logged to Google Sheet")
#     except Exception as e:
#         print(f"[WARNING] Could not log trade to Google Sheet: {e}")

# async def execute_buy(client, amount_usd, current_price, trade_type="DCA"):
#     try:
#         # Calculate quantity
#         quantity = round(amount_usd / current_price, 6)
#         print(f"[DEBUG] Calculated quantity: {quantity}")  # Debugging
        
#         # Check LOT_SIZE filter
#         if quantity < 0.0001:
#             print(f"[ERROR] Buy quantity {quantity} is below minimum lot size (0.0001 BTC)")
#             return None
        
#         # Format quantity as plain decimal string
#         quantity_str = format(quantity, 'f')
#         print(f"[DEBUG] Formatted quantity: {quantity_str}")  # Debugging
        
#         # Place the order
#         order = client.order_market_buy(symbol='BTCUSDT', quantity=quantity_str)
#         trade_time = datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')
        
#         # Get updated balances after buy
#         portfolio = get_portfolio(client)
#         btc_balance = portfolio['btc']
#         btc_value_usd = round(btc_balance * current_price, 2)
        
#         trade_record = {
#             'timestamp': trade_time,
#             'type': 'BUY',
#             'trade_type': trade_type,
#             'price': current_price,
#             'quantity': quantity,
#             'amount_usd': amount_usd,
#             'btc_balance': btc_balance,
#             'btc_value_usd': btc_value_usd,
#             'profit_loss_usd': ''  # Not applicable for buy
#         }
#         await log_trade(trade_record)
#         print(f"[OK] Buy executed: {quantity_str} BTC at ${current_price:,.2f} ({trade_type})")
#         return trade_record
#     except Exception as e:
#         print(f"[ERROR] Buy failed: {e}")
#         return None

# async def execute_sell(client, quantity, current_price, trade_type="SELL"):
#     try:
#         quantity = round(quantity, 6)
#         if quantity < 0.0001:
#             print(f"[ERROR] Sell quantity {quantity} is below minimum lot size (0.0001 BTC)")
#             return None
#         quantity_str = format(quantity, 'f')
#         order = client.order_market_sell(symbol='BTCUSDT', quantity=quantity_str)
#         trade_time = datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')
#         portfolio = get_portfolio(client)
#         btc_balance = portfolio['btc']
#         btc_value_usd = round(btc_balance * current_price, 2)
#         # Calculate profit/loss compared to previous BTC VALUE USD
#         prev_btc_value_usd = None
#         try:
#             df = pd.read_csv('../data/trade_log.csv')
#             last_trade = df[df['btc_value_usd'].notnull() & (df['btc_value_usd'] != '')].iloc[-1] if not df[df['btc_value_usd'].notnull() & (df['btc_value_usd'] != '')].empty else None
#             if last_trade is not None:
#                 prev_btc_value_usd = float(last_trade['btc_value_usd'])
#         except Exception:
#             prev_btc_value_usd = None
#         profit_loss_usd = ''
#         if prev_btc_value_usd is not None:
#             profit_loss_usd = round(btc_value_usd - prev_btc_value_usd, 2)
#         trade_record = {
#             'timestamp': trade_time,
#             'type': 'SELL',
#             'trade_type': trade_type,
#             'price': current_price,
#             'quantity': quantity,
#             'amount_usd': quantity * current_price,
#             'btc_balance': btc_balance,
#             'btc_value_usd': btc_value_usd,
#             'profit_loss_usd': profit_loss_usd
#         }
#         await log_trade(trade_record)
#         print(f"[OK] Sell executed: {quantity_str} BTC at ${current_price:,.2f} ({trade_type})")
#         return trade_record
#     except Exception as e:
#         print(f"[ERROR] Sell failed: {e}")
#         return None

# if __name__ == "__main__":
#     print(f"Testing trade_executor module with {'Binance Spot Testnet' if testnet_mode else 'Binance Live'}...")
#     async def main():
#         try:
#             client = initialize_binance_client()
#             portfolio = get_portfolio(client)
#             print(f"[TEST] Initial Portfolio: {portfolio['btc']:.6f} BTC, ${portfolio['usdt']:,.2f} USDT")
#             ticker = client.get_symbol_ticker(symbol='BTCUSDT')
#             current_price = float(ticker['price'])
#             print(f"[TEST] Current BTC price: ${current_price:,.2f}")
            
#             # Calculate minimum USDT for 0.0001 BTC and MIN_NOTIONAL
#             #min_buy_usdt = max(round(0.0001 * current_price + 1, 2), 10)  # Ensure $10 minimum notional
#             min_buy_usdt  = 150 
#             print(f"[TEST] Minimum USDT required for buy: ${min_buy_usdt:,.2f}")
            
#             # Perform a test buy trade (minimum required USDT)
#             if portfolio['usdt'] >= min_buy_usdt:
#                 trade_record = await execute_buy(client, min_buy_usdt, current_price, trade_type="TEST_BUY")
#                 if trade_record:
#                     print(f"[TEST] Buy trade executed: {trade_record}")
#                 else:
#                     print("[TEST] Buy trade failed")
#             else:
#                 print("[TEST] Insufficient USDT balance for test buy")
            
#             portfolio = get_portfolio(client)
#             print(f"[TEST] Portfolio after buy: {portfolio['btc']:.6f} BTC, ${portfolio['usdt']:,.2f} USDT")
            
#             # Perform a test sell trade (sell 0.01 BTC if available)
#             if portfolio['btc'] >= 0.001:
#                 trade_record = await execute_sell(client, 0.001, current_price, trade_type="TEST_SELL")
#                 if trade_record:
#                     print(f"[TEST] Sell trade executed: {trade_record}")
#                 else:
#                     print("[TEST] Sell trade failed")
#             else:
#                 print("[TEST] Insufficient BTC balance for test sell")
            
#             portfolio = get_portfolio(client)
#             print(f"[TEST] Portfolio after sell: {portfolio['btc']:.6f} BTC, ${portfolio['usdt']:,.2f} USDT")
#         except Exception as e:
#             print(f"[TEST ERROR] {e}")
#     asyncio.run(main())



# -------------- Buy error fix ------------------------------------------
"""
Module Number: 3 Trade Executor Module for Bitcoin Trading Agent

Purpose: Manages trade execution and portfolio tracking using Binance API (supports testnet and live).
Logs trades to local CSV and Google Sheet.

Inputs:
- Binance API credentials (from .env)
- Trade parameters (amount, price, stop-loss) from strategy_manager
- Configuration from config_manager

Outputs:
- Executed trades (buy/sell)
- Portfolio status (BTC and USD balance)
- Transaction logs saved to '../data/trade_log.csv' and Google Sheet 'Trade Logs'

Dependencies: python-binance, pandas, dotenv, gspread, google-auth
"""

import os
import pandas as pd
from binance.client import Client
from dotenv import load_dotenv
import time
from datetime import datetime
import asyncio
import gspread
from google.oauth2.service_account import Credentials

# Global testnet mode variable
testnet_mode = True  # Set to False for live trading

def initialize_binance_client():
    load_dotenv()
    if testnet_mode:
        api_key = os.getenv('BINANCE_TESTNET_API_KEY')
        api_secret = os.getenv('BINANCE_TESTNET_SECRET_KEY')
        base_url = os.getenv('TESTNET_BASE_URL')
    else:
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_SECRET_KEY')
        base_url = os.getenv('BINANCE_BASE_URL')
    if not api_key or not api_secret or not base_url:
        raise Exception("Binance API credentials or base URL missing in .env")
    client = Client(api_key, api_secret)
    client.API_URL = base_url
    try:
        server_time = client.get_server_time()['serverTime']
        local_time = int(time.time() * 1000)
        client.time_offset = server_time - local_time
        print(f"[INFO] Time offset set to {client.time_offset} ms")
    except Exception as e:
        print(f"[WARNING] Could not sync time offset: {e}")
    return client

def get_portfolio(client):
    try:
        account = client.get_account()
        btc_balance = float([asset for asset in account['balances'] if asset['asset'] == 'BTC'][0]['free'])
        usdt_balance = float([asset for asset in account['balances'] if asset['asset'] == 'USDT'][0]['free'])
        return {'btc': btc_balance, 'usdt': usdt_balance}
    except Exception as e:
        print(f"[ERROR] Failed to get portfolio: {e}")
        return {'btc': 0, 'usdt': 0}

async def log_trade(trade_record):
    """Async log trade details to CSV and Google Sheet."""
    os.makedirs('../data', exist_ok=True)
    trade_log_path = '../data/trade_log.csv'
    df = pd.DataFrame([trade_record])
    loop = asyncio.get_event_loop()
    if os.path.exists(trade_log_path):
        await loop.run_in_executor(
            None,
            lambda: df.to_csv(trade_log_path, mode='a', header=False, index=False)
        )
    else:
        await loop.run_in_executor(
            None,
            lambda: df.to_csv(trade_log_path, header=True, index=False)
        )
    await log_trade_to_google_sheet(trade_record)

async def log_trade_to_google_sheet(trade_record):
    """Async append trade record to Google Sheet 'Trade Logs'."""
    try:
        load_dotenv()
        sheet_id = os.getenv('GOOGLE_SHEETS_ID')
        creds_path = os.getenv('GOOGLE_SHEETS_API_KEY')
        scopes_url = os.getenv('GOOGLE_SHEETS_SCOPE')
        if not creds_path or not sheet_id or not scopes_url:
            print("[WARNING] Google Sheets logging skipped: missing credentials, sheet ID, or scope in .env")
            return
        scopes = [scopes_url]
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        worksheet = sh.worksheet("Trade Logs")
        # Add header if sheet is empty
        if worksheet.row_count == 0 or not worksheet.get_all_values():
            header = [
                "Timestamp", "Type", "Trade Type", "Price BTC", "Quantity", "Value USD",
                "BTC Balance", "BTC Value USD", "Profit/Loss USD"
            ]
            worksheet.append_row(header, value_input_option='USER_ENTERED')
        row = [
            trade_record.get('timestamp', ''),
            trade_record.get('type', ''),
            trade_record.get('trade_type', ''),
            trade_record.get('price', ''),
            trade_record.get('quantity', ''),
            trade_record.get('amount_usd', ''),
            trade_record.get('btc_balance', ''),
            trade_record.get('btc_value_usd', ''),
            trade_record.get('profit_loss_usd', '')
        ]
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, worksheet.append_row, row, 'USER_ENTERED')
        print("[OK] Trade logged to Google Sheet")
    except Exception as e:
        print(f"[WARNING] Could not log trade to Google Sheet: {e}")

async def execute_buy(client, amount_usd, current_price, trade_type="DCA"):
    try:
        # Format amount_usd as a string without trailing zeros (e.g., '150' instead of '150.0')
        quote_order_qty_str = f"{amount_usd:.8f}".rstrip('0').rstrip('.') if '.' in f"{amount_usd:.8f}" else f"{amount_usd}"
        
        # Use quoteOrderQty for market buy to specify USDT amount directly
        order = client.order_market_buy(symbol='BTCUSDT', quoteOrderQty=quote_order_qty_str)
        trade_time = datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')
        
        # Approximate quantity for logging (actual may vary slightly due to market execution)
        approx_quantity = amount_usd / current_price
        
        # Get updated balances after buy
        portfolio = get_portfolio(client)
        btc_balance = portfolio['btc']
        btc_value_usd = round(btc_balance * current_price, 2)
        
        trade_record = {
            'timestamp': trade_time,
            'type': 'BUY',
            'trade_type': trade_type,
            'price': current_price,
            'quantity': approx_quantity,  # Use approx for log; fetch actual from order if needed
            'amount_usd': amount_usd,
            'btc_balance': btc_balance,
            'btc_value_usd': btc_value_usd,
            'profit_loss_usd': ''  # Not applicable for buy , only when selling
        }
        await log_trade(trade_record)
        print(f"[OK] Buy executed: approx {approx_quantity:.6f} BTC at ${current_price:,.2f} ({trade_type}) for ${amount_usd}")
        return trade_record
    except Exception as e:
        print(f"[ERROR] Buy failed: {e}")
        return None

async def execute_sell(client, quantity, current_price, trade_type="SELL"):
    try:
        quantity = round(quantity, 6)
        if quantity < 0.0001:
            print(f"[ERROR] Sell quantity {quantity} is below minimum lot size (0.0001 BTC)")
            return None
        quantity_str = format(quantity, 'f')
        order = client.order_market_sell(symbol='BTCUSDT', quantity=quantity_str)
        trade_time = datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')
        portfolio = get_portfolio(client)
        btc_balance = portfolio['btc']
        btc_value_usd = round(btc_balance * current_price, 2)
        # Calculate profit/loss compared to previous BTC VALUE USD
        prev_btc_value_usd = None
        try:
            df = pd.read_csv('../data/trade_log.csv')
            last_trade = df[df['btc_value_usd'].notnull() & (df['btc_value_usd'] != '')].iloc[-1] if not df[df['btc_value_usd'].notnull() & (df['btc_value_usd'] != '')].empty else None
            if last_trade is not None:
                prev_btc_value_usd = float(last_trade['btc_value_usd'])
        except Exception:
            prev_btc_value_usd = None
        profit_loss_usd = ''
        if prev_btc_value_usd is not None:
            profit_loss_usd = round(btc_value_usd - prev_btc_value_usd, 2)
        trade_record = {
            'timestamp': trade_time,
            'type': 'SELL',
            'trade_type': trade_type,
            'price': current_price,
            'quantity': quantity,
            'amount_usd': quantity * current_price,
            'btc_balance': btc_balance,
            'btc_value_usd': btc_value_usd,
            'profit_loss_usd': profit_loss_usd
        }
        await log_trade(trade_record)
        print(f"[OK] Sell executed: {quantity_str} BTC at ${current_price:,.2f} ({trade_type})")
        return trade_record
    except Exception as e:
        print(f"[ERROR] Sell failed: {e}")
        return None

if __name__ == "__main__":
    print(f"Testing trade_executor module with {'Binance Spot Testnet' if testnet_mode else 'Binance Live'}...")
    async def main():
        try:
            client = initialize_binance_client()
            portfolio = get_portfolio(client)
            print(f"[TEST] Initial Portfolio: {portfolio['btc']:.6f} BTC, ${portfolio['usdt']:,.2f} USDT")
            ticker = client.get_symbol_ticker(symbol='BTCUSDT')
            current_price = float(ticker['price'])
            print(f"[TEST] Current BTC price: ${current_price:,.2f}")
            
            # Calculate minimum USDT for 0.0001 BTC and MIN_NOTIONAL
            #min_buy_usdt = max(round(0.0001 * current_price + 1, 2), 10)  # Ensure $10 minimum notional
            min_buy_usdt  = 150 
            print(f"[TEST] Minimum USDT required for buy: ${min_buy_usdt:,.2f}")
            
            # Perform a test buy trade (minimum required USDT)
            if portfolio['usdt'] >= min_buy_usdt:
                trade_record = await execute_buy(client, min_buy_usdt, current_price, trade_type="TEST_BUY")
                if trade_record:
                    print(f"[TEST] Buy trade executed: {trade_record}")
                else:
                    print("[TEST] Buy trade failed")
            else:
                print("[TEST] Insufficient USDT balance for test buy")
            
            portfolio = get_portfolio(client)
            print(f"[TEST] Portfolio after buy: {portfolio['btc']:.6f} BTC, ${portfolio['usdt']:,.2f} USDT")
            
            # Perform a test sell trade (sell 0.01 BTC if available)
            if portfolio['btc'] >= 0.001:
                trade_record = await execute_sell(client, 0.001, current_price, trade_type="TEST_SELL")
                if trade_record:
                    print(f"[TEST] Sell trade executed: {trade_record}")
                else:
                    print("[TEST] Sell trade failed")
            else:
                print("[TEST] Insufficient BTC balance for test sell")
            
            portfolio = get_portfolio(client)
            print(f"[TEST] Portfolio after sell: {portfolio['btc']:.6f} BTC, ${portfolio['usdt']:,.2f} USDT")
        except Exception as e:
            print(f"[TEST ERROR] {e}")
    asyncio.run(main())
