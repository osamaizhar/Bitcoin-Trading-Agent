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

def parse_latest_data_from_md(md_path="complete_bitcoin_data.md"):
    """Parse latest market data from markdown file."""
    latest_data = {}
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        price_match = re.search(r"\*\*Current Price\*\*: \$([0-9\.,]+)", content)
        if price_match:
            latest_data['current_price'] = float(price_match.group(1).replace(',', ''))
        atr_match = re.search(r"\*\*ATR \(14\)\*\*: \$([0-9\.,]+)", content)
        rsi_match = re.search(r"\*\*RSI \(14\)\*\*: ([0-9\.]+)", content)
        sma20_match = re.search(r"\*\*SMA 20\*\*: \$([0-9\.,]+)", content)
        sma50_match = re.search(r"\*\*SMA 50\*\*: \$([0-9\.,]+)", content)
        macd_match = re.search(r"\*\*MACD\*\*: ([\-0-9\.]+)", content)
        macd_signal_match = re.search(r"\*\*MACD Signal\*\*: ([\-0-9\.]+)", content)
        if atr_match:
            latest_data['atr_14'] = float(atr_match.group(1).replace(',', ''))
        if rsi_match:
            latest_data['rsi_14'] = float(rsi_match.group(1))
        if sma20_match:
            latest_data['sma_20'] = float(sma20_match.group(1).replace(',', ''))
        if sma50_match:
            latest_data['sma_50'] = float(sma50_match.group(1).replace(',', ''))
        if macd_match:
            latest_data['macd'] = float(macd_match.group(1))
        if macd_signal_match:
            latest_data['macd_signal'] = float(macd_signal_match.group(1))
        return latest_data
    except Exception as e:
        print(f"[ERROR] Failed to parse markdown data: {e}")
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

def build_llm_context(portfolio, active_trades, latest_data, config, last_10_trades):
    """Bundle all relevant strategy triggers, market info, and last 10 trades for LLM context."""
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
        'market_data': latest_data,
        'dca_triggered': dca_triggered,
        'dca_price_drop_pct': price_drop,
        'stop_loss_triggers': stop_loss_triggers,
        'config': config,
        'recent_trade_history': last_10_trades
    }
    return context

def get_llm_decision(context):
    """
    Query Groq LLM for trading decision using full context.
    Returns dict: {action, confidence, rationale}
    """
    try:
        client = initialize_groq_client()
        # Compose prompt for LLM
        system_prompt = f"""
You are a Bitcoin trading assistant. Analyze the following context and suggest a trading action (BUY, SELL, or HOLD) with a confidence score (0-100). Provide a brief rationale.

CONTEXT:
{json.dumps(context, indent=2)}

Respond ONLY with valid JSON (no markdown, no explanation, no code block markers):

{{
    "action": "BUY|SELL|HOLD",
    "confidence": <0-100>,
    "rationale": "<brief explanation>"
}}
"""
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
        )
        response_text = response.choices[0].message.content.strip()
        decision = extract_json_from_response(response_text)
        if decision:
            print(f"[LLM] Decision: {decision['action']} ({decision['confidence']}%) - {decision['rationale']}")
            return decision
        else:
            return {
                "action": "HOLD",
                "confidence": 50,
                "rationale": "LLM response parsing failed, defaulting to HOLD."
            }
    except Exception as e:
        print(f"[ERROR] LLM decision failed: {e}")
        return {
            "action": "HOLD",
            "confidence": 50,
            "rationale": "LLM decision failed, defaulting to HOLD."
        }

def manage_trades(portfolio, active_trades, last_10_trades):
    """
    Main strategy manager function.
    - Loads config and latest market data
    - Accepts last 10 trades externally
    - Builds LLM context with all triggers and trade history
    - Calls LLM for final decision
    - Returns a single decision and updated active trades
    """
    config = load_config()
    latest_data = parse_latest_data_from_md()
    context = build_llm_context(portfolio, active_trades, latest_data, config, last_10_trades)
    llm_decision = get_llm_decision(context)

    current_price = latest_data.get('current_price', 0)
    position_size_pct = config.get('position_size_pct', 2.0)
    budget = config.get('budget', 10000)

    # Only execute LLM's decision
    if llm_decision['action'] == 'BUY' and portfolio['usdt'] >= (budget * position_size_pct / 100):
        amount = budget * position_size_pct / 100
        decision = {
            'action': 'BUY',
            'amount': min(amount, portfolio['usdt']),
            'rationale': llm_decision.get('rationale', ''),
            'confidence': llm_decision.get('confidence', 0)
        }
        active_trades.append({
            'entry_price': current_price,
            'quantity': min(amount, portfolio['usdt']) / current_price,
            'atr': latest_data.get('atr_14', 0)
        })
    elif llm_decision['action'] == 'SELL' and portfolio['btc'] > 0:
        decision = {
            'action': 'SELL',
            'quantity': portfolio['btc'],
            'rationale': llm_decision.get('rationale', ''),
            'confidence': llm_decision.get('confidence', 0)
        }
        active_trades.clear()
    else:
        decision = {
            'action': 'HOLD',
            'rationale': llm_decision.get('rationale', ''),
            'confidence': llm_decision.get('confidence', 0)
        }

    # Portfolio safeguard: stop trading if drawdown too big
    max_drawdown = config.get('max_drawdown', 25)
    portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
    if portfolio_value < budget * (1 - max_drawdown / 100):
        print(f"[SAFEGUARD] Portfolio value ${portfolio_value:,.2f} < {100 - max_drawdown}% of budget ${budget:,.2f}. Pausing trades.")
        return None, active_trades

    return decision, active_trades

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