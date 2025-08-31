# """
# Script: export_hourly_yahoo_binance_excel.py
# Purpose: Collect last 6 months of hourly BTC/USD data from Yahoo Finance and Binance, and save to a single Excel file with separate columns for each source.
# Dependencies: pandas, yfinance, ccxt
# Usage: python last_6_months_hourly_data_btc.py
# """

# import os
# import pandas as pd
# import yfinance as yf
# import ccxt
# from datetime import datetime, timedelta, timezone

# def fetch_yahoo_hourly():
#     """Fetch 6 months of hourly BTC/USD data from Yahoo Finance."""
#     print("[INFO] Fetching Yahoo Finance hourly data...")
#     btc = yf.Ticker("BTC-USD")
#     hist = btc.history(period="6mo", interval="1h")
#     hist_df = hist.reset_index()
#     hist_df = hist_df.rename(columns={
#         'Open': 'yahoo_open',
#         'High': 'yahoo_high',
#         'Low': 'yahoo_low',
#         'Close': 'yahoo_close',
#         'Volume': 'yahoo_volume',
#         'Datetime': 'date'
#     })
#     # Ensure 'date' column is present and timezone-naive
#     if 'Date' in hist_df.columns:
#         hist_df['date'] = pd.to_datetime(hist_df['Date']).dt.tz_localize(None)
#     else:
#         hist_df['date'] = pd.to_datetime(hist_df['date']).dt.tz_localize(None)
#     hist_df = hist_df[['date', 'yahoo_open', 'yahoo_high', 'yahoo_low', 'yahoo_close', 'yahoo_volume']]
#     print(f"[OK] Yahoo Finance: {len(hist_df)} hourly records")
#     return hist_df

# def fetch_binance_hourly(symbol='BTC/USDT', months=6):
#     """Fetch 6 months of hourly BTC/USDT data from Binance using ccxt."""
#     print("[INFO] Fetching Binance hourly data...")
#     exchange = ccxt.binance()
#     since = exchange.parse8601((datetime.now(timezone.utc) - timedelta(days=30*months)).strftime('%Y-%m-%dT%H:%M:%S'))
#     all_ohlcv = []
#     timeframe = '1h'
#     limit = 1000

#     while True:
#         ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
#         if not ohlcv:
#             break
#         all_ohlcv += ohlcv
#         since = ohlcv[-1][0] + 1
#         print(f"  Downloaded {len(all_ohlcv)} rows so far...")
#         if len(ohlcv) < limit:
#             break

#     df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'binance_open', 'binance_high', 'binance_low', 'binance_close', 'binance_volume'])
#     df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize(None)
#     df = df[['date', 'binance_open', 'binance_high', 'binance_low', 'binance_close', 'binance_volume']]
#     print(f"[OK] Binance: {len(df)} hourly records")
#     return df

# def merge_and_export(yahoo_df, binance_df, output_path):
#     """Merge Yahoo and Binance hourly data on date and export to Excel."""
#     print("[INFO] Merging Yahoo and Binance data...")
#     yahoo_df['date'] = pd.to_datetime(yahoo_df['date']).dt.tz_localize(None)
#     binance_df['date'] = pd.to_datetime(binance_df['date']).dt.tz_localize(None)
#     combined = pd.merge(yahoo_df, binance_df, on='date', how='outer')
#     combined = combined.sort_values('date').reset_index(drop=True)
#     # Only create directory if one is specified
#     dir_name = os.path.dirname(output_path)
#     if dir_name:
#         os.makedirs(dir_name, exist_ok=True)
#     combined.to_excel(output_path, index=False)
#     print(f"✅ Combined hourly data saved to Excel: {output_path}")

# if __name__ == "__main__":
#     yahoo_df = fetch_yahoo_hourly()
#     binance_df = fetch_binance_hourly()
#     output_path = 'btc_hourly_yahoo_binance_6mo.xlsx'  # Save in current directory
#     merge_and_export(yahoo_df, binance_df, output_path)

# --------------------- Trying to fix binance api data missing issue -----------------------------------------------
"""
Script: export_hourly_yahoo_binance_excel.py
Purpose: Collect last 6 months of hourly BTC/USD data from Yahoo Finance and Binance, and save to a single Excel file with separate columns for each source.
Dependencies: pandas, yfinance, ccxt
Usage: python last_6_months_hourly_data_btc.py
"""

import os
import pandas as pd
import yfinance as yf
import ccxt
from datetime import datetime, timedelta, timezone

def fetch_yahoo_hourly():
    """Fetch 6 months of hourly BTC/USD data from Yahoo Finance."""
    print("[INFO] Fetching Yahoo Finance hourly data...")
    btc = yf.Ticker("BTC-USD")
    hist = btc.history(period="6mo", interval="1h")
    hist_df = hist.reset_index()
    hist_df = hist_df.rename(columns={
        'Open': 'yahoo_open',
        'High': 'yahoo_high',
        'Low': 'yahoo_low',
        'Close': 'yahoo_close',
        'Volume': 'yahoo_volume',
        'Datetime': 'date'
    })
    # Ensure 'date' column is present and timezone-naive
    if 'Date' in hist_df.columns:
        hist_df['date'] = pd.to_datetime(hist_df['Date']).dt.tz_localize(None)
    else:
        hist_df['date'] = pd.to_datetime(hist_df['date']).dt.tz_localize(None)
    hist_df = hist_df[['date', 'yahoo_open', 'yahoo_high', 'yahoo_low', 'yahoo_close', 'yahoo_volume']]
    print(f"[OK] Yahoo Finance: {len(hist_df)} hourly records")
    print("Earliest Yahoo date:", hist_df['date'].min())
    print("Latest Yahoo date:", hist_df['date'].max())
    return hist_df

def fetch_binance_hourly(symbol='BTC/USDT', months=6):
    """Fetch 6 months of hourly BTC/USDT data from Binance using ccxt."""
    print("[INFO] Fetching Binance hourly data...")
    exchange = ccxt.binance()
    since = exchange.parse8601((datetime.now(timezone.utc) - timedelta(days=30*months)).strftime('%Y-%m-%dT%H:%M:%S'))
    all_ohlcv = []
    timeframe = '1h'
    limit = 1000

    while True:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
        if not ohlcv:
            break
        all_ohlcv += ohlcv
        since = ohlcv[-1][0] + 1
        print(f"  Downloaded {len(all_ohlcv)} rows so far...")
        if len(ohlcv) < limit:
            break

    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'binance_open', 'binance_high', 'binance_low', 'binance_close', 'binance_volume'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize(None)
    print(f"[OK] Binance: {len(df)} hourly records")
    print("Earliest Binance date:", df['date'].min())
    print("Latest Binance date:", df['date'].max())
    df = df[['date', 'binance_open', 'binance_high', 'binance_low', 'binance_close', 'binance_volume']]
    return df

def merge_and_export(yahoo_df, binance_df, output_path):
    """Merge Yahoo and Binance hourly data on date and export to Excel."""
    print("[INFO] Merging Yahoo and Binance data...")
    yahoo_df['date'] = pd.to_datetime(yahoo_df['date']).dt.tz_localize(None)
    binance_df['date'] = pd.to_datetime(binance_df['date']).dt.tz_localize(None)
    combined = pd.merge(yahoo_df, binance_df, on='date', how='outer')
    combined = combined.sort_values('date').reset_index(drop=True)
    # Only create directory if one is specified
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    combined.to_excel(output_path, index=False)
    print(f"✅ Combined hourly data saved to Excel: {output_path}")

if __name__ == "__main__":
    yahoo_df = fetch_yahoo_hourly()
    binance_df = fetch_binance_hourly()
    output_path = 'btc_hourly_yahoo_binance_6mo.xlsx'  # Save in current directory