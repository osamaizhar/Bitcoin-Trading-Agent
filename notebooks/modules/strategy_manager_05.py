# """
# Strategy Manager Module for Bitcoin Trading Agent
# Module Number: 4
# Purpose: Implements trading strategies (DCA, ATR-based stop-loss, hybrid) and manages active trades.

# Inputs:
# - Market data from 01_data_collection (yahoo_df, indicators)
# - Configuration parameters from 02_config_manager
# - LLM suggestions from 05_llm_decision
# - Current portfolio from 03_trade_executor

# Outputs:
# - Trade decisions (buy/sell) to be executed
# - Active trade tracking with stop-loss levels
# - Strategy performance metrics

# Dependencies: pandas, numpy, 01_data_collection
# """

# import pandas as pd
# import numpy as np
# from datetime import datetime
# import asyncio
# from data_collection import collect_yahoo_async

# def load_config():
#     """Load configuration from config.cfg."""
#     # Initialize empty config dictionary
#     config = {}
#     try:
#         # Read config file line by line
#         with open("config.cfg", "r") as f:
#             for line in f:
#                 if line.strip() and not line.startswith('#'):
#                     # Split line into key-value pair, handle empty values
#                     key, value = line.strip().split('=', 1) if '=' in line else (line.strip(), '')
#                     # Convert to appropriate types: float for numbers, bool for true/false, string otherwise
#                     if value.lower() == 'true':
#                         config[key] = True
#                     elif value.lower() == 'false':
#                         config[key] = False
#                     elif value.replace('.', '').isdigit():
#                         config[key] = float(value)
#                     else:
#                         config[key] = value
#         return config
#     except Exception as e:
#         # Log error and return empty config to prevent crashes
#         print(f"[ERROR] Failed to load config: {e}")
#         return {}

# def check_dca_trigger(yahoo_df, config, last_price, current_price):
#     """Check if DCA buy condition is met."""
#     # Get DCA parameters from config
#     dca_percentage = config.get('dca_percentage', 3.0)
#     position_size_pct = config.get('position_size_pct', 2.0)
#     enable_dca = config.get('enable_dca', True)
#     if not enable_dca:
#         return None
#     # Calculate percentage price drop
#     price_drop = ((last_price - current_price) / last_price) * 100
#     if price_drop >= dca_percentage:
#         # Trigger DCA buy if drop exceeds threshold
#         print(f"[DCA] Price dropped {price_drop:.2f}% (>= {dca_percentage}%)")
#         amount = (config.get('budget', 10000) * position_size_pct / 100)
#         return {'action': 'BUY', 'amount': min(amount, 10.0), 'trade_type': 'DCA'}  # Limit to $10 for testing
#     return None

# def check_atr_stop_loss(yahoo_df, active_trades, current_price, config):
#     """Check if stop-loss is triggered for active trades."""
#     # Get ATR multiplier from config
#     atr_multiplier = config.get('atr_multiplier', 1.5)
#     enable_atr_stops = config.get('enable_atr_stops', True)
#     if not enable_atr_stops:
#         return []
#     trades_to_close = []
#     for trade in active_trades:
#         # Calculate stop-loss price using ATR
#         stop_loss = trade['entry_price'] - (trade['atr'] * atr_multiplier)
#         if current_price <= stop_loss:
#             # Trigger sell if price falls below stop-loss
#             trades_to_close.append({
#                 'action': 'SELL',
#                 'quantity': trade['quantity'],
#                 'trade_type': 'STOP_LOSS'
#             })
#             print(f"[STOP_LOSS] Triggered at ${current_price:,.2f} (Stop: ${stop_loss:,.2f})")
#     return trades_to_close

# def check_opportunistic_trade(yahoo_df, llm_suggestion, config):
#     """Check for LLM-suggested opportunistic trades."""
#     if llm_suggestion and llm_suggestion.get('action') == 'BUY':
#         # Get position size from config
#         position_size_pct = config.get('position_size_pct', 2.0)
#         amount = (config.get('budget', 10000) * position_size_pct / 100)
#         print(f"[LLM] Opportunistic buy suggested: ${amount:,.2f}")
#         return {'action': 'BUY', 'amount': min(amount, 10.0), 'trade_type': 'SWING'}  # Limit to $10 for testing
#     return None

# def manage_trades(yahoo_df, current_price, portfolio, active_trades, llm_suggestion):
#     """Manage trading strategies and return trade decisions."""
#     # Load configuration for strategy parameters
#     config = load_config()
#     # Use previous close price as last price for DCA calculation
#     last_price = yahoo_df['close'].iloc[1] if len(yahoo_df) > 1 else current_price
#     decisions = []

#     # Check DCA trigger
#     dca_decision = check_dca_trigger(yahoo_df, config, last_price, current_price)
#     if dca_decision and portfolio['usdt'] >= dca_decision['amount']:
#         decisions.append(dca_decision)

#     # Check stop-loss for active trades
#     stop_loss_decisions = check_atr_stop_loss(yahoo_df, active_trades, current_price, config)
#     decisions.extend(stop_loss_decisions)

#     # Check LLM-suggested opportunistic trade
#     opp_decision = check_opportunistic_trade(yahoo_df, llm_suggestion, config)
#     if opp_decision and portfolio['usdt'] >= opp_decision['amount']:
#         decisions.append(opp_decision)
#         # Add new trade to active trades for stop-loss tracking
#         active_trades.append({
#             'entry_price': current_price,
#             'quantity': opp_decision['amount'] / current_price,
#             'atr': yahoo_df['atr_14'].iloc[-1]
#         })

#     # Check portfolio safeguard (pause if portfolio drops max_drawdown %)
#     budget = config.get('budget', 10000)
#     max_drawdown = config.get('max_drawdown', 25)
#     portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#     if portfolio_value < budget * (1 - max_drawdown / 100):
#         print(f"[SAFEGUARD] Portfolio value ${portfolio_value:,.2f} < {100 - max_drawdown}% of budget ${budget:,.2f}. Pausing trades.")
#         return [], active_trades

#     return decisions, active_trades

# if __name__ == "__main__":
#     """Test 04_strategy_manager module with real market data and a small trade."""
#     print("Testing 04_strategy_manager module with real trade...")
#     try:
#         # Fetch real market data
#         yahoo_df, current_price, indicators = asyncio.run(collect_yahoo_async())
#         if yahoo_df is None or current_price is None:
#             raise Exception("Failed to fetch market data")
        
#         # Mock portfolio and LLM suggestion
#         portfolio = {'btc': 0.0, 'usdt': 100.0}  # Small balance for testing
#         active_trades = []
#         llm_suggestion = {'action': 'BUY', 'confidence': 80, 'rationale': 'Test trade trigger'}
        
#         # Test strategy decisions
#         decisions, active_trades = manage_trades(yahoo_df, current_price, portfolio, active_trades, llm_suggestion)
#         print(f"[TEST] Trade decisions: {decisions}")
#         print(f"[TEST] Active trades: {active_trades}")
        
#         # Execute a real trade if a buy decision is made
#         from trade_executor import initialize_binance_client, execute_buy
#         client = initialize_binance_client()
#         for decision in decisions:
#             if decision['action'] == 'BUY':
#                 trade_record = execute_buy(client, decision['amount'], current_price, decision['trade_type'])
#                 print(f"[TEST] Real trade executed: {trade_record}")
#     except Exception as e:
#         print(f"[TEST ERROR] {e}")



# ---------------- Updated Code , removed dependency on old data_collection file -------------------------------
# """
# Strategy Manager Module for Bitcoin Trading Agent
# Module Number: 4
# Purpose: Implements trading strategies (DCA, ATR-based stop-loss, hybrid) and manages active trades.

# Inputs:
# - Latest market data and indicators from complete_bitcoin_data.md (generated by 01_data_collection.py)
# - Configuration parameters from 02_config_manager
# - LLM suggestions from 05_llm_decision
# - Current portfolio from 03_trade_executor

# Outputs:
# - Trade decisions (buy/sell) to be executed
# - Active trade tracking with stop-loss levels
# - Strategy performance metrics

# Dependencies: pandas, numpy
# """

# import pandas as pd
# import numpy as np
# from datetime import datetime
# import re

# def load_config():
#     """Load configuration from config.cfg."""
#     config = {}
#     try:
#         with open("config.cfg", "r") as f:
#             for line in f:
#                 if line.strip() and not line.startswith('#'):
#                     key, value = line.strip().split('=', 1) if '=' in line else (line.strip(), '')
#                     if value.lower() == 'true':
#                         config[key] = True
#                     elif value.lower() == 'false':
#                         config[key] = False
#                     elif value.replace('.', '').isdigit():
#                         config[key] = float(value)
#                     else:
#                         config[key] = value
#         return config
#     except Exception as e:
#         print(f"[ERROR] Failed to load config: {e}")
#         return {}

# def parse_latest_data_from_md(md_path="complete_bitcoin_data.md"):
#     """Parse latest price and indicators from complete_bitcoin_data.md."""
#     latest_data = {}
#     try:
#         with open(md_path, "r", encoding="utf-8") as f:
#             content = f.read()
#         # Extract current price
#         price_match = re.search(r"\*\*Current Price\*\*: \$([0-9\.,]+)", content)
#         if price_match:
#             latest_data['current_price'] = float(price_match.group(1).replace(',', ''))
#         # Extract technical indicators
#         atr_match = re.search(r"\*\*ATR \(14\)\*\*: \$([0-9\.,]+)", content)
#         rsi_match = re.search(r"\*\*RSI \(14\)\*\*: ([0-9\.]+)", content)
#         sma20_match = re.search(r"\*\*SMA 20\*\*: \$([0-9\.,]+)", content)
#         sma50_match = re.search(r"\*\*SMA 50\*\*: \$([0-9\.,]+)", content)
#         macd_match = re.search(r"\*\*MACD\*\*: ([\-0-9\.]+)", content)
#         macd_signal_match = re.search(r"\*\*MACD Signal\*\*: ([\-0-9\.]+)", content)
#         if atr_match:
#             latest_data['atr_14'] = float(atr_match.group(1).replace(',', ''))
#         if rsi_match:
#             latest_data['rsi_14'] = float(rsi_match.group(1))
#         if sma20_match:
#             latest_data['sma_20'] = float(sma20_match.group(1).replace(',', ''))
#         if sma50_match:
#             latest_data['sma_50'] = float(sma50_match.group(1).replace(',', ''))
#         if macd_match:
#             latest_data['macd'] = float(macd_match.group(1))
#         if macd_signal_match:
#             latest_data['macd_signal'] = float(macd_signal_match.group(1))
#         return latest_data
#     except Exception as e:
#         print(f"[ERROR] Failed to parse markdown data: {e}")
#         return {}

# def check_dca_trigger(latest_data, config, last_price, current_price):
#     """Check if DCA buy condition is met."""
#     dca_percentage = config.get('dca_percentage', 3.0)
#     position_size_pct = config.get('position_size_pct', 2.0)
#     enable_dca = config.get('enable_dca', True)
#     if not enable_dca:
#         return None
#     price_drop = ((last_price - current_price) / last_price) * 100
#     if price_drop >= dca_percentage:
#         print(f"[DCA] Price dropped {price_drop:.2f}% (>= {dca_percentage}%)")
#         amount = (config.get('budget', 10000) * position_size_pct / 100)
#         return {'action': 'BUY', 'amount': min(amount, 10.0), 'trade_type': 'DCA'}
#     return None

# def check_atr_stop_loss(active_trades, current_price, config, atr_value):
#     """Check if stop-loss is triggered for active trades."""
#     atr_multiplier = config.get('atr_multiplier', 1.5)
#     enable_atr_stops = config.get('enable_atr_stops', True)
#     if not enable_atr_stops:
#         return []
#     trades_to_close = []
#     for trade in active_trades:
#         stop_loss = trade['entry_price'] - (atr_value * atr_multiplier)
#         if current_price <= stop_loss:
#             trades_to_close.append({
#                 'action': 'SELL',
#                 'quantity': trade['quantity'],
#                 'trade_type': 'STOP_LOSS'
#             })
#             print(f"[STOP_LOSS] Triggered at ${current_price:,.2f} (Stop: ${stop_loss:,.2f})")
#     return trades_to_close

# def check_opportunistic_trade(llm_suggestion, config, current_price):
#     """Check for LLM-suggested opportunistic trades."""
#     if llm_suggestion and llm_suggestion.get('action') == 'BUY':
#         position_size_pct = config.get('position_size_pct', 2.0)
#         amount = (config.get('budget', 10000) * position_size_pct / 100)
#         print(f"[LLM] Opportunistic buy suggested: ${amount:,.2f}")
#         return {'action': 'BUY', 'amount': min(amount, 10.0), 'trade_type': 'SWING'}
#     return None

# def manage_trades(portfolio, active_trades, llm_suggestion):
#     """Manage trading strategies and return trade decisions."""
#     config = load_config()
#     latest_data = parse_latest_data_from_md()
#     current_price = latest_data.get('current_price', 0)
#     atr_value = latest_data.get('atr_14', 0)
#     sma_20 = latest_data.get('sma_20', 0)
#     # Use SMA 20 as last price for DCA calculation (or fallback to current price)
#     last_price = sma_20 if sma_20 else current_price
#     decisions = []

#     # Check DCA trigger
#     dca_decision = check_dca_trigger(latest_data, config, last_price, current_price)
#     if dca_decision and portfolio['usdt'] >= dca_decision['amount']:
#         decisions.append(dca_decision)

#     # Check stop-loss for active trades
#     stop_loss_decisions = check_atr_stop_loss(active_trades, current_price, config, atr_value)
#     decisions.extend(stop_loss_decisions)

#     # Check LLM-suggested opportunistic trade
#     opp_decision = check_opportunistic_trade(llm_suggestion, config, current_price)
#     if opp_decision and portfolio['usdt'] >= opp_decision['amount']:
#         decisions.append(opp_decision)
#         active_trades.append({
#             'entry_price': current_price,
#             'quantity': opp_decision['amount'] / current_price,
#             'atr': atr_value
#         })

#     # Portfolio safeguard
#     budget = config.get('budget', 10000)
#     max_drawdown = config.get('max_drawdown', 25)
#     portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#     if portfolio_value < budget * (1 - max_drawdown / 100):
#         print(f"[SAFEGUARD] Portfolio value ${portfolio_value:,.2f} < {100 - max_drawdown}% of budget ${budget:,.2f}. Pausing trades.")
#         return [], active_trades

#     return decisions, active_trades

# if __name__ == "__main__":
#     """Test 04_strategy_manager module with latest data from complete_bitcoin_data.md."""
#     print("Testing 04_strategy_manager module with latest markdown data...")
#     try:
#         # Mock portfolio and LLM suggestion
#         portfolio = {'btc': 0.0, 'usdt': 100.0}
#         active_trades = []
#         llm_suggestion = {'action': 'BUY', 'confidence': 80, 'rationale': 'Test trade trigger'}
#         decisions, active_trades = manage_trades(portfolio, active_trades, llm_suggestion)
#         print(f"[TEST] Trade decisions: {decisions}")
#         print(f"[TEST] Active trades: {active_trades}")
#         # Execute a real trade if a buy decision is made
#         from trade_executor_03 import initialize_binance_client, execute_buy
#         client = initialize_binance_client()
#         for decision in decisions:
#             if decision['action'] == 'BUY':
#                 trade_record = execute_buy(client, decision['amount'], active_trades[-1]['entry_price'], decision['trade_type'])
#                 print(f"[TEST] Real trade executed: {trade_record}")
#     except Exception as e:
#         print(f"[TEST ERROR] {e}")

# ------------------------ Commented out + Docstrings --------------------------------

# """
# Strategy Manager Module for Bitcoin Trading Agent
# Module Number: 4
# Purpose: Implements trading strategies (DCA, ATR-based stop-loss, hybrid) and manages active trades.

# Inputs:
# - Latest market data and indicators from complete_bitcoin_data.md (generated by 01_data_collection.py)
# - Configuration parameters from 02_config_manager
# - LLM suggestions from 05_llm_decision
# - Current portfolio from 03_trade_executor

# Outputs:
# - Trade decisions (buy/sell) to be executed
# - Active trade tracking with stop-loss levels
# - Strategy performance metrics

# Dependencies: pandas, numpy
# """

# # Import libraries
# import pandas as pd     # for data handling (though not heavily used here)
# import numpy as np      # for numeric operations
# from datetime import datetime  # for time-based tasks (not really used here yet)
# import re               # for regex parsing of markdown file

# def load_config():
#     """
#     Loads configuration settings from config.cfg file.
#     Each line in the config is read and converted into a dictionary entry.
#     Handles booleans, numbers, and strings.
#     """
#     config = {}  # store config values in a dict
#     try:
#         with open("config.cfg", "r") as f:  # open config file
#             for line in f:  # read line by line
#                 if line.strip() and not line.startswith('#'):  # skip empty lines and comments
#                     # split key=value format
#                     key, value = line.strip().split('=', 1) if '=' in line else (line.strip(), '')
#                     # convert string values to proper types
#                     if value.lower() == 'true':
#                         config[key] = True
#                     elif value.lower() == 'false':
#                         config[key] = False
#                     elif value.replace('.', '').isdigit():  # check if numeric
#                         config[key] = float(value)
#                     else:
#                         config[key] = value  # fallback: leave as string
#         return config
#     except Exception as e:  # if config load fails
#         print(f"[ERROR] Failed to load config: {e}")
#         return {}

# def parse_latest_data_from_md(md_path="complete_bitcoin_data.md"):
#     """
#     Reads a markdown file and extracts latest Bitcoin market data and indicators:
#     - Current Price
#     - ATR (14), RSI (14)
#     - SMA 20, SMA 50
#     - MACD and MACD Signal
#     """
#     latest_data = {}  # store parsed indicators
#     try:
#         with open(md_path, "r", encoding="utf-8") as f:
#             content = f.read()  # read the entire markdown file

#         # Extract current price using regex
#         price_match = re.search(r"\*\*Current Price\*\*: \$([0-9\.,]+)", content)
#         if price_match:
#             latest_data['current_price'] = float(price_match.group(1).replace(',', ''))

#         # Extract technical indicators one by one
#         atr_match = re.search(r"\*\*ATR \(14\)\*\*: \$([0-9\.,]+)", content)
#         rsi_match = re.search(r"\*\*RSI \(14\)\*\*: ([0-9\.]+)", content)
#         sma20_match = re.search(r"\*\*SMA 20\*\*: \$([0-9\.,]+)", content)
#         sma50_match = re.search(r"\*\*SMA 50\*\*: \$([0-9\.,]+)", content)
#         macd_match = re.search(r"\*\*MACD\*\*: ([\-0-9\.]+)", content)
#         macd_signal_match = re.search(r"\*\*MACD Signal\*\*: ([\-0-9\.]+)", content)

#         # Save extracted values after cleaning
#         if atr_match:
#             latest_data['atr_14'] = float(atr_match.group(1).replace(',', ''))
#         if rsi_match:
#             latest_data['rsi_14'] = float(rsi_match.group(1))
#         if sma20_match:
#             latest_data['sma_20'] = float(sma20_match.group(1).replace(',', ''))
#         if sma50_match:
#             latest_data['sma_50'] = float(sma50_match.group(1).replace(',', ''))
#         if macd_match:
#             latest_data['macd'] = float(macd_match.group(1))
#         if macd_signal_match:
#             latest_data['macd_signal'] = float(macd_signal_match.group(1))

#         return latest_data
#     except Exception as e:
#         print(f"[ERROR] Failed to parse markdown data: {e}")
#         return {}

# def check_dca_trigger(latest_data, config, last_price, current_price):
#     """
#     Checks if Dollar-Cost Averaging (DCA) condition is met:
#     - If price drops by configured percentage since last price, trigger a buy.
#     """
#     dca_percentage = config.get('dca_percentage', 3.0)     # default: 3% drop
#     position_size_pct = config.get('position_size_pct', 2.0)  # buy size % of budget
#     enable_dca = config.get('enable_dca', True)  # whether DCA is enabled
#     if not enable_dca:
#         return None

#     # Calculate percentage drop
#     price_drop = ((last_price - current_price) / last_price) * 100
#     if price_drop >= dca_percentage:  # condition met
#         print(f"[DCA] Price dropped {price_drop:.2f}% (>= {dca_percentage}%)")
#         amount = (config.get('budget', 10000) * position_size_pct / 100)  # buy amount
#         return {'action': 'BUY', 'amount': min(amount, 10.0), 'trade_type': 'DCA'}
#     return None

# def check_atr_stop_loss(active_trades, current_price, config, atr_value):
#     """
#     Checks if any active trade should be stopped out using ATR stop loss rule:
#     - If price <= entry price - (ATR * multiplier), trigger sell.
#     """
#     atr_multiplier = config.get('atr_multiplier', 1.5)  # how wide stop-loss is
#     enable_atr_stops = config.get('enable_atr_stops', True)
#     if not enable_atr_stops:
#         return []

#     trades_to_close = []  # store triggered stop-loss trades
#     for trade in active_trades:
#         stop_loss = trade['entry_price'] - (atr_value * atr_multiplier)
#         if current_price <= stop_loss:  # stop-loss hit
#             trades_to_close.append({
#                 'action': 'SELL',
#                 'quantity': trade['quantity'],
#                 'trade_type': 'STOP_LOSS'
#             })
#             print(f"[STOP_LOSS] Triggered at ${current_price:,.2f} (Stop: ${stop_loss:,.2f})")
#     return trades_to_close

# def check_opportunistic_trade(llm_suggestion, config, current_price):
#     """
#     If LLM suggests a BUY trade, open a small opportunistic trade.
#     """
#     if llm_suggestion and llm_suggestion.get('action') == 'BUY':
#         position_size_pct = config.get('position_size_pct', 2.0)
#         amount = (config.get('budget', 10000) * position_size_pct / 100)
#         print(f"[LLM] Opportunistic buy suggested: ${amount:,.2f}")
#         return {'action': 'BUY', 'amount': min(amount, 10.0), 'trade_type': 'SWING'}
#     return None

# def manage_trades(portfolio, active_trades, llm_suggestion):
#     """
#     Main strategy manager function.
#     Orchestrates:
#     - DCA buys
#     - ATR stop-loss checks
#     - Opportunistic LLM trades
#     - Portfolio safeguard (avoid too much drawdown)
#     """
#     config = load_config()  # load trading settings
#     latest_data = parse_latest_data_from_md()  # get market indicators
#     current_price = latest_data.get('current_price', 0)
#     atr_value = latest_data.get('atr_14', 0)
#     sma_20 = latest_data.get('sma_20', 0)

#     # Use SMA 20 as "last price" baseline for DCA (fallback: current price)
#     last_price = sma_20 if sma_20 else current_price
#     decisions = []  # list of trade actions

#     '''
#     Calls check_dca_trigger to determine if a DCA buy condition is met (e.g., price drop exceeds the configured percentage).
#     If the condition is met and the portfolio has enough USDT, the decision is added to the decisions list.
#     '''
#     # 1. Check for DCA buy
#     dca_decision = check_dca_trigger(latest_data, config, last_price, current_price)
#     if dca_decision and portfolio['usdt'] >= dca_decision['amount']:
#         decisions.append(dca_decision)

#     # 2. Check stop-loss for all active trades
#     stop_loss_decisions = check_atr_stop_loss(active_trades, current_price, config, atr_value)
#     decisions.extend(stop_loss_decisions)

#     # 3. Check for LLM opportunistic trade
#     opp_decision = check_opportunistic_trade(llm_suggestion, config, current_price)
#     if opp_decision and portfolio['usdt'] >= opp_decision['amount']:
#         decisions.append(opp_decision)
#         active_trades.append({
#             'entry_price': current_price,
#             'quantity': opp_decision['amount'] / current_price,  # how much BTC bought
#             'atr': atr_value
#         })

#     # 4. Portfolio safeguard: stop trading if drawdown too big
#     budget = config.get('budget', 10000)
#     max_drawdown = config.get('max_drawdown', 25)
#     portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#     if portfolio_value < budget * (1 - max_drawdown / 100):
#         print(f"[SAFEGUARD] Portfolio value ${portfolio_value:,.2f} < {100 - max_drawdown}% of budget ${budget:,.2f}. Pausing trades.")
#         return [], active_trades

#     return decisions, active_trades

# if __name__ == "__main__":
#     """
#     Test section for standalone run:
#     - Uses a mock portfolio
#     - Generates fake LLM suggestion
#     - Runs through trade manager
#     - Tries to execute a buy order if condition met
#     """
#     print("Testing 04_strategy_manager module with latest markdown data...")
#     try:
#         # Create fake portfolio and LLM suggestion
#         portfolio = {'btc': 0.0, 'usdt': 100.0}
#         active_trades = []
#         llm_suggestion = {'action': 'BUY', 'confidence': 80, 'rationale': 'Test trade trigger'}

#         # Run strategy manager
#         decisions, active_trades = manage_trades(portfolio, active_trades, llm_suggestion)
#         print(f"[TEST] Trade decisions: {decisions}")
#         print(f"[TEST] Active trades: {active_trades}")

#         # Try to actually execute a real buy trade if decision says so
#         from trade_executor_03 import initialize_binance_client, execute_buy
#         client = initialize_binance_client()
#         for decision in decisions:
#             if decision['action'] == 'BUY':
#                 trade_record = execute_buy(client, decision['amount'], active_trades[-1]['entry_price'], decision['trade_type'])
#                 print(f"[TEST] Real trade executed: {trade_record}")
#     except Exception as e:
#         print(f"[TEST ERROR] {e}")

# ------------- Test code v2 , no fake portfolio -------------------- ----------------------
# if __name__ == "__main__":
#     """
#     Live test section – runs against **real Binance account**.
#     - No mock portfolio or fake LLM suggestion
#     - Reads current portfolio from Binance
#     - Uses live LLM decision
#     - Executes real trades if BUY is signalled
#     """
#     import os
#     from trade_executor_03 import initialize_binance_client, get_portfolio

#     print("Live test: running strategy_manager with real Binance data…")
#     try:
#         client = initialize_binance_client()
#         portfolio = get_portfolio(client)          # ← actual balances
#         active_trades = []                           # start clean

#         # --- live LLM decision -------------------------------------------------
#         llm_suggestion = live_llm_decision()       # ← your real call goes here
#         # -----------------------------------------------------------------------

#         decisions, active_trades = manage_trades(portfolio, active_trades,
#                                                  llm_suggestion)

#         print(f"[LIVE] Trade decisions: {decisions}")
#         print(f"[LIVE] Active trades: {active_trades}")

#         # execute any BUY signals
#         from trade_executor_03 import execute_buy
#         for d in decisions:
#             if d['action'] == 'BUY':
#                 rec = execute_buy(client, d['amount'],
#                                   active_trades[-1]['entry_price'],
#                                   d['trade_type'])
#                 print(f"[LIVE] Buy executed: {rec}")

#     except Exception as e:
#         print(f"[LIVE ERROR] {e}")


# -------------- Based on latest changes in llm_decision --------------------------------

"""
Strategy Manager Module for Bitcoin Trading Agent
Module Number: 4
Purpose: Implements trading strategies (DCA, ATR-based stop-loss, hybrid) and manages active trades.

Inputs:
- Latest market data and indicators from complete_bitcoin_data.md (generated by 01_data_collection.py)
- Configuration parameters from 02_config_manager
- LLM suggestions from 05_llm_decision (now includes full market data, portfolio, and trade history context)
- Current portfolio from 03_trade_executor

Outputs:
- Trade decisions (buy/sell) to be executed
- Active trade tracking with stop-loss levels
- Strategy performance metrics

Dependencies: pandas, numpy
"""

import pandas as pd     # Import pandas for data manipulation and handling
import numpy as np      # Import numpy for numerical operations and calculations
from datetime import datetime  # Import datetime for handling timestamps in trade operations
import re               # Import re for regular expression parsing of markdown files

def load_config():
    """Loads configuration settings from config.cfg file."""
    config = {}  # Initialize empty dictionary to store configuration key-value pairs
    try:
        with open("config.cfg", "r") as f:  # Open config.cfg file in read mode
            for line in f:  # Iterate through each line in the file
                if line.strip() and not line.startswith('#'):  # Skip empty lines and comments
                    key, value = line.strip().split('=', 1) if '=' in line else (line.strip(), '')  # Split line into key-value pair at first '='
                    if value.lower() == 'true':  # Check if value is 'true' (case-insensitive)
                        config[key] = True  # Store as boolean True
                    elif value.lower() == 'false':  # Check if value is 'false' (case-insensitive)
                        config[key] = False  # Store as boolean False
                    elif value.replace('.', '').isdigit():  # Check if value is numeric (allowing decimals)
                        config[key] = float(value)  # Convert to float and store
                    else:
                        config[key] = value  # Store as string for non-boolean, non-numeric values
        return config  # Return the configuration dictionary
    except Exception as e:  # Catch any errors during file reading or parsing
        print(f"[ERROR] Failed to load config: {e}")  # Log error message
        return {}  # Return empty dictionary on failure

def parse_latest_data_from_md(md_path="complete_bitcoin_data.md"):
    """Reads markdown file and extracts latest Bitcoin market data and indicators."""
    latest_data = {}  # Initialize empty dictionary to store parsed market data
    try:
        with open(md_path, "r", encoding="utf-8") as f:  # Open markdown file in read mode with UTF-8 encoding
            content = f.read()  # Read entire file content
        price_match = re.search(r"\*\*Current Price\*\*: \$([0-9\.,]+)", content)  # Search for current price using regex
        if price_match:  # If price is found
            latest_data['current_price'] = float(price_match.group(1).replace(',', ''))  # Remove commas and convert to float
        atr_match = re.search(r"\*\*ATR \(14\)\*\*: \$([0-9\.,]+)", content)  # Search for ATR (14) value
        rsi_match = re.search(r"\*\*RSI \(14\)\*\*: ([0-9\.]+)", content)  # Search for RSI (14) value
        sma20_match = re.search(r"\*\*SMA 20\*\*: \$([0-9\.,]+)", content)  # Search for SMA (20) value
        sma50_match = re.search(r"\*\*SMA 50\*\*: \$([0-9\.,]+)", content)  # Search for SMA (50) value
        macd_match = re.search(r"\*\*MACD\*\*: ([\-0-9\.]+)", content)  # Search for MACD value
        macd_signal_match = re.search(r"\*\*MACD Signal\*\*: ([\-0-9\.]+)", content)  # Search for MACD Signal value
        if atr_match:  # If ATR is found
            latest_data['atr_14'] = float(atr_match.group(1).replace(',', ''))  # Remove commas and convert to float
        if rsi_match:  # If RSI is found
            latest_data['rsi_14'] = float(rsi_match.group(1))  # Convert to float
        if sma20_match:  # If SMA (20) is found
            latest_data['sma_20'] = float(sma20_match.group(1).replace(',', ''))  # Remove commas and convert to float
        if sma50_match:  # If SMA (50) is found
            latest_data['sma_50'] = float(sma50_match.group(1).replace(',', ''))  # Remove commas and convert to float
        if macd_match:  # If MACD is found
            latest_data['macd'] = float(macd_match.group(1))  # Convert to float
        if macd_signal_match:  # If MACD Signal is found
            latest_data['macd_signal'] = float(macd_signal_match.group(1))  # Convert to float
        return latest_data  # Return dictionary with parsed market data
    except Exception as e:  # Catch any errors during file reading or parsing
        print(f"[ERROR] Failed to parse markdown data: {e}")  # Log error message
        return {}  # Return empty dictionary on failure

def check_dca_trigger(latest_data, config, last_price, current_price):
    """Checks if Dollar-Cost Averaging (DCA) condition is met."""
    dca_percentage = config.get('dca_percentage', 3.0)  # Get DCA trigger percentage, default 3%
    position_size_pct = config.get('position_size_pct', 2.0)  # Get position size percentage, default 2%
    enable_dca = config.get('enable_dca', True)  # Check if DCA is enabled, default True
    if not enable_dca:  # If DCA is disabled
        return None  # Return None to skip DCA
    price_drop = ((last_price - current_price) / last_price) * 100  # Calculate percentage price drop
    if price_drop >= dca_percentage:  # Check if price drop meets or exceeds DCA threshold
        print(f"[DCA] Price dropped {price_drop:.2f}% (>= {dca_percentage}%)")  # Log DCA trigger
        amount = (config.get('budget', 10000) * position_size_pct / 100)  # Calculate trade amount based on budget
        return {'action': 'BUY', 'amount': min(amount, 10.0), 'trade_type': 'DCA'}  # Return buy decision, capped at $10
    return None  # Return None if DCA condition not met

def check_atr_stop_loss(active_trades, current_price, config, atr_value):
    """Checks if any active trade should be stopped out using ATR stop loss rule."""
    atr_multiplier = config.get('atr_multiplier', 1.5)  # Get ATR multiplier, default 1.5
    enable_atr_stops = config.get('enable_atr_stops', True)  # Check if ATR stop-loss is enabled, default True
    if not enable_atr_stops:  # If ATR stop-loss is disabled
        return []  # Return empty list to skip stop-loss checks
    trades_to_close = []  # Initialize list for trades to close
    for trade in active_trades:  # Iterate through active trades
        stop_loss = trade['entry_price'] - (atr_value * atr_multiplier)  # Calculate stop-loss price
        if current_price <= stop_loss:  # Check if current price triggers stop-loss
            trades_to_close.append({  # Add sell decision to list
                'action': 'SELL',  # Specify sell action
                'quantity': trade['quantity'],  # Use trade's quantity
                'trade_type': 'STOP_LOSS'  # Mark as stop-loss trade
            })
            print(f"[STOP_LOSS] Triggered at ${current_price:,.2f} (Stop: ${stop_loss:,.2f})")  # Log stop-loss trigger
    return trades_to_close  # Return list of trades to close

def check_opportunistic_trade(llm_suggestion, config, current_price):
    """
    If LLM suggests a BUY trade, open a small opportunistic trade.
    Now expects llm_suggestion to include full context (action, confidence, rationale, etc.)
    """
    if llm_suggestion and llm_suggestion.get('action') == 'BUY':  # Check if LLM suggests a buy
        position_size_pct = config.get('position_size_pct', 2.0)  # Get position size percentage, default 2%
        amount = (config.get('budget', 10000) * position_size_pct / 100)  # Calculate trade amount based on budget
        print(f"[LLM] Opportunistic buy suggested: ${amount:,.2f} | Confidence: {llm_suggestion.get('confidence', 'N/A')} | Rationale: {llm_suggestion.get('rationale', '')}")  # Log LLM suggestion details
        return {'action': 'BUY', 'amount': min(amount, 10.0), 'trade_type': 'SWING'}  # Return buy decision, capped at $10
    return None  # Return None if no valid LLM buy suggestion

def manage_trades(portfolio, active_trades, llm_suggestion):
    """
    Main strategy manager function.
    Orchestrates:
    - DCA buys
    - ATR stop-loss checks
    - Opportunistic LLM trades (now with full context from llm_decision_04)
    - Portfolio safeguard (avoid too much drawdown)
    """
    config = load_config()  # Load configuration settings
    latest_data = parse_latest_data_from_md()  # Load latest market data from markdown
    current_price = latest_data.get('current_price', 0)  # Get current Bitcoin price, default 0
    atr_value = latest_data.get('atr_14', 0)  # Get ATR (14) value, default 0
    sma_20 = latest_data.get('sma_20', 0)  # Get SMA (20) value, default 0
    last_price = sma_20 if sma_20 else current_price  # Use SMA (20) as last price, fallback to current price
    decisions = []  # Initialize list for trade decisions

    # 1. Check for DCA buy
    dca_decision = check_dca_trigger(latest_data, config, last_price, current_price)  # Check DCA conditions
    if dca_decision and portfolio['usdt'] >= dca_decision['amount']:  # Verify sufficient USDT for DCA
        decisions.append(dca_decision)  # Add DCA decision to list

    # 2. Check stop-loss for all active trades
    stop_loss_decisions = check_atr_stop_loss(active_trades, current_price, config, atr_value)  # Check ATR stop-loss
    decisions.extend(stop_loss_decisions)  # Add stop-loss decisions to list

    # 3. Check for LLM opportunistic trade (now expects full context from llm_decision_04)
    opp_decision = check_opportunistic_trade(llm_suggestion, config, current_price)  # Check LLM-based trade
    if opp_decision and portfolio['usdt'] >= opp_decision['amount']:  # Verify sufficient USDT for LLM trade
        decisions.append(opp_decision)  # Add LLM decision to list
        active_trades.append({  # Record new trade in active trades
            'entry_price': current_price,  # Store entry price
            'quantity': opp_decision['amount'] / current_price,  # Calculate quantity (BTC)
            'atr': atr_value  # Store ATR value for stop-loss
        })

    # 4. Portfolio safeguard: stop trading if drawdown too big
    budget = config.get('budget', 10000)  # Get budget, default $10,000
    max_drawdown = config.get('max_drawdown', 25)  # Get max drawdown percentage, default 25%
    portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']  # Calculate total portfolio value
    if portfolio_value < budget * (1 - max_drawdown / 100):  # Check if drawdown exceeds limit
        print(f"[SAFEGUARD] Portfolio value ${portfolio_value:,.2f} < {100 - max_drawdown}% of budget ${budget:,.2f}. Pausing trades.")  # Log safeguard trigger
        return [], active_trades  # Return empty decisions list to pause trading

    return decisions, active_trades  # Return trade decisions and updated active trades

if __name__ == "__main__":
    """
    Live test section – runs against **real Binance account**.
    - Reads current portfolio from Binance
    - Uses live LLM decision (with full context)
    - Executes real trades if BUY is signalled
    """
    from trade_executor_03 import initialize_binance_client, get_portfolio  # Import Binance client functions
    from llm_decision_04 import get_llm_decision  # Import LLM decision function

    print("Live test: running strategy_manager with real Binance data…")  # Log start of live test
    try:
        client = initialize_binance_client()  # Initialize Binance API client
        portfolio = get_portfolio(client)  # Retrieve current portfolio from Binance
        active_trades = []  # Initialize empty list for active trades

        # --- live LLM decision (full context: market data, portfolio, trade history) ---
        llm_suggestion = get_llm_decision(use_google_sheet=True)  # Get LLM decision with Google Sheets context
        # -------------------------------------------------------------------------------

        decisions, active_trades = manage_trades(portfolio, active_trades, llm_suggestion)  # Run strategy manager

        print(f"[LIVE] Trade decisions: {decisions}")  # Log trade decisions
        print(f"[LIVE] Active trades: {active_trades}")  # Log active trades

        # execute any BUY signals
        from trade_executor_03 import execute_buy  # Import buy execution function
        for d in decisions:  # Iterate through trade decisions
            if d['action'] == 'BUY':  # Check for buy decisions
                rec = execute_buy(client, d['amount'],  # Execute buy order
                                  active_trades[-1]['entry_price'],  # Use latest entry price
                                  d['trade_type'])  # Specify trade type
                print(f"[LIVE] Buy executed: {rec}")  # Log executed buy record

    except Exception as e:  # Catch any errors during live test
        print(f"[ERROR] Live test failed: {e}")  # Log error message