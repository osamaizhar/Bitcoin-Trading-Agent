
# # ---------------------------------------- LLM Decision Part ----------------------------------------------------------
#         context = {
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'trade_history': trade_log[-10:]
#         }
#         if count < 6 :
#             print(f"Context Passing into LLM: {json.dumps(context, indent=2)}")
#             count+=1
#         # Get LLM suggestion using the combined module
#         llm_suggestion = get_llm_decision({
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'trade_history': trade_log[-10:]
#         })
        
#         # Pass LLM suggestion to manage_trades (not trade_log)
#         decision, active_trades = manage_trades(portfolio, active_trades, llm_suggestion)
#         print(f"[INFO] Decision made: {decision}\n Active trades: {active_trades}")
        
#         # Process the single decision (not a list)
#         if decision and decision['action'] == 'BUY' and portfolio['usdt'] >= decision['amount']:
#             btc_bought = decision['amount'] / current_price
#             portfolio['btc'] += btc_bought
#             portfolio['usdt'] -= decision['amount']
#             portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#             trade_record = {
#                 'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'type': 'BUY',
#                 'price': current_price,
#                 'quantity': btc_bought,
#                 'amount_usd': decision['amount'],
#                 'btc_balance': portfolio['btc'],
#                 'btc_value_usd': portfolio['btc'] * current_price,
#                 'portfolio_value': portfolio['btc'] * current_price + portfolio['usdt'],
#                 'usdt_balance': portfolio['usdt'],
#                 'profit_loss_usd': ''
#             }
#             log_trade(trade_record, trade_log, trade_log_path)
#             await log_trade_to_google_sheet(trade_record)
#         elif decision and decision['action'] == 'SELL' and portfolio['btc'] >= decision['quantity']:
#             portfolio['btc'] -= decision['quantity']
#             portfolio['usdt'] += decision['quantity'] * current_price
#             portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#             trade_record = {
#                 'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'type': 'SELL',
#                 'price': current_price,
#                 'quantity': decision['quantity'],
#                 'amount_usd': decision['quantity'] * current_price,
#                 'btc_balance': portfolio['btc'],
#                 'btc_value_usd': portfolio['btc'] * current_price,
#                 'portfolio_value': portfolio_value,
#                 'usdt_balance': portfolio['usdt'],
#                 'profit_loss_usd': ''
#             }
#             log_trade(trade_record, trade_log, trade_log_path)
#             await log_trade_to_google_sheet(trade_record)
#             active_trades = [t for t in active_trades if t.get('quantity', None) != decision['quantity']]
#         elif decision and decision['action'] == 'HOLD':
#             portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#             trade_record = {
#                 'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'type': 'HOLD',
#                 'price': current_price,
#                 'quantity': 0,
#                 'amount_usd': 0,
#                 'btc_balance': portfolio['btc'],
#                 'btc_value_usd': portfolio['btc'] * current_price,
#                 'portfolio_value': portfolio_value,
#                 'usdt_balance': portfolio['usdt'],
#                 'profit_loss_usd': ''
#             }
#             log_trade(trade_record, trade_log, trade_log_path)
#             await log_trade_to_google_sheet(trade_record)
            
#         portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#         portfolio_history.append({'date': current_date, 'value': portfolio_value})

#         # Daily P&L calculation
#         day = current_date.date()
#         if prev_day is None:
#             prev_day = day
#             prev_day_value = portfolio_value
#         if day != prev_day:
#             daily_pnl = portfolio_value - prev_day_value
#             daily_pnl_log.append({'date': prev_day, 'daily_pnl': daily_pnl, 'portfolio_value': prev_day_value})
#             prev_day = day
#             prev_day_value = portfolio_value

#     # Final day P&L
#     if prev_day is not None:
#         daily_pnl = portfolio_value - prev_day_value
#         daily_pnl_log.append({'date': prev_day, 'daily_pnl': daily_pnl, 'portfolio_value': portfolio_value})

#     # Fill daily_pnl for each trade
#     for trade in trade_log:
#         trade_day = datetime.strptime(trade['Timestamp'], '%Y-%m-%d %H:%M:%S').date()
#         trade['PROFIT / LOSS USD'] = next((d['daily_pnl'] for d in daily_pnl_log if d['date'] == trade_day), None)

#     pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)
#     daily_pnl_df = pd.DataFrame(daily_pnl_log)
#     portfolio_df = pd.DataFrame(portfolio_history)
    
#     # Generate summary statistics
#     if len(portfolio_df) > 0:
#         initial_value = portfolio_df['value'].iloc[0]
#         final_value = portfolio_df['value'].iloc[-1]
#         total_return = (final_value - initial_value) / initial_value * 100
#         num_trades = len(trade_log)
        
#         print("\n[BACKTEST SUMMARY]")
#         print(f"Initial Value: ${initial_value:,.2f}")
#         print(f"Final Value: ${final_value:,.2f}")
#         print(f"Total Return: {total_return:.2f}%")
#         print(f"Number of Trades: {num_trades}")
#         print(f"Max Portfolio Value: ${portfolio_df['value'].max():,.2f}")
#         print(f"Min Portfolio Value: ${portfolio_df['value'].min():,.2f}")
        
#         # Plot results
#         plt.figure(figsize=(14, 6))
#         plt.subplot(2, 1, 1)
#         plt.plot(portfolio_df['date'], portfolio_df['value'], label='Portfolio Value')
#         plt.title('Portfolio Value Over Time')
#         plt.ylabel('Value (USD)')
#         plt.legend()
        
#         if len(daily_pnl_df) > 0:
#             plt.subplot(2, 1, 2)
#             plt.bar(daily_pnl_df['date'], daily_pnl_df['daily_pnl'], label='Daily P&L')
#             plt.title('Daily Profit/Loss')
#             plt.ylabel('Daily P&L (USD)')
#             plt.xlabel('Date')
#             plt.legend()
        
#         plt.tight_layout()
#         plt.show()
#     else:
#         print("[ERROR] No portfolio data generated during backtest!")

#     if os.path.exists(temp_md_path):
#         os.remove(temp_md_path)

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     asyncio.run(run_backtest())
#     print("Backtest completed.")








# ----------------------------------------- removed google sheet ---------------------------------
# import os
# import sys
# import asyncio
# import pandas as pd
# import matplotlib.pyplot as plt
# from datetime import datetime, timedelta
# import ta
# import json
# from llm_decision_strategy_05 import manage_trades, get_llm_decision

# # ---- EDIT THESE SETTINGS TO CHANGE INTERVAL AND DURATION ----
# TRADE_INTERVAL_HOURS = 1      # Set to 1 for hourly, 24 for daily, etc.
# TRADE_DURATION = "1 week"     # <--- Change this to your desired duration

# def parse_duration(duration_str):
#     duration_str = duration_str.lower().strip()
#     if "day" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=n)
#     elif "week" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(weeks=n)
#     elif "month" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=30 * n)
#     else:
#         return timedelta(weeks=1)

# def load_config():
#     config = {}
#     with open("config.cfg", "r") as f:
#         for line in f:
#             if line.strip() and not line.startswith('#'):
#                 parts = line.strip().split('=', 1)
#                 key = parts[0].strip()
#                 value = parts[1].strip() if len(parts) > 1 else ''
#                 if value.lower() == 'true':
#                     config[key] = True
#                 elif value.lower() == 'false':
#                     config[key] = False
#                 elif value.replace('.', '', 1).isdigit():
#                     config[key] = float(value)
#                 else:
#                     config[key] = value
#     print(f"Fetched Config : {config}")
#     return config

# def generate_md_report(current_date, row, indicators, portfolio, current_price):
#     md_content = f"""
# # Complete Bitcoin Data Collection Report

# ## Yahoo Finance Data

# | Date | Open | High | Low | Close | Volume |
# |------|------|------|-----|-------|--------|
# | {current_date.strftime('%Y-%m-%d %H:%M:%S')} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,.0f} |

# ### Technical Indicators (Current Values)

# - **ATR (14)**: ${indicators['atr_14']:,.2f}
# - **RSI (14)**: {indicators['rsi_14']:.2f}
# - **SMA 20**: ${indicators['sma_20']:,.2f}
# - **SMA 50**: ${indicators['sma_50']:,.2f}
# - **MACD**: {indicators['macd']:.2f}
# - **MACD Signal**: {indicators['macd_signal']:.2f}

# ## Portfolio Status

# - BTC: {portfolio['btc']}
# - USDT: {portfolio['usdt']}
# - Portfolio Value: {portfolio['btc'] * current_price + portfolio['usdt']}
# """
#     return md_content

# def log_trade(trade_record, trade_log):
#     trade_log.append(trade_record)

# async def run_backtest():
#     # Use CSV for faster loading if available
#     data_file = 'btc_hourly_yahoo_binance_6mo.csv'
#     if not os.path.exists(data_file):
#         data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
#     if not os.path.exists(data_file):
#         print(f"ERROR: Data file '{data_file}' not found!")
#         return

#     # Load data
#     if data_file.endswith('.csv'):
#         df = pd.read_csv(data_file)
#     else:
#         df = pd.read_excel(data_file)
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)

#     print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

#     # Fill price columns
#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])

#     # Precompute indicators (outside loop)
#     df['atr_14'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
#     df['rsi_14'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
#     df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
#     df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
#     macd_indicator = ta.trend.MACD(df['close'])
#     df['macd'] = macd_indicator.macd()
#     df['macd_signal'] = macd_indicator.macd_signal()

#     config = load_config()
#     budget = config.get('budget', 10000)
#     portfolio = {'btc': 0.0, 'usdt': budget}
#     active_trades = []
#     trade_log = []
#     trade_log_path = "backtest_trade_log.csv"
#     if os.path.exists(trade_log_path):
#         os.remove(trade_log_path)
#     portfolio_history = []
#     daily_pnl_log = []

#     prev_day = None
#     prev_day_value = None

#     subsample = TRADE_INTERVAL_HOURS
#     end_date = df['date'].max()
#     duration = parse_duration(TRADE_DURATION)
#     start_date = end_date - duration

#     print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

#     df_test = df[df['date'] >= start_date]
#     if len(df_test) == 0:
#         print(f"[ERROR] No data found for the selected period!")
#         return

#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")
#     count = 0
#     for i, row in df_subsampled.iterrows():
#         if pd.isna(row['close']):
#             continue
#         current_date = row['date']
#         current_price = row['close']
#         indicators = {
#             'atr_14': row['atr_14'],
#             'rsi_14': row['rsi_14'],
#             'sma_20': row['sma_20'],
#             'sma_50': row['sma_50'],
#             'macd': row['macd'],
#             'macd_signal': row['macd_signal']
#         }
#         md_content = generate_md_report(current_date, row, indicators, portfolio, current_price)
#         context = {
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'trade_history': trade_log[-10:]
#         }
#         if count < 1:
#             print(f"Context Passing into LLM: {json.dumps(context, indent=2)}")
#             count += 1
#         llm_suggestion = get_llm_decision({
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'trade_history': trade_log[-10:]
#         })
#         decision, active_trades = manage_trades(portfolio, active_trades, llm_suggestion)
#         print(f"[INFO] Decision made: {decision}\n Active trades: {active_trades}")

#         # Log only to memory, write to CSV every 10 trades
#         if decision and decision['action'] == 'BUY' and portfolio['usdt'] >= decision['amount']:
#             btc_bought = decision['amount'] / current_price
#             portfolio['btc'] += btc_bought
#             portfolio['usdt'] -= decision['amount']
#             portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#             trade_record = {
#                 'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'Type': 'BUY',
#                 'Price BTC': current_price,
#                 'Quantity': btc_bought,
#                 'Value USD (Cost)': decision['amount'],
#                 'BTC BALANCE': portfolio['btc'],
#                 'BTC VALUE USD': portfolio['btc'] * current_price,
#                 'Total Portfolio Value': portfolio['btc'] * current_price + portfolio['usdt'],
#                 'USD BALANCE': portfolio['usdt'],
#                 'PROFIT / LOSS USD': ''
#             }
#             log_trade(trade_record, trade_log)
#         elif decision and decision['action'] == 'SELL' and portfolio['btc'] >= decision['quantity']:
#             portfolio['btc'] -= decision['quantity']
#             portfolio['usdt'] += decision['quantity'] * current_price
#             portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#             trade_record = {
#                 'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'Type': 'SELL',
#                 'Price BTC': current_price,
#                 'Quantity': decision['quantity'],
#                 'Value USD (Cost)': decision['quantity'] * current_price,
#                 'BTC BALANCE': portfolio['btc'],
#                 'BTC VALUE USD': portfolio['btc'] * current_price,
#                 'Total Portfolio Value': portfolio_value,
#                 'USD BALANCE': portfolio['usdt'],
#                 'PROFIT / LOSS USD': ''
#             }
#             log_trade(trade_record, trade_log)
#             active_trades = [t for t in active_trades if t.get('quantity', None) != decision['quantity']]
#         elif decision and decision['action'] == 'HOLD':
#             portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#             trade_record = {
#                 'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'Type': 'HOLD',
#                 'Price BTC': current_price,
#                 'Quantity': 0,
#                 'Value USD (Cost)': 0,
#                 'BTC BALANCE': portfolio['btc'],
#                 'BTC VALUE USD': portfolio['btc'] * current_price,
#                 'Total Portfolio Value': portfolio_value,
#                 'USD BALANCE': portfolio['usdt'],
#                 'PROFIT / LOSS USD': ''
#             }
#             log_trade(trade_record, trade_log)

#         # Write to CSV every 10 trades
#         if len(trade_log) % 10 == 0 and len(trade_log) > 0:
#             pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

#         portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#         portfolio_history.append({'date': current_date, 'value': portfolio_value})

#         day = current_date.date()
#         if prev_day is None:
#             prev_day = day
#             prev_day_value = portfolio_value
#         if day != prev_day:
#             daily_pnl = portfolio_value - prev_day_value
#             daily_pnl_log.append({'date': prev_day, 'daily_pnl': daily_pnl, 'portfolio_value': prev_day_value})
#             prev_day = day
#             prev_day_value = portfolio_value

#     if prev_day is not None:
#         daily_pnl = portfolio_value - prev_day_value
#         daily_pnl_log.append({'date': prev_day, 'daily_pnl': daily_pnl, 'portfolio_value': portfolio_value})

#     for trade in trade_log:
#         trade_day = datetime.strptime(trade['Timestamp'], '%Y-%m-%d %H:%M:%S').date()
#         trade['PROFIT / LOSS USD'] = next((d['daily_pnl'] for d in daily_pnl_log if d['date'] == trade_day), None)

#     # Write any remaining trades at the end
#     if len(trade_log) % 10 != 0:
#         pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)
#     daily_pnl_df = pd.DataFrame(daily_pnl_log)
#     portfolio_df = pd.DataFrame(portfolio_history)

#     if len(portfolio_df) > 0:
#         initial_value = portfolio_df['value'].iloc[0]
#         final_value = portfolio_df['value'].iloc[-1]
#         total_return = (final_value - initial_value) / initial_value * 100
#         num_trades = len(trade_log)

#         print("\n[BACKTEST SUMMARY]")
#         print(f"Initial Value: ${initial_value:,.2f}")
#         print(f"Final Value: ${final_value:,.2f}")
#         print(f"Total Return: {total_return:.2f}%")
#         print(f"Number of Trades: {num_trades}")
#         print(f"Max Portfolio Value: ${portfolio_df['value'].max():,.2f}")
#         print(f"Min Portfolio Value: ${portfolio_df['value'].min():,.2f}")

#         plt.figure(figsize=(14, 6))
#         plt.subplot(2, 1, 1)
#         plt.plot(portfolio_df['date'], portfolio_df['value'], label='Portfolio Value')
#         plt.title('Portfolio Value Over Time')
#         plt.ylabel('Value (USD)')
#         plt.legend()

#         if len(daily_pnl_df) > 0:
#             plt.subplot(2, 1, 2)
#             plt.bar(daily_pnl_df['date'], daily_pnl_df['daily_pnl'], label='Daily P&L')
#             plt.title('Daily Profit/Loss')
#             plt.ylabel('Daily P&L (USD)')
#             plt.xlabel('Date')
#             plt.legend()

#         plt.tight_layout()
#         plt.show()
#     else:
#         print("[ERROR] No portfolio data generated during backtest!")

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     asyncio.run(run_backtest())
#     print("Backtest completed.")
    

# ----------------------------------------- changed llm output and prints a bit ---------------------------------

# import os
# import sys
# import asyncio
# import pandas as pd
# import functools
# import matplotlib.pyplot as plt
# from datetime import datetime, timedelta
# import time
# import ta
# import json
# from llm_decision_strategy_05 import manage_trades, get_llm_decision

# # ---- EDIT THESE SETTINGS TO CHANGE INTERVAL AND DURATION ----
# TRADE_INTERVAL_HOURS = 1      # Set to 1 for hourly, 24 for daily, etc.
# TRADE_DURATION = "1 week"     # <--- Change this to your desired duration

# def parse_duration(duration_str):
#     duration_str = duration_str.lower().strip()
#     if "day" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=n)
#     elif "week" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(weeks=n)
#     elif "month" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=30 * n)
#     else:
#         return timedelta(weeks=1)

# def load_config():
#     config = {}
#     with open("config.cfg", "r") as f:
#         for line in f:
#             if line.strip() and not line.startswith('#'):
#                 parts = line.strip().split('=', 1)
#                 key = parts[0].strip()
#                 value = parts[1].strip() if len(parts) > 1 else ''
#                 if value.lower() == 'true':
#                     config[key] = True
#                 elif value.lower() == 'false':
#                     config[key] = False
#                 elif value.replace('.', '', 1).isdigit():
#                     config[key] = float(value)
#                 else:
#                     config[key] = value
#     print(f"Fetched Config : {config}")
#     return config

# def generate_md_report(current_date, row, indicators, portfolio, current_price):
#     md_content = f"""
# # Complete Bitcoin Data Collection Report

# ## Yahoo Finance Data

# | Date | Open | High | Low | Close | Volume |
# |------|------|------|-----|-------|--------|
# | {current_date.strftime('%Y-%m-%d %H:%M:%S')} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,.0f} |

# ### Technical Indicators (Current Values)

# - **ATR (14)**: ${indicators['atr_14']:,.2f}
# - **RSI (14)**: {indicators['rsi_14']:.2f}
# - **SMA 20**: ${indicators['sma_20']:,.2f}
# - **SMA 50**: ${indicators['sma_50']:,.2f}
# - **MACD**: {indicators['macd']:.2f}
# - **MACD Signal**: {indicators['macd_signal']:.2f}

# ## Portfolio Status

# - BTC: {portfolio['btc']}
# - USDT: {portfolio['usdt']}
# - Portfolio Value: {portfolio['btc'] * current_price + portfolio['usdt']}
# """
#     return md_content

# def log_trade(trade_record, trade_log):
#     trade_log.append(trade_record)

# async def run_backtest():
#     # Use CSV for faster loading if available
#     data_file = 'btc_hourly_yahoo_binance_6mo.csv'
#     if not os.path.exists(data_file):
#         data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
#     if not os.path.exists(data_file):
#         print(f"ERROR: Data file '{data_file}' not found!")
#         return

#     # Load data
#     if data_file.endswith('.csv'):
#         df = pd.read_csv(data_file)
#     else:
#         df = pd.read_excel(data_file)
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)

#     print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

#     # Fill price columns
#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])

#     # Precompute indicators (outside loop)
#     df['atr_14'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
#     df['rsi_14'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
#     df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
#     df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
#     macd_indicator = ta.trend.MACD(df['close'])
#     df['macd'] = macd_indicator.macd()
#     df['macd_signal'] = macd_indicator.macd_signal()

#     config = load_config()
#     budget = config.get('budget', 10000)
#     portfolio = {'btc': 0.0, 'usdt': budget}
#     active_trades = []
#     trade_log = []
#     trade_log_path = "backtest_trade_log.csv"
#     if os.path.exists(trade_log_path):
#         os.remove(trade_log_path)
#     portfolio_history = []
#     daily_pnl_log = []

#     prev_day = None
#     prev_day_value = None

#     subsample = TRADE_INTERVAL_HOURS
#     end_date = df['date'].max()
#     duration = parse_duration(TRADE_DURATION)
#     start_date = end_date - duration

#     print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

#     df_test = df[df['date'] >= start_date]
#     if len(df_test) == 0:
#         print(f"[ERROR] No data found for the selected period!")
#         return

#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")

#     decision_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}
#     for i, row in df_subsampled.iterrows():
#         if pd.isna(row['close']):
#             continue
#         current_date = row['date']
#         current_price = row['close']
#         indicators = {
#             'atr_14': row['atr_14'],
#             'rsi_14': row['rsi_14'],
#             'sma_20': row['sma_20'],
#             'sma_50': row['sma_50'],
#             'macd': row['macd'],
#             'macd_signal': row['macd_signal']
#         }
#         md_content = generate_md_report(current_date, row, indicators, portfolio, current_price)
#         context = {
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'trade_history': trade_log[-10:]
#         }
#         # llm_suggestion = get_llm_decision({
#         #     'md_content': md_content,
#         #     'portfolio': portfolio,
#         #     'trade_history': trade_log[-10:]
#         # })
#         # print(f"LLM Suggestion: {llm_suggestion}")
#         decision, active_trades = manage_trades(portfolio, active_trades, llm_suggestion)

#         # Print only the decision and increment count
#         print(f"Trade {i+1}: Decision = {decision['action']}")
#         if decision['action'] in decision_counts:
#             decision_counts[decision['action']] += 1

#         # Log only to memory, write to CSV every 10 trades
#         if decision and decision['action'] == 'BUY' and portfolio['usdt'] >= decision.get('amount', 0):
#             btc_bought = decision['amount'] / current_price
#             portfolio['btc'] += btc_bought
#             portfolio['usdt'] -= decision['amount']
#             portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#             trade_record = {
#                 'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'Type': 'BUY',
#                 'Price BTC': current_price,
#                 'Quantity': btc_bought,
#                 'Value USD (Cost)': decision['amount'],
#                 'BTC BALANCE': portfolio['btc'],
#                 'BTC VALUE USD': portfolio['btc'] * current_price,
#                 'Total Portfolio Value': portfolio['btc'] * current_price + portfolio['usdt'],
#                 'USD BALANCE': portfolio['usdt'],
#                 'PROFIT / LOSS USD': ''
#             }
#             log_trade(trade_record, trade_log)
#         elif decision and decision['action'] == 'SELL' and portfolio['btc'] >= decision.get('quantity', 0):
#             portfolio['btc'] -= decision['quantity']
#             portfolio['usdt'] += decision['quantity'] * current_price
#             portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#             trade_record = {
#                 'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'Type': 'SELL',
#                 'Price BTC': current_price,
#                 'Quantity': decision['quantity'],
#                 'Value USD (Cost)': decision['quantity'] * current_price,
#                 'BTC BALANCE': portfolio['btc'],
#                 'BTC VALUE USD': portfolio['btc'] * current_price,
#                 'Total Portfolio Value': portfolio_value,
#                 'USD BALANCE': portfolio['usdt'],
#                 'PROFIT / LOSS USD': ''
#             }
#             log_trade(trade_record, trade_log)
#             active_trades = [t for t in active_trades if t.get('quantity', None) != decision['quantity']]
#         elif decision and decision['action'] == 'HOLD':
#             portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#             trade_record = {
#                 'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'Type': 'HOLD',
#                 'Price BTC': current_price,
#                 'Quantity': 0,
#                 'Value USD (Cost)': 0,
#                 'BTC BALANCE': portfolio['btc'],
#                 'BTC VALUE USD': portfolio['btc'] * current_price,
#                 'Total Portfolio Value': portfolio_value,
#                 'USD BALANCE': portfolio['usdt'],
#                 'PROFIT / LOSS USD': ''
#             }
#             log_trade(trade_record, trade_log)

#         # Write to CSV every 10 trades
#         if len(trade_log) % 10 == 0 and len(trade_log) > 0:
#             pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

#         portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#         portfolio_history.append({'date': current_date, 'value': portfolio_value})

#         day = current_date.date()
#         if prev_day is None:
#             prev_day = day
#             prev_day_value = portfolio_value
#         if day != prev_day:
#             daily_pnl = portfolio_value - prev_day_value
#             daily_pnl_log.append({'date': prev_day, 'daily_pnl': daily_pnl, 'portfolio_value': prev_day_value})
#             prev_day = day
#             prev_day_value = portfolio_value

#     if prev_day is not None:
#         daily_pnl = portfolio_value - prev_day_value
#         daily_pnl_log.append({'date': prev_day, 'daily_pnl': daily_pnl, 'portfolio_value': portfolio_value})

#     for trade in trade_log:
#         trade_day = datetime.strptime(trade['Timestamp'], '%Y-%m-%d %H:%M:%S').date()
#         trade['PROFIT / LOSS USD'] = next((d['daily_pnl'] for d in daily_pnl_log if d['date'] == trade_day), None)

#     # Write any remaining trades at the end
#     if len(trade_log) % 10 != 0:
#         pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)
#     daily_pnl_df = pd.DataFrame(daily_pnl_log)
#     portfolio_df = pd.DataFrame(portfolio_history)

#     print("\nDecision Counts:")
#     for k, v in decision_counts.items():
#         print(f"{k}: {v}")

#     if len(portfolio_df) > 0:
#         initial_value = portfolio_df['value'].iloc[0]
#         final_value = portfolio_df['value'].iloc[-1]
#         total_return = (final_value - initial_value) / initial_value * 100
#         num_trades = len(trade_log)

#         print("\n[BACKTEST SUMMARY]")
#         print(f"Initial Value: ${initial_value:,.2f}")
#         print(f"Final Value: ${final_value:,.2f}")
#         print(f"Total Return: {total_return:.2f}%")
#         print(f"Number of Trades: {num_trades}")
#         print(f"Max Portfolio Value: ${portfolio_df['value'].max():,.2f}")
#         print(f"Min Portfolio Value: ${portfolio_df['value'].min():,.2f}")

#         plt.figure(figsize=(14, 6))
#         plt.subplot(2, 1, 1)
#         plt.plot(portfolio_df['date'], portfolio_df['value'], label='Portfolio Value')
#         plt.title('Portfolio Value Over Time')
#         plt.ylabel('Value (USD)')
#         plt.legend()

#         if len(daily_pnl_df) > 0:
#             plt.subplot(2, 1, 2)
#             plt.bar(daily_pnl_df['date'], daily_pnl_df['daily_pnl'], label='Daily P&L')
#             plt.title('Daily Profit/Loss')
#             plt.ylabel('Daily P&L (USD)')
#             plt.xlabel('Date')
#             plt.legend()

#         plt.tight_layout()
#         plt.show()
#     else:
#         print("[ERROR] No portfolio data generated during backtest!")

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     asyncio.run(run_backtest())
#     print("Backtest completed.")

# ------------------- Updated manage trades function --------------------------------------------

# import os
# import sys
# import asyncio
# import pandas as pd
# import matplotlib.pyplot as plt
# from datetime import datetime, timedelta
# import time
# import ta
# import json
# from llm_decision_strategy_05 import manage_trades, get_llm_decision

# # ---- EDIT THESE SETTINGS TO CHANGE INTERVAL AND DURATION ----
# TRADE_INTERVAL_HOURS = 1      # Set to 1 for hourly, 24 for daily, etc.
# TRADE_DURATION = "1 week"     # <--- Change this to your desired duration

# def parse_duration(duration_str):
#     duration_str = duration_str.lower().strip()
#     if "day" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=n)
#     elif "week" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(weeks=n)
#     elif "month" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=30 * n)
#     else:
#         return timedelta(weeks=1)

# def load_config():
#     config = {}
#     with open("config.cfg", "r") as f:
#         for line in f:
#             if line.strip() and not line.startswith('#'):
#                 parts = line.strip().split('=', 1)
#                 key = parts[0].strip()
#                 value = parts[1].strip() if len(parts) > 1 else ''
#                 if value.lower() == 'true':
#                     config[key] = True
#                 elif value.lower() == 'false':
#                     config[key] = False
#                 elif value.replace('.', '', 1).isdigit():
#                     config[key] = float(value)
#                 else:
#                     config[key] = value
#     print(f"Fetched Config : {config}")
#     return config

# def generate_md_report(current_date, row, indicators, portfolio, current_price):
#     md_content = f"""
# # Complete Bitcoin Data Collection Report

# ## Yahoo Finance Data

# | Date | Open | High | Low | Close | Volume |
# |------|------|------|-----|-------|--------|
# | {current_date.strftime('%Y-%m-%d %H:%M:%S')} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,.0f} |

# ### Technical Indicators (Current Values)

# - **ATR (14)**: ${indicators['atr_14']:,.2f}
# - **RSI (14)**: {indicators['rsi_14']:.2f}
# - **SMA 20**: ${indicators['sma_20']:,.2f}
# - **SMA 50**: ${indicators['sma_50']:,.2f}
# - **EMA 12**: ${indicators['ema_12']:,.2f}
# - **EMA 26**: ${indicators['ema_26']:,.2f}
# - **Bollinger Upper (20)**: ${indicators['bb_upper']:,.2f}
# - **Bollinger Middle (20)**: ${indicators['bb_middle']:,.2f}
# - **Bollinger Lower (20)**: ${indicators['bb_lower']:,.2f}
# - **MACD**: {indicators['macd']:.2f}
# - **MACD Signal**: {indicators['macd_signal']:.2f}
# - **Volume SMA 20**: {indicators['volume_sma_20']:,.0f}
# - **ATR Volatility Ratio**: {indicators['atr_volatility_ratio']:.4f}

# ## Portfolio Status

# - BTC: {portfolio['btc']}
# - USDT: {portfolio['usdt']}
# - Portfolio Value: {portfolio['btc'] * current_price + portfolio['usdt']}
# """
#     return md_content

# def log_trade(trade_record, trade_log):
#     trade_log.append(trade_record)

# async def run_backtest():
#     data_file = 'btc_hourly_yahoo_binance_6mo.csv'
#     if not os.path.exists(data_file):
#         data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
#     if not os.path.exists(data_file):
#         print(f"ERROR: Data file '{data_file}' not found!")
#         return

#     if data_file.endswith('.csv'):
#         df = pd.read_csv(data_file)
#     else:
#         df = pd.read_excel(data_file)
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)

#     print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])

#     # Precompute indicators (outside loop) - Added remaining indicators
#     df['atr_14'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
#     df['rsi_14'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
#     df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
#     df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
#     df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
#     df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
#     bb_indicator = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
#     df['bb_upper'] = bb_indicator.bollinger_hband()
#     df['bb_middle'] = bb_indicator.bollinger_mavg()
#     df['bb_lower'] = bb_indicator.bollinger_lband()
#     macd_indicator = ta.trend.MACD(df['close'])
#     df['macd'] = macd_indicator.macd()
#     df['macd_signal'] = macd_indicator.macd_signal()
#     df['volume_sma_20'] = ta.trend.sma_indicator(df['volume'], window=20)
#     df['atr_volatility_ratio'] = df['atr_14'] / df['close']  # Normalized ATR for volatility

#     config = load_config()
#     budget = config.get('budget', 10000)
#     portfolio = {'btc': 0.0, 'usdt': budget}
#     active_trades = []
#     trade_log = []
#     trade_log_path = "backtest_trade_log.csv"
#     if os.path.exists(trade_log_path):
#         os.remove(trade_log_path)
#     portfolio_history = []
#     daily_pnl_log = []

#     prev_day = None
#     prev_day_value = None

#     subsample = TRADE_INTERVAL_HOURS
#     end_date = df['date'].max()
#     duration = parse_duration(TRADE_DURATION)
#     start_date = end_date - duration

#     print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

#     df_test = df[df['date'] >= start_date]
#     if len(df_test) == 0:
#         print(f"[ERROR] No data found for the selected period!")
#         return

#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")

#     decision_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}
#     for i, row in df_subsampled.iterrows():
#         if pd.isna(row['close']):
#             continue
#         current_date = row['date']
#         current_price = row['close']
#         indicators = {
#             'atr_14': row['atr_14'],
#             'rsi_14': row['rsi_14'],
#             'sma_20': row['sma_20'],
#             'sma_50': row['sma_50'],
#             'ema_12': row['ema_12'],
#             'ema_26': row['ema_26'],
#             'bb_upper': row['bb_upper'],
#             'bb_middle': row['bb_middle'],
#             'bb_lower': row['bb_lower'],
#             'macd': row['macd'],
#             'macd_signal': row['macd_signal'],
#             'volume_sma_20': row['volume_sma_20'],
#             'atr_volatility_ratio': row['atr_volatility_ratio']
#         }
#         md_content = generate_md_report(current_date, row, indicators, portfolio, current_price)
#         last_10_trades = trade_log[-10:]
#         context = {
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'trade_history': last_10_trades
#         }
#         decision, active_trades = manage_trades(portfolio, active_trades, last_10_trades, config, context, latest_data=md_content)
#         print(f"Trade {i+1}: Decision = {decision['action']}")
#         if decision['action'] in decision_counts:
#             decision_counts[decision['action']] += 1

#         # Log only to memory, write to CSV every 10 trades
#         if decision and decision['action'] == 'BUY' and portfolio['usdt'] >= decision.get('amount', 0):
#             btc_bought = decision['amount'] / current_price
#             portfolio['btc'] += btc_bought
#             portfolio['usdt'] -= decision['amount']
#             portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#             trade_record = {
#                 'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'Type': 'BUY',
#                 'Price BTC': current_price,
#                 'Quantity': btc_bought,
#                 'Value USD (Cost)': decision['amount'],
#                 'BTC BALANCE': portfolio['btc'],
#                 'BTC VALUE USD': portfolio['btc'] * current_price,
#                 'Total Portfolio Value': portfolio['btc'] * current_price + portfolio['usdt'],
#                 'USD BALANCE': portfolio['usdt'],
#                 'PROFIT / LOSS USD': ''
#             }
#             log_trade(trade_record, trade_log)
#         elif decision and decision['action'] == 'SELL' and portfolio['btc'] >= decision.get('quantity', 0):
#             portfolio['btc'] -= decision['quantity']
#             portfolio['usdt'] += decision['quantity'] * current_price
#             portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#             trade_record = {
#                 'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'Type': 'SELL',
#                 'Price BTC': current_price,
#                 'Quantity': decision['quantity'],
#                 'Value USD (Cost)': decision['quantity'] * current_price,
#                 'BTC BALANCE': portfolio['btc'],
#                 'BTC VALUE USD': portfolio['btc'] * current_price,
#                 'Total Portfolio Value': portfolio_value,
#                 'USD BALANCE': portfolio['usdt'],
#                 'PROFIT / LOSS USD': ''
#             }
#             log_trade(trade_record, trade_log)
#             active_trades = [t for t in active_trades if t.get('quantity', None) != decision['quantity']]
#         elif decision and decision['action'] == 'HOLD':
#             portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#             trade_record = {
#                 'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'Type': 'HOLD',
#                 'Price BTC': current_price,
#                 'Quantity': 0,
#                 'Value USD (Cost)': 0,
#                 'BTC BALANCE': portfolio['btc'],
#                 'BTC VALUE USD': portfolio['btc'] * current_price,
#                 'Total Portfolio Value': portfolio_value,
#                 'USD BALANCE': portfolio['usdt'],
#                 'PROFIT / LOSS USD': ''
#             }
#             log_trade(trade_record, trade_log)

#         # Write to CSV every 10 trades
#         if len(trade_log) % 10 == 0 and len(trade_log) > 0:
#             pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

#         portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#         portfolio_history.append({'date': current_date, 'value': portfolio_value})

#         day = current_date.date()
#         if prev_day is None:
#             prev_day = day
#             prev_day_value = portfolio_value
#         if day != prev_day:
#             daily_pnl = portfolio_value - prev_day_value
#             daily_pnl_log.append({'date': prev_day, 'daily_pnl': daily_pnl, 'portfolio_value': prev_day_value})
#             prev_day = day
#             prev_day_value = portfolio_value

#     if prev_day is not None:
#         daily_pnl = portfolio_value - prev_day_value
#         daily_pnl_log.append({'date': prev_day, 'daily_pnl': daily_pnl, 'portfolio_value': portfolio_value})

#     for trade in trade_log:
#         trade_day = datetime.strptime(trade['Timestamp'], '%Y-%m-%d %H:%M:%S').date()
#         trade['PROFIT / LOSS USD'] = next((d['daily_pnl'] for d in daily_pnl_log if d['date'] == trade_day), None)

#     # Write any remaining trades at the end
#     if len(trade_log) % 10 != 0:
#         pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)
#     daily_pnl_df = pd.DataFrame(daily_pnl_log)
#     portfolio_df = pd.DataFrame(portfolio_history)

#     print("\nDecision Counts:")
#     for k, v in decision_counts.items():
#         print(f"{k}: {v}")

#     if len(portfolio_df) > 0:
#         initial_value = portfolio_df['value'].iloc[0]
#         final_value = portfolio_df['value'].iloc[-1]
#         total_return = (final_value - initial_value) / initial_value * 100
#         num_trades = len(trade_log)

#         print("\n[BACKTEST SUMMARY]")
#         print(f"Initial Value: ${initial_value:,.2f}")
#         print(f"Final Value: ${final_value:,.2f}")
#         print(f"Total Return: {total_return:.2f}%")
#         print(f"Number of Trades: {num_trades}")
#         print(f"Max Portfolio Value: ${portfolio_df['value'].max():,.2f}")
#         print(f"Min Portfolio Value: ${portfolio_df['value'].min():,.2f}")

#         plt.figure(figsize=(14, 6))
#         plt.subplot(2, 1, 1)
#         plt.plot(portfolio_df['date'], portfolio_df['value'], label='Portfolio Value')
#         plt.title('Portfolio Value Over Time')
#         plt.ylabel('Value (USD)')
#         plt.legend()

#         if len(daily_pnl_df) > 0:
#             plt.subplot(2, 1, 2)
#             plt.bar(daily_pnl_df['date'], daily_pnl_df['daily_pnl'], label='Daily P&L')
#             plt.title('Daily Profit/Loss')
#             plt.ylabel('Daily P&L (USD)')
#             plt.xlabel('Date')
#             plt.legend()

#         plt.tight_layout()
#         plt.show()
#     else:
#         print("[ERROR] No portfolio data generated during backtest!")

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     asyncio.run(run_backtest())
#     print("Backtest completed.")



# --------------------- Portfolio now being manage by manage trades function ------------------------------------

# import os
# import sys
# import asyncio
# import pandas as pd
# from datetime import datetime, timedelta
# import ta
# import json
# from llm_decision_strategy_05 import get_llm_decision
# from pprint import pprint
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# def plot_trade_log(trade_log_path="backtest_trade_log.csv"):
#     df = pd.read_csv(trade_log_path)
#     df['Timestamp'] = pd.to_datetime(df['Timestamp'])
#     plt.style.use('dark_background')

#     fig, axs = plt.subplots(4, 1, figsize=(16, 16), sharex=True)

#     # USD Balance
#     axs[0].plot(df['Timestamp'], df['USD BALANCE'], color='lime', label='USD Balance')
#     axs[0].set_ylabel('USD Balance')
#     axs[0].set_title('USD Balance Over Time')
#     axs[0].legend(loc='upper right')
#     axs[0].grid(True, alpha=0.3)

#     # Total Portfolio Value
#     axs[2].plot(df['Timestamp'], df['Total Portfolio Value'], color='deepskyblue', label='Total Portfolio Value')
#     axs[2].set_ylabel('Portfolio Value (USD)')
#     axs[2].set_title('Total Portfolio Value Over Time')
#     axs[2].legend(loc='upper right')
#     axs[2].grid(True, alpha=0.3)

#     # BTC Value (USD)
#     axs[1].plot(df['Timestamp'], df['BTC VALUE USD'], color='orange', label='BTC Value (USD)')
#     axs[1].set_ylabel('BTC Value (USD)')
#     axs[1].set_title('BTC Value (USD) Over Time')
#     axs[1].legend(loc='upper right')
#     axs[1].grid(True, alpha=0.3)

#     # BTC Price
#     axs[3].plot(df['Timestamp'], df['Price BTC'], color='white', label='BTC Price')
#     axs[3].set_ylabel('BTC Price')
#     axs[3].set_title('BTC Price Over Time')
#     axs[3].legend(loc='upper right')
#     axs[3].grid(True, alpha=0.3)
#     axs[3].set_xlabel('Timestamp')

#     # Format x-axis for hourly ticks
#     axs[3].xaxis.set_major_locator(mdates.HourLocator(interval=6))
#     axs[3].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
#     plt.xticks(rotation=45)

#     plt.tight_layout()
#     plt.show()

# # ---- EDIT THESE SETTINGS TO CHANGE INTERVAL AND DURATION ----
# TRADE_INTERVAL_HOURS = 1      # Set to 1 for hourly, 24 for daily, etc.
# TRADE_DURATION = "1 week"     # <--- Change this to your desired duration

# def parse_duration(duration_str):
#     duration_str = duration_str.lower().strip()
#     if "day" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=n)
#     elif "week" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(weeks=n)
#     elif "month" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=30 * n)
#     else:
#         return timedelta(weeks=1)

# def load_config():
#     config = {}
#     with open("config.cfg", "r") as f:
#         for line in f:
#             if line.strip() and not line.startswith('#'):
#                 parts = line.strip().split('=', 1)
#                 key = parts[0].strip()
#                 value = parts[1].strip() if len(parts) > 1 else ''
#                 if value.lower() == 'true':
#                     config[key] = True
#                 elif value.lower() == 'false':
#                     config[key] = False
#                 elif value.replace('.', '', 1).isdigit():
#                     config[key] = float(value)
#                 else:
#                     config[key] = value
#     print(f"Fetched Config : {config}")
#     return config

# def generate_md_report(current_date, row, indicators, portfolio, current_price):
#     md_content = f"""
# # Complete Bitcoin Data Collection Report

# ## Yahoo Finance Data

# | Date | Open | High | Low | Close | Volume |
# |------|------|------|-----|-------|--------|
# | {current_date.strftime('%Y-%m-%d %H:%M:%S')} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,.0f} |

# ### Technical Indicators (Current Values)

# - **ATR (14)**: ${indicators['atr_14'] if indicators['atr_14'] is not None else 'N/A'}
# - **RSI (14)**: {indicators['rsi_14'] if indicators['rsi_14'] is not None else 'N/A'}
# - **SMA 20**: ${indicators['sma_20'] if indicators['sma_20'] is not None else 'N/A'}
# - **SMA 50**: ${indicators['sma_50'] if indicators['sma_50'] is not None else 'N/A'}
# - **EMA 12**: ${indicators['ema_12'] if indicators['ema_12'] is not None else 'N/A'}
# - **EMA 26**: ${indicators['ema_26'] if indicators['ema_26'] is not None else 'N/A'}
# - **Bollinger Upper (20)**: ${indicators['bb_upper'] if indicators['bb_upper'] is not None else 'N/A'}
# - **Bollinger Middle (20)**: ${indicators['bb_middle'] if indicators['bb_middle'] is not None else 'N/A'}
# - **Bollinger Lower (20)**: ${indicators['bb_lower'] if indicators['bb_lower'] is not None else 'N/A'}
# - **MACD**: {indicators['macd'] if indicators['macd'] is not None else 'N/A'}
# - **MACD Signal**: {indicators['macd_signal'] if indicators['macd_signal'] is not None else 'N/A'}
# - **Volume SMA 20**: {indicators['volume_sma_20'] if indicators['volume_sma_20'] is not None else 'N/A'}
# - **ATR Volatility Ratio**: {indicators['atr_volatility_ratio'] if indicators['atr_volatility_ratio'] is not None else 'N/A'}

# ## Portfolio Status

# - BTC: {portfolio['btc']}
# - USDT: {portfolio['usdt']}
# - Portfolio Value: {portfolio['btc'] * current_price + portfolio['usdt']}
# """
#     return md_content

# async def run_backtest():
#     data_file = 'btc_hourly_yahoo_binance_6mo.csv'
#     if not os.path.exists(data_file):
#         data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
#     if not os.path.exists(data_file):
#         print(f"ERROR: Data file '{data_file}' not found!")
#         return

#     if data_file.endswith('.csv'):
#         df = pd.read_csv(data_file)
#     else:
#         df = pd.read_excel(data_file)
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)

#     print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])

#     config = load_config()
#     budget = config.get('budget', 10000)
#     portfolio = {'btc': 0.0, 'usdt': budget}
#     trade_log = []
#     trade_log_path = "backtest_trade_log.csv"
#     if os.path.exists(trade_log_path):
#         os.remove(trade_log_path)

#     subsample = TRADE_INTERVAL_HOURS
#     start_date = df['date'].min()
#     #end_date = df['date'].max()
#     duration = parse_duration(TRADE_DURATION)
#     end_date = start_date + duration
#     #end_date = df['date'].max() 
#     #start_date = end_date - duration
#     print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

#     df_test = df[df['date'] >= start_date]
#     if len(df_test) == 0:
#         print(f"[ERROR] No data found for the selected period!")
#         return

#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")

#     for i, row in df_subsampled.iterrows():
#         if pd.isna(row['close']):
#             continue
#         current_date = row['date']
#         current_price = row['close']

#         # --- Recalculate indicators using data up to current row ---
#         df_slice = df_test[df_test['date'] <= current_date].copy()
#         min_window = 14  # Largest window used for indicators
#         if len(df_slice) < min_window:
#             indicators = {
#                 'atr_14': None,
#                 'rsi_14': None,
#                 'sma_20': None,
#                 'sma_50': None,
#                 'ema_12': None,
#                 'ema_26': None,
#                 'bb_upper': None,
#                 'bb_middle': None,
#                 'bb_lower': None,
#                 'macd': None,
#                 'macd_signal': None,
#                 'volume_sma_20': None,
#                 'atr_volatility_ratio': None
#             }
#         else:
#             indicators = {
#                 'atr_14': ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1],
#                 'rsi_14': ta.momentum.RSIIndicator(df_slice['close'], window=14).rsi().iloc[-1],
#                 'sma_20': ta.trend.sma_indicator(df_slice['close'], window=20).iloc[-1],
#                 'sma_50': ta.trend.sma_indicator(df_slice['close'], window=50).iloc[-1],
#                 'ema_12': ta.trend.ema_indicator(df_slice['close'], window=12).iloc[-1],
#                 'ema_26': ta.trend.ema_indicator(df_slice['close'], window=26).iloc[-1],
#                 'bb_upper': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_hband().iloc[-1],
#                 'bb_middle': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_mavg().iloc[-1],
#                 'bb_lower': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_lband().iloc[-1],
#                 'macd': ta.trend.MACD(df_slice['close']).macd().iloc[-1],
#                 'macd_signal': ta.trend.MACD(df_slice['close']).macd_signal().iloc[-1],
#                 'volume_sma_20': ta.trend.sma_indicator(df_slice['volume'], window=20).iloc[-1],
#                 'atr_volatility_ratio': (ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1] / df_slice['close'].iloc[-1])
#             }

#         md_content = generate_md_report(current_date, row, indicators, portfolio, current_price)
#         context = {
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'trade_history': trade_log[-10:]
#         }
#         #pprint(f"Context: {trade_log[-10:]}")
#         decision = get_llm_decision(context)
#         pprint(f"LLM Decision : {decision}")
#         action = decision.get('action', 'None')
#         quantity = decision.get('quantity', 0)

#         # --- Portfolio management ---
#         value_usd_cost = 0
#         reason = None

#         if action == 'BUY':
#             value_usd_cost = quantity * current_price
#             if quantity <= 0:
#                 reason = "LLM suggested BUY with zero or negative quantity"
#             elif portfolio['usdt'] < value_usd_cost:
#                 reason = f"Insufficient USD balance for BUY (needed ${value_usd_cost:.2f}, available ${portfolio['usdt']:.2f})"
#             else:
#                 portfolio['usdt'] -= value_usd_cost
#                 portfolio['btc'] += quantity

#         elif action == 'SELL':
#             value_usd_cost = quantity * current_price
#             if quantity <= 0:
#                 reason = "LLM suggested SELL with zero or negative quantity"
#             elif portfolio['btc'] < quantity:
#                 reason = f"Insufficient BTC balance for SELL (needed {quantity:.6f}, available {portfolio['btc']:.6f})"
#             else:
#                 portfolio['btc'] -= quantity
#                 portfolio['usdt'] += value_usd_cost

#         else:
#             quantity = 0
#             value_usd_cost = 0

#         if reason:
#             action = f"Overwrite LLM Decision to HOLD: {reason}"
#             quantity = 0
#             value_usd_cost = 0

#         btc_value_usd = portfolio['btc'] * current_price
#         total_portfolio_value = btc_value_usd + portfolio['usdt']

#         trade_record = {
#             'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#             'Type': action,
#             'Price BTC': current_price,
#             'Quantity': quantity,
#             'Value USD (Cost)': value_usd_cost,
#             'BTC BALANCE': portfolio['btc'],
#             'BTC VALUE USD': btc_value_usd,
#             'Total Portfolio Value': total_portfolio_value,
#             'USD BALANCE': portfolio['usdt'],
#         }
#         trade_log.append(trade_record)
#         pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     #asyncio.run(run_backtest())
#     print("Backtest completed.")
#     # Call this after your backtest
#     plot_trade_log()


# ------------------------------------------ USD PROFIT SYSTEM PORTFOLIO ---------------------------------------------

# import os
# import sys
# import asyncio
# import pandas as pd
# from datetime import datetime, timedelta
# import ta
# import json
# from llm_decision_strategy_05 import get_llm_decision
# from pprint import pprint
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# BINANCE_FEE_RATE = 0.001  # 0.1% per trade

# def plot_trade_log(trade_log_path="backtest_trade_log.csv"):
#     df = pd.read_csv(trade_log_path)
#     df['Timestamp'] = pd.to_datetime(df['Timestamp'])
#     plt.style.use('dark_background')

#     fig, axs = plt.subplots(5, 1, figsize=(16, 20), sharex=True)

#     axs[0].plot(df['Timestamp'], df['USD BALANCE'], color='lime', label='USD Balance')
#     axs[0].set_ylabel('USD Balance')
#     axs[0].set_title('USD Balance Over Time')
#     axs[0].legend(loc='upper right')
#     axs[0].grid(True, alpha=0.3)

#     axs[1].plot(df['Timestamp'], df['USD PROFIT'], color='gold', label='USD Profit')
#     axs[1].set_ylabel('USD Profit')
#     axs[1].set_title('USD Profit Over Time')
#     axs[1].legend(loc='upper right')
#     axs[1].grid(True, alpha=0.3)

#     axs[2].plot(df['Timestamp'], df['BTC VALUE USD'], color='orange', label='BTC Value (USD)')
#     axs[2].set_ylabel('BTC Value (USD)')
#     axs[2].set_title('BTC Value (USD) Over Time')
#     axs[2].legend(loc='upper right')
#     axs[2].grid(True, alpha=0.3)

#     axs[3].plot(df['Timestamp'], df['Total Portfolio Value'], color='deepskyblue', label='Total Portfolio Value')
#     axs[3].set_ylabel('Portfolio Value (USD)')
#     axs[3].set_title('Total Portfolio Value Over Time')
#     axs[3].legend(loc='upper right')
#     axs[3].grid(True, alpha=0.3)

#     axs[4].plot(df['Timestamp'], df['Price BTC'], color='white', label='BTC Price')
#     axs[4].set_ylabel('BTC Price')
#     axs[4].set_title('BTC Price Over Time')
#     axs[4].legend(loc='upper right')
#     axs[4].grid(True, alpha=0.3)
#     axs[4].set_xlabel('Timestamp')

#     axs[4].xaxis.set_major_locator(mdates.HourLocator(interval=6))
#     axs[4].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
#     plt.xticks(rotation=45)

#     plt.tight_layout()
#     plt.show()

# TRADE_INTERVAL_HOURS = 1
# TRADE_DURATION = "1 week"

# def parse_duration(duration_str):
#     duration_str = duration_str.lower().strip()
#     if "day" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=n)
#     elif "week" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(weeks=n)
#     elif "month" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=30 * n)
#     else:
#         return timedelta(weeks=1)

# def load_config():
#     config = {}
#     with open("config.cfg", "r") as f:
#         for line in f:
#             if line.strip() and not line.startswith('#'):
#                 parts = line.strip().split('=', 1)
#                 key = parts[0].strip()
#                 value = parts[1].strip() if len(parts) > 1 else ''
#                 if value.lower() == 'true':
#                     config[key] = True
#                 elif value.lower() == 'false':
#                     config[key] = False
#                 elif value.replace('.', '', 1).isdigit():
#                     config[key] = float(value)
#                 else:
#                     config[key] = value
#     print(f"Fetched Config : {config}")
#     return config

# def generate_md_report(current_date, row, indicators, portfolio, current_price):
#     md_content = f"""
# # Complete Bitcoin Data Collection Report

# ## Yahoo Finance Data

# | Date | Open | High | Low | Close | Volume |
# |------|------|------|-----|-------|--------|
# | {current_date.strftime('%Y-%m-%d %H:%M:%S')} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,.0f} |

# ### Technical Indicators (Current Values)

# - **ATR (14)**: ${indicators['atr_14'] if indicators['atr_14'] is not None else 'N/A'}
# - **RSI (14)**: {indicators['rsi_14'] if indicators['rsi_14'] is not None else 'N/A'}
# - **SMA 20**: ${indicators['sma_20'] if indicators['sma_20'] is not None else 'N/A'}
# - **SMA 50**: ${indicators['sma_50'] if indicators['sma_50'] is not None else 'N/A'}
# - **EMA 12**: ${indicators['ema_12'] if indicators['ema_12'] is not None else 'N/A'}
# - **EMA 26**: ${indicators['ema_26'] if indicators['ema_26'] is not None else 'N/A'}
# - **Bollinger Upper (20)**: ${indicators['bb_upper'] if indicators['bb_upper'] is not None else 'N/A'}
# - **Bollinger Middle (20)**: ${indicators['bb_middle'] if indicators['bb_middle'] is not None else 'N/A'}
# - **Bollinger Lower (20)**: ${indicators['bb_lower'] if indicators['bb_lower'] is not None else 'N/A'}
# - **MACD**: {indicators['macd'] if indicators['macd'] is not None else 'N/A'}
# - **MACD Signal**: {indicators['macd_signal'] if indicators['macd_signal'] is not None else 'N/A'}
# - **Volume SMA 20**: {indicators['volume_sma_20'] if indicators['volume_sma_20'] is not None else 'N/A'}
# - **ATR Volatility Ratio**: {indicators['atr_volatility_ratio'] if indicators['atr_volatility_ratio'] is not None else 'N/A'}

# ## Portfolio Status

# - BTC: {portfolio['btc']}
# - USDT: {portfolio['usdt']}
# - USD PROFIT: {portfolio['usd_profit']}
# - Portfolio Value: {portfolio['btc'] * current_price + portfolio['usdt']}
# """
#     return md_content

# async def run_backtest():
#     data_file = 'btc_hourly_yahoo_binance_6mo.csv'
#     if not os.path.exists(data_file):
#         data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
#     if not os.path.exists(data_file):
#         print(f"ERROR: Data file '{data_file}' not found!")
#         return

#     if data_file.endswith('.csv'):
#         df = pd.read_csv(data_file)
#     else:
#         df = pd.read_excel(data_file)
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)

#     print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])

#     config = load_config()
#     budget = config.get('budget', 10000)
#     portfolio = {'btc': 0.0, 'usdt': budget, 'usd_profit': 0.0}
#     trade_log = []
#     trade_log_path = "backtest_trade_log.csv"
#     if os.path.exists(trade_log_path):
#         os.remove(trade_log_path)

#     subsample = TRADE_INTERVAL_HOURS
#     start_date = df['date'].min()
#     duration = parse_duration(TRADE_DURATION)
#     end_date = start_date + duration
#     print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

#     df_test = df[df['date'] >= start_date]
#     if len(df_test) == 0:
#         print(f"[ERROR] No data found for the selected period!")
#         return

#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")

#     for i, row in df_subsampled.iterrows():
#         if pd.isna(row['close']):
#             continue
#         current_date = row['date']
#         current_price = row['close']

#         df_slice = df_test[df_test['date'] <= current_date].copy()
#         min_window = 14
#         if len(df_slice) < min_window:
#             indicators = {
#                 'atr_14': None,
#                 'rsi_14': None,
#                 'sma_20': None,
#                 'sma_50': None,
#                 'ema_12': None,
#                 'ema_26': None,
#                 'bb_upper': None,
#                 'bb_middle': None,
#                 'bb_lower': None,
#                 'macd': None,
#                 'macd_signal': None,
#                 'volume_sma_20': None,
#                 'atr_volatility_ratio': None
#             }
#         else:
#             indicators = {
#                 'atr_14': ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1],
#                 'rsi_14': ta.momentum.RSIIndicator(df_slice['close'], window=14).rsi().iloc[-1],
#                 'sma_20': ta.trend.sma_indicator(df_slice['close'], window=20).iloc[-1],
#                 'sma_50': ta.trend.sma_indicator(df_slice['close'], window=50).iloc[-1],
#                 'ema_12': ta.trend.ema_indicator(df_slice['close'], window=12).iloc[-1],
#                 'ema_26': ta.trend.ema_indicator(df_slice['close'], window=26).iloc[-1],
#                 'bb_upper': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_hband().iloc[-1],
#                 'bb_middle': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_mavg().iloc[-1],
#                 'bb_lower': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_lband().iloc[-1],
#                 'macd': ta.trend.MACD(df_slice['close']).macd().iloc[-1],
#                 'macd_signal': ta.trend.MACD(df_slice['close']).macd_signal().iloc[-1],
#                 'volume_sma_20': ta.trend.sma_indicator(df_slice['volume'], window=20).iloc[-1],
#                 'atr_volatility_ratio': (ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1] / df_slice['close'].iloc[-1])
#             }

#         md_content = generate_md_report(current_date, row, indicators, portfolio, current_price)
#         context = {
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'trade_history': trade_log[-10:]
#         }
#         decision = get_llm_decision(context)
#         pprint(f"LLM Decision : {decision}")
#         action = decision.get('action', 'None')
#         quantity = decision.get('quantity', 0)
#         profit_amount = decision.get('profit_amount', 0)

#         value_usd_cost = 0
#         fee = 0
#         reason = None

#         if action == 'BUY':
#             value_usd_cost = quantity * current_price
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             total_cost = value_usd_cost + fee
#             if quantity <= 0:
#                 reason = "LLM suggested BUY with zero or negative quantity"
#             elif portfolio['usdt'] < total_cost:
#                 reason = f"Insufficient USD balance for BUY (needed ${total_cost:.2f}, available ${portfolio['usdt']:.2f})"
#             else:
#                 portfolio['usdt'] -= total_cost
#                 portfolio['btc'] += quantity
#         elif action == 'SELL':
#             value_usd_cost = quantity * current_price
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             net_usd = value_usd_cost - fee
#             if quantity <= 0:
#                 reason = "LLM suggested SELL with zero or negative quantity"
#             elif portfolio['btc'] < quantity:
#                 reason = f"Insufficient BTC balance for SELL (needed {quantity:.6f}, available {portfolio['btc']:.6f})"
#             else:
#                 portfolio['btc'] -= quantity
#                 portfolio['usdt'] += net_usd
#         elif action == 'PROFIT':
#             if profit_amount <= 0:
#                 reason = "LLM suggested PROFIT with zero or negative amount"
#             elif portfolio['usdt'] < profit_amount:
#                 reason = f"Insufficient USD balance for PROFIT extraction (needed ${profit_amount:.2f}, available ${portfolio['usdt']:.2f})"
#             else:
#                 portfolio['usdt'] -= profit_amount
#                 portfolio['usd_profit'] += profit_amount
#             value_usd_cost = profit_amount
#         else:
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         if reason:
#             action = f"Overwrite LLM Decision to HOLD: {reason}"
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         btc_value_usd = portfolio['btc'] * current_price
#         total_portfolio_value = btc_value_usd + portfolio['usdt']

#         trade_record = {
#             'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#             'Type': action if action != 'PROFIT' else 'PROFIT',
#             'Price BTC': current_price,
#             'Quantity': quantity if action != 'PROFIT' else 0,
#             'Value USD (Cost)': value_usd_cost,
#             'Fee USD': fee,
#             'BTC BALANCE': portfolio['btc'],
#             'BTC VALUE USD': btc_value_usd,
#             'Total Portfolio Value': total_portfolio_value,
#             'USD BALANCE': portfolio['usdt'],
#             'USD PROFIT': portfolio['usd_profit'],
#         }
#         trade_log.append(trade_record)
#         pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     asyncio.run(run_backtest())
#     print("Backtest completed.")
#     #plot_trade_log()

# ------------------------------------------ USD PROFIT SYSTEM with Dynamic Budget ---------------------------------------------
# import os
# import sys
# import asyncio
# import pandas as pd
# from datetime import datetime, timedelta
# import ta
# import json
# from llm_decision_strategy_05 import get_llm_decision
# from pprint import pprint
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# BINANCE_FEE_RATE = 0.001  # 0.1% per trade

# def plot_trade_log(trade_log_path="backtest_trade_log.csv"):
#     df = pd.read_csv(trade_log_path)
#     df['Timestamp'] = pd.to_datetime(df['Timestamp'])
#     plt.style.use('dark_background')

#     fig, axs = plt.subplots(5, 1, figsize=(16, 20), sharex=True)

#     axs[0].plot(df['Timestamp'], df['USD BALANCE'], color='lime', label='USD Balance')
#     axs[0].set_ylabel('USD Balance')
#     axs[0].set_title('USD Balance Over Time')
#     axs[0].legend(loc='upper right')
#     axs[0].grid(True, alpha=0.3)

#     axs[1].plot(df['Timestamp'], df['USD PROFIT'], color='gold', label='USD Profit')
#     axs[1].set_ylabel('USD Profit')
#     axs[1].set_title('USD Profit Over Time')
#     axs[1].legend(loc='upper right')
#     axs[1].grid(True, alpha=0.3)

#     axs[2].plot(df['Timestamp'], df['BTC VALUE USD'], color='orange', label='BTC Value (USD)')
#     axs[2].set_ylabel('BTC Value (USD)')
#     axs[2].set_title('BTC Value (USD) Over Time')
#     axs[2].legend(loc='upper right')
#     axs[2].grid(True, alpha=0.3)

#     axs[3].plot(df['Timestamp'], df['Total Portfolio Value'], color='deepskyblue', label='Total Portfolio Value')
#     axs[3].set_ylabel('Portfolio Value (USD)')
#     axs[3].set_title('Total Portfolio Value Over Time')
#     axs[3].legend(loc='upper right')
#     axs[3].grid(True, alpha=0.3)

#     axs[4].plot(df['Timestamp'], df['Price BTC'], color='white', label='BTC Price')
#     axs[4].set_ylabel('BTC Price')
#     axs[4].set_title('BTC Price Over Time')
#     axs[4].legend(loc='upper right')
#     axs[4].grid(True, alpha=0.3)
#     axs[4].set_xlabel('Timestamp')

#     axs[4].xaxis.set_major_locator(mdates.HourLocator(interval=6))
#     axs[4].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
#     plt.xticks(rotation=45)

#     plt.tight_layout()
#     plt.show()

# TRADE_INTERVAL_HOURS = 1
# TRADE_DURATION = "1 week"

# def parse_duration(duration_str):
#     duration_str = duration_str.lower().strip()
#     if "day" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=n)
#     elif "week" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(weeks=n)
#     elif "month" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=30 * n)
#     else:
#         return timedelta(weeks=1)

# def load_config():
#     config = {}
#     with open("config.cfg", "r") as f:
#         for line in f:
#             if line.strip() and not line.startswith('#'):
#                 parts = line.strip().split('=', 1)
#                 key = parts[0].strip()
#                 value = parts[1].strip() if len(parts) > 1 else ''
#                 if value.lower() == 'true':
#                     config[key] = True
#                 elif value.lower() == 'false':
#                     config[key] = False
#                 elif value.replace('.', '', 1).isdigit():
#                     config[key] = float(value)
#                 else:
#                     config[key] = value
#     print(f"Fetched Config : {config}")
#     return config

# def generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold):
#     md_content = f"""
# # Complete Bitcoin Data Collection Report

# ## Yahoo Finance Data

# | Date | Open | High | Low | Close | Volume |
# |------|------|------|-----|-------|--------|
# | {current_date.strftime('%Y-%m-%d %H:%M:%S')} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,.0f} |

# ### Technical Indicators (Current Values)

# - **ATR (14)**: ${indicators['atr_14'] if indicators['atr_14'] is not None else 'N/A'}
# - **RSI (14)**: {indicators['rsi_14'] if indicators['rsi_14'] is not None else 'N/A'}
# - **SMA 20**: ${indicators['sma_20'] if indicators['sma_20'] is not None else 'N/A'}
# - **SMA 50**: ${indicators['sma_50'] if indicators['sma_50'] is not None else 'N/A'}
# - **EMA 12**: ${indicators['ema_12'] if indicators['ema_12'] is not None else 'N/A'}
# - **EMA 26**: ${indicators['ema_26'] if indicators['ema_26'] is not None else 'N/A'}
# - **Bollinger Upper (20)**: ${indicators['bb_upper'] if indicators['bb_upper'] is not None else 'N/A'}
# - **Bollinger Middle (20)**: ${indicators['bb_middle'] if indicators['bb_middle'] is not None else 'N/A'}
# - **Bollinger Lower (20)**: ${indicators['bb_lower'] if indicators['bb_lower'] is not None else 'N/A'}
# - **MACD**: {indicators['macd'] if indicators['macd'] is not None else 'N/A'}
# - **MACD Signal**: {indicators['macd_signal'] if indicators['macd_signal'] is not None else 'N/A'}
# - **Volume SMA 20**: {indicators['volume_sma_20'] if indicators['volume_sma_20'] is not None else 'N/A'}
# - **ATR Volatility Ratio**: {indicators['atr_volatility_ratio'] if indicators['atr_volatility_ratio'] is not None else 'N/A'}

# ## Portfolio Status

# - BTC: {portfolio['btc']}
# - USDT: {portfolio['usdt']}
# - USD PROFIT: {portfolio['usd_profit']}
# - Portfolio Value: {portfolio['btc'] * current_price + portfolio['usdt']}
# - PROFIT THRESHOLD (Dynamic Budget): {profit_threshold}
# """
#     return md_content

# async def run_backtest():
#     data_file = 'btc_hourly_yahoo_binance_6mo.csv'
#     if not os.path.exists(data_file):
#         data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
#     if not os.path.exists(data_file):
#         print(f"ERROR: Data file '{data_file}' not found!")
#         return

#     if data_file.endswith('.csv'):
#         df = pd.read_csv(data_file)
#     else:
#         df = pd.read_excel(data_file)
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)

#     print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])

#     config = load_config()
#     # ------------------------------------ Setting Initial Budget ------------------------------------
#     initial_budget = config.get('budget', 10000)
#     profit_threshold = initial_budget
#     portfolio = {'btc': 0.0, 'usdt': initial_budget, 'usd_profit': 0.0}
#     trade_log = []
#     trade_log_path = "backtest_trade_log.csv"
#     if os.path.exists(trade_log_path):
#         os.remove(trade_log_path)

#     subsample = TRADE_INTERVAL_HOURS
#     start_date = df['date'].min()
#     duration = parse_duration(TRADE_DURATION)
#     end_date = start_date + duration
#     print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

#     df_test = df[df['date'] >= start_date]
#     if len(df_test) == 0:
#         print(f"[ERROR] No data found for the selected period!")
#         return

#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")


#     for i, row in df_subsampled.iterrows():
#         if pd.isna(row['close']):
#             continue
#         current_date = row['date']
#         current_price = row['close']

#         df_slice = df_test[df_test['date'] <= current_date].copy()
#         min_window = 14
#         if len(df_slice) < min_window:
#             indicators = {
#                 'atr_14': None,
#                 'rsi_14': None,
#                 'sma_20': None,
#                 'sma_50': None,
#                 'ema_12': None,
#                 'ema_26': None,
#                 'bb_upper': None,
#                 'bb_middle': None,
#                 'bb_lower': None,
#                 'macd': None,
#                 'macd_signal': None,
#                 'volume_sma_20': None,
#                 'atr_volatility_ratio': None
#             }
#         else:
#             indicators = {
#                 'atr_14': ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1],
#                 'rsi_14': ta.momentum.RSIIndicator(df_slice['close'], window=14).rsi().iloc[-1],
#                 'sma_20': ta.trend.sma_indicator(df_slice['close'], window=20).iloc[-1],
#                 'sma_50': ta.trend.sma_indicator(df_slice['close'], window=50).iloc[-1],
#                 'ema_12': ta.trend.ema_indicator(df_slice['close'], window=12).iloc[-1],
#                 'ema_26': ta.trend.ema_indicator(df_slice['close'], window=26).iloc[-1],
#                 'bb_upper': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_hband().iloc[-1],
#                 'bb_middle': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_mavg().iloc[-1],
#                 'bb_lower': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_lband().iloc[-1],
#                 'macd': ta.trend.MACD(df_slice['close']).macd().iloc[-1],
#                 'macd_signal': ta.trend.MACD(df_slice['close']).macd_signal().iloc[-1],
#                 'volume_sma_20': ta.trend.sma_indicator(df_slice['volume'], window=20).iloc[-1],
#                 'atr_volatility_ratio': (ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1] / df_slice['close'].iloc[-1])
#             }

#         # Pass dynamic profit threshold to LLM context
#         md_content = generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold)
#         context = {
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'profit_threshold': profit_threshold,
#             'trade_history': trade_log[-10:]
#         }

#         # ------------------------------------------------------- LLM Decision -------------------------------------------------------
#         decision = get_llm_decision(context)
#         pprint(f"LLM Decision : {decision}")
#         action = decision.get('action', 'None')
#         quantity = decision.get('quantity', 0)
#         profit_amount = decision.get('profit_amount', 0)

#         value_usd_cost = 0
#         fee = 0
#         reason = None

#         if action == 'BUY':
#             value_usd_cost = quantity * current_price
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             total_cost = value_usd_cost + fee
#             if quantity <= 0:
#                 reason = "LLM suggested BUY with zero or negative quantity"
#             elif portfolio['usdt'] < total_cost:
#                 reason = f"Insufficient USD balance for BUY (needed ${total_cost:.2f}, available ${portfolio['usdt']:.2f})"
#             else:
#                 portfolio['usdt'] -= total_cost
#                 portfolio['btc'] += quantity
#         elif action == 'SELL':
#             value_usd_cost = quantity * current_price
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             net_usd = value_usd_cost - fee
#             if quantity <= 0:
#                 reason = "LLM suggested SELL with zero or negative quantity"
#             elif portfolio['btc'] < quantity:
#                 reason = f"Insufficient BTC balance for SELL (needed {quantity:.6f}, available {portfolio['btc']:.6f})"
#             else:
#                 portfolio['btc'] -= quantity
#                 portfolio['usdt'] += net_usd
#         elif action == 'PROFIT':
#             if profit_amount <= 0:
#                 reason = "LLM suggested PROFIT with zero or negative amount"
#             elif portfolio['usdt'] < profit_amount:
#                 reason = f"Insufficient USD balance for PROFIT extraction (needed ${profit_amount:.2f}, available ${portfolio['usdt']:.2f})"
#             else:
#                 portfolio['usdt'] -= profit_amount
#                 portfolio['usd_profit'] += profit_amount
#                 profit_threshold += profit_amount  # Update dynamic profit threshold
#             value_usd_cost = profit_amount
#         else:
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         if reason:
#             action = f"Overwrite LLM Decision to HOLD: {reason}"
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         btc_value_usd = portfolio['btc'] * current_price
#         total_portfolio_value = btc_value_usd + portfolio['usdt']

#         trade_record = {
#             'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#             'Type': action if action != 'PROFIT' else 'PROFIT',
#             'Price BTC': current_price,
#             'Quantity': quantity if action != 'PROFIT' else 0,
#             'Value USD (Cost)': value_usd_cost,
#             'Fee USD': fee,
#             'BTC BALANCE': portfolio['btc'],
#             'BTC VALUE USD': btc_value_usd,
#             'Total Portfolio Value': total_portfolio_value,
#             'USD BALANCE': portfolio['usdt'],
#             'USD PROFIT': portfolio['usd_profit'],
#             'PROFIT THRESHOLD': profit_threshold
#         }
#         trade_log.append(trade_record)
#         pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     asyncio.run(run_backtest())
#     print("Backtest completed.")
#     plot_trade_log()


# ------------------------------------------ Monitoring Open High Low and Close BTC prices and LLM Rationale in Logs now and new plot ---------------------------------------------

# import os
# import sys
# import asyncio
# import pandas as pd
# from datetime import datetime, timedelta
# import ta
# import json
# from llm_decision_strategy_05 import get_llm_decision
# from pprint import pprint
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# BINANCE_FEE_RATE = 0.000  # 0.1% per trade

# def plot_trade_log(trade_log_path="backtest_trade_log.csv"):
#     df = pd.read_csv(trade_log_path)
#     df['Timestamp'] = pd.to_datetime(df['Timestamp'])
#     plt.style.use('dark_background')

#     fig, axs = plt.subplots(4, 1, figsize=(16, 18), sharex=True)

#     # Plot BTC High, Low, Close
#     # axs[0].plot(df['Timestamp'], df['High'], color='red', label='BTC High')
#     # axs[0].plot(df['Timestamp'], df['Low'], color='blue', label='BTC Low')
#     axs[0].plot(df['Timestamp'], df['Close'], color='white', label='BTC Close')
#     axs[0].set_ylabel('BTC Price')
#     axs[0].set_title('BTC High/Low/Close Over Time')
#     axs[0].legend(loc='upper right')
#     axs[0].grid(True, alpha=0.3)

#     # USD Balance
#     axs[1].plot(df['Timestamp'], df['USD BALANCE'], color='lime', label='USD Balance')
#     axs[1].set_ylabel('USD Balance')
#     axs[1].set_title('USD Balance Over Time')
#     axs[1].legend(loc='upper right')
#     axs[1].grid(True, alpha=0.3)

#     # USD Profit
#     axs[2].plot(df['Timestamp'], df['USD PROFIT'], color='gold', label='USD Profit')
#     axs[2].set_ylabel('USD Profit')
#     axs[2].set_title('USD Profit Over Time')
#     axs[2].legend(loc='upper right')
#     axs[2].grid(True, alpha=0.3)

#     # Portfolio Value
#     axs[3].plot(df['Timestamp'], df['Total Portfolio Value'], color='deepskyblue', label='Total Portfolio Value')
#     axs[3].set_ylabel('Portfolio Value (USD)')
#     axs[3].set_title('Total Portfolio Value Over Time')
#     axs[3].legend(loc='upper right')
#     axs[3].grid(True, alpha=0.3)
#     axs[3].set_xlabel('Timestamp')

#     axs[3].xaxis.set_major_locator(mdates.HourLocator(interval=6))
#     axs[3].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
#     plt.xticks(rotation=45)

#     plt.tight_layout()
#     plt.show()

# TRADE_INTERVAL_HOURS = 1
# TRADE_DURATION = "1 week"

# def parse_duration(duration_str):
#     duration_str = duration_str.lower().strip()
#     if "day" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=n)
#     elif "week" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(weeks=n)
#     elif "month" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=30 * n)
#     else:
#         return timedelta(weeks=1)

# def load_config():
#     config = {}
#     with open("config.cfg", "r") as f:
#         for line in f:
#             if line.strip() and not line.startswith('#'):
#                 parts = line.strip().split('=', 1)
#                 key = parts[0].strip()
#                 value = parts[1].strip() if len(parts) > 1 else ''
#                 if value.lower() == 'true':
#                     config[key] = True
#                 elif value.lower() == 'false':
#                     config[key] = False
#                 elif value.replace('.', '', 1).isdigit():
#                     config[key] = float(value)
#                 else:
#                     config[key] = value
#     print(f"Fetched Config : {config}")
#     return config

# def generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold):
#     md_content = f"""
# # Complete Bitcoin Data Collection Report

# ## Yahoo Finance Data

# | Date | Open | High | Low | Close | Volume |
# |------|------|------|-----|-------|--------|
# | {current_date.strftime('%Y-%m-%d %H:%M:%S')} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,.0f} |

# ### Technical Indicators (Current Values)

# - **ATR (14)**: ${indicators['atr_14'] if indicators['atr_14'] is not None else 'N/A'}
# - **RSI (14)**: {indicators['rsi_14'] if indicators['rsi_14'] is not None else 'N/A'}
# - **SMA 20**: ${indicators['sma_20'] if indicators['sma_20'] is not None else 'N/A'}
# - **SMA 50**: ${indicators['sma_50'] if indicators['sma_50'] is not None else 'N/A'}
# - **EMA 12**: ${indicators['ema_12'] if indicators['ema_12'] is not None else 'N/A'}
# - **EMA 26**: ${indicators['ema_26'] if indicators['ema_26'] is not None else 'N/A'}
# - **Bollinger Upper (20)**: ${indicators['bb_upper'] if indicators['bb_upper'] is not None else 'N/A'}
# - **Bollinger Middle (20)**: ${indicators['bb_middle'] if indicators['bb_middle'] is not None else 'N/A'}
# - **Bollinger Lower (20)**: ${indicators['bb_lower'] if indicators['bb_lower'] is not None else 'N/A'}
# - **MACD**: {indicators['macd'] if indicators['macd'] is not None else 'N/A'}
# - **MACD Signal**: {indicators['macd_signal'] if indicators['macd_signal'] is not None else 'N/A'}
# - **Volume SMA 20**: {indicators['volume_sma_20'] if indicators['volume_sma_20'] is not None else 'N/A'}
# - **ATR Volatility Ratio**: {indicators['atr_volatility_ratio'] if indicators['atr_volatility_ratio'] is not None else 'N/A'}

# ## Portfolio Status

# - BTC: {portfolio['btc']}
# - USDT: {portfolio['usdt']}
# - USD PROFIT: {portfolio['usd_profit']}
# - Portfolio Value: {portfolio['btc'] * current_price + portfolio['usdt']}
# - PROFIT THRESHOLD (Dynamic Budget): {profit_threshold}
# """
#     return md_content

# async def run_backtest():
#     data_file = 'btc_hourly_yahoo_binance_6mo.csv'
#     if not os.path.exists(data_file):
#         data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
#     if not os.path.exists(data_file):
#         print(f"ERROR: Data file '{data_file}' not found!")
#         return

#     if data_file.endswith('.csv'):
#         df = pd.read_csv(data_file)
#     else:
#         df = pd.read_excel(data_file)
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)

#     print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])

#     config = load_config()
#     initial_budget = config.get('budget', 10000)
#     profit_threshold = initial_budget
#     portfolio = {'btc': 0.0, 'usdt': initial_budget, 'usd_profit': 0.0}
#     trade_log = []
#     trade_log_path = "backtest_trade_log.csv"
#     if os.path.exists(trade_log_path):
#         os.remove(trade_log_path)

#     subsample = TRADE_INTERVAL_HOURS
#     start_date = df['date'].min()
#     duration = parse_duration(TRADE_DURATION)
#     end_date = start_date + duration
#     print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

#     df_test = df[df['date'] >= start_date]
#     if len(df_test) == 0:
#         print(f"[ERROR] No data found for the selected period!")
#         return

#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")

#     for i, row in df_subsampled.iterrows():
#         if pd.isna(row['close']):
#             continue
#         current_date = row['date']
#         current_price = row['close']

#         df_slice = df_test[df_test['date'] <= current_date].copy()
#         min_window = 14
#         if len(df_slice) < min_window:
#             indicators = {
#                 'atr_14': None,
#                 'rsi_14': None,
#                 'sma_20': None,
#                 'sma_50': None,
#                 'ema_12': None,
#                 'ema_26': None,
#                 'bb_upper': None,
#                 'bb_middle': None,
#                 'bb_lower': None,
#                 'macd': None,
#                 'macd_signal': None,
#                 'volume_sma_20': None,
#                 'atr_volatility_ratio': None
#             }
#         else:
#             indicators = {
#                 'atr_14': ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1],
#                 'rsi_14': ta.momentum.RSIIndicator(df_slice['close'], window=14).rsi().iloc[-1],
#                 'sma_20': ta.trend.sma_indicator(df_slice['close'], window=20).iloc[-1],
#                 'sma_50': ta.trend.sma_indicator(df_slice['close'], window=50).iloc[-1],
#                 'ema_12': ta.trend.ema_indicator(df_slice['close'], window=12).iloc[-1],
#                 'ema_26': ta.trend.ema_indicator(df_slice['close'], window=26).iloc[-1],
#                 'bb_upper': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_hband().iloc[-1],
#                 'bb_middle': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_mavg().iloc[-1],
#                 'bb_lower': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_lband().iloc[-1],
#                 'macd': ta.trend.MACD(df_slice['close']).macd().iloc[-1],
#                 'macd_signal': ta.trend.MACD(df_slice['close']).macd_signal().iloc[-1],
#                 'volume_sma_20': ta.trend.sma_indicator(df_slice['volume'], window=20).iloc[-1],
#                 'atr_volatility_ratio': (ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1] / df_slice['close'].iloc[-1])
#             }

#         md_content = generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold)
#         context = {
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'profit_threshold': profit_threshold,
#             'trade_history': trade_log[-10:]
#         }

#         decision = get_llm_decision(context)
#         pprint(f"LLM Decision : {decision}")
#         action = decision.get('action', 'None')
#         quantity = decision.get('quantity', 0)
#         profit_amount = decision.get('profit_amount', 0)

#         value_usd_cost = 0
#         fee = 0
#         reason = None

#         if action == 'BUY':
#             value_usd_cost = quantity * current_price
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             total_cost = value_usd_cost + fee
#             if quantity <= 0:
#                 reason = "LLM suggested BUY with zero or negative quantity"
#             elif portfolio['usdt'] < total_cost:
#                 reason = f"Insufficient USD balance for BUY (needed ${total_cost:.2f}, available ${portfolio['usdt']:.2f})"
#             else:
#                 portfolio['usdt'] -= total_cost
#                 portfolio['btc'] += quantity
#         elif action == 'SELL':
#             value_usd_cost = quantity * current_price
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             net_usd = value_usd_cost - fee
#             if quantity <= 0:
#                 reason = "LLM suggested SELL with zero or negative quantity"
#             elif portfolio['btc'] < quantity:
#                 reason = f"Insufficient BTC balance for SELL (needed {quantity:.6f}, available {portfolio['btc']:.6f})"
#             else:
#                 portfolio['btc'] -= quantity
#                 portfolio['usdt'] += net_usd
#         elif action == 'PROFIT':
#             if profit_amount <= 0:
#                 reason = "LLM suggested PROFIT with zero or negative amount"
#             elif portfolio['usdt'] < profit_amount:
#                 reason = f"Insufficient USD balance for PROFIT extraction (needed ${profit_amount:.2f}, available ${portfolio['usdt']:.2f})"
#             else:
#                 portfolio['usdt'] -= profit_amount
#                 portfolio['usd_profit'] += profit_amount
#                 profit_threshold += profit_amount  # Update dynamic profit threshold
#             value_usd_cost = profit_amount
#         else:
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         if reason:
#             action = f"Overwrite LLM Decision to HOLD: {reason}"
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         btc_value_usd = portfolio['btc'] * current_price
#         total_portfolio_value = btc_value_usd + portfolio['usdt']

#         trade_record = {
#             'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#             'Type': action if action != 'PROFIT' else 'PROFIT',
#             'Open': row['open'],
#             # 'High': row['high'],
#             # 'Low': row['low'],
#             'Close': row['close'],
#             #'Volume': row['volume'],
#             'Quantity': quantity if action != 'PROFIT' else 0,
#             'Value USD (Cost)': value_usd_cost,
#             #'Fee USD': fee,
#             'BTC BALANCE': portfolio['btc'],
#             'BTC VALUE USD': btc_value_usd,
#             'Total Portfolio Value': total_portfolio_value,
#             'USD BALANCE': portfolio['usdt'],
#             'USD PROFIT': portfolio['usd_profit'],
#             'PROFIT THRESHOLD': profit_threshold,
#             #'LLM Rationale': decision.get('rationale', '')
#         }
#         trade_log.append(trade_record)
#         pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     #asyncio.run(run_backtest())
#     print("Backtest completed.")
#     plot_trade_log()



# ------------------------------------------ Dynamic Profit threshold adjusting based on last 10 trades if it gets stuck on hold for 10 trades consecutively ---------------------------------------------
# import os
# import sys
# import asyncio
# import pandas as pd
# from datetime import datetime, timedelta
# import ta
# import json
# from llm_decision_strategy_05 import get_llm_decision
# from pprint import pprint
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# BINANCE_FEE_RATE = 0.000  # 0.1% per trade

# def plot_trade_log(trade_log_path="backtest_trade_log.csv"):
#     df = pd.read_csv(trade_log_path)
#     df['Timestamp'] = pd.to_datetime(df['Timestamp'])
#     plt.style.use('dark_background')

#     fig, axs = plt.subplots(4, 1, figsize=(16, 18), sharex=True)

#     axs[0].plot(df['Timestamp'], df['Close'], color='white', label='BTC Close')
#     axs[0].set_ylabel('BTC Price')
#     axs[0].set_title('BTC Close Over Time')
#     axs[0].legend(loc='upper right')
#     axs[0].grid(True, alpha=0.3)

#     axs[1].plot(df['Timestamp'], df['USD BALANCE'], color='lime', label='USD Balance')
#     axs[1].set_ylabel('USD Balance')
#     axs[1].set_title('USD Balance Over Time')
#     axs[1].legend(loc='upper right')
#     axs[1].grid(True, alpha=0.3)

#     axs[2].plot(df['Timestamp'], df['USD PROFIT'], color='gold', label='USD Profit')
#     axs[2].set_ylabel('USD Profit')
#     axs[2].set_title('USD Profit Over Time')
#     axs[2].legend(loc='upper right')
#     axs[2].grid(True, alpha=0.3)

#     axs[3].plot(df['Timestamp'], df['Total Portfolio Value'], color='deepskyblue', label='Total Portfolio Value')
#     axs[3].set_ylabel('Portfolio Value (USD)')
#     axs[3].set_title('Total Portfolio Value Over Time')
#     axs[3].legend(loc='upper right')
#     axs[3].grid(True, alpha=0.3)
#     axs[3].set_xlabel('Timestamp')

#     axs[3].xaxis.set_major_locator(mdates.HourLocator(interval=6))
#     axs[3].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
#     plt.xticks(rotation=45)

#     plt.tight_layout()
#     plt.show()

# TRADE_INTERVAL_HOURS = 1
# TRADE_DURATION = "1 week"

# def parse_duration(duration_str):
#     duration_str = duration_str.lower().strip()
#     if "day" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=n)
#     elif "week" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(weeks=n)
#     elif "month" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=30 * n)
#     else:
#         return timedelta(weeks=1)

# def load_config():
#     config = {}
#     with open("config.cfg", "r") as f:
#         for line in f:
#             if line.strip() and not line.startswith('#'):
#                 parts = line.strip().split('=', 1)
#                 key = parts[0].strip()
#                 value = parts[1].strip() if len(parts) > 1 else ''
#                 if value.lower() == 'true':
#                     config[key] = True
#                 elif value.lower() == 'false':
#                     config[key] = False
#                 elif value.replace('.', '', 1).isdigit():
#                     config[key] = float(value)
#                 else:
#                     config[key] = value
#     print(f"Fetched Config : {config}")
#     return config

# def generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold):
#     md_content = f"""
# # Complete Bitcoin Data Collection Report

# ## Yahoo Finance Data

# | Date | Open | High | Low | Close | Volume |
# |------|------|------|-----|-------|--------|
# | {current_date.strftime('%Y-%m-%d %H:%M:%S')} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,.0f} |

# ### Technical Indicators (Current Values)

# - **ATR (14)**: ${indicators['atr_14'] if indicators['atr_14'] is not None else 'N/A'}
# - **RSI (14)**: {indicators['rsi_14'] if indicators['rsi_14'] is not None else 'N/A'}
# - **SMA 20**: ${indicators['sma_20'] if indicators['sma_20'] is not None else 'N/A'}
# - **SMA 50**: ${indicators['sma_50'] if indicators['sma_50'] is not None else 'N/A'}
# - **EMA 12**: ${indicators['ema_12'] if indicators['ema_12'] is not None else 'N/A'}
# - **EMA 26**: ${indicators['ema_26'] if indicators['ema_26'] is not None else 'N/A'}
# - **Bollinger Upper (20)**: ${indicators['bb_upper'] if indicators['bb_upper'] is not None else 'N/A'}
# - **Bollinger Middle (20)**: ${indicators['bb_middle'] if indicators['bb_middle'] is not None else 'N/A'}
# - **Bollinger Lower (20)**: ${indicators['bb_lower'] if indicators['bb_lower'] is not None else 'N/A'}
# - **MACD**: {indicators['macd'] if indicators['macd'] is not None else 'N/A'}
# - **MACD Signal**: {indicators['macd_signal'] if indicators['macd_signal'] is not None else 'N/A'}
# - **Volume SMA 20**: {indicators['volume_sma_20'] if indicators['volume_sma_20'] is not None else 'N/A'}
# - **ATR Volatility Ratio**: {indicators['atr_volatility_ratio'] if indicators['atr_volatility_ratio'] is not None else 'N/A'}

# ## Portfolio Status

# - BTC: {portfolio['btc']}
# - USDT: {portfolio['usdt']}
# - USD PROFIT: {portfolio['usd_profit']}
# - Portfolio Value: {portfolio['btc'] * current_price + portfolio['usdt']}
# - PROFIT THRESHOLD: {profit_threshold}
# """
#     return md_content

# async def run_backtest():
#     data_file = 'btc_hourly_yahoo_binance_6mo.csv'
#     if not os.path.exists(data_file):
#         data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
#     if not os.path.exists(data_file):
#         print(f"ERROR: Data file '{data_file}' not found!")
#         return

#     if data_file.endswith('.csv'):
#         df = pd.read_csv(data_file)
#     else:
#         df = pd.read_excel(data_file)
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)

#     print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])

#     config = load_config()
#     initial_budget = config.get('budget', 10000)
#     portfolio = {'btc': 0.0, 'usdt': initial_budget, 'usd_profit': 0.0}
#     trade_log = []
#     trade_log_path = "backtest_trade_log.csv"
#     if os.path.exists(trade_log_path):
#         os.remove(trade_log_path)

#     subsample = TRADE_INTERVAL_HOURS
#     start_date = df['date'].min()
#     duration = parse_duration(TRADE_DURATION)
#     end_date = start_date + duration
#     print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

#     df_test = df[df['date'] >= start_date]
#     if len(df_test) == 0:
#         print(f"[ERROR] No data found for the selected period!")
#         return

#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")

#     profit_threshold = initial_budget
#     consecutive_hold_count = 0

#     for i, row in df_subsampled.iterrows():
#         if pd.isna(row['close']):
#             continue
#         current_date = row['date']
#         current_price = row['close']

#         df_slice = df_test[df_test['date'] <= current_date].copy()
#         min_window = 14
#         if len(df_slice) < min_window:
#             indicators = {
#                 'atr_14': None,
#                 'rsi_14': None,
#                 'sma_20': None,
#                 'sma_50': None,
#                 'ema_12': None,
#                 'ema_26': None,
#                 'bb_upper': None,
#                 'bb_middle': None,
#                 'bb_lower': None,
#                 'macd': None,
#                 'macd_signal': None,
#                 'volume_sma_20': None,
#                 'atr_volatility_ratio': None
#             }
#         else:
#             indicators = {
#                 'atr_14': ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1],
#                 'rsi_14': ta.momentum.RSIIndicator(df_slice['close'], window=14).rsi().iloc[-1],
#                 'sma_20': ta.trend.sma_indicator(df_slice['close'], window=20).iloc[-1],
#                 'sma_50': ta.trend.sma_indicator(df_slice['close'], window=50).iloc[-1],
#                 'ema_12': ta.trend.ema_indicator(df_slice['close'], window=12).iloc[-1],
#                 'ema_26': ta.trend.ema_indicator(df_slice['close'], window=26).iloc[-1],
#                 'bb_upper': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_hband().iloc[-1],
#                 'bb_middle': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_mavg().iloc[-1],
#                 'bb_lower': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_lband().iloc[-1],
#                 'macd': ta.trend.MACD(df_slice['close']).macd().iloc[-1],
#                 'macd_signal': ta.trend.MACD(df_slice['close']).macd_signal().iloc[-1],
#                 'volume_sma_20': ta.trend.sma_indicator(df_slice['volume'], window=20).iloc[-1],
#                 'atr_volatility_ratio': (ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1] / df_slice['close'].iloc[-1])
#             }

#         md_content = generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold)
#         context = {
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'profit_threshold': profit_threshold,
#             'trade_history': trade_log[-10:]
#         }

#         decision = get_llm_decision(context)
#         pprint(f"LLM Decision : {decision}")
#         action = decision.get('action', 'None')
#         quantity = decision.get('quantity', 0)
#         profit_amount = decision.get('profit_amount', 0)

#         value_usd_cost = 0
#         fee = 0
#         reason = None

#         # --- Portfolio management ---
#         if action == 'BUY':
#             consecutive_hold_count = 0
#             value_usd_cost = quantity * current_price
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             total_cost = value_usd_cost + fee
#             if quantity <= 0:
#                 reason = "LLM suggested BUY with zero or negative quantity"
#             elif portfolio['usdt'] < total_cost:
#                 reason = f"Insufficient USD balance for BUY (needed ${total_cost:.2f}, available ${portfolio['usdt']:.2f})"
#             else:
#                 portfolio['usdt'] -= total_cost
#                 portfolio['btc'] += quantity
#         elif action == 'SELL':
#             consecutive_hold_count = 0
#             value_usd_cost = quantity * current_price
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             net_usd = value_usd_cost - fee
#             if quantity <= 0:
#                 reason = "LLM suggested SELL with zero or negative quantity"
#             elif portfolio['btc'] < quantity:
#                 reason = f"Insufficient BTC balance for SELL (needed {quantity:.6f}, available {portfolio['btc']:.6f})"
#             else:
#                 portfolio['btc'] -= quantity
#                 portfolio['usdt'] += net_usd
#         elif action == 'PROFIT':
#             consecutive_hold_count = 0
#             if profit_amount <= 0:
#                 reason = "LLM suggested PROFIT with zero or negative amount"
#             elif portfolio['usdt'] < profit_amount:
#                 reason = f"Insufficient USD balance for PROFIT extraction (needed ${profit_amount:.2f}, available ${portfolio['usdt']:.2f})"
#             else:
#                 portfolio['usdt'] -= profit_amount
#                 portfolio['usd_profit'] += profit_amount
#                 profit_threshold += profit_amount  # Increase threshold by secured profit
#             value_usd_cost = profit_amount
#         elif action == 'HOLD':
#             consecutive_hold_count += 1
#             # Only update threshold if 5 consecutive HOLDs
#             if consecutive_hold_count >= 5 and len(trade_log) >= 10:
#                 last_10_values = [t['Total Portfolio Value'] for t in trade_log[-10:]]
#                 profit_threshold = sum(last_10_values) / len(last_10_values)
#                 print(f"[THRESHOLD RESET] Updated profit threshold to last 10 trades average: {profit_threshold:.2f}")
#                 consecutive_hold_count = 0
#         else:
#             consecutive_hold_count = 0
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         if reason:
#             action = f"Overwrite LLM Decision to HOLD: {reason}"
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         btc_value_usd = portfolio['btc'] * current_price
#         total_portfolio_value = btc_value_usd + portfolio['usdt']

#         trade_record = {
#             'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#             'Type': action if action != 'PROFIT' else 'PROFIT',
#             'Open': row['open'],
#             'Close': row['close'],
#             'Quantity': quantity if action != 'PROFIT' else 0,
#             'Value USD (Cost)': value_usd_cost,
#             'BTC BALANCE': portfolio['btc'],
#             'BTC VALUE USD': btc_value_usd,
#             'Total Portfolio Value': total_portfolio_value,
#             'USD BALANCE': portfolio['usdt'],
#             'USD PROFIT': portfolio['usd_profit'],
#             'PROFIT THRESHOLD': profit_threshold,
#         }
#         trade_log.append(trade_record)
#         pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     asyncio.run(run_backtest())
#     print("Backtest completed.")
#     plot_trade_log()


# ----------------------------------------- Sell then profit Logic --------------------------------------------------------
# import os
# import sys
# import asyncio
# import pandas as pd
# from datetime import datetime, timedelta
# import ta
# import json
# from llm_decision_strategy_05 import get_llm_decision
# from pprint import pprint
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# BINANCE_FEE_RATE = 0.000  # 0.1% per trade

# def plot_trade_log(trade_log_path="backtest_trade_log.csv"):
#     df = pd.read_csv(trade_log_path)
#     df['Timestamp'] = pd.to_datetime(df['Timestamp'])
#     plt.style.use('dark_background')

#     fig, axs = plt.subplots(4, 1, figsize=(16, 18), sharex=True)

#     axs[0].plot(df['Timestamp'], df['Close'], color='white', label='BTC Close')
#     axs[0].set_ylabel('BTC Price')
#     axs[0].set_title('BTC Close Over Time')
#     axs[0].legend(loc='upper right')
#     axs[0].grid(True, alpha=0.3)

#     axs[1].plot(df['Timestamp'], df['USD BALANCE'], color='lime', label='USD Balance')
#     axs[1].set_ylabel('USD Balance')
#     axs[1].set_title('USD Balance Over Time')
#     axs[1].legend(loc='upper right')
#     axs[1].grid(True, alpha=0.3)

#     axs[2].plot(df['Timestamp'], df['USD PROFIT'], color='gold', label='USD Profit')
#     axs[2].set_ylabel('USD Profit')
#     axs[2].set_title('USD Profit Over Time')
#     axs[2].legend(loc='upper right')
#     axs[2].grid(True, alpha=0.3)

#     axs[3].plot(df['Timestamp'], df['Total Portfolio Value'], color='deepskyblue', label='Total Portfolio Value')
#     axs[3].set_ylabel('Portfolio Value (USD)')
#     axs[3].set_title('Total Portfolio Value Over Time')
#     axs[3].legend(loc='upper right')
#     axs[3].grid(True, alpha=0.3)
#     axs[3].set_xlabel('Timestamp')

#     axs[3].xaxis.set_major_locator(mdates.HourLocator(interval=6))
#     axs[3].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
#     plt.xticks(rotation=45)

#     plt.tight_layout()
#     plt.show()

# TRADE_INTERVAL_HOURS = 1
# TRADE_DURATION = "1 week"

# def parse_duration(duration_str):
#     duration_str = duration_str.lower().strip()
#     if "day" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=n)
#     elif "week" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(weeks=n)
#     elif "month" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=30 * n)
#     else:
#         return timedelta(weeks=1)

# def load_config():
#     config = {}
#     with open("config.cfg", "r") as f:
#         for line in f:
#             if line.strip() and not line.startswith('#'):
#                 parts = line.strip().split('=', 1)
#                 key = parts[0].strip()
#                 value = parts[1].strip() if len(parts) > 1 else ''
#                 if value.lower() == 'true':
#                     config[key] = True
#                 elif value.lower() == 'false':
#                     config[key] = False
#                 elif value.replace('.', '', 1).isdigit():
#                     config[key] = float(value)
#                 else:
#                     config[key] = value
#     print(f"Fetched Config : {config}")
#     return config

# def generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold):
#     md_content = f"""
# # Complete Bitcoin Data Collection Report

# ## Yahoo Finance Data

# | Date | Open | High | Low | Close | Volume |
# |------|------|------|-----|-------|--------|
# | {current_date.strftime('%Y-%m-%d %H:%M:%S')} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,.0f} |

# ### Technical Indicators (Current Values)

# - **ATR (14)**: ${indicators['atr_14'] if indicators['atr_14'] is not None else 'N/A'}
# - **RSI (14)**: {indicators['rsi_14'] if indicators['rsi_14'] is not None else 'N/A'}
# - **SMA 20**: ${indicators['sma_20'] if indicators['sma_20'] is not None else 'N/A'}
# - **SMA 50**: ${indicators['sma_50'] if indicators['sma_50'] is not None else 'N/A'}
# - **EMA 12**: ${indicators['ema_12'] if indicators['ema_12'] is not None else 'N/A'}
# - **EMA 26**: ${indicators['ema_26'] if indicators['ema_26'] is not None else 'N/A'}
# - **Bollinger Upper (20)**: ${indicators['bb_upper'] if indicators['bb_upper'] is not None else 'N/A'}
# - **Bollinger Middle (20)**: ${indicators['bb_middle'] if indicators['bb_middle'] is not None else 'N/A'}
# - **Bollinger Lower (20)**: ${indicators['bb_lower'] if indicators['bb_lower'] is not None else 'N/A'}
# - **MACD**: {indicators['macd'] if indicators['macd'] is not None else 'N/A'}
# - **MACD Signal**: {indicators['macd_signal'] if indicators['macd_signal'] is not None else 'N/A'}
# - **Volume SMA 20**: {indicators['volume_sma_20'] if indicators['volume_sma_20'] is not None else 'N/A'}
# - **ATR Volatility Ratio**: {indicators['atr_volatility_ratio'] if indicators['atr_volatility_ratio'] is not None else 'N/A'}

# ## Portfolio Status

# - BTC: {portfolio['btc']}
# - USDT: {portfolio['usdt']}
# - USD PROFIT: {portfolio['usd_profit']}
# - Portfolio Value: {portfolio['btc'] * current_price + portfolio['usdt']}
# - PROFIT THRESHOLD: {profit_threshold}
# """
#     return md_content

# async def run_backtest():
#     data_file = 'btc_hourly_yahoo_binance_6mo.csv'
#     if not os.path.exists(data_file):
#         data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
#     if not os.path.exists(data_file):
#         print(f"ERROR: Data file '{data_file}' not found!")
#         return

#     if data_file.endswith('.csv'):
#         df = pd.read_csv(data_file)
#     else:
#         df = pd.read_excel(data_file)
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)

#     print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])

#     config = load_config()
#     initial_budget = config.get('budget', 10000)
#     portfolio = {'btc': 0.0, 'usdt': initial_budget, 'usd_profit': 0.0}
#     trade_log = []
#     trade_log_path = "backtest_trade_log.csv"
#     if os.path.exists(trade_log_path):
#         os.remove(trade_log_path)

#     subsample = TRADE_INTERVAL_HOURS
#     start_date = df['date'].min()
#     duration = parse_duration(TRADE_DURATION)
#     end_date = start_date + duration
#     print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

#     df_test = df[df['date'] >= start_date]
#     if len(df_test) == 0:
#         print(f"[ERROR] No data found for the selected period!")
#         return

#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")

#     profit_threshold = initial_budget
#     consecutive_hold_count = 0

#     for i, row in df_subsampled.iterrows():
#         if pd.isna(row['close']):
#             continue
#         current_date = row['date']
#         current_price = row['close']

#         df_slice = df_test[df_test['date'] <= current_date].copy()
#         min_window = 14
#         if len(df_slice) < min_window:
#             indicators = {
#                 'atr_14': None,
#                 'rsi_14': None,
#                 'sma_20': None,
#                 'sma_50': None,
#                 'ema_12': None,
#                 'ema_26': None,
#                 'bb_upper': None,
#                 'bb_middle': None,
#                 'bb_lower': None,
#                 'macd': None,
#                 'macd_signal': None,
#                 'volume_sma_20': None,
#                 'atr_volatility_ratio': None
#             }
#         else:
#             indicators = {
#                 'atr_14': ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1],
#                 'rsi_14': ta.momentum.RSIIndicator(df_slice['close'], window=14).rsi().iloc[-1],
#                 'sma_20': ta.trend.sma_indicator(df_slice['close'], window=20).iloc[-1],
#                 'sma_50': ta.trend.sma_indicator(df_slice['close'], window=50).iloc[-1],
#                 'ema_12': ta.trend.ema_indicator(df_slice['close'], window=12).iloc[-1],
#                 'ema_26': ta.trend.ema_indicator(df_slice['close'], window=26).iloc[-1],
#                 'bb_upper': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_hband().iloc[-1],
#                 'bb_middle': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_mavg().iloc[-1],
#                 'bb_lower': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_lband().iloc[-1],
#                 'macd': ta.trend.MACD(df_slice['close']).macd().iloc[-1],
#                 'macd_signal': ta.trend.MACD(df_slice['close']).macd_signal().iloc[-1],
#                 'volume_sma_20': ta.trend.sma_indicator(df_slice['volume'], window=20).iloc[-1],
#                 'atr_volatility_ratio': (ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1] / df_slice['close'].iloc[-1])
#             }

#         md_content = generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold)
#         context = {
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'profit_threshold': profit_threshold,
#             'trade_history': trade_log[-10:]
#         }

#         decision = get_llm_decision(context)
#         pprint(f"LLM Decision : {decision}")
#         action = decision.get('action', 'None')
#         quantity = decision.get('quantity', 0)
#         profit_amount = decision.get('profit_amount', 0)

#         value_usd_cost = 0
#         fee = 0
#         reason = None

#         # --- Portfolio management ---
#         if action == 'BUY':
#             consecutive_hold_count = 0
#             value_usd_cost = quantity * current_price
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             total_cost = value_usd_cost + fee
#             if quantity <= 0:
#                 reason = "LLM suggested BUY with zero or negative quantity"
#             elif portfolio['usdt'] < total_cost:
#                 reason = f"Insufficient USD balance for BUY (needed ${total_cost:.2f}, available ${portfolio['usdt']:.2f})"
#             else:
#                 portfolio['usdt'] -= total_cost
#                 portfolio['btc'] += quantity
#         elif action == 'SELL':
#             consecutive_hold_count = 0
#             value_usd_cost = quantity * current_price
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             net_usd = value_usd_cost - fee
#             if quantity <= 0:
#                 reason = "LLM suggested SELL with zero or negative quantity"
#             elif portfolio['btc'] < quantity:
#                 reason = f"Insufficient BTC balance for SELL (needed {quantity:.6f}, available {portfolio['btc']:.6f})"
#             else:
#                 portfolio['btc'] -= quantity
#                 portfolio['usdt'] += net_usd
#         elif action == 'PROFIT':
#             consecutive_hold_count = 0
#             if profit_amount <= 0:
#                 reason = "LLM suggested PROFIT with zero or negative amount"
#             else:
#                 # Always SELL enough BTC to cover profit_amount, then move USDT to USD PROFIT
#                 btc_to_sell = profit_amount / current_price
#                 if portfolio['btc'] < btc_to_sell:
#                     reason = f"Insufficient BTC to SELL for PROFIT extraction (needed {btc_to_sell:.6f}, available {portfolio['btc']:.6f})"
#                 else:
#                     # SELL BTC for profit_amount USD
#                     portfolio['btc'] -= btc_to_sell
#                     portfolio['usdt'] += profit_amount
#                     # Log SELL action
#                     sell_record = {
#                         'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                         'Type': 'SELL (for PROFIT)',
#                         'Open': row['open'],
#                         'Close': row['close'],
#                         'Quantity': btc_to_sell,
#                         'Value USD (Cost)': profit_amount,
#                         'BTC BALANCE': portfolio['btc'],
#                         'BTC VALUE USD': portfolio['btc'] * current_price,
#                         'Total Portfolio Value': portfolio['btc'] * current_price + portfolio['usdt'],
#                         'USD BALANCE': portfolio['usdt'],
#                         'USD PROFIT': portfolio['usd_profit'],
#                         'PROFIT THRESHOLD': profit_threshold,
#                     }
#                     trade_log.append(sell_record)
#                     # Move USD to USD PROFIT
#                     portfolio['usdt'] -= profit_amount
#                     portfolio['usd_profit'] += profit_amount
#                     profit_threshold += profit_amount
#                     value_usd_cost = profit_amount
#         elif action == 'HOLD':
#             consecutive_hold_count += 1
#             # Only update threshold if 10 consecutive HOLDs
#             if consecutive_hold_count >= 10 and len(trade_log) >= 10:
#                 last_10_values = [t['Total Portfolio Value'] for t in trade_log[-10:]]
#                 profit_threshold = sum(last_10_values) / len(last_10_values)
#                 print(f"[THRESHOLD RESET] Updated profit threshold to last 10 trades average: {profit_threshold:.2f}")
#                 consecutive_hold_count = 0
#         else:
#             consecutive_hold_count = 0
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         if reason:
#             action = f"Overwrite LLM Decision to HOLD: {reason}"
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         btc_value_usd = portfolio['btc'] * current_price
#         total_portfolio_value = btc_value_usd + portfolio['usdt']

#         trade_record = {
#             'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#             'Type': action if action != 'PROFIT' else 'PROFIT',
#             'Open': row['open'],
#             'Close': row['close'],
#             'Quantity': quantity if action != 'PROFIT' else 0,
#             'Value USD (Cost)': value_usd_cost,
#             'BTC BALANCE': portfolio['btc'],
#             'BTC VALUE USD': btc_value_usd,
#             'Total Portfolio Value': total_portfolio_value,
#             'USD BALANCE': portfolio['usdt'],
#             'USD PROFIT': portfolio['usd_profit'],
#             'PROFIT THRESHOLD': profit_threshold,
#         }
#         trade_log.append(trade_record)
#         pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     #asyncio.run(run_backtest())
#     print("Backtest completed.")
#     plot_trade_log()

# ------------------------------------------ Dynamic Profit threshold adjusting based on last 5 trades if it gets stuck on hold for 5 trades consecutively ---------------------------------------------

# import os
# import sys
# import asyncio
# import pandas as pd
# from datetime import datetime, timedelta
# import ta
# import json
# from llm_decision_strategy_05 import get_llm_decision
# from pprint import pprint
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# BINANCE_FEE_RATE = 0.000  # 0.1% per trade

# def plot_trade_log(trade_log_path="backtest_trade_log.csv"):
#     df = pd.read_csv(trade_log_path)
#     df['Timestamp'] = pd.to_datetime(df['Timestamp'])
#     plt.style.use('dark_background')

#     fig, axs = plt.subplots(5, 1, figsize=(16, 22), sharex=True)

#     axs[0].plot(df['Timestamp'], df['Close'], color='white', label='BTC Close')
#     axs[0].set_ylabel('BTC Price')
#     axs[0].set_title('BTC Close Over Time')
#     axs[0].legend(loc='upper right')
#     axs[0].grid(True, alpha=0.3)

#     axs[1].plot(df['Timestamp'], df['USD BALANCE'], color='lime', label='USD Balance')
#     axs[1].set_ylabel('USD Balance')
#     axs[1].set_title('USD Balance Over Time')
#     axs[1].legend(loc='upper right')
#     axs[1].grid(True, alpha=0.3)

#     axs[2].plot(df['Timestamp'], df['USD PROFIT'], color='gold', label='USD Profit')
#     axs[2].set_ylabel('USD Profit')
#     axs[2].set_title('USD Profit Over Time')
#     axs[2].legend(loc='upper right')
#     axs[2].grid(True, alpha=0.3)

#     axs[3].plot(df['Timestamp'], df['BTC BALANCE'], color='orange', label='BTC Balance')
#     axs[3].set_ylabel('BTC Balance')
#     axs[3].set_title('BTC Balance Over Time')
#     axs[3].legend(loc='upper right')
#     axs[3].grid(True, alpha=0.3)

#     axs[4].plot(df['Timestamp'], df['Total Portfolio Value'], color='deepskyblue', label='Total Portfolio Value')
#     axs[4].set_ylabel('Portfolio Value (USD)')
#     axs[4].set_title('Total Portfolio Value Over Time')
#     axs[4].legend(loc='upper right')
#     axs[4].grid(True, alpha=0.3)
#     axs[4].set_xlabel('Timestamp')

#     axs[4].xaxis.set_major_locator(mdates.HourLocator(interval=6))
#     axs[4].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
#     plt.xticks(rotation=45)

#     plt.tight_layout()
#     plt.show()

# TRADE_INTERVAL_HOURS = 1
# TRADE_DURATION = "1 week"

# def parse_duration(duration_str):
#     duration_str = duration_str.lower().strip()
#     if "day" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=n)
#     elif "week" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(weeks=n)
#     elif "month" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=30 * n)
#     else:
#         return timedelta(weeks=1)

# def load_config():
#     config = {}
#     with open("config.cfg", "r") as f:
#         for line in f:
#             if line.strip() and not line.startswith('#'):
#                 parts = line.strip().split('=', 1)
#                 key = parts[0].strip()
#                 value = parts[1].strip() if len(parts) > 1 else ''
#                 if value.lower() == 'true':
#                     config[key] = True
#                 elif value.lower() == 'false':
#                     config[key] = False
#                 elif value.replace('.', '', 1).isdigit():
#                     config[key] = float(value)
#                 else:
#                     config[key] = value
#     print(f"Fetched Config : {config}")
#     return config

# def generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold):
#     md_content = f"""
# # Complete Bitcoin Data Collection Report

# ## Yahoo Finance Data

# | Date | Open | High | Low | Close | Volume |
# |------|------|------|-----|-------|--------|
# | {current_date.strftime('%Y-%m-%d %H:%M:%S')} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,.0f} |

# ### Technical Indicators (Current Values)

# - **ATR (14)**: ${indicators['atr_14'] if indicators['atr_14'] is not None else 'N/A'}
# - **RSI (14)**: {indicators['rsi_14'] if indicators['rsi_14'] is not None else 'N/A'}
# - **SMA 20**: ${indicators['sma_20'] if indicators['sma_20'] is not None else 'N/A'}
# - **SMA 50**: ${indicators['sma_50'] if indicators['sma_50'] is not None else 'N/A'}
# - **EMA 12**: ${indicators['ema_12'] if indicators['ema_12'] is not None else 'N/A'}
# - **EMA 26**: ${indicators['ema_26'] if indicators['ema_26'] is not None else 'N/A'}
# - **Bollinger Upper (20)**: ${indicators['bb_upper'] if indicators['bb_upper'] is not None else 'N/A'}
# - **Bollinger Middle (20)**: ${indicators['bb_middle'] if indicators['bb_middle'] is not None else 'N/A'}
# - **Bollinger Lower (20)**: ${indicators['bb_lower'] if indicators['bb_lower'] is not None else 'N/A'}
# - **MACD**: {indicators['macd'] if indicators['macd'] is not None else 'N/A'}
# - **MACD Signal**: {indicators['macd_signal'] if indicators['macd_signal'] is not None else 'N/A'}
# - **Volume SMA 20**: {indicators['volume_sma_20'] if indicators['volume_sma_20'] is not None else 'N/A'}
# - **ATR Volatility Ratio**: {indicators['atr_volatility_ratio'] if indicators['atr_volatility_ratio'] is not None else 'N/A'}

# ## Portfolio Status

# - BTC: {portfolio['btc']}
# - USDT: {portfolio['usdt']}
# - USD PROFIT: {portfolio['usd_profit']}
# - Portfolio Value: {portfolio['btc'] * current_price + portfolio['usdt']}
# - PROFIT THRESHOLD: {profit_threshold}
# """
#     return md_content

# async def run_backtest():
#     data_file = 'btc_hourly_yahoo_binance_6mo.csv'
#     if not os.path.exists(data_file):
#         data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
#     if not os.path.exists(data_file):
#         print(f"ERROR: Data file '{data_file}' not found!")
#         return

#     if data_file.endswith('.csv'):
#         df = pd.read_csv(data_file)
#     else:
#         df = pd.read_excel(data_file)
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)

#     print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])

#     config = load_config()
#     initial_budget = config.get('budget', 10000)
#     portfolio = {'btc': 0.0, 'usdt': initial_budget, 'usd_profit': 0.0}
#     trade_log = []
#     trade_log_path = "backtest_trade_log.csv"
#     if os.path.exists(trade_log_path):
#         os.remove(trade_log_path)

#     subsample = TRADE_INTERVAL_HOURS
#     start_date = df['date'].min()
#     duration = parse_duration(TRADE_DURATION)
#     end_date = start_date + duration
#     print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

#     df_test = df[df['date'] >= start_date]
#     if len(df_test) == 0:
#         print(f"[ERROR] No data found for the selected period!")
#         return

#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")

#     profit_threshold = initial_budget
#     consecutive_hold_count = 0

#     for i, row in df_subsampled.iterrows():
#         if pd.isna(row['close']):
#             continue
#         current_date = row['date']
#         current_price = row['close']

#         df_slice = df_test[df_test['date'] <= current_date].copy()
#         min_window = 14
#         if len(df_slice) < min_window:
#             indicators = {
#                 'atr_14': None,
#                 'rsi_14': None,
#                 'sma_20': None,
#                 'sma_50': None,
#                 'ema_12': None,
#                 'ema_26': None,
#                 'bb_upper': None,
#                 'bb_middle': None,
#                 'bb_lower': None,
#                 'macd': None,
#                 'macd_signal': None,
#                 'volume_sma_20': None,
#                 'atr_volatility_ratio': None
#             }
#         else:
#             indicators = {
#                 'atr_14': ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1],
#                 'rsi_14': ta.momentum.RSIIndicator(df_slice['close'], window=14).rsi().iloc[-1],
#                 'sma_20': ta.trend.sma_indicator(df_slice['close'], window=20).iloc[-1],
#                 'sma_50': ta.trend.sma_indicator(df_slice['close'], window=50).iloc[-1],
#                 'ema_12': ta.trend.ema_indicator(df_slice['close'], window=12).iloc[-1],
#                 'ema_26': ta.trend.ema_indicator(df_slice['close'], window=26).iloc[-1],
#                 'bb_upper': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_hband().iloc[-1],
#                 'bb_middle': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_mavg().iloc[-1],
#                 'bb_lower': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_lband().iloc[-1],
#                 'macd': ta.trend.MACD(df_slice['close']).macd().iloc[-1],
#                 'macd_signal': ta.trend.MACD(df_slice['close']).macd_signal().iloc[-1],
#                 'volume_sma_20': ta.trend.sma_indicator(df_slice['volume'], window=20).iloc[-1],
#                 'atr_volatility_ratio': (ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1] / df_slice['close'].iloc[-1])
#             }

#         md_content = generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold)
#         context = {
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'profit_threshold': profit_threshold,
#             'trade_history': trade_log[-10:]
#         }

#         decision = get_llm_decision(context)
#         pprint(f"LLM Decision : {decision}")
#         action = decision.get('action', 'None')
#         quantity = decision.get('quantity', 0)
#         profit_amount = decision.get('profit_amount', 0)

#         value_usd_cost = 0
#         fee = 0
#         reason = None

#         # --- Portfolio management ---
#         if action == 'BUY':
#             consecutive_hold_count = 0
#             value_usd_cost = quantity * current_price
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             total_cost = value_usd_cost + fee
#             if quantity <= 0:
#                 reason = "LLM suggested BUY with zero or negative quantity"
#             elif portfolio['usdt'] < total_cost:
#                 reason = f"Insufficient USD balance for BUY (needed ${total_cost:.2f}, available ${portfolio['usdt']:.2f})"
#             else:
#                 portfolio['usdt'] -= total_cost
#                 portfolio['btc'] += quantity
#         elif action == 'SELL':
#             consecutive_hold_count = 0
#             value_usd_cost = quantity * current_price
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             net_usd = value_usd_cost - fee
#             if quantity <= 0:
#                 reason = "LLM suggested SELL with zero or negative quantity"
#             elif portfolio['btc'] < quantity:
#                 reason = f"Insufficient BTC balance for SELL (needed {quantity:.6f}, available {portfolio['btc']:.6f})"
#             else:
#                 portfolio['btc'] -= quantity
#                 portfolio['usdt'] += net_usd
#         elif action == 'PROFIT':
#             consecutive_hold_count = 0
#             if profit_amount <= 0:
#                 reason = "LLM suggested PROFIT with zero or negative amount"
#             else:
#                 # Always SELL enough BTC to cover profit_amount, then move USDT to USD PROFIT
#                 btc_to_sell = profit_amount / current_price
#                 if portfolio['btc'] < btc_to_sell:
#                     reason = f"Insufficient BTC to SELL for PROFIT extraction (needed {btc_to_sell:.6f}, available {portfolio['btc']:.6f})"
#                 else:
#                     # SELL BTC for profit_amount USD
#                     portfolio['btc'] -= btc_to_sell
#                     portfolio['usdt'] += profit_amount
#                     # Log SELL action
#                     sell_record = {
#                         'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                         'Type': 'SELL (for PROFIT)',
#                         'Open': row['open'],
#                         'Close': row['close'],
#                         'Quantity': btc_to_sell,
#                         'Value USD (Cost)': profit_amount,
#                         'BTC BALANCE': portfolio['btc'],
#                         'BTC VALUE USD': portfolio['btc'] * current_price,
#                         'Total Portfolio Value': portfolio['btc'] * current_price + portfolio['usdt'],
#                         'USD BALANCE': portfolio['usdt'],
#                         'USD PROFIT': portfolio['usd_profit'],
#                         'PROFIT THRESHOLD': profit_threshold,
#                     }
#                     trade_log.append(sell_record)
#                     # Move USD to USD PROFIT
#                     portfolio['usdt'] -= profit_amount
#                     portfolio['usd_profit'] += profit_amount
#                     profit_threshold += profit_amount
#                     value_usd_cost = profit_amount
#         elif action == 'HOLD':
#             consecutive_hold_count += 1
#             # Only update threshold if 5 consecutive HOLDs
#             if consecutive_hold_count >= 5 and len(trade_log) >= 10:
#                 last_10_values = [t['Total Portfolio Value'] for t in trade_log[-10:]]
#                 profit_threshold = sum(last_10_values) / len(last_10_values)
#                 print(f"[THRESHOLD RESET] Updated profit threshold to last 10 trades average: {profit_threshold:.2f}")
#                 consecutive_hold_count = 0
#         else:
#             consecutive_hold_count = 0
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         if reason:
#             action = f"Overwrite LLM Decision to HOLD: {reason}"
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         btc_value_usd = portfolio['btc'] * current_price
#         total_portfolio_value = btc_value_usd + portfolio['usdt']

#         trade_record = {
#             'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#             'Type': action if action != 'PROFIT' else 'PROFIT',
#             'Open': row['open'],
#             'Close': row['close'],
#             'Quantity': quantity if action != 'PROFIT' else 0,
#             'Value USD (Cost)': value_usd_cost,
#             'BTC BALANCE': portfolio['btc'],
#             'BTC VALUE USD': btc_value_usd,
#             'Total Portfolio Value': total_portfolio_value,
#             'USD BALANCE': portfolio['usdt'],
#             'USD PROFIT': portfolio['usd_profit'],
#             'PROFIT THRESHOLD': profit_threshold,
#         }
#         trade_log.append(trade_record)
#         pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     #asyncio.run(run_backtest())
#     print("Backtest completed.")
#     plot_trade_log()


# ------------------------------------------ Dynamic Profit threshold adjusting plus btc amount is suggested as usd value rather than quantity ---------------------------------------------
# import os
# import sys
# import asyncio
# import pandas as pd
# from datetime import datetime, timedelta
# import ta
# import json
# from llm_decision_strategy_05 import get_llm_decision
# from pprint import pprint
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# BINANCE_FEE_RATE = 0.000  # 0.1% per trade

# def plot_trade_log(trade_log_path="backtest_trade_log.csv"):
#     df = pd.read_csv(trade_log_path)
#     df['Timestamp'] = pd.to_datetime(df['Timestamp'])
#     plt.style.use('dark_background')

#     fig, axs = plt.subplots(5, 1, figsize=(16, 22), sharex=True)

#     axs[0].plot(df['Timestamp'], df['Close'], color='white', label='BTC Close')
#     axs[0].set_ylabel('BTC Price')
#     axs[0].set_title('BTC Close Over Time')
#     axs[0].legend(loc='upper right')
#     axs[0].grid(True, alpha=0.3)

#     axs[1].plot(df['Timestamp'], df['USD BALANCE'], color='lime', label='USD Balance')
#     axs[1].set_ylabel('USD Balance')
#     axs[1].set_title('USD Balance Over Time')
#     axs[1].legend(loc='upper right')
#     axs[1].grid(True, alpha=0.3)

#     axs[2].plot(df['Timestamp'], df['USD PROFIT'], color='gold', label='USD Profit')
#     axs[2].set_ylabel('USD Profit')
#     axs[2].set_title('USD Profit Over Time')
#     axs[2].legend(loc='upper right')
#     axs[2].grid(True, alpha=0.3)

#     axs[3].plot(df['Timestamp'], df['BTC BALANCE'], color='orange', label='BTC Balance')
#     axs[3].set_ylabel('BTC Balance')
#     axs[3].set_title('BTC Balance Over Time')
#     axs[3].legend(loc='upper right')
#     axs[3].grid(True, alpha=0.3)

#     axs[4].plot(df['Timestamp'], df['Total Portfolio Value'], color='deepskyblue', label='Total Portfolio Value')
#     axs[4].set_ylabel('Portfolio Value (USD)')
#     axs[4].set_title('Total Portfolio Value Over Time')
#     axs[4].legend(loc='upper right')
#     axs[4].grid(True, alpha=0.3)
#     axs[4].set_xlabel('Timestamp')

#     axs[4].xaxis.set_major_locator(mdates.HourLocator(interval=6))
#     axs[4].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
#     plt.xticks(rotation=45)

#     plt.tight_layout()
#     plt.show()

# TRADE_INTERVAL_HOURS = 1
# TRADE_DURATION = "1 week"

# def parse_duration(duration_str):
#     duration_str = duration_str.lower().strip()
#     if "day" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=n)
#     elif "week" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(weeks=n)
#     elif "month" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=30 * n)
#     else:
#         return timedelta(weeks=1)

# def load_config():
#     config = {}
#     with open("config.cfg", "r") as f:
#         for line in f:
#             if line.strip() and not line.startswith('#'):
#                 parts = line.strip().split('=', 1)
#                 key = parts[0].strip()
#                 value = parts[1].strip() if len(parts) > 1 else ''
#                 if value.lower() == 'true':
#                     config[key] = True
#                 elif value.lower() == 'false':
#                     config[key] = False
#                 elif value.replace('.', '', 1).isdigit():
#                     config[key] = float(value)
#                 else:
#                     config[key] = value
#     print(f"Fetched Config : {config}")
#     return config

# def generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold):
#     md_content = f"""
# # Complete Bitcoin Data Collection Report

# ## Yahoo Finance Data

# | Date | Open | High | Low | Close | Volume |
# |------|------|------|-----|-------|--------|
# | {current_date.strftime('%Y-%m-%d %H:%M:%S')} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,.0f} |

# ### Technical Indicators (Current Values)

# - **ATR (14)**: ${indicators['atr_14'] if indicators['atr_14'] is not None else 'N/A'}
# - **RSI (14)**: {indicators['rsi_14'] if indicators['rsi_14'] is not None else 'N/A'}
# - **SMA 20**: ${indicators['sma_20'] if indicators['sma_20'] is not None else 'N/A'}
# - **SMA 50**: ${indicators['sma_50'] if indicators['sma_50'] is not None else 'N/A'}
# - **EMA 12**: ${indicators['ema_12'] if indicators['ema_12'] is not None else 'N/A'}
# - **EMA 26**: ${indicators['ema_26'] if indicators['ema_26'] is not None else 'N/A'}
# - **Bollinger Upper (20)**: ${indicators['bb_upper'] if indicators['bb_upper'] is not None else 'N/A'}
# - **Bollinger Middle (20)**: ${indicators['bb_middle'] if indicators['bb_middle'] is not None else 'N/A'}
# - **Bollinger Lower (20)**: ${indicators['bb_lower'] if indicators['bb_lower'] is not None else 'N/A'}
# - **MACD**: {indicators['macd'] if indicators['macd'] is not None else 'N/A'}
# - **MACD Signal**: {indicators['macd_signal'] if indicators['macd_signal'] is not None else 'N/A'}
# - **Volume SMA 20**: {indicators['volume_sma_20'] if indicators['volume_sma_20'] is not None else 'N/A'}
# - **ATR Volatility Ratio**: {indicators['atr_volatility_ratio'] if indicators['atr_volatility_ratio'] is not None else 'N/A'}

# ## Portfolio Status

# - BTC: {portfolio['btc']}
# - USDT: {portfolio['usdt']}
# - USD PROFIT: {portfolio['usd_profit']}
# - Portfolio Value: {portfolio['btc'] * current_price + portfolio['usdt']}
# - PROFIT THRESHOLD: {profit_threshold}
# """
#     return md_content

# async def run_backtest():
#     data_file = 'btc_hourly_yahoo_binance_6mo.csv'
#     if not os.path.exists(data_file):
#         data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
#     if not os.path.exists(data_file):
#         print(f"ERROR: Data file '{data_file}' not found!")
#         return

#     if data_file.endswith('.csv'):
#         df = pd.read_csv(data_file)
#     else:
#         df = pd.read_excel(data_file)
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)

#     print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])

#     config = load_config()
#     initial_budget = config.get('budget', 10000)
#     portfolio = {'btc': 0.0, 'usdt': initial_budget, 'usd_profit': 0.0}
#     trade_log = []
#     trade_log_path = "backtest_trade_log.csv"
#     if os.path.exists(trade_log_path):
#         os.remove(trade_log_path)

#     subsample = TRADE_INTERVAL_HOURS
#     start_date = df['date'].min()
#     duration = parse_duration(TRADE_DURATION)
#     end_date = start_date + duration
#     print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

#     df_test = df[df['date'] >= start_date]
#     if len(df_test) == 0:
#         print(f"[ERROR] No data found for the selected period!")
#         return

#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")

#     profit_threshold = initial_budget
#     consecutive_hold_count = 0

#     for i, row in df_subsampled.iterrows():
#         if pd.isna(row['close']):
#             continue
#         current_date = row['date']
#         current_price = row['close']

#         df_slice = df_test[df_test['date'] <= current_date].copy()
#         min_window = 14
#         if len(df_slice) < min_window:
#             indicators = {
#                 'atr_14': None,
#                 'rsi_14': None,
#                 'sma_20': None,
#                 'sma_50': None,
#                 'ema_12': None,
#                 'ema_26': None,
#                 'bb_upper': None,
#                 'bb_middle': None,
#                 'bb_lower': None,
#                 'macd': None,
#                 'macd_signal': None,
#                 'volume_sma_20': None,
#                 'atr_volatility_ratio': None
#             }
#         else:
#             indicators = {
#                 'atr_14': ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1],
#                 'rsi_14': ta.momentum.RSIIndicator(df_slice['close'], window=14).rsi().iloc[-1],
#                 'sma_20': ta.trend.sma_indicator(df_slice['close'], window=20).iloc[-1],
#                 'sma_50': ta.trend.sma_indicator(df_slice['close'], window=50).iloc[-1],
#                 'ema_12': ta.trend.ema_indicator(df_slice['close'], window=12).iloc[-1],
#                 'ema_26': ta.trend.ema_indicator(df_slice['close'], window=26).iloc[-1],
#                 'bb_upper': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_hband().iloc[-1],
#                 'bb_middle': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_mavg().iloc[-1],
#                 'bb_lower': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_lband().iloc[-1],
#                 'macd': ta.trend.MACD(df_slice['close']).macd().iloc[-1],
#                 'macd_signal': ta.trend.MACD(df_slice['close']).macd_signal().iloc[-1],
#                 'volume_sma_20': ta.trend.sma_indicator(df_slice['volume'], window=20).iloc[-1],
#                 'atr_volatility_ratio': (ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1] / df_slice['close'].iloc[-1])
#             }

#         md_content = generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold)
#         context = {
#             'md_content': md_content,
#             'portfolio': portfolio,
#             'profit_threshold': profit_threshold,
#             'trade_history': trade_log[-10:]
#         }

#         decision = get_llm_decision(context)
#         pprint(f"LLM Decision : {decision}")
#         action = decision.get('action', 'None')
#         buy_amount = decision.get('buy_amount', 0)
#         quantity = decision.get('quantity', 0)
#         profit_amount = decision.get('profit_amount', 0)

#         value_usd_cost = 0
#         fee = 0
#         reason = None

#         # --- Portfolio management ---
#         if action == 'BUY':
#             consecutive_hold_count = 0
#             value_usd_cost = buy_amount
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             total_cost = value_usd_cost + fee
#             if buy_amount <= 0:
#                 reason = "LLM suggested BUY with zero or negative USD amount"
#             elif portfolio['usdt'] < total_cost:
#                 reason = f"Insufficient USD balance for BUY (needed ${total_cost:.2f}, available ${portfolio['usdt']:.2f})"
#             else:
#                 btc_bought = buy_amount / current_price
#                 portfolio['usdt'] -= total_cost
#                 portfolio['btc'] += btc_bought
#                 quantity = btc_bought  # For logging
#         elif action == 'SELL':
#             consecutive_hold_count = 0
#             value_usd_cost = quantity * current_price
#             fee = value_usd_cost * BINANCE_FEE_RATE
#             net_usd = value_usd_cost - fee
#             if quantity <= 0:
#                 reason = "LLM suggested SELL with zero or negative quantity"
#             elif portfolio['btc'] < quantity:
#                 reason = f"Insufficient BTC balance for SELL (needed {quantity:.6f}, available {portfolio['btc']:.6f})"
#             else:
#                 portfolio['btc'] -= quantity
#                 portfolio['usdt'] += net_usd
#         elif action == 'PROFIT':
#             consecutive_hold_count = 0
#             if profit_amount <= 0:
#                 reason = "LLM suggested PROFIT with zero or negative amount"
#             else:
#                 btc_to_sell = profit_amount / current_price
#                 if portfolio['btc'] < btc_to_sell:
#                     reason = f"Insufficient BTC to SELL for PROFIT extraction (needed {btc_to_sell:.6f}, available {portfolio['btc']:.6f})"
#                 else:
#                     # SELL BTC for profit_amount USD
#                     portfolio['btc'] -= btc_to_sell
#                     portfolio['usdt'] += profit_amount
#                     # Log SELL action
#                     sell_record = {
#                         'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                         'Type': 'SELL (for PROFIT)',
#                         'Open': row['open'],
#                         'Close': row['close'],
#                         'Quantity': btc_to_sell,
#                         'Value USD (Cost)': profit_amount,
#                         'BTC BALANCE': portfolio['btc'],
#                         'BTC VALUE USD': portfolio['btc'] * current_price,
#                         'Total Portfolio Value': portfolio['btc'] * current_price + portfolio['usdt'],
#                         'USD BALANCE': portfolio['usdt'],
#                         'USD PROFIT': portfolio['usd_profit'],
#                         'PROFIT THRESHOLD': profit_threshold,
#                     }
#                     trade_log.append(sell_record)
#                     # Move USD to USD PROFIT
#                     portfolio['usdt'] -= profit_amount
#                     portfolio['usd_profit'] += profit_amount
#                     profit_threshold += profit_amount
#                     value_usd_cost = profit_amount
#         elif action == 'HOLD':
#             consecutive_hold_count += 1
#             # Only update threshold if 5 consecutive HOLDs
#             if consecutive_hold_count >= 5 and len(trade_log) >= 10:
#                 last_10_values = [t['Total Portfolio Value'] for t in trade_log[-10:]]
#                 profit_threshold = sum(last_10_values) / len(last_10_values)
#                 print(f"[THRESHOLD RESET] Updated profit threshold to last 10 trades average: {profit_threshold:.2f}")
#                 consecutive_hold_count = 0
#         else:
#             consecutive_hold_count = 0
#             buy_amount = 0
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         if reason:
#             action = f"Overwrite LLM Decision to HOLD: {reason}"
#             buy_amount = 0
#             quantity = 0
#             value_usd_cost = 0
#             fee = 0

#         btc_value_usd = portfolio['btc'] * current_price
#         total_portfolio_value = btc_value_usd + portfolio['usdt']

#         trade_record = {
#             'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#             'Type': action if action != 'PROFIT' else 'PROFIT',
#             'Open': row['open'],
#             'Close': row['close'],
#             'Quantity': quantity if action != 'PROFIT' else 0,
#             'Buy USD Amount': buy_amount if action == 'BUY' else 0,
#             'Value USD (Cost)': value_usd_cost,
#             'BTC BALANCE': portfolio['btc'],
#             'BTC VALUE USD': btc_value_usd,
#             'Total Portfolio Value': total_portfolio_value,
#             'USD BALANCE': portfolio['usdt'],
#             'USD PROFIT': portfolio['usd_profit'],
#             'PROFIT THRESHOLD': profit_threshold,
#         }
#         trade_log.append(trade_record)
#         pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     asyncio.run(run_backtest())
#     print("Backtest completed.")
#     plot_trade_log()


# ---------------------------------------------- Treshold Fix ------------------------------------------------------------------------------------
import os
import sys
import asyncio
import pandas as pd
from datetime import datetime, timedelta
import ta
import json
from llm_decision_strategy_05 import get_llm_decision
from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BINANCE_FEE_RATE = 0.000  # 0.1% per trade

def plot_trade_log(trade_log_path="backtest_trade_log.csv"):
    df = pd.read_csv(trade_log_path)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    plt.style.use('dark_background')

    fig, axs = plt.subplots(5, 1, figsize=(16, 22), sharex=True)

    axs[0].plot(df['Timestamp'], df['Close'], color='white', label='BTC Close')
    axs[0].set_ylabel('BTC Price')
    axs[0].set_title('BTC Close Over Time')
    axs[0].legend(loc='upper right')
    axs[0].grid(True, alpha=0.3)

    axs[1].plot(df['Timestamp'], df['USD BALANCE'], color='lime', label='USD Balance')
    axs[1].set_ylabel('USD Balance')
    axs[1].set_title('USD Balance Over Time')
    axs[1].legend(loc='upper right')
    axs[1].grid(True, alpha=0.3)

    axs[2].plot(df['Timestamp'], df['USD PROFIT'], color='gold', label='USD Profit')
    axs[2].set_ylabel('USD Profit')
    axs[2].set_title('USD Profit Over Time')
    axs[2].legend(loc='upper right')
    axs[2].grid(True, alpha=0.3)

    axs[3].plot(df['Timestamp'], df['BTC BALANCE'], color='orange', label='BTC Balance')
    axs[3].set_ylabel('BTC Balance')
    axs[3].set_title('BTC Balance Over Time')
    axs[3].legend(loc='upper right')
    axs[3].grid(True, alpha=0.3)

    axs[4].plot(df['Timestamp'], df['Total Portfolio Value'], color='deepskyblue', label='Total Portfolio Value')
    axs[4].set_ylabel('Portfolio Value (USD)')
    axs[4].set_title('Total Portfolio Value Over Time')
    axs[4].legend(loc='upper right')
    axs[4].grid(True, alpha=0.3)
    axs[4].set_xlabel('Timestamp')

    axs[4].xaxis.set_major_locator(mdates.HourLocator(interval=6))
    axs[4].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

TRADE_INTERVAL_HOURS = 1
TRADE_DURATION = "1 week"

def parse_duration(duration_str):
    duration_str = duration_str.lower().strip()
    if "day" in duration_str:
        n = int(duration_str.split()[0])
        return timedelta(days=n)
    elif "week" in duration_str:
        n = int(duration_str.split()[0])
        return timedelta(weeks=n)
    elif "month" in duration_str:
        n = int(duration_str.split()[0])
        return timedelta(days=30 * n)
    else:
        return timedelta(weeks=1)

def load_config():
    config = {}
    with open("config.cfg", "r") as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('=', 1)
                key = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ''
                if value.lower() == 'true':
                    config[key] = True
                elif value.lower() == 'false':
                    config[key] = False
                elif value.replace('.', '', 1).isdigit():
                    config[key] = float(value)
                else:
                    config[key] = value
    print(f"Fetched Config : {config}")
    return config

def generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold):
    md_content = f"""
# Complete Bitcoin Data Collection Report

## Yahoo Finance Data

| Date | Open | High | Low | Close | Volume |
|------|------|------|-----|-------|--------|
| {current_date.strftime('%Y-%m-%d %H:%M:%S')} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,.0f} |

### Technical Indicators (Current Values)

- **ATR (14)**: ${indicators['atr_14'] if indicators['atr_14'] is not None else 'N/A'}
- **RSI (14)**: {indicators['rsi_14'] if indicators['rsi_14'] is not None else 'N/A'}
- **SMA 20**: ${indicators['sma_20'] if indicators['sma_20'] is not None else 'N/A'}
- **SMA 50**: ${indicators['sma_50'] if indicators['sma_50'] is not None else 'N/A'}
- **EMA 12**: ${indicators['ema_12'] if indicators['ema_12'] is not None else 'N/A'}
- **EMA 26**: ${indicators['ema_26'] if indicators['ema_26'] is not None else 'N/A'}
- **Bollinger Upper (20)**: ${indicators['bb_upper'] if indicators['bb_upper'] is not None else 'N/A'}
- **Bollinger Middle (20)**: ${indicators['bb_middle'] if indicators['bb_middle'] is not None else 'N/A'}
- **Bollinger Lower (20)**: ${indicators['bb_lower'] if indicators['bb_lower'] is not None else 'N/A'}
- **MACD**: {indicators['macd'] if indicators['macd'] is not None else 'N/A'}
- **MACD Signal**: {indicators['macd_signal'] if indicators['macd_signal'] is not None else 'N/A'}
- **Volume SMA 20**: {indicators['volume_sma_20'] if indicators['volume_sma_20'] is not None else 'N/A'}
- **ATR Volatility Ratio**: {indicators['atr_volatility_ratio'] if indicators['atr_volatility_ratio'] is not None else 'N/A'}

## Portfolio Status

- BTC: {portfolio['btc']}
- USDT: {portfolio['usdt']}
- USD PROFIT: {portfolio['usd_profit']}
- Portfolio Value: {portfolio['btc'] * current_price + portfolio['usdt']}
- PROFIT THRESHOLD: {profit_threshold}
"""
    return md_content

async def run_backtest():
    data_file = 'btc_hourly_yahoo_binance_6mo.csv'
    if not os.path.exists(data_file):
        data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
    if not os.path.exists(data_file):
        print(f"ERROR: Data file '{data_file}' not found!")
        return

    if data_file.endswith('.csv'):
        df = pd.read_csv(data_file)
    else:
        df = pd.read_excel(data_file)
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', inplace=True)

    print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

    df['close'] = df['binance_close'].fillna(df['yahoo_close'])
    df['open'] = df['binance_open'].fillna(df['yahoo_open'])
    df['high'] = df['binance_high'].fillna(df['yahoo_high'])
    df['low'] = df['binance_low'].fillna(df['yahoo_low'])
    df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])

    config = load_config()
    initial_budget = config.get('budget', 10000)
    portfolio = {'btc': 0.0, 'usdt': initial_budget, 'usd_profit': 0.0}
    trade_log = []
    trade_log_path = "backtest_trade_log.csv"
    if os.path.exists(trade_log_path):
        os.remove(trade_log_path)

    subsample = TRADE_INTERVAL_HOURS
    start_date = df['date'].min()
    duration = parse_duration(TRADE_DURATION)
    end_date = start_date + duration
    print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

    df_test = df[df['date'] >= start_date]
    if len(df_test) == 0:
        print(f"[ERROR] No data found for the selected period!")
        return

    df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
    print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")

    profit_threshold = initial_budget
    consecutive_hold_count = 0

    for i, row in df_subsampled.iterrows():
        if pd.isna(row['close']):
            continue
        current_date = row['date']
        current_price = row['close']

        df_slice = df_test[df_test['date'] <= current_date].copy()
        min_window = 14
        if len(df_slice) < min_window:
            indicators = {
                'atr_14': None,
                'rsi_14': None,
                'sma_20': None,
                'sma_50': None,
                'ema_12': None,
                'ema_26': None,
                'bb_upper': None,
                'bb_middle': None,
                'bb_lower': None,
                'macd': None,
                'macd_signal': None,
                'volume_sma_20': None,
                'atr_volatility_ratio': None
            }
        else:
            indicators = {
                'atr_14': ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1],
                'rsi_14': ta.momentum.RSIIndicator(df_slice['close'], window=14).rsi().iloc[-1],
                'sma_20': ta.trend.sma_indicator(df_slice['close'], window=20).iloc[-1],
                'sma_50': ta.trend.sma_indicator(df_slice['close'], window=50).iloc[-1],
                'ema_12': ta.trend.ema_indicator(df_slice['close'], window=12).iloc[-1],
                'ema_26': ta.trend.ema_indicator(df_slice['close'], window=26).iloc[-1],
                'bb_upper': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_hband().iloc[-1],
                'bb_middle': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_mavg().iloc[-1],
                'bb_lower': ta.volatility.BollingerBands(df_slice['close'], window=20, window_dev=2).bollinger_lband().iloc[-1],
                'macd': ta.trend.MACD(df_slice['close']).macd().iloc[-1],
                'macd_signal': ta.trend.MACD(df_slice['close']).macd_signal().iloc[-1],
                'volume_sma_20': ta.trend.sma_indicator(df_slice['volume'], window=20).iloc[-1],
                'atr_volatility_ratio': (ta.volatility.AverageTrueRange(df_slice['high'], df_slice['low'], df_slice['close'], window=14).average_true_range().iloc[-1] / df_slice['close'].iloc[-1])
            }

        md_content = generate_md_report(current_date, row, indicators, portfolio, current_price, profit_threshold)
        context = {
            'md_content': md_content,
            'portfolio': portfolio,
            'profit_threshold': profit_threshold,
            'trade_history': trade_log[-10:]
        }

        decision = get_llm_decision(context)
        pprint(f"LLM Decision : {decision}")
        action = decision.get('action', 'None')
        buy_amount = decision.get('buy_amount', 0)
        quantity = decision.get('quantity', 0)
        profit_amount = decision.get('profit_amount', 0)

        value_usd_cost = 0
        fee = 0
        reason = None

        # --- Portfolio management ---
        if action == 'BUY':
            consecutive_hold_count = 0
            value_usd_cost = buy_amount
            fee = value_usd_cost * BINANCE_FEE_RATE
            total_cost = value_usd_cost + fee
            if buy_amount <= 0:
                reason = "LLM suggested BUY with zero or negative USD amount"
            elif portfolio['usdt'] < total_cost:
                reason = f"Insufficient USD balance for BUY (needed ${total_cost:.2f}, available ${portfolio['usdt']:.2f})"
            else:
                btc_bought = buy_amount / current_price
                portfolio['usdt'] -= total_cost
                portfolio['btc'] += btc_bought
                quantity = btc_bought  # For logging
        elif action == 'SELL':
            consecutive_hold_count = 0
            value_usd_cost = quantity * current_price
            fee = value_usd_cost * BINANCE_FEE_RATE
            net_usd = value_usd_cost - fee
            if quantity <= 0:
                reason = "LLM suggested SELL with zero or negative quantity"
            elif portfolio['btc'] < quantity:
                reason = f"Insufficient BTC balance for SELL (needed {quantity:.6f}, available {portfolio['btc']:.6f})"
            else:
                portfolio['btc'] -= quantity
                portfolio['usdt'] += net_usd
        elif action == 'PROFIT':
            consecutive_hold_count = 0
            if profit_amount <= 0:
                reason = "LLM suggested PROFIT with zero or negative amount"
            else:
                btc_to_sell = profit_amount / current_price
                if portfolio['btc'] < btc_to_sell:
                    reason = f"Insufficient BTC to SELL for PROFIT extraction (needed {btc_to_sell:.6f}, available {portfolio['btc']:.6f})"
                else:
                    # SELL BTC for profit_amount USD
                    portfolio['btc'] -= btc_to_sell
                    portfolio['usdt'] += profit_amount
                    # Log SELL action
                    sell_record = {
                        'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'Type': 'SELL (for PROFIT)',
                        'Open': row['open'],
                        'Close': row['close'],
                        'Quantity': btc_to_sell,
                        'Value USD (Cost)': profit_amount,
                        'BTC BALANCE': portfolio['btc'],
                        'BTC VALUE USD': portfolio['btc'] * current_price,
                        'Total Portfolio Value': portfolio['btc'] * current_price + portfolio['usdt'],
                        'USD BALANCE': portfolio['usdt'],
                        'USD PROFIT': portfolio['usd_profit'],
                        'PROFIT THRESHOLD': profit_threshold,
                    }
                    trade_log.append(sell_record)
                    # Move USD to USD PROFIT
                    portfolio['usdt'] -= profit_amount
                    portfolio['usd_profit'] += profit_amount
                    profit_threshold += profit_amount
                    value_usd_cost = profit_amount
        elif action == 'HOLD':
            pass
            # consecutive_hold_count += 1
            # # Only update threshold if 5 consecutive HOLDs
            # if consecutive_hold_count >= 5 and len(trade_log) >= 10:
            #     # last_10_values = [t['Total Portfolio Value'] for t in trade_log[-10:]]
            #     #profit_threshold = sum(last_10_values) / len(last_10_values)
            #     profit_threshold =  initial_budget
            #     #print(f"[THRESHOLD RESET] Updated profit threshold to last 10 trades average: {profit_threshold:.2f}")
            #     print(f"[THRESHOLD RESET] Updated profit threshold to initial budget: {profit_threshold:.2f}")
                
            #     consecutive_hold_count = 0
        else:
            consecutive_hold_count = 0
            buy_amount = 0
            quantity = 0
            value_usd_cost = 0
            fee = 0

        if reason:
            action = f"Overwrite LLM Decision to HOLD: {reason}"
            buy_amount = 0
            quantity = 0
            value_usd_cost = 0
            fee = 0

        btc_value_usd = portfolio['btc'] * current_price
        total_portfolio_value = btc_value_usd + portfolio['usdt']

        trade_record = {
            'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
            'Type': action if action != 'PROFIT' else 'PROFIT',
            'Open': row['open'],
            'Close': row['close'],
            'Quantity': quantity if action != 'PROFIT' else 0,
            'Buy USD Amount': buy_amount if action == 'BUY' else 0,
            'Value USD (Cost)': value_usd_cost,
            'BTC BALANCE': portfolio['btc'],
            'BTC VALUE USD': btc_value_usd,
            'Total Portfolio Value': total_portfolio_value,
            'USD BALANCE': portfolio['usdt'],
            'USD PROFIT': portfolio['usd_profit'],
            'PROFIT THRESHOLD': profit_threshold,
            'Profit Extract Amount': profit_amount if action == 'PROFIT' else 0  # <-- Added column
        }
        trade_log.append(trade_record)
        pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

if __name__ == "__main__":
    print("Running in backtest mode...")
    asyncio.run(run_backtest())
    print("Backtest completed.")
    plot_trade_log()