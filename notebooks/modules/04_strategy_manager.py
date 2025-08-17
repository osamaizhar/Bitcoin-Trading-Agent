"""
Strategy Manager Module for Bitcoin Trading Agent
Module Number: 4
Purpose: Implements trading strategies (DCA, ATR-based stop-loss, hybrid) and manages active trades.

Inputs:
- Market data from 01_data_collection (yahoo_df, indicators)
- Configuration parameters from 02_config_manager
- LLM suggestions from 05_llm_decision
- Current portfolio from 03_trade_executor

Outputs:
- Trade decisions (buy/sell) to be executed
- Active trade tracking with stop-loss levels
- Strategy performance metrics

Dependencies: pandas, numpy, 01_data_collection
"""

import pandas as pd
import numpy as np
from datetime import datetime
import asyncio
from data_collection import collect_yahoo_async

def load_config():
    """Load configuration from config.cfg."""
    # Initialize empty config dictionary
    config = {}
    try:
        # Read config file line by line
        with open("config.cfg", "r") as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    # Split line into key-value pair, handle empty values
                    key, value = line.strip().split('=', 1) if '=' in line else (line.strip(), '')
                    # Convert to appropriate types: float for numbers, bool for true/false, string otherwise
                    if value.lower() == 'true':
                        config[key] = True
                    elif value.lower() == 'false':
                        config[key] = False
                    elif value.replace('.', '').isdigit():
                        config[key] = float(value)
                    else:
                        config[key] = value
        return config
    except Exception as e:
        # Log error and return empty config to prevent crashes
        print(f"[ERROR] Failed to load config: {e}")
        return {}

def check_dca_trigger(yahoo_df, config, last_price, current_price):
    """Check if DCA buy condition is met."""
    # Get DCA parameters from config
    dca_percentage = config.get('dca_percentage', 3.0)
    position_size_pct = config.get('position_size_pct', 2.0)
    enable_dca = config.get('enable_dca', True)
    if not enable_dca:
        return None
    # Calculate percentage price drop
    price_drop = ((last_price - current_price) / last_price) * 100
    if price_drop >= dca_percentage:
        # Trigger DCA buy if drop exceeds threshold
        print(f"[DCA] Price dropped {price_drop:.2f}% (>= {dca_percentage}%)")
        amount = (config.get('budget', 10000) * position_size_pct / 100)
        return {'action': 'BUY', 'amount': min(amount, 10.0), 'trade_type': 'DCA'}  # Limit to $10 for testing
    return None

def check_atr_stop_loss(yahoo_df, active_trades, current_price, config):
    """Check if stop-loss is triggered for active trades."""
    # Get ATR multiplier from config
    atr_multiplier = config.get('atr_multiplier', 1.5)
    enable_atr_stops = config.get('enable_atr_stops', True)
    if not enable_atr_stops:
        return []
    trades_to_close = []
    for trade in active_trades:
        # Calculate stop-loss price using ATR
        stop_loss = trade['entry_price'] - (trade['atr'] * atr_multiplier)
        if current_price <= stop_loss:
            # Trigger sell if price falls below stop-loss
            trades_to_close.append({
                'action': 'SELL',
                'quantity': trade['quantity'],
                'trade_type': 'STOP_LOSS'
            })
            print(f"[STOP_LOSS] Triggered at ${current_price:,.2f} (Stop: ${stop_loss:,.2f})")
    return trades_to_close

def check_opportunistic_trade(yahoo_df, llm_suggestion, config):
    """Check for LLM-suggested opportunistic trades."""
    if llm_suggestion and llm_suggestion.get('action') == 'BUY':
        # Get position size from config
        position_size_pct = config.get('position_size_pct', 2.0)
        amount = (config.get('budget', 10000) * position_size_pct / 100)
        print(f"[LLM] Opportunistic buy suggested: ${amount:,.2f}")
        return {'action': 'BUY', 'amount': min(amount, 10.0), 'trade_type': 'SWING'}  # Limit to $10 for testing
    return None

def manage_trades(yahoo_df, current_price, portfolio, active_trades, llm_suggestion):
    """Manage trading strategies and return trade decisions."""
    # Load configuration for strategy parameters
    config = load_config()
    # Use previous close price as last price for DCA calculation
    last_price = yahoo_df['close'].iloc[1] if len(yahoo_df) > 1 else current_price
    decisions = []

    # Check DCA trigger
    dca_decision = check_dca_trigger(yahoo_df, config, last_price, current_price)
    if dca_decision and portfolio['usdt'] >= dca_decision['amount']:
        decisions.append(dca_decision)

    # Check stop-loss for active trades
    stop_loss_decisions = check_atr_stop_loss(yahoo_df, active_trades, current_price, config)
    decisions.extend(stop_loss_decisions)

    # Check LLM-suggested opportunistic trade
    opp_decision = check_opportunistic_trade(yahoo_df, llm_suggestion, config)
    if opp_decision and portfolio['usdt'] >= opp_decision['amount']:
        decisions.append(opp_decision)
        # Add new trade to active trades for stop-loss tracking
        active_trades.append({
            'entry_price': current_price,
            'quantity': opp_decision['amount'] / current_price,
            'atr': yahoo_df['atr_14'].iloc[-1]
        })

    # Check portfolio safeguard (pause if portfolio drops max_drawdown %)
    budget = config.get('budget', 10000)
    max_drawdown = config.get('max_drawdown', 25)
    portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
    if portfolio_value < budget * (1 - max_drawdown / 100):
        print(f"[SAFEGUARD] Portfolio value ${portfolio_value:,.2f} < {100 - max_drawdown}% of budget ${budget:,.2f}. Pausing trades.")
        return [], active_trades

    return decisions, active_trades

if __name__ == "__main__":
    """Test 04_strategy_manager module with real market data and a small trade."""
    print("Testing 04_strategy_manager module with real trade...")
    try:
        # Fetch real market data
        yahoo_df, current_price, indicators = asyncio.run(collect_yahoo_async())
        if yahoo_df is None or current_price is None:
            raise Exception("Failed to fetch market data")
        
        # Mock portfolio and LLM suggestion
        portfolio = {'btc': 0.0, 'usdt': 100.0}  # Small balance for testing
        active_trades = []
        llm_suggestion = {'action': 'BUY', 'confidence': 80, 'rationale': 'Test trade trigger'}
        
        # Test strategy decisions
        decisions, active_trades = manage_trades(yahoo_df, current_price, portfolio, active_trades, llm_suggestion)
        print(f"[TEST] Trade decisions: {decisions}")
        print(f"[TEST] Active trades: {active_trades}")
        
        # Execute a real trade if a buy decision is made
        from trade_executor import initialize_binance_client, execute_buy
        client = initialize_binance_client()
        for decision in decisions:
            if decision['action'] == 'BUY':
                trade_record = execute_buy(client, decision['amount'], current_price, decision['trade_type'])
                print(f"[TEST] Real trade executed: {trade_record}")
    except Exception as e:
        print(f"[TEST ERROR] {e}")