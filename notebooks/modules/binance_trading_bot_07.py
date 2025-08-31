# """
# Bitcoin Trading Agent Main Script
# Module Number: 7
# Purpose: Integrates all modules to run a 24/7 Bitcoin trading bot using Binance API.

# Inputs:
# - Market data from 01_data_collection
# - Configuration from 02_config_manager
# - Trades executed via 03_trade_executor
# - Strategies from 04_strategy_manager
# - LLM decisions from 05_llm_decision
# - Notifications via 06_notification_manager

# Outputs:
# - Continuous trading operation
# - Trade logs, notifications, and weekly reports

# Dependencies: asyncio, schedule, pandas, 01_data_collection, 02_config_manager, 03_trade_executor, 04_strategy_manager, 05_llm_decision, 06_notification_manager
# """

# import asyncio
# import schedule
# import time
# from datetime import datetime
# import pandas as pd
# from trade_executor_03 import initialize_binance_client, get_portfolio, execute_buy, execute_sell
# from strategy_manager_05 import manage_trades
# from llm_decision_04 import get_llm_decision
# # from notification_manager_06 import send_telegram_notification, schedule_weekly_report
# from data_collection import main as collect_data
# from config_manager import load_dotenv

# async def trading_loop():
#     """Main trading loop running every 30 minutes."""
#     # Initialize Binance client for trading
#     client = initialize_binance_client()
#     # Track active trades for stop-loss monitoring
#     active_trades = []

#     while True:
#         print(f"\n[INFO] Starting trading cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

#         # Collect market data (update: expects latest structure)
#         yahoo_df, current_price, indicators = await collect_data()
#         if yahoo_df is None or current_price is None:
#             print("[ERROR] Data collection failed. Retrying in 30 minutes.")
#             await asyncio.sleep(1800)
#             continue

#         # Get current portfolio balance (latest structure: {'btc': float, 'usdt': float})
#         portfolio = get_portfolio(client)
#         print(f"[INFO] Portfolio: {portfolio['btc']:.6f} BTC, ${portfolio['usdt']:,.2f} USDT")

#         # Get LLM trading suggestion (full context: market data, portfolio, trade history)
#         llm_suggestion = get_llm_decision(use_google_sheet=True)

#         # Generate trade decisions based on strategies (latest: expects full context)
#         decisions, active_trades = manage_trades(portfolio, active_trades, llm_suggestion)

#         # Execute trade decisions
#         for decision in decisions:
#             if decision['action'] == 'BUY' and portfolio['usdt'] >= decision['amount']:
#                 # Execute buy order if sufficient USD balance
#                 trade_record = execute_buy(client, decision['amount'], active_trades[-1]['entry_price'], decision['trade_type'])
#                 if trade_record:
#                     # send_telegram_notification(trade_record)  # Notification code commented out
#                     pass
#             elif decision['action'] == 'SELL' and portfolio['btc'] >= decision['quantity']:
#                 # Execute sell order if sufficient BTC balance
#                 trade_record = execute_sell(client, decision['quantity'], active_trades[-1]['entry_price'], decision['trade_type'])
#                 if trade_record:
#                     # send_telegram_notification(trade_record)  # Notification code commented out
#                     # Remove sold trade from active trades
#                     active_trades = [t for t in active_trades if t['quantity'] != decision['quantity']]

#         # Schedule weekly report (commented out)
#         # schedule_weekly_report(portfolio, current_price, '../data/trade_log.csv')
#         schedule.run_pending()

#         print(f"[INFO] Cycle complete. Sleeping for 30 minutes.")
#         await asyncio.sleep(1800)  # 30 minutes

# if __name__ == "__main__":
#     """Test 07_binance_trading_bot module with one real trading cycle."""
#     print("Testing 07_binance_trading_bot module with real trade...")
#     try:
#         # Run one real trading cycle
#         asyncio.run(trading_loop())
#         print("[TEST] One real trading cycle completed")
#     except Exception as e:
#         print(f"[ERROR] Exception during trading loop: {e}")




# ------------------------------ V2 Has support for Sim Trade last6 monts data --------------------------
import os
import sys
import argparse
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import ta
from strategy_manager_05 import manage_trades
from llm_decision_04 import get_llm_decision
from trade_executor_03 import execute_buy, execute_sell, log_trade  # <-- Import logging and trade functions

def refresh_config():
    import subprocess
    result = subprocess.run([sys.executable, "config_manager_02.py"], cwd=os.path.dirname(__file__))
    if result.returncode != 0:
        sys.exit(1)

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
    return config

async def run_backtest():
    df = pd.read_excel('btc_hourly_yahoo_binance_6mo.xlsx')
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', inplace=True)
    df['close'] = df['binance_close'].fillna(df['yahoo_close'])
    df['open'] = df['binance_open'].fillna(df['yahoo_open'])
    df['high'] = df['binance_high'].fillna(df['yahoo_high'])
    df['low'] = df['binance_low'].fillna(df['yahoo_low'])
    df['volume'] = df['binance_volume'].fillna(df['yahoo_volume'])
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
    pd.DataFrame(columns=['type', 'price', 'amount', 'btc', 'usdt', 'timestamp', 'portfolio_value', 'daily_pnl']).to_csv(trade_log_path, index=False)
    portfolio_history = []
    daily_pnl_log = []

    prev_day = None
    prev_day_value = None

    for i, row in df.iterrows():
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
        # Generate markdown for current hour for LLM (simulate live mode input)
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
        temp_md_path = "temp_bitcoin_data.md"
        with open(temp_md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        llm_suggestion = get_llm_decision(md_path=temp_md_path, use_google_sheet=False)
        decisions, active_trades = manage_trades(portfolio, active_trades, llm_suggestion)
        for decision in decisions:
            if decision['action'] == 'BUY' and portfolio['usdt'] >= decision['amount']:
                btc_bought = decision['amount'] / current_price
                portfolio['btc'] += btc_bought
                portfolio['usdt'] -= decision['amount']
                portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
                trade_record = {
                    'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': 'BUY',
                    'trade_type': decision.get('trade_type', 'BACKTEST_BUY'),
                    'price': current_price,
                    'quantity': btc_bought,
                    'amount_usd': decision['amount'],
                    'btc_balance': portfolio['btc'],
                    'btc_value_usd': portfolio['btc'] * current_price,
                    'profit_loss_usd': '',  # Not applicable for buy
                }
                await log_trade(trade_record)  # <-- Log to CSV and GSheet
                trade_log.append(trade_record)
            elif decision['action'] == 'SELL' and portfolio['btc'] >= decision['quantity']:
                portfolio['btc'] -= decision['quantity']
                portfolio['usdt'] += decision['quantity'] * current_price
                portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
                trade_record = {
                    'timestamp': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': 'SELL',
                    'trade_type': decision.get('trade_type', 'BACKTEST_SELL'),
                    'price': current_price,
                    'quantity': decision['quantity'],
                    'amount_usd': decision['quantity'] * current_price,
                    'btc_balance': portfolio['btc'],
                    'btc_value_usd': portfolio['btc'] * current_price,
                    'profit_loss_usd': '',  # You can add P&L logic here if needed
                }
                await log_trade(trade_record)  # <-- Log to CSV and GSheet
                trade_log.append(trade_record)
        portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
        portfolio_history.append({'date': current_date, 'value': portfolio_value})

        # Daily P&L calculation
        day = current_date.date()
        if prev_day is None:
            prev_day = day
            prev_day_value = portfolio_value
        if day != prev_day:
            daily_pnl = portfolio_value - prev_day_value
            daily_pnl_log.append({'date': prev_day, 'daily_pnl': daily_pnl, 'portfolio_value': prev_day_value})
            prev_day = day
            prev_day_value = portfolio_value

    # Final day P&L
    if prev_day is not None:
        daily_pnl = portfolio_value - prev_day_value
        daily_pnl_log.append({'date': prev_day, 'daily_pnl': daily_pnl, 'portfolio_value': portfolio_value})

    # Fill daily_pnl for each trade
    for trade in trade_log:
        trade_day = datetime.strptime(trade['timestamp'], '%Y-%m-%d %H:%M:%S').date()
        trade['daily_pnl'] = next((d['daily_pnl'] for d in daily_pnl_log if d['date'] == trade_day), None)

    pd.DataFrame(trade_log).to_csv(trade_log_path, index=False)
    daily_pnl_df = pd.DataFrame(daily_pnl_log)
    portfolio_df = pd.DataFrame(portfolio_history)
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

    # Plot portfolio value and daily P&L
    plt.figure(figsize=(14, 6))
    plt.subplot(2, 1, 1)
    plt.plot(portfolio_df['date'], portfolio_df['value'], label='Portfolio Value')
    plt.title('Portfolio Value Over Time')
    plt.ylabel('Value (USD)')
    plt.legend()
    plt.subplot(2, 1, 2)
    plt.bar(daily_pnl_df['date'], daily_pnl_df['daily_pnl'], label='Daily P&L')
    plt.title('Daily Profit/Loss')
    plt.ylabel('Daily P&L (USD)')
    plt.xlabel('Date')
    plt.legend()
    plt.tight_layout()
    plt.show()

    if os.path.exists(temp_md_path):
        os.remove(temp_md_path)

if __name__ == "__main__":
    refresh_config()
    print("Running in backtest mode...")
    asyncio.run(run_backtest())
    print("Backtest completed.")