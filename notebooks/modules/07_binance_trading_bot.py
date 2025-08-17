"""
Bitcoin Trading Agent Main Script
Module Number: 7
Purpose: Integrates all modules to run a 24/7 Bitcoin trading bot using Binance API.

Inputs:
- Market data from 01_data_collection
- Configuration from 02_config_manager
- Trades executed via 03_trade_executor
- Strategies from 04_strategy_manager
- LLM decisions from 05_llm_decision
- Notifications via 06_notification_manager

Outputs:
- Continuous trading operation
- Trade logs, notifications, and weekly reports

Dependencies: asyncio, schedule, pandas, 01_data_collection, 02_config_manager, 03_trade_executor, 04_strategy_manager, 05_llm_decision, 06_notification_manager
"""

import asyncio
import schedule
import time
from datetime import datetime
import pandas as pd
from trade_executor import initialize_binance_client, get_portfolio, execute_buy, execute_sell
from strategy_manager import manage_trades
from llm_decision import get_llm_decision
from notification_manager import send_telegram_notification, schedule_weekly_report
from data_collection import main as collect_data
from config_manager import load_dotenv

async def trading_loop():
    """Main trading loop running every 30 minutes."""
    # Initialize Binance client for trading
    client = initialize_binance_client()
    # Track active trades for stop-loss monitoring
    active_trades = []
    
    while True:
        print(f"\n[INFO] Starting trading cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Collect market data
        yahoo_df, current_price, indicators = await collect_data()
        if yahoo_df is None or current_price is None:
            print("[ERROR] Data collection failed. Retrying in 30 minutes.")
            await asyncio.sleep(1800)
            continue
        
        # Get current portfolio balance
        portfolio = get_portfolio(client)
        print(f"[INFO] Portfolio: {portfolio['btc']:.6f} BTC, ${portfolio['usdt']:,.2f} USDT")
        
        # Get LLM trading suggestion
        llm_suggestion = get_llm_decision(yahoo_df, current_price, indicators)
        
        # Generate trade decisions based on strategies
        decisions, active_trades = manage_trades(yahoo_df, current_price, portfolio, active_trades, llm_suggestion)
        
        # Execute trade decisions
        for decision in decisions:
            if decision['action'] == 'BUY' and portfolio['usdt'] >= decision['amount']:
                # Execute buy order if sufficient USD balance
                trade_record = execute_buy(client, decision['amount'], current_price, decision['trade_type'])
                if trade_record:
                    send_telegram_notification(trade_record)
            elif decision['action'] == 'SELL' and portfolio['btc'] >= decision['quantity']:
                # Execute sell order if sufficient BTC balance
                trade_record = execute_sell(client, decision['quantity'], current_price, decision['trade_type'])
                if trade_record:
                    send_telegram_notification(trade_record)
                    # Remove sold trade from active trades
                    active_trades = [t for t in active_trades if t['quantity'] != decision['quantity']]
        
        # Schedule weekly report
        schedule_weekly_report(portfolio, current_price, '../data/trade_log.csv')
        schedule.run_pending()
        
        print(f"[INFO] Cycle complete. Sleeping for 30 minutes.")
        await asyncio.sleep(1800)  # 30 minutes

if __name__ == "__main__":
    """Test 07_binance_trading_bot module with one real trading cycle."""
    print("Testing 07_binance_trading_bot module with real trade...")
    try:
        # Run one real trading cycle
        asyncio.run(trading_loop())
        print("[TEST] One real trading cycle completed")
    except Exception as e:
        print(f"[TEST ERROR] {e}")