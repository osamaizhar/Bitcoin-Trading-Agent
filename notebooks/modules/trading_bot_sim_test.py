# -------------------- v3 Trade duration configs ---------------------------------------------


# import os
# import sys
# import asyncio
# import pandas as pd
# import matplotlib.pyplot as plt
# from datetime import datetime, timedelta
# import ta
# import json
# from strategy_manager_05 import manage_trades
# from llm_decision_04 import get_llm_decision
# from trade_executor_03 import log_trade_to_google_sheet  # Google Sheets logging

# # ---- EDIT THESE SETTINGS TO CHANGE INTERVAL AND DURATION ----
# TRADE_INTERVAL_HOURS = 1      # Set to 1 for hourly, 24 for daily, etc.

# # Supported options: "1 day", "2 days", "10 days", "1 week", "2 weeks", "1 month", "2 months"
# TRADE_DURATION = "2 days"     # <--- Change this to your desired duration
# # -------------------------------------------------------------

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
#         # Default to 1 week if not recognized
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

# def log_trade(trade_record, trade_log, trade_log_path):
#     trade_log.append(trade_record)
#     pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

# async def run_backtest():
#     df = pd.read_excel('btc_hourly_yahoo_binance_6mo.xlsx')
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)
#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])
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

#     # --- Interval and duration logic ---
#     subsample = TRADE_INTERVAL_HOURS
#     end_date = df['date'].max()
#     duration = parse_duration(TRADE_DURATION)
#     start_date = end_date - duration
#     df_test = df[df['date'] >= start_date]
#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")

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
#         temp_md_path = "temp_bitcoin_data.md"
#         with open(temp_md_path, "w", encoding="utf-8") as f:
#             f.write(md_content)

#         llm_suggestion = get_llm_decision(
#             md_path=temp_md_path,
#             portfolio=portfolio,
#             trade_history=trade_log[-10:]
#         )
#         decisions, active_trades = manage_trades(portfolio, active_trades, llm_suggestion)
#         print(f"[INFO] Decisions made: {decisions}\n Active trades: {active_trades}")
#         # Log all actions including HOLD
#         for decision in decisions:
#             if decision['action'] == 'BUY' and portfolio['usdt'] >= decision['amount']:
#                 btc_bought = decision['amount'] / current_price
#                 portfolio['btc'] += btc_bought
#                 portfolio['usdt'] -= decision['amount']
#                 portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#                 trade_record = {
#                     'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                     'type': 'BUY',
#                     'trade_type': decision.get('trade_type', 'BACKTEST_BUY'),
#                     'price': current_price,
#                     'quantity': btc_bought,
#                     'amount_usd': decision['amount'],
#                     'btc_balance': portfolio['btc'],
#                     'btc_value_usd': portfolio['btc'] * current_price,
#                     'portfolio_value': portfolio['btc'] * current_price + portfolio['usdt'],
#                     'usdt_balance': portfolio['usdt'],
#                     'profit_loss_usd': ''
#                 }
#                 log_trade(trade_record, trade_log, trade_log_path)
#                 await log_trade_to_google_sheet(trade_record)
#             elif decision['action'] == 'SELL' and portfolio['btc'] >= decision['quantity']:
#                 portfolio['btc'] -= decision['quantity']
#                 portfolio['usdt'] += decision['quantity'] * current_price
#                 portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#                 trade_record = {
#                     'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                     'type': 'SELL',
#                     'trade_type': decision.get('trade_type', 'BACKTEST_SELL'),
#                     'price': current_price,
#                     'quantity': decision['quantity'],
#                     'amount_usd': decision['quantity'] * current_price,
#                     'btc_balance': portfolio['btc'],
#                     'btc_value_usd': portfolio['btc'] * current_price,
#                     'portfolio_value': portfolio_value,
#                     'usdt_balance': portfolio['usdt'],
#                     'profit_loss_usd': ''
#                 }
#                 log_trade(trade_record, trade_log, trade_log_path)
#                 await log_trade_to_google_sheet(trade_record)
#                 active_trades = [t for t in active_trades if t.get('quantity', None) != decision['quantity']]
#             elif decision['action'] == 'HOLD':
#                 portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#                 trade_record = {
#                     'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                     'type': 'HOLD',
#                     'trade_type': decision.get('trade_type', 'BACKTEST_HOLD'),
#                     'price': current_price,
#                     'quantity': 0,
#                     'amount_usd': 0,
#                     'btc_balance': portfolio['btc'],
#                     'btc_value_usd': portfolio['btc'] * current_price,
#                     'portfolio_value': portfolio_value,
#                     'usdt_balance': portfolio['usdt'],
#                     'profit_loss_usd': ''
#                 }
#                 log_trade(trade_record, trade_log, trade_log_path)
#                 await log_trade_to_google_sheet(trade_record)
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
#         trade_day = datetime.strptime(trade['timestamp'], '%Y-%m-%d %H:%M:%S').date()
#         trade['daily_pnl'] = next((d['daily_pnl'] for d in daily_pnl_log if d['date'] == trade_day), None)

#     pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)
#     daily_pnl_df = pd.DataFrame(daily_pnl_log)
#     portfolio_df = pd.DataFrame(portfolio_history)
#     initial_value = portfolio_df['value'].iloc[0]
#     final_value = portfolio_df['value'].iloc[-1]
#     total_return = (final_value - initial_value) / initial_value * 100
#     num_trades = len(trade_log)
#     print("\n[BACKTEST SUMMARY]")
#     print(f"Initial Value: ${initial_value:,.2f}")
#     print(f"Final Value: ${final_value:,.2f}")
#     print(f"Total Return: {total_return:.2f}%")
#     print(f"Number of Trades: {num_trades}")
#     print(f"Max Portfolio Value: ${portfolio_df['value'].max():,.2f}")
#     print(f"Min Portfolio Value: ${portfolio_df['value'].min():,.2f}")

#     plt.figure(figsize=(14, 6))
#     plt.subplot(2, 1, 1)
#     plt.plot(portfolio_df['date'], portfolio_df['value'], label='Portfolio Value')
#     plt.title('Portfolio Value Over Time')
#     plt.ylabel('Value (USD)')
#     plt.legend()
#     plt.subplot(2, 1, 2)
#     plt.bar(daily_pnl_df['date'], daily_pnl_df['daily_pnl'], label='Daily P&L')
#     plt.title('Daily Profit/Loss')
#     plt.ylabel('Daily P&L (USD)')
#     plt.xlabel('Date')
#     plt.legend()
#     plt.tight_layout()
#     plt.show()

#     if os.path.exists(temp_md_path):
#         os.remove(temp_md_path)

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     asyncio.run(run_backtest())
#     print("Backtest completed.")




# --------------------------- Hold Decision Tracking added ----------------------------------------------------------

# import os
# import sys
# import asyncio
# import pandas as pd
# import matplotlib.pyplot as plt
# from datetime import datetime, timedelta
# import ta
# import json
# from strategy_manager_05 import manage_trades
# from llm_decision_04 import get_llm_decision
# from trade_executor_03 import log_trade_to_google_sheet  # Google Sheets logging

# # ---- EDIT THESE SETTINGS TO CHANGE INTERVAL AND DURATION ----
# TRADE_INTERVAL_HOURS = 1      # Set to 1 for hourly, 24 for daily, etc.

# # Supported options: "1 day", "2 days", "10 days", "1 week", "2 weeks", "1 month", "2 months"
# TRADE_DURATION = "1 week"     # <--- Change this to your desired duration
# # -------------------------------------------------------------

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
#         # Default to 1 week if not recognized
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

# def log_trade(trade_record, trade_log, trade_log_path):
#     trade_log.append(trade_record)
#     pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

# async def run_backtest():
#     df = pd.read_excel('btc_hourly_yahoo_binance_6mo.xlsx')
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)
#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])
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

#     # --- Interval and duration logic ---
#     subsample = TRADE_INTERVAL_HOURS
#     end_date = df['date'].max()
#     duration = parse_duration(TRADE_DURATION)
#     start_date = end_date - duration
#     df_test = df[df['date'] >= start_date]
#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")

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
#         temp_md_path = "temp_bitcoin_data.md"
#         with open(temp_md_path, "w", encoding="utf-8") as f:
#             f.write(md_content)

#         llm_suggestion = get_llm_decision(
#             md_path=temp_md_path,
#             portfolio=portfolio,
#             trade_history=trade_log[-10:]
#         )
#         decisions, active_trades = manage_trades(portfolio, active_trades, llm_suggestion)
#         print(f"[INFO] Decisions made: {decisions}\n Active trades: {active_trades}")
#         # Log all actions including HOLD
#         for decision in decisions:
#             if decision['action'] == 'BUY' and portfolio['usdt'] >= decision['amount']:
#                 btc_bought = decision['amount'] / current_price
#                 portfolio['btc'] += btc_bought
#                 portfolio['usdt'] -= decision['amount']
#                 portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#                 trade_record = {
#                     'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                     'type': 'BUY',
#                     'trade_type': decision.get('trade_type', 'BACKTEST_BUY'),
#                     'price': current_price,
#                     'quantity': btc_bought,
#                     'amount_usd': decision['amount'],
#                     'btc_balance': portfolio['btc'],
#                     'btc_value_usd': portfolio['btc'] * current_price,
#                     'portfolio_value': portfolio['btc'] * current_price + portfolio['usdt'],
#                     'usdt_balance': portfolio['usdt'],
#                     'profit_loss_usd': ''
#                 }
#                 log_trade(trade_record, trade_log, trade_log_path)
#                 await log_trade_to_google_sheet(trade_record)
#             elif decision['action'] == 'SELL' and portfolio['btc'] >= decision['quantity']:
#                 portfolio['btc'] -= decision['quantity']
#                 portfolio['usdt'] += decision['quantity'] * current_price
#                 portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#                 trade_record = {
#                     'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                     'type': 'SELL',
#                     'trade_type': decision.get('trade_type', 'BACKTEST_SELL'),
#                     'price': current_price,
#                     'quantity': decision['quantity'],
#                     'amount_usd': decision['quantity'] * current_price,
#                     'btc_balance': portfolio['btc'],
#                     'btc_value_usd': portfolio['btc'] * current_price,
#                     'portfolio_value': portfolio_value,
#                     'usdt_balance': portfolio['usdt'],
#                     'profit_loss_usd': ''
#                 }
#                 log_trade(trade_record, trade_log, trade_log_path)
#                 await log_trade_to_google_sheet(trade_record)
#                 active_trades = [t for t in active_trades if t.get('quantity', None) != decision['quantity']]
#             elif decision['action'] == 'HOLD':
#                 portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#                 trade_record = {
#                     'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                     'type': 'HOLD',
#                     'trade_type': decision.get('trade_type', 'BACKTEST_HOLD'),
#                     'price': current_price,
#                     'quantity': 0,
#                     'amount_usd': 0,
#                     'btc_balance': portfolio['btc'],
#                     'btc_value_usd': portfolio['btc'] * current_price,
#                     'portfolio_value': portfolio_value,
#                     'usdt_balance': portfolio['usdt'],
#                     'profit_loss_usd': ''
#                 }
#                 log_trade(trade_record, trade_log, trade_log_path)
#                 await log_trade_to_google_sheet(trade_record)
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
#         trade_day = datetime.strptime(trade['timestamp'], '%Y-%m-%d %H:%M:%S').date()
#         trade['daily_pnl'] = next((d['daily_pnl'] for d in daily_pnl_log if d['date'] == trade_day), None)

#     pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)
#     daily_pnl_df = pd.DataFrame(daily_pnl_log)
#     portfolio_df = pd.DataFrame(portfolio_history)
#     initial_value = portfolio_df['value'].iloc[0]
#     final_value = portfolio_df['value'].iloc[-1]
#     total_return = (final_value - initial_value) / initial_value * 100
#     num_trades = len(trade_log)
#     print("\n[BACKTEST SUMMARY]")
#     print(f"Initial Value: ${initial_value:,.2f}")
#     print(f"Final Value: ${final_value:,.2f}")
#     print(f"Total Return: {total_return:.2f}%")
#     print(f"Number of Trades: {num_trades}")
#     print(f"Max Portfolio Value: ${portfolio_df['value'].max():,.2f}")
#     print(f"Min Portfolio Value: ${portfolio_df['value'].min():,.2f}")

#     plt.figure(figsize=(14, 6))
#     plt.subplot(2, 1, 1)
#     plt.plot(portfolio_df['date'], portfolio_df['value'], label='Portfolio Value')
#     plt.title('Portfolio Value Over Time')
#     plt.ylabel('Value (USD)')
#     plt.legend()
#     plt.subplot(2, 1, 2)
#     plt.bar(daily_pnl_df['date'], daily_pnl_df['daily_pnl'], label='Daily P&L')
#     plt.title('Daily Profit/Loss')
#     plt.ylabel('Daily P&L (USD)')
#     plt.xlabel('Date')
#     plt.legend()
#     plt.tight_layout()
#     plt.show()

#     if os.path.exists(temp_md_path):
#         os.remove(temp_md_path)

# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     asyncio.run(run_backtest())
#     print("Backtest completed.")



# ----------------------- Based on new llm_decision_strategy_05.py code -----------------------------
# import os
# import sys
# import asyncio
# import pandas as pd
# import matplotlib.pyplot as plt
# from datetime import datetime, timedelta
# import ta
# import json
# # Updated import to use the combined module
# from llm_decision_strategy_05 import manage_trades, get_llm_decision
# from trade_executor_03 import log_trade_to_google_sheet  # Google Sheets logging

# # ---- EDIT THESE SETTINGS TO CHANGE INTERVAL AND DURATION ----
# TRADE_INTERVAL_HOURS = 1      # Set to 1 for hourly, 24 for daily, etc.

# # Supported options: "1 day", "2 days", "10 days", "1 week", "2 weeks", "1 month", "2 months"
# TRADE_DURATION = "1 week"     # <--- Change this to your desired duration
# # -------------------------------------------------------------

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
#         # Default to 1 week if not recognized
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

# def log_trade(trade_record, trade_log, trade_log_path):
#     # Rename fields to match the desired spreadsheet column headers
#     renamed_record = {
#         'Timestamp': trade_record['timestamp'],
#         'Type': trade_record['type'],
#         'Price BTC': trade_record['price'],
#         'Quantity': trade_record['quantity'],
#         'Value USD (Cost)': trade_record['amount_usd'],
#         'BTC BALANCE': trade_record['btc_balance'],
#         'BTC VALUE USD': trade_record['btc_value_usd'],
#         'Total Portfolio Value': trade_record['portfolio_value'],
#         'USD BALANCE': trade_record['usdt_balance'],
#         'PROFIT / LOSS USD': trade_record['profit_loss_usd']
#     }
#     trade_log.append(renamed_record)
#     pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

# async def run_backtest():
#     # Load data from Excel file
#     data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
#     if not os.path.exists(data_file):
#         print(f"ERROR: Data file '{data_file}' not found!")
#         return
    
#     df = pd.read_excel(data_file)
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)
    
#     # Print date range info
#     print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")
    
#     # Process BTC price data
#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open'] = df['binance_open'].fillna(df['yahoo_open'])
#     df['high'] = df['binance_high'].fillna(df['yahoo_high'])
#     df['low'] = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])
    
#     # Calculate technical indicators
#     df['atr_14'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
#     df['rsi_14'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
#     df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
#     df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
#     macd_indicator = ta.trend.MACD(df['close'])
#     df['macd'] = macd_indicator.macd()
#     df['macd_signal'] = macd_indicator.macd_signal()
    
#     # Load trading configuration
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

#     # --- Interval and duration logic ---
#     subsample = TRADE_INTERVAL_HOURS
#     end_date = df['date'].max()
#     duration = parse_duration(TRADE_DURATION)
#     start_date = end_date - duration
    
#     # Print trading period info
#     print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
#     # Filter data based on date range
#     df_test = df[df['date'] >= start_date]
    
#     if len(df_test) == 0:
#         print(f"[ERROR] No data found for the selected period!")
#         return
        
#     # Apply the interval subsampling
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
#         temp_md_path = "temp_bitcoin_data.md"
#         with open(temp_md_path, "w", encoding="utf-8") as f:
#             f.write(md_content)
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

import os
import sys
import asyncio
import pandas as pd
import functools
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
import ta
import json
from llm_decision_strategy_05 import manage_trades, get_llm_decision

# ---- EDIT THESE SETTINGS TO CHANGE INTERVAL AND DURATION ----
TRADE_INTERVAL_HOURS = 1      # Set to 1 for hourly, 24 for daily, etc.
TRADE_DURATION = "1 week"     # <--- Change this to your desired duration

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

def generate_md_report(current_date, row, indicators, portfolio, current_price):
    md_content = f"""
# Complete Bitcoin Data Collection Report

## Yahoo Finance Data

| Date | Open | High | Low | Close | Volume |
|------|------|------|-----|-------|--------|
| {current_date.strftime('%Y-%m-%d %H:%M:%S')} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,.0f} |

### Technical Indicators (Current Values)

- **ATR (14)**: ${indicators['atr_14']:,.2f}
- **RSI (14)**: {indicators['rsi_14']:.2f}
- **SMA 20**: ${indicators['sma_20']:,.2f}
- **SMA 50**: ${indicators['sma_50']:,.2f}
- **MACD**: {indicators['macd']:.2f}
- **MACD Signal**: {indicators['macd_signal']:.2f}

## Portfolio Status

- BTC: {portfolio['btc']}
- USDT: {portfolio['usdt']}
- Portfolio Value: {portfolio['btc'] * current_price + portfolio['usdt']}
"""
    return md_content

def log_trade(trade_record, trade_log):
    trade_log.append(trade_record)

async def run_backtest():
    # Use CSV for faster loading if available
    data_file = 'btc_hourly_yahoo_binance_6mo.csv'
    if not os.path.exists(data_file):
        data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
    if not os.path.exists(data_file):
        print(f"ERROR: Data file '{data_file}' not found!")
        return

    # Load data
    if data_file.endswith('.csv'):
        df = pd.read_csv(data_file)
    else:
        df = pd.read_excel(data_file)
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', inplace=True)

    print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

    # Fill price columns
    df['close'] = df['binance_close'].fillna(df['yahoo_close'])
    df['open'] = df['binance_open'].fillna(df['yahoo_open'])
    df['high'] = df['binance_high'].fillna(df['yahoo_high'])
    df['low'] = df['binance_low'].fillna(df['yahoo_low'])
    df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])

    # Precompute indicators (outside loop)
    df['atr_14'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
    df['rsi_14'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
    df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
    macd_indicator = ta.trend.MACD(df['close'])
    df['macd'] = macd_indicator.macd()
    df['macd_signal'] = macd_indicator.macd_signal()

    config = load_config()
    budget = config.get('budget', 10000)
    portfolio = {'btc': 0.0, 'usdt': budget}
    active_trades = []
    trade_log = []
    trade_log_path = "backtest_trade_log.csv"
    if os.path.exists(trade_log_path):
        os.remove(trade_log_path)
    portfolio_history = []
    daily_pnl_log = []

    prev_day = None
    prev_day_value = None

    subsample = TRADE_INTERVAL_HOURS
    end_date = df['date'].max()
    duration = parse_duration(TRADE_DURATION)
    start_date = end_date - duration

    print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

    df_test = df[df['date'] >= start_date]
    if len(df_test) == 0:
        print(f"[ERROR] No data found for the selected period!")
        return

    df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
    print(f"[INFO] Running backtest on {len(df_subsampled)} data points (interval: {subsample}h, period: {TRADE_DURATION})")

    decision_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}
    for i, row in df_subsampled.iterrows():
        if pd.isna(row['close']):
            continue
        current_date = row['date']
        current_price = row['close']
        indicators = {
            'atr_14': row['atr_14'],
            'rsi_14': row['rsi_14'],
            'sma_20': row['sma_20'],
            'sma_50': row['sma_50'],
            'macd': row['macd'],
            'macd_signal': row['macd_signal']
        }
        md_content = generate_md_report(current_date, row, indicators, portfolio, current_price)
        context = {
            'md_content': md_content,
            'portfolio': portfolio,
            'trade_history': trade_log[-10:]
        }
        # llm_suggestion = get_llm_decision({
        #     'md_content': md_content,
        #     'portfolio': portfolio,
        #     'trade_history': trade_log[-10:]
        # })
        # print(f"LLM Suggestion: {llm_suggestion}")
        decision, active_trades = manage_trades(portfolio, active_trades, llm_suggestion)

        # Print only the decision and increment count
        print(f"Trade {i+1}: Decision = {decision['action']}")
        if decision['action'] in decision_counts:
            decision_counts[decision['action']] += 1

        # Log only to memory, write to CSV every 10 trades
        if decision and decision['action'] == 'BUY' and portfolio['usdt'] >= decision.get('amount', 0):
            btc_bought = decision['amount'] / current_price
            portfolio['btc'] += btc_bought
            portfolio['usdt'] -= decision['amount']
            portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
            trade_record = {
                'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                'Type': 'BUY',
                'Price BTC': current_price,
                'Quantity': btc_bought,
                'Value USD (Cost)': decision['amount'],
                'BTC BALANCE': portfolio['btc'],
                'BTC VALUE USD': portfolio['btc'] * current_price,
                'Total Portfolio Value': portfolio['btc'] * current_price + portfolio['usdt'],
                'USD BALANCE': portfolio['usdt'],
                'PROFIT / LOSS USD': ''
            }
            log_trade(trade_record, trade_log)
        elif decision and decision['action'] == 'SELL' and portfolio['btc'] >= decision.get('quantity', 0):
            portfolio['btc'] -= decision['quantity']
            portfolio['usdt'] += decision['quantity'] * current_price
            portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
            trade_record = {
                'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                'Type': 'SELL',
                'Price BTC': current_price,
                'Quantity': decision['quantity'],
                'Value USD (Cost)': decision['quantity'] * current_price,
                'BTC BALANCE': portfolio['btc'],
                'BTC VALUE USD': portfolio['btc'] * current_price,
                'Total Portfolio Value': portfolio_value,
                'USD BALANCE': portfolio['usdt'],
                'PROFIT / LOSS USD': ''
            }
            log_trade(trade_record, trade_log)
            active_trades = [t for t in active_trades if t.get('quantity', None) != decision['quantity']]
        elif decision and decision['action'] == 'HOLD':
            portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
            trade_record = {
                'Timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                'Type': 'HOLD',
                'Price BTC': current_price,
                'Quantity': 0,
                'Value USD (Cost)': 0,
                'BTC BALANCE': portfolio['btc'],
                'BTC VALUE USD': portfolio['btc'] * current_price,
                'Total Portfolio Value': portfolio_value,
                'USD BALANCE': portfolio['usdt'],
                'PROFIT / LOSS USD': ''
            }
            log_trade(trade_record, trade_log)

        # Write to CSV every 10 trades
        if len(trade_log) % 10 == 0 and len(trade_log) > 0:
            pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

        portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
        portfolio_history.append({'date': current_date, 'value': portfolio_value})

        day = current_date.date()
        if prev_day is None:
            prev_day = day
            prev_day_value = portfolio_value
        if day != prev_day:
            daily_pnl = portfolio_value - prev_day_value
            daily_pnl_log.append({'date': prev_day, 'daily_pnl': daily_pnl, 'portfolio_value': prev_day_value})
            prev_day = day
            prev_day_value = portfolio_value

    if prev_day is not None:
        daily_pnl = portfolio_value - prev_day_value
        daily_pnl_log.append({'date': prev_day, 'daily_pnl': daily_pnl, 'portfolio_value': portfolio_value})

    for trade in trade_log:
        trade_day = datetime.strptime(trade['Timestamp'], '%Y-%m-%d %H:%M:%S').date()
        trade['PROFIT / LOSS USD'] = next((d['daily_pnl'] for d in daily_pnl_log if d['date'] == trade_day), None)

    # Write any remaining trades at the end
    if len(trade_log) % 10 != 0:
        pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)
    daily_pnl_df = pd.DataFrame(daily_pnl_log)
    portfolio_df = pd.DataFrame(portfolio_history)

    print("\nDecision Counts:")
    for k, v in decision_counts.items():
        print(f"{k}: {v}")

    if len(portfolio_df) > 0:
        initial_value = portfolio_df['value'].iloc[0]
        final_value = portfolio_df['value'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value * 100
        num_trades = len(trade_log)

        print("\n[BACKTEST SUMMARY]")
        print(f"Initial Value: ${initial_value:,.2f}")
        print(f"Final Value: ${final_value:,.2f}")
        print(f"Total Return: {total_return:.2f}%")
        print(f"Number of Trades: {num_trades}")
        print(f"Max Portfolio Value: ${portfolio_df['value'].max():,.2f}")
        print(f"Min Portfolio Value: ${portfolio_df['value'].min():,.2f}")

        plt.figure(figsize=(14, 6))
        plt.subplot(2, 1, 1)
        plt.plot(portfolio_df['date'], portfolio_df['value'], label='Portfolio Value')
        plt.title('Portfolio Value Over Time')
        plt.ylabel('Value (USD)')
        plt.legend()

        if len(daily_pnl_df) > 0:
            plt.subplot(2, 1, 2)
            plt.bar(daily_pnl_df['date'], daily_pnl_df['daily_pnl'], label='Daily P&L')
            plt.title('Daily Profit/Loss')
            plt.ylabel('Daily P&L (USD)')
            plt.xlabel('Date')
            plt.legend()

        plt.tight_layout()
        plt.show()
    else:
        print("[ERROR] No portfolio data generated during backtest!")

if __name__ == "__main__":
    print("Running in backtest mode...")
    asyncio.run(run_backtest())
    print("Backtest completed.")



# -------------------------------- removed manage_trades func ---------------------------------------------
# notebooks/modules/trading_bot_sim_test.py
# notebooks/modules/trading_bot_sim_test.py
# import os
# import sys
# import asyncio
# import pandas as pd
# import matplotlib.pyplot as plt
# from datetime import datetime, timedelta
# import time
# import ta
# import json
# from llm_decision_strategy_05 import get_llm_decision

# # -------------------------------------------------
# #  SETTINGS – change these to alter back‑test range
# # -------------------------------------------------
# TRADE_INTERVAL_HOURS = 1          # 1 = hourly, 24 = daily, etc.
# TRADE_DURATION = "1 week"         # e.g. "2 days", "1 month", …

# # -------------------------------------------------
# #  HELPER FUNCTIONS
# # -------------------------------------------------
# def parse_duration(duration_str: str) -> timedelta:
#     """Convert a human‑readable duration (e.g. “2 days”) to a timedelta."""
#     duration_str = duration_str.lower().strip()
#     if "day" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=n)
#     if "week" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(weeks=n)
#     if "month" in duration_str:
#         n = int(duration_str.split()[0])
#         return timedelta(days=30 * n)
#     # fallback – 1 week
#     return timedelta(weeks=1)


# def load_config() -> dict:
#     """Read `config.cfg` into a dict, converting booleans / numbers."""
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
#     """Create a tiny markdown snapshot for the LLM."""
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


# def log_trade(trade_record: dict, trade_log: list, trade_log_path: str):
#     """
#     Append the trade to the in‑memory list *and* write the single row to CSV.
#     The CSV header is written only once (when the file does not exist or is empty).
#     """
#     trade_log.append(trade_record)

#     df_new = pd.DataFrame([trade_record])
#     write_header = not os.path.exists(trade_log_path) or os.path.getsize(trade_log_path) == 0
#     df_new.to_csv(trade_log_path, mode='a', header=write_header, index=False)


# # -------------------------------------------------
# #  MAIN BACK‑TEST LOOP
# # -------------------------------------------------
# async def run_backtest():
#     # ---- 1️⃣ Load data (CSV preferred, fallback to Excel) ----
#     data_file = 'btc_hourly_yahoo_binance_6mo.csv'
#     if not os.path.exists(data_file):
#         data_file = 'btc_hourly_yahoo_binance_6mo.xlsx'
#     if not os.path.exists(data_file):
#         print(f"ERROR: Data file '{data_file}' not found!")
#         return

#     df = pd.read_csv(data_file) if data_file.endswith('.csv') else pd.read_excel(data_file)
#     df['date'] = pd.to_datetime(df['date'])
#     df.sort_values('date', inplace=True)

#     print(f"[INFO] Data range: {df['date'].min().strftime('%Y-%m-%d %H:%M:%S')} "
#           f"to {df['date'].max().strftime('%Y-%m-%d %H:%M:%S')}")

#     # ---- 2️⃣ Normalise price columns (Binance → Yahoo fallback) ----
#     df['close'] = df['binance_close'].fillna(df['yahoo_close'])
#     df['open']  = df['binance_open'].fillna(df['yahoo_open'])
#     df['high']  = df['binance_high'].fillna(df['yahoo_high'])
#     df['low']   = df['binance_low'].fillna(df['yahoo_low'])
#     df['volume']= df['binance_volume'].fillna(df['yahoo_volume'])

#     # ---- 3️⃣ Pre‑compute technical indicators (outside the loop) ----
#     df['atr_14'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
#     df['rsi_14'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
#     df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
#     df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
#     macd = ta.trend.MACD(df['close'])
#     df['macd'] = macd.macd()
#     df['macd_signal'] = macd.macd_signal()

#     # ---- 4️⃣ Load config & initialise structures ----
#     config = load_config()
#     budget = config.get('budget', 10000)
#     portfolio = {'btc': 0.0, 'usdt': budget}
#     trade_log = []                         # in‑memory list (optional)
#     trade_log_path = "backtest_trade_log.csv"
#     if os.path.exists(trade_log_path):
#         os.remove(trade_log_path)         # fresh file each run

#     portfolio_history = []
#     daily_pnl_log = []

#     prev_day = None
#     prev_day_value = None

#     # ---- 5️⃣ Determine back‑test window & subsample interval ----
#     subsample = TRADE_INTERVAL_HOURS
#     end_date = df['date'].max()
#     duration = parse_duration(TRADE_DURATION)
#     start_date = end_date - duration

#     print(f"[INFO] Trading period: {start_date.strftime('%Y-%m-%d %H:%M:%S')} "
#           f"to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")

#     df_test = df[df['date'] >= start_date]
#     if df_test.empty:
#         print("[ERROR] No data found for the selected period!")
#         return

#     df_subsampled = df_test.iloc[::subsample, :].reset_index(drop=True)
#     print(f"[INFO] Running backtest on {len(df_subsampled)} data points "
#           f"(interval: {subsample}h, period: {TRADE_DURATION})")

#     decision_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}

#     # ---- 6️⃣ Main loop – one row = one decision ----
#     for i, row in df_subsampled.iterrows():
#         if pd.isna(row['close']):
#             continue

#         trade_start = time.perf_counter()

#         current_date  = row['date']
#         current_price = row['close']
#         indicators = {
#             'atr_14'      : row['atr_14'],
#             'rsi_14'      : row['rsi_14'],
#             'sma_20'      : row['sma_20'],
#             'sma_50'      : row['sma_50'],
#             'macd'        : row['macd'],
#             'macd_signal' : row['macd_signal']
#         }

#         md_content = generate_md_report(
#             current_date, row, indicators, portfolio, current_price)

#         # Get LLM suggestion (expects a dict)
#         llm_suggestion = get_llm_decision({
#             'md_content'   : md_content,
#             'portfolio'    : portfolio,
#             'trade_history': trade_log[-10:]          # last 10 trades for context
#         })

#         trade_end = time.perf_counter()
#         trade_time = trade_end - trade_start

#         action = llm_suggestion.get('action', 'N/A')
#         print(f"Trade {i+1}: Decision = {action} (Time: {trade_time:.2f}s)")

#         if action in decision_counts:
#             decision_counts[action] += 1

#         # -------------------------------------------------
#         # 7️⃣ Apply decision & write trade immediately
#         # -------------------------------------------------
#         if action == 'BUY' and 'amount' in llm_suggestion and portfolio['usdt'] >= llm_suggestion['amount']:
#             btc_bought = llm_suggestion['amount'] / current_price
#             portfolio['btc'] += btc_bought
#             portfolio['usdt'] -= llm_suggestion['amount']

#             trade_record = {
#                 'Timestamp'          : current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'Type'               : 'BUY',
#                 'Price BTC'          : current_price,
#                 'Quantity'           : btc_bought,
#                 'Value USD (Cost)'   : llm_suggestion['amount'],
#                 'BTC BALANCE'        : portfolio['btc'],
#                 'BTC VALUE USD'      : portfolio['btc'] * current_price,
#                 'Total Portfolio Value': portfolio['btc'] * current_price + portfolio['usdt'],
#                 'USD BALANCE'        : portfolio['usdt'],
#                 'PROFIT / LOSS USD'  : ''           # will be filled after the run
#             }
#             log_trade(trade_record, trade_log, trade_log_path)

#         elif action == 'SELL' and 'quantity' in llm_suggestion and portfolio['btc'] >= llm_suggestion['quantity']:
#             portfolio['btc'] -= llm_suggestion['quantity']
#             portfolio['usdt'] += llm_suggestion['quantity'] * current_price

#             trade_record = {
#                 'Timestamp'          : current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'Type'               : 'SELL',
#                 'Price BTC'          : current_price,
#                 'Quantity'           : llm_suggestion['quantity'],
#                 'Value USD (Cost)'   : llm_suggestion['quantity'] * current_price,
#                 'BTC BALANCE'        : portfolio['btc'],
#                 'BTC VALUE USD'      : portfolio['btc'] * current_price,
#                 'Total Portfolio Value': portfolio['btc'] * current_price + portfolio['usdt'],
#                 'USD BALANCE'        : portfolio['usdt'],
#                 'PROFIT / LOSS USD'  : ''
#             }
#             log_trade(trade_record, trade_log, trade_log_path)

#         elif action == 'HOLD':
#             trade_record = {
#                 'Timestamp'          : current_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'Type'               : 'HOLD',
#                 'Price BTC'          : current_price,
#                 'Quantity'           : 0,
#                 'Value USD (Cost)'   : 0,
#                 'BTC BALANCE'        : portfolio['btc'],
#                 'BTC VALUE USD'      : portfolio['btc'] * current_price,
#                 'Total Portfolio Value': portfolio['btc'] * current_price + portfolio['usdt'],
#                 'USD BALANCE'        : portfolio['usdt'],
#                 'PROFIT / LOSS USD'  : ''
#             }
#             log_trade(trade_record, trade_log, trade_log_path)

#         # -------------------------------------------------
#         # 8️⃣ Portfolio & daily P&L tracking
#         # -------------------------------------------------
#         portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#         portfolio_history.append({'date': current_date, 'value': portfolio_value})

#         day = current_date.date()
#         if prev_day is None:
#             prev_day = day
#             prev_day_value = portfolio_value
#         elif day != prev_day:
#             daily_pnl = portfolio_value - prev_day_value
#             daily_pnl_log.append({
#                 'date'          : prev_day,
#                 'daily_pnl'     : daily_pnl,
#                 'portfolio_value': prev_day_value
#             })
#             prev_day = day
#             prev_day_value = portfolio_value

#     # -------------------------------------------------
#     # 9️⃣ Final day P&L & attach daily P&L to each trade
#     # -------------------------------------------------
#     if prev_day is not None:
#         daily_pnl = portfolio_value - prev_day_value
#         daily_pnl_log.append({
#             'date'          : prev_day,
#             'daily_pnl'     : daily_pnl,
#             'portfolio_value': portfolio_value
#         })

#     for trade in trade_log:
#         trade_day = datetime.strptime(trade['Timestamp'], '%Y-%m-%d %H:%M:%S').date()
#         trade['PROFIT / LOSS USD'] = next(
#             (d['daily_pnl'] for d in daily_pnl_log if d['date'] == trade_day), None)

#     # Overwrite once at the end to add the profit/loss column
#     pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)

#     # -------------------------------------------------
#     # 10️⃣ Summary statistics & plots
#     # -------------------------------------------------
#     daily_pnl_df = pd.DataFrame(daily_pnl_log)
#     portfolio_df = pd.DataFrame(portfolio_history)

#     print("\nDecision Counts:")
#     for k, v in decision_counts.items():
#         print(f"{k}: {v}")

#     if not portfolio_df.empty:
#         initial_value = portfolio_df['value'].iloc[0]
#         final_value   = portfolio_df['value'].iloc[-1]
#         total_return  = (final_value - initial_value) / initial_value * 100
#         num_trades    = len(trade_log)

#         print("\n[BACKTEST SUMMARY]")
#         print(f"Initial Value: ${initial_value:,.2f}")
#         print(f"Final Value:   ${final_value:,.2f}")
#         print(f"Total Return:  {total_return:.2f}%")
#         print(f"Number of Trades: {num_trades}")
#         print(f"Max Portfolio Value: ${portfolio_df['value'].max():,.2f}")
#         print(f"Min Portfolio Value: ${portfolio_df['value'].min():,.2f}")

#         plt.figure(figsize=(14, 6))

#         # Portfolio value over time
#         plt.subplot(2, 1, 1)
#         plt.plot(portfolio_df['date'], portfolio_df['value'], label='Portfolio Value')
#         plt.title('Portfolio Value Over Time')
#         plt.ylabel('Value (USD)')
#         plt.legend()

#         # Daily P&L bar chart
#         if not daily_pnl_df.empty:
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


# # -------------------------------------------------
# #  ENTRY POINT
# # -------------------------------------------------
# if __name__ == "__main__":
#     print("Running in backtest mode...")
#     asyncio.run(run_backtest())
#     print("Backtest completed.")