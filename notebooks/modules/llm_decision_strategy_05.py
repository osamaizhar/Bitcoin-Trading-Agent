"""
LLM-Driven Strategy Manager for Bitcoin Trading Agent
-----------------------------------------------------
This module is called at regular intervals (set in your trading bot sim file).
It calculates all relevant strategy triggers (DCA, ATR, etc.), bundles them into context,
and passes everything to the LLM for a single autonomous trade decision (BUY/SELL/HOLD).

- Loads config from config.cfg
- Parses latest market data from markdown
- Accepts last 10 trades externally (as argument)
- Bundles all relevant info for LLM context
- Calls LLM for final decision using Groq API
- Returns a single decision for execution/logging

Usage (in trading bot sim loop):
    decision, active_trades = manage_trades(portfolio, active_trades, last_10_trades)
"""

import os
import re
import json
import time

from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

def load_config():
    """Load configuration parameters from config.cfg file."""
    config = {}
    try:
        with open("config.cfg", "r") as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1) if '=' in line else (line.strip(), '')
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
        print(f"[ERROR] Failed to load config: {e}")
        return {}

# def parse_latest_data_from_md(md_path="complete_bitcoin_data.md"):
#     """Parse latest market data from markdown file."""
#     latest_data = {}
#     try:
#         with open(md_path, "r", encoding="utf-8") as f:
#             content = f.read()
#         price_match = re.search(r"\*\*Current Price\*\*: \$([0-9\.,]+)", content)
#         if price_match:
#             latest_data['current_price'] = float(price_match.group(1).replace(',', ''))
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

# ------------------------ v2 handles more indicators -------------------------------------
def parse_latest_data_from_md_content(md_content):
    """Parse latest market data from markdown content string."""
    latest_data = {}
    try:
        price_match = re.search(r"\*\*Current Price\*\*: \$([0-9\.,]+)", md_content)
        if price_match:
            latest_data['current_price'] = float(price_match.group(1).replace(',', ''))
        atr_match = re.search(r"\*\*ATR \(14\)\*\*: \$([0-9\.,]+)", md_content)
        rsi_match = re.search(r"\*\*RSI \(14\)\*\*: ([0-9\.]+)", md_content)
        sma20_match = re.search(r"\*\*SMA 20\*\*: \$([0-9\.,]+)", md_content)
        sma50_match = re.search(r"\*\*SMA 50\*\*: \$([0-9\.,]+)", md_content)
        ema12_match = re.search(r"\*\*EMA 12\*\*: \$([0-9\.,]+)", md_content)
        ema26_match = re.search(r"\*\*EMA 26\*\*: \$([0-9\.,]+)", md_content)
        bb_upper_match = re.search(r"\*\*Bollinger Upper \(20\)\*\*: \$([0-9\.,]+)", md_content)
        bb_middle_match = re.search(r"\*\*Bollinger Middle \(20\)\*\*: \$([0-9\.,]+)", md_content)
        bb_lower_match = re.search(r"\*\*Bollinger Lower \(20\)\*\*: \$([0-9\.,]+)", md_content)
        macd_match = re.search(r"\*\*MACD\*\*: ([\-0-9\.]+)", md_content)
        macd_signal_match = re.search(r"\*\*MACD Signal\*\*: ([\-0-9\.]+)", md_content)
        volume_sma20_match = re.search(r"\*\*Volume SMA 20\*\*: ([0-9\.,]+)", md_content)
        atr_volatility_ratio_match = re.search(r"\*\*ATR Volatility Ratio\*\*: ([0-9\.]+)", md_content)
        if atr_match:
            latest_data['atr_14'] = float(atr_match.group(1).replace(',', ''))
        if rsi_match:
            latest_data['rsi_14'] = float(rsi_match.group(1))
        if sma20_match:
            latest_data['sma_20'] = float(sma20_match.group(1).replace(',', ''))
        if sma50_match:
            latest_data['sma_50'] = float(sma50_match.group(1).replace(',', ''))
        if ema12_match:
            latest_data['ema_12'] = float(ema12_match.group(1).replace(',', ''))
        if ema26_match:
            latest_data['ema_26'] = float(ema26_match.group(1).replace(',', ''))
        if bb_upper_match:
            latest_data['bb_upper'] = float(bb_upper_match.group(1).replace(',', ''))
        if bb_middle_match:
            latest_data['bb_middle'] = float(bb_middle_match.group(1).replace(',', ''))
        if bb_lower_match:
            latest_data['bb_lower'] = float(bb_lower_match.group(1).replace(',', ''))
        if macd_match:
            latest_data['macd'] = float(macd_match.group(1))
        if macd_signal_match:
            latest_data['macd_signal'] = float(macd_signal_match.group(1))
        if volume_sma20_match:
            latest_data['volume_sma_20'] = float(volume_sma20_match.group(1).replace(',', ''))
        if atr_volatility_ratio_match:
            latest_data['atr_volatility_ratio'] = float(atr_volatility_ratio_match.group(1))
        return latest_data
    except Exception as e:
        print(f"[ERROR] Failed to parse markdown content: {e}")
        return {}




def extract_json_from_response(response_text):
    """Extract JSON object from LLM response text."""
    response_text = response_text.strip()
    response_text = response_text.replace('```json', '').replace('```', '').strip()
    try:
        return json.loads(response_text)
    except Exception:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception as e:
                print(f"[ERROR] Failed to parse JSON: {e}")
                print(f"[RAW RESPONSE] {response_text}")
                return None
        else:
            print("[ERROR] LLM response did not contain valid JSON.")
            print(f"[RAW RESPONSE] {response_text}")
            return None

def initialize_groq_client():
    """Initialize Groq client with API key from .env."""
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise Exception("Groq API key missing in .env")
    return Groq(api_key=api_key)

# def build_llm_context(portfolio, active_trades, latest_data, config, last_10_trades):
#     """Bundle all relevant strategy triggers, market info, and last 10 trades for LLM context."""
#     sma_20 = latest_data.get('sma_20', 0)
#     current_price = latest_data.get('current_price', 0)
#     last_price = sma_20 if sma_20 else current_price
#     dca_percentage = config.get('dca_percentage', 3.0)
#     price_drop = ((last_price - current_price) / last_price) * 100 if last_price else 0
#     dca_triggered = price_drop >= dca_percentage

#     atr_value = latest_data.get('atr_14', 0)
#     atr_multiplier = config.get('atr_multiplier', 1.5)
#     stop_loss_triggers = []
#     for trade in active_trades:
#         stop_loss = trade['entry_price'] - (atr_value * atr_multiplier)
#         if current_price <= stop_loss:
#             stop_loss_triggers.append({
#                 'entry_price': trade['entry_price'],
#                 'stop_loss': stop_loss,
#                 'current_price': current_price
#             })

#     context = {
#         'portfolio': portfolio,
#         'active_trades': active_trades,
#         'market_data': latest_data,
#         'dca_triggered': dca_triggered,
#         'dca_price_drop_pct': price_drop,
#         'stop_loss_triggers': stop_loss_triggers,
#         'config': config,
#         'recent_trade_history': last_10_trades
#     }
#     return context
# ---------------------- v2 for more indicators -------------------------------------
def build_llm_context(portfolio, active_trades, latest_data, config, last_10_trades):
    """Bundle all relevant strategy triggers, market info, and last 10 trades for LLM context, including new indicators."""
    sma_20 = latest_data.get('sma_20', 0)
    current_price = latest_data.get('current_price', 0)
    last_price = sma_20 if sma_20 else current_price
    dca_percentage = config.get('dca_percentage', 3.0)
    price_drop = ((last_price - current_price) / last_price) * 100 if last_price else 0
    dca_triggered = price_drop >= dca_percentage

    atr_value = latest_data.get('atr_14', 0)
    atr_multiplier = config.get('atr_multiplier', 1.5)
    stop_loss_triggers = []
    for trade in active_trades:
        stop_loss = trade['entry_price'] - (atr_value * atr_multiplier)
        if current_price <= stop_loss:
            stop_loss_triggers.append({
                'entry_price': trade['entry_price'],
                'stop_loss': stop_loss,
                'current_price': current_price
            })

    context = {
        'portfolio': portfolio,
        'active_trades': active_trades,
        'market_data': latest_data,  # Now includes new indicators like EMA, Bollinger, Volume SMA, ATR Ratio
        'dca_triggered': dca_triggered,
        'dca_price_drop_pct': price_drop,
        'stop_loss_triggers': stop_loss_triggers,
        'config': config,
        'recent_trade_history': last_10_trades
    }
    return context


# def get_llm_decision(context):
#     """
#     Query Groq LLM for trading decision using full context.
#     Returns dict: {action, confidence, rationale}
#     """
#     try:
#         client = initialize_groq_client()
#         # Compose prompt for LLM
#         system_prompt = f"""
# You are an expert Bitcoin trading algorithm designed to maximize profits on hourly timeframes. Analyze the provided market data and suggest the most profitable action (BUY, SELL, or HOLD) with a confidence score (0-100).

# YOUR PRIMARY OBJECTIVE: Generate maximum profit on EACH trade by identifying high-probability setups with clear entry/exit points.

# TRADING RULES:
# 1. ONLY BUY when there are strong signals of an imminent upward price movement (2%+ potential within hours)
# 2. ONLY SELL when:
#    - You've captured at least 1.5% profit, OR
#    - Clear reversal signals indicate the uptrend is ending, OR
#    - Stop conditions are triggered to protect capital
# 3. DEFAULT to HOLD unless a high-confidence (70%+) opportunity exists
# 4. AVOID frequent trading - quality over quantity is essential

# TECHNICAL INDICATORS - BUY WHEN:
# - RSI crosses above 30 from oversold territory
# - Price bounces off support with increasing volume
# - MACD shows bullish crossover or divergence
# - Price is testing key support with decreasing selling pressure

# TECHNICAL INDICATORS - SELL WHEN:
# - RSI reaches overbought territory (70+)
# - Price hits resistance with declining momentum
# - MACD shows bearish crossover or divergence
# - Price action shows reversal patterns at resistance

# PROVIDE SPECIFIC RATIONALE: Include exact price targets, stop-loss levels, and the specific technical signals that triggered your decision.

# CONTEXT:
# {json.dumps(context, indent=2)}

# Respond ONLY with valid JSON (no markdown, no explanation, no code block markers):

# {{
#     "action": "BUY|SELL|HOLD",
#     "confidence": <0-100>,
#     "rationale": "<brief explanation>"
# }}
# """
#         response = client.chat.completions.create(
#             model="meta-llama/llama-4-maverick-17b-128e-instruct",
#             messages=[
#                 {"role": "system", "content": system_prompt}
#             ],
#         )
#         response_text = response.choices[0].message.content.strip()
#         decision = extract_json_from_response(response_text)
#         if decision:
#             print(f"[LLM] Decision: {decision['action']} ({decision['confidence']}%) - {decision['rationale']}")
#             return decision
#         else:
#             return {
#                 "action": "HOLD",
#                 "confidence": 50,
#                 "rationale": "LLM response parsing failed, defaulting to HOLD."
#             }
#     except Exception as e:
#         print(f"[ERROR] LLM decision failed: {e}")
#         return {
#             "action": "HOLD",
#             "confidence": 50,
#             "rationale": "LLM decision failed, defaulting to HOLD."
#         }

# ---------------------------- Updated with reducded print -------------------------------
def track_time(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"[Time Tracker] `{func.__name__}` took {end - start:.4f} seconds")
        return result

    return wrapper

# @track_time
# def get_llm_decision(context):
#     """
#     Query Groq LLM for trading decision using full context, including new indicators.
#     Returns dict: {action, amount (for BUY), quantity (for SELL), confidence, rationale}
#     """
#     try:
#         client = initialize_groq_client()
#         # Compose prompt for LLM, updated with new indicators
#         system_prompt = f"""
# You are an expert Bitcoin trading algorithm designed to maximize profits on hourly timeframes. Analyze the provided market data and suggest the most profitable action (BUY, SELL, or HOLD) with a confidence score (0-100).

# YOUR PRIMARY OBJECTIVE: Generate maximum profit on EACH trade by identifying high-probability setups with clear entry/exit points, focusing on DCA (Dollar-Cost Averaging) and ATR (Average True Range) indicators.

# TRADING RULES:
# 1. ONLY BUY when there are strong signals of an imminent upward price movement (2%+ potential within hours), especially on DCA triggers with high volume.
# 2. ONLY SELL when:
#    - You've captured at least 1.5% profit, OR
#    - Clear reversal signals indicate the uptrend is ending, OR
#    - ATR-based stop-loss or volatility ratio indicates risk.
# 3. DEFAULT to HOLD unless a high-confidence (70%+) opportunity exists.
# 4. AVOID frequent trading - quality over quantity is essential.

# TECHNICAL INDICATORS - BUY WHEN:
# - RSI crosses above 30 from oversold territory.
# - Price bounces off Bollinger Lower band with increasing volume (DCA confirmation).
# - EMA 12 crosses above EMA 26 (bullish trend).
# - MACD shows bullish crossover or divergence.
# - Price is testing key support with decreasing selling pressure and high Volume SMA 20.

# TECHNICAL INDICATORS - SELL WHEN:
# - RSI reaches overbought territory (70+).
# - Price hits Bollinger Upper band with declining momentum.
# - EMA 12 crosses below EMA 26 (bearish trend).
# - MACD shows bearish crossover or divergence.
# - ATR Volatility Ratio is high, indicating potential reversal or stop-loss trigger.
# - Price action shows reversal patterns at resistance.

# PROVIDE SPECIFIC RATIONALE: Include exact price targets, stop-loss levels (using ATR), and the specific technical signals that triggered your decision.

# For BUY: Specify the USD amount to invest (e.g., based on position size, available funds, portfolio, recent trades, indicators).
# For SELL: Specify the BTC quantity to sell (e.g., full position, partial based on risk, portfolio, recent trades, indicators).

# CONTEXT:
# {json.dumps(context, indent=2)}

# Respond ONLY with valid JSON (no markdown, no explanation, no code block markers):

# {{
#     "action": "BUY|SELL|HOLD",
#     "amount": <USD amount for BUY, omit for others>,
#     "quantity": <BTC quantity for SELL, omit for others>,
#     "confidence": <0-100>,
#     "rationale": "<brief explanation>"
# }}
# """
#         response = client.chat.completions.create(
#             model="meta-llama/llama-4-maverick-17b-128e-instruct",
#             messages=[
#                 {"role": "system", "content": system_prompt}
#             ],
#         )
#         response_text = response.choices[0].message.content.strip()
#         decision = extract_json_from_response(response_text)
#         if decision:
#             # Return full decision including amount/quantity if present
#             return {
#                 "action": decision.get("action"),
#                 "amount": decision.get("amount"),  # For BUY
#                 "quantity": decision.get("quantity"),  # For SELL
#                 "confidence": decision.get("confidence", 0),
#                 "rationale": decision.get("rationale", "")
#             }
#         else:
#             return {
#                 "action": "HOLD",
#                 "rationale": "LLM response parsing failed, defaulting to HOLD."
#             }
#     except Exception as e:
#         return {
#             "action": "HOLD",
#             "rationale": "LLM decision failed, defaulting to HOLD."
        # }
# ----------------------- Now gives quantity of buy sell as well ----------------------------------------
@track_time
def get_llm_decision(context):
    """
    Query Groq LLM for trading decision using full context.
    Returns dict: {action, amount (for BUY), quantity (for SELL), confidence, rationale}
    """
    try:
        client = initialize_groq_client()
        # Compose prompt for LLM
        system_prompt = f"""
You are an expert Bitcoin trading algorithm focused on maximizing and securing profits on hourly timeframes.
Your top priorities are:
- **Maximize total portfolio value** (BTC value at current price + USDT balance + USD PROFIT).
- **Grow USD PROFIT over time** by extracting profits whenever the total portfolio value exceeds the dynamic profit threshold.
- **Smart reinvestment**: Always keep enough USDT in the trading balance to allow for future BUY actions and to avoid the portfolio value dropping to zero.

PROFIT THRESHOLD LOGIC:
- The profit threshold starts as the initial budget.
- Each time you secure profit (PROFIT action), the threshold increases by the amount secured.
- Only extract profit when portfolio value exceeds this dynamic threshold.

IMPORTANT PROFIT RULE:
- You can only move USD to the USD PROFIT balance if you have sufficient USDT available.
- If you want to secure profits but your USDT balance is insufficient, you must SELL BTC first to realize gains in USDT, then move USD to USD PROFIT.
- Do not suggest a PROFIT action unless there is enough USDT in the portfolio to cover the profit_amount.

REINVESTMENT & PORTFOLIO GROWTH LOGIC:
- When you suggest a PROFIT action, only a portion (e.g., 50%) of the profit (amount above the threshold) is moved to USD PROFIT (secured).
- The remaining portion of the profit stays in the USDT balance and is available for future reinvestment (future BUY actions).
- Never move all USDT to USD PROFIT; always leave enough USDT in the trading balance to allow for future BUY actions and to avoid the portfolio value dropping to zero.
- If the USDT balance is low after PROFIT, prioritize keeping at least 30% of the initial budget in USDT for reinvestment and trading flexibility.
- **Always prioritize actions that grow both the total portfolio value and USD PROFIT over time.** Frequent trading is allowed if it results in consistent growth of both.
- Clearly specify in your rationale how much is secured, how much is left for reinvestment, and how your action will help maximize total portfolio value and USD PROFIT.

BINANCE MINIMUMS:
- For BUY: Never suggest a buy_amount that would result in less than 0.0001 BTC purchased. Calculate buy_amount so that buy_amount / current_price >= 0.0001 BTC.
- For SELL: Never suggest selling less than 0.0001 BTC. Only suggest SELL if quantity >= 0.0001 BTC and portfolio has sufficient BTC.

TRADING RULES:
1. BUY: Suggest the USD amount to buy BTC (field: "buy_amount"). Do NOT suggest BTC quantity directly. Always check the portfolio's available USD balance before suggesting a BUY. Never spend all available USD—always leave at least 30% of the budget unspent to buy future dips. **Prioritize BUY actions when BTC price drops significantly or technical indicators confirm a dip.**
2. SELL: Suggest the BTC quantity to sell (field: "quantity"). Consider partial sells to lock in gains while maintaining some BTC exposure. **Prioritize SELL actions when BTC price increases significantly or technical indicators confirm a rally.**
3. PROFIT: Whenever total portfolio value exceeds the dynamic profit threshold, prioritize extracting profits. Move a portion (e.g., 50%) of the profit (amount above the threshold) into the USD PROFIT balance, and leave the remainder in USDT for reinvestment. The USD PROFIT balance is not used for trading and represents secured gains. For PROFIT, always specify the USD amount to secure in the field "profit_amount". Only suggest PROFIT if USDT balance is sufficient and if it does not harm future portfolio growth.
4. DEFAULT to HOLD unless a high-confidence (70%+) opportunity exists.

PORTFOLIO FIELDS:
- BTC: Bitcoin balance
- USDT: USD trading balance
- USD PROFIT: Secured profit, not used for trading
- PROFIT THRESHOLD: Initial budget + all previously secured profits

ACTIONS:
- BUY: Buy BTC with USDT (specify buy_amount in USD, ensure at least 30% USD remains after purchase)
- SELL: Sell BTC for USDT (specify quantity, consider partial sells)
- HOLD: No action
- PROFIT: Move USD from USDT to USD PROFIT (secured gains, specify profit_amount; only if USDT balance is sufficient)

TECHNICAL INDICATORS:
- BUY when RSI crosses above 30, price bounces off support, MACD bullish crossover, or volume increases on a dip. **Also prioritize BUY when BTC price drops significantly compared to recent averages.**
- SELL when RSI reaches 70+, price hits resistance, MACD bearish crossover, or volume decreases on a rise. **Also prioritize SELL when BTC price increases significantly compared to recent averages.**

PROVIDE SPECIFIC RATIONALE: Include exact price targets, stop-loss levels, and the specific technical signals that triggered your decision. Always explain why you chose to secure profits, how much is left for reinvestment, and how your action will help maximize total portfolio value and USD PROFIT.


CONTEXT:
{json.dumps(context, indent=2)}

Respond ONLY with valid JSON (no markdown, no explanation, no code block markers):

{{
    "action": "BUY|SELL|HOLD|PROFIT",
    "buy_amount": <USD amount for BUY, omit for others>,
    "quantity": <BTC quantity for SELL, omit for others>,
    "profit_amount": <USD amount for PROFIT, omit for others>,
    "confidence": <0-100>,
    "rationale": "<brief explanation including how much is secured and how much is left for reinvestment>"
}}

"""
        response = client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct-0905",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.2 
        )
        response_text = response.choices[0].message.content.strip()
        decision = extract_json_from_response(response_text)
        if decision:
            # Return full decision including amount/quantity if present
            return {
                "action": decision.get("action"),
                "buy_amount": decision.get("buy_amount"),  # For BUY
                "quantity": decision.get("quantity"),
                "profit_amount": decision.get("profit_amount"),  # For PROFIT
                "confidence": decision.get("confidence", 0),
                "rationale": decision.get("rationale", "")
            }
        else:
            return {
                "action": "HOLD",
                "rationale": "LLM response parsing failed, defaulting to HOLD."
            }
    except Exception as e:
        return {
            "action": "HOLD",
            "rationale": "LLM decision failed, defaulting to HOLD."
        }
    # def manage_trades(portfolio, active_trades, last_10_trades):
    #     """
    #     Main strategy manager function.
    #     - Loads config and latest market data
    #     - Accepts last 10 trades externally
    #     - Builds LLM context with all triggers and trade history
    #     - Calls LLM for final decision
    #     - Returns a single decision and updated active trades
    #     """
    #     config = load_config()
    #     latest_data = parse_latest_data_from_md()
    #     context = build_llm_context(portfolio, active_trades, latest_data, config, last_10_trades)
    #     llm_decision = get_llm_decision(context)

    #     current_price = latest_data.get('current_price', 0)
    #     position_size_pct = config.get('position_size_pct', 2.0)
    #     budget = config.get('budget', 10000)

    #     # Only execute LLM's decision
    #     if llm_decision['action'] == 'BUY' and portfolio['usdt'] >= (budget * position_size_pct / 100):
    #         amount = budget * position_size_pct / 100
    #         decision = {
    #             'action': 'BUY',
    #             'amount': min(amount, portfolio['usdt']),
    #             'rationale': llm_decision.get('rationale', ''),
    #             'confidence': llm_decision.get('confidence', 0)
    #         }
    #         active_trades.append({
    #             'entry_price': current_price,
    #             'quantity': min(amount, portfolio['usdt']) / current_price,
    #             'atr': latest_data.get('atr_14', 0)
    #         })
    #     elif llm_decision['action'] == 'SELL' and portfolio['btc'] > 0:
    #         decision = {
    #             'action': 'SELL',
    #             'quantity': portfolio['btc'],
    #             'rationale': llm_decision.get('rationale', ''),
    #             'confidence': llm_decision.get('confidence', 0)
    #         }
    #         active_trades.clear()
    #     else:
    #         decision = {
    #             'action': 'HOLD',
    #             'rationale': llm_decision.get('rationale', ''),
    #             'confidence': llm_decision.get('confidence', 0)
    #         }

    #     # Portfolio safeguard: stop trading if drawdown too big
    #     max_drawdown = config.get('max_drawdown', 25)
    #     portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
    #     if portfolio_value < budget * (1 - max_drawdown / 100):
    #         print(f"[SAFEGUARD] Portfolio value ${portfolio_value:,.2f} < {100 - max_drawdown}% of budget ${budget:,.2f}. Pausing trades.")
    #         return None, active_trades

    #     return decision, active_trades


# ------------------- Manage Trades v2 , extenally provided inputs ---------------------------------------------------

# config = load_config()
# latest_data = parse_latest_data_from_md()
# context = build_llm_context(portfolio, active_trades, latest_data, config, last_10_trades)

# def manage_trades(portfolio, active_trades, last_10_trades, config, latest_data, context):
#     llm_decision = get_llm_decision(context)
#     current_price = latest_data.get('current_price', 0)
#     position_size_pct = config.get('position_size_pct', 2.0)
#     budget = config.get('budget', 10000)

#     # Only execute LLM's decision
#     if llm_decision['action'] == 'BUY' and portfolio['usdt'] >= (budget * position_size_pct / 100):
#         amount = budget * position_size_pct / 100
#         decision = {
#             'action': 'BUY',
#             'amount': min(amount, portfolio['usdt']),
#             'rationale': llm_decision.get('rationale', ''),
#             'confidence': llm_decision.get('confidence', 0)
#         }
#         active_trades.append({
#             'entry_price': current_price,
#             'quantity': min(amount, portfolio['usdt']) / current_price,
#             'atr': latest_data.get('atr_14', 0)
#         })
#     elif llm_decision['action'] == 'SELL' and portfolio['btc'] > 0:
#         decision = {
#             'action': 'SELL',
#             'quantity': portfolio['btc'],
#             'rationale': llm_decision.get('rationale', ''),
#             'confidence': llm_decision.get('confidence', 0)
#         }
#         active_trades.clear()
#     else:
#         decision = {
#             'action': 'HOLD',
#             'rationale': llm_decision.get('rationale', ''),
#             'confidence': llm_decision.get('confidence', 0)
#         }

#     # Portfolio safeguard: stop trading if drawdown too big
#     max_drawdown = config.get('max_drawdown', 25)
#     portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#     if portfolio_value < budget * (1 - max_drawdown / 100):
#         print(f"[SAFEGUARD] Portfolio value ${portfolio_value:,.2f} < {100 - max_drawdown}% of budget ${budget:,.2f}. Pausing trades.")
#         return None, active_trades

#     return decision, active_trades


# ----------------- manage_trades func v3 with md_content markdown support rather than getting latest_data separately as a string -------------------
# def manage_trades(portfolio, active_trades, last_10_trades, config, context ,md_content):
#     """
#     Updated: Pass md_content instead of latest_data.
#     """
#     latest_data = parse_latest_data_from_md_content(md_content)
#     sma_20 = latest_data.get('sma_20', 0)
#     current_price = latest_data.get('current_price', 0)
#     last_price = sma_20 if sma_20 else current_price
#     dca_percentage = config.get('dca_percentage', 3.0)
#     price_drop = ((last_price - current_price) / last_price) * 100 if last_price else 0
#     dca_triggered = price_drop >= dca_percentage

#     atr_value = latest_data.get('atr_14', 0)
#     atr_multiplier = config.get('atr_multiplier', 1.5)
#     stop_loss_triggers = []
#     for trade in active_trades:
#         stop_loss = trade['entry_price'] - (atr_value * atr_multiplier)
#         if current_price <= stop_loss:
#             stop_loss_triggers.append({
#                 'entry_price': trade['entry_price'],
#                 'stop_loss': stop_loss,
#                 'current_price': current_price
#             })

#     # Example LLM decision logic (replace with your LLM call)
#     position_size_pct = config.get('position_size_pct', 2.0)
#     budget = config.get('budget', 10000)
#     decision = get_llm_decision(context)

#     # Example buy/sell logic (replace with your own)
#     if dca_triggered and portfolio['usdt'] >= (budget * position_size_pct / 100):
#         amount = budget * position_size_pct / 100
#         decision = {
#             'action': 'BUY',
#             'amount': min(amount, portfolio['usdt']),
#             'rationale': 'DCA triggered.',
#             'confidence': 80
#         }
#         active_trades.append({
#             'entry_price': current_price,
#             'quantity': min(amount, portfolio['usdt']) / current_price,
#             'atr': atr_value
#         })
#     elif stop_loss_triggers and portfolio['btc'] > 0:
#         decision = {
#             'action': 'SELL',
#             'quantity': portfolio['btc'],
#             'rationale': 'Stop-loss triggered.',
#             'confidence': 90
#         }
#         active_trades.clear()

#     # Portfolio safeguard: stop trading if drawdown too big
#     max_drawdown = config.get('max_drawdown', 25)
#     portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
#     if portfolio_value < budget * (1 - max_drawdown / 100):
#         print(f"[SAFEGUARD] Portfolio value ${portfolio_value:,.2f} < {100 - max_drawdown}% of budget ${budget:,.2f}. Pausing trades.")
#         return None, active_trades

#     return decision, active_trades

# --------------------- Updated manage_trades now all decisions are made by llm as all indicators will be calculatd externally and passed into the llm as md_content as context / latest_data
# def manage_trades(portfolio, active_trades, last_10_trades, config, context, latest_data=None):
#     """
#     Updated: Strictly LLM-driven decisions only.
#     Executes BUY, SELL, or HOLD based on LLM output.
#     Returns the updated portfolio, decision, and active trades.
#     """
#     # Parse latest_data if provided as a string (md_content)
#     if latest_data is None or isinstance(latest_data, str):
#         if isinstance(latest_data, str):
#             latest_data = parse_latest_data_from_md_content(latest_data)
#         elif isinstance(context, dict) and 'md_content' in context:
#             latest_data = parse_latest_data_from_md_content(context['md_content'])
#         else:
#             latest_data = parse_latest_data_from_md()

#     current_price = latest_data.get('current_price', 0)
#     print(f"Current Price BTC: {current_price}")
#     # Get LLM decision
#     llm_decision = get_llm_decision(context)
#     print(f"LLM Decision: {llm_decision}")
#     if llm_decision and llm_decision.get('action') in ['BUY', 'SELL', 'HOLD']:
#         decision = {
#             'action': llm_decision.get('action'),
#             'rationale': llm_decision.get('rationale', ''),
#             'confidence': llm_decision.get('confidence', 0)
#         }

#         # Handle BUY action
#         if decision['action'] == 'BUY':
#             if 'amount' in llm_decision:
#                 decision['amount'] = llm_decision['amount']
#                 if decision['amount'] > portfolio['usdt']:
#                     decision['action'] = 'HOLD'
#                     decision['rationale'] = 'Insufficient USD balance for BUY.'
#                 else:
#                     decision['quantity'] = decision['amount'] / current_price if current_price else 0
#                     #decision['quantity'] = decision['amount']
#                     # Update portfolio and active trades
#                     portfolio['usdt'] -= decision['amount']
#                     portfolio['btc'] += decision['quantity']
#                     active_trades.append({
#                         'entry_price': current_price,
#                         'quantity': decision['quantity'],
#                         'atr': latest_data.get('atr_14', 0)
#                     })
#             else:
#                 decision['action'] = 'HOLD'
#                 decision['rationale'] = 'LLM did not specify amount for BUY.'

#         # Handle SELL action
#         elif decision['action'] == 'SELL':
#             if 'quantity' in llm_decision:
#                 decision['quantity'] = min(llm_decision['quantity'], portfolio['btc'])

#                 # Update portfolio and active trades
#                 portfolio['btc'] -= decision['quantity']
#                 portfolio['usdt'] += decision['quantity'] * current_price

#                 # Remove sold quantity from active trades
#                 sold_quantity = decision['quantity']
#                 for trade in active_trades[:]:
#                     if sold_quantity >= trade['quantity']:
#                         sold_quantity -= trade['quantity']
#                         active_trades.remove(trade)
#                     else:
#                         trade['quantity'] -= sold_quantity
#                         sold_quantity = 0
#                         break
#             else:
#                 decision['action'] = 'HOLD'
#                 decision['rationale'] = 'LLM did not specify quantity for SELL.'

#     else:
#         decision = {
#             'action': 'HOLD',
#             'rationale': 'LLM failed or invalid response.',
#             'confidence': 50
#         }

#     # Safeguard: Prevent BUY if USD balance is insufficient
#     if decision['action'] == 'BUY' and portfolio['usdt'] < decision.get('amount', 0):
#         decision['action'] = 'HOLD'
#         decision['rationale'] = 'Insufficient USD balance for BUY.'

#     # Update BTC VALUE USD in the portfolio
#     portfolio['btc_value_usd'] = portfolio['btc'] * current_price

#     return portfolio, decision, active_trades`

# -------------------- Updated manage_trades v4 only deals with llm decision and active trades -----------------------------------------------------
def manage_trades(portfolio, active_trades, last_10_trades, config, context, latest_data=None):
    """
    Calls LLM for a decision and returns it, along with active trades.
    No portfolio management or balance updates.
    """
    # Parse latest_data if provided as a string (md_content)
    if latest_data is None or isinstance(latest_data, str):
        if isinstance(latest_data, str):
            latest_data = parse_latest_data_from_md_content(latest_data)
        elif isinstance(context, dict) and 'md_content' in context:
            latest_data = parse_latest_data_from_md_content(context['md_content'])
        else:
            latest_data = parse_latest_data_from_md()

    llm_decision = get_llm_decision(context)
    print(f"LLM Decision: {llm_decision}")

    # Return the decision and active trades (no portfolio changes)
    return llm_decision, active_trades
# ------------------- TEST CODE -------------------
if __name__ == "__main__":
    # Example test portfolio and trades
    test_portfolio = {'btc': 0.01, 'usdt': 100.0}
    test_active_trades = [
        {'entry_price': 30000, 'quantity': 0.005, 'atr': 500}
    ]
    # Example last 10 trades (stub data)
    test_last_10_trades = [
        {'timestamp': '2025-08-30 10:00:00', 'action': 'BUY', 'price': 29500, 'amount': 50, 'btc': 0.0017, 'usdt': 50},
        {'timestamp': '2025-08-30 11:00:00', 'action': 'SELL', 'price': 29700, 'amount': 50, 'btc': 0.0, 'usdt': 100},
        {'timestamp': '2025-08-30 12:00:00', 'action': 'BUY', 'price': 29400, 'amount': 25, 'btc': 0.00085, 'usdt': 75},
        {'timestamp': '2025-08-30 13:00:00', 'action': 'BUY', 'price': 29300, 'amount': 25, 'btc': 0.0017, 'usdt': 50},
        {'timestamp': '2025-08-30 14:00:00', 'action': 'HOLD', 'price': 29200, 'amount': 0, 'btc': 0.0017, 'usdt': 50},
        {'timestamp': '2025-08-30 15:00:00', 'action': 'BUY', 'price': 29100, 'amount': 10, 'btc': 0.00205, 'usdt': 40},
        {'timestamp': '2025-08-30 16:00:00', 'action': 'SELL', 'price': 29350, 'amount': 10, 'btc': 0.0017, 'usdt': 50},
        {'timestamp': '2025-08-30 17:00:00', 'action': 'HOLD', 'price': 29400, 'amount': 0, 'btc': 0.0017, 'usdt': 50},
        {'timestamp': '2025-08-30 18:00:00', 'action': 'BUY', 'price': 29500, 'amount': 20, 'btc': 0.00237, 'usdt': 30},
        {'timestamp': '2025-08-30 19:00:00', 'action': 'SELL', 'price': 29600, 'amount': 20, 'btc': 0.0017, 'usdt': 50}
    ]
    print("Running LLM-driven strategy manager test...")
    decision, updated_trades = manage_trades(test_portfolio, test_active_trades, test_last_10_trades)
    print("Decision:", decision)
    print("Updated Active Trades:", updated_trades)