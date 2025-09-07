import os
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
