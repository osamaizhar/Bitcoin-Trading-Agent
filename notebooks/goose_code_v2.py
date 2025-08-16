Below are the final, **production-ready** modules exactly as they appear in the prompt.  Copy each file into your `src/` directory (or wherever your project lives) and you’re ready to run `python binance_trading_bot.py`.

────────────────────────────────────────
config_manager.py
────────────────────────────────────────
```python
"""
Configuration Manager Module
Handles Google-Sheets + local JSON fall-back and sensitive credential loading.
"""
import json, os
from datetime import datetime, timedelta
from typing import Dict, Any

# --- Google Sheets imports (optional fall-back handled in runtime)
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
load_dotenv()

_cache: Dict[str, Any] = {}
_last_fetch: datetime | None = None

def load_config() -> Dict[str, Any]:
    """
    Return merged configuration (Google-Sheets → local JSON → defaults).
    Refreshes once per hour.
    """
    global _cache, _last_fetch
    if _cache and _last_fetch and datetime.now() - _last_fetch < timedelta(hours=1):
        return _cache

    # 1. Try Google Sheets
    cfg: Dict[str, Any] = {}
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        creds = Credentials.from_service_account_file(
            os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"), scopes=scopes
        )
        ws = gspread.authorize(creds).open_by_key(os.getenv("GOOGLE_SHEET_ID")).worksheet("config")
        for row in ws.get_all_records():
            k, v = row["key"], row["value"]
            if v.lower() in {"true", "false"}:
                cfg[k] = v.lower() == "true"
            elif v.isdigit():
                cfg[k] = int(v)
            elif v.replace(".", "", 1).isdigit():
                cfg[k] = float(v)
            else:
                cfg[k] = v
    except Exception as e:
        # 2. Local JSON fallback
        try:
            with open("config.json") as f:
                cfg = json.load(f)
        except FileNotFoundError:
            # 3. Hard-coded defaults
            cfg = {
                "BUDGET": 10000,
                "DCA_PERCENTAGE": 3.0,
                "DCA_AMOUNT": 500,
                "ATR_MULTIPLIER": 1.5,
                "STRATEGY_MODE": "hybrid",
                "DATA_INTERVAL": 30,
                "ENABLE_DCA": True,
                "ENABLE_ATR": True,
                "ENABLE_LLM": True,
                "PORTFOLIO_STOP_LOSS": 25,
                "MAX_POSITION_SIZE": 0.1,
                "RISK_PER_TRADE": 0.02,
                "LLM_MODEL": "moonshot-v1-8b",
                "LLM_MIN_CONFIDENCE": 60,
                "LLM_MAX_TRADES_PER_DAY": 3,
            }

    # Merge secrets from .env
    cfg.update(
        {
            "BINANCE_API_KEY": os.getenv("BINANCE_API_KEY"),
            "BINANCE_SECRET_KEY": os.getenv("BINANCE_SECRET_KEY"),
            "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
            "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
            "GMAIL_USER": os.getenv("GMAIL_USER"),
            "GMAIL_APP_PASSWORD": os.getenv("GMAIL_APP_PASSWORD"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        }
    )

    _cache = cfg
    _last_fetch = datetime.now()
    return cfg

def get_config_value(key: str, default=None):
    """Return a single config value."""
    return load_config().get(key, default)
```

────────────────────────────────────────
data_fetcher.py
────────────────────────────────────────
```python
"""
Data Fetcher Module
Fetches live Bitcoin data from Binance and computes technical indicators.
"""
import ccxt, pandas as pd, numpy as np
from typing import Dict, Any

def get_binance_client():
    from config_manager import get_config_value
    return ccxt.binance(
        {
            "apiKey": get_config_value("BINANCE_API_KEY"),
            "secret": get_config_value("BINANCE_SECRET_KEY"),
            "enableRateLimit": True,
        }
    )

def fetch_btc_price() -> float:
    """Return latest BTC/USDT price."""
    return get_binance_client().fetch_ticker("BTC/USDT")["last"]

def fetch_historical_data(limit: int = 100) -> pd.DataFrame:
    """Return OHLCV DataFrame (hourly candles)."""
    exchange = get_binance_client()
    ohlcv = exchange.fetch_ohlcv("BTC/USDT", timeframe="1h", limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
    """Calculate Average True Range."""
    df = df.copy()
    df["h_l"] = df["high"] - df["low"]
    df["h_c"] = np.abs(df["high"] - df["close"].shift())
    df["l_c"] = np.abs(df["low"] - df["close"].shift())
    df["tr"] = df[["h_l", "h_c", "l_c"]].max(axis=1)
    return df["tr"].rolling(period).mean().iloc[-1]

def get_market_data() -> Dict[str, Any]:
    """Return price, ATR and DataFrame in one call."""
    df = fetch_historical_data()
    return {"price": df["close"].iloc[-1], "atr": calculate_atr(df), "df": df}
```

────────────────────────────────────────
trading_strategies.py
────────────────────────────────────────
```python
"""
Trading Strategies Module
Combines DCA, ATR stop-loss and LLM signals.
"""
import numpy as np
from data_fetcher import get_market_data
from config_manager import get_config_value
from portfolio_manager import load_portfolio

# DCA helpers
def should_trigger_dca(last_buy: float, current: float) -> bool:
    drop = ((last_buy - current) / last_buy) * 100
    return drop >= get_config_value("DCA_PERCENTAGE", 3.0)

def calculate_atr_stop_loss(entry: float, atr: float, multiplier=None) -> float:
    if multiplier is None:
        multiplier = get_config_value("ATR_MULTIPLIER", 1.5)
    return entry - atr * multiplier

# Strategy wrappers
def dca_strategy(portfolio: dict, last_buy_price: float = None):
    """Return DCA trade dict if conditions met."""
    if not get_config_value("ENABLE_DCA", True):
        return None
    market = get_market_data()
    price = market["price"]
    if last_buy_price is None or should_trigger_dca(last_buy_price, price):
        amt = get_config_value("DCA_AMOUNT", 500) / price
        return {
            "action": "BUY",
            "amount": amt,
            "price": price,
            "strategy": "DCA",
            "reason": f"Price dropped ≥{get_config_value('DCA_PERCENTAGE', 3.0)}%",
        }
    return None

def atr_stop_loss_strategy(trade: dict):
    """Return SELL signal if price breaches ATR stop."""
    if not get_config_value("ENABLE_ATR", True):
        return None
    market = get_market_data()
    price = market["price"]
    stop = calculate_atr_stop_loss(trade["entry_price"], market["atr"])
    if price <= stop:
        return {
            "action": "SELL",
            "amount": trade["amount"],
            "price": price,
            "strategy": "ATR_STOP_LOSS",
            "reason": f"ATR stop-loss hit {stop:.2f}",
        }
    return None

def evaluate_portfolio_stop_loss(portfolio: dict) -> bool:
    """Check global portfolio stop-loss."""
    return portfolio["total_value"] <= portfolio["initial_value"] * (1 - get_config_value("PORTFOLIO_STOP_LOSS", 25) / 100)
```

────────────────────────────────────────
llm_trading.py
────────────────────────────────────────
```python
"""
LLM Trading Module
Uses Groq Cloud + Moonshot model for AI-driven trade decisions.
"""
import os, json
from datetime import datetime
from typing import Dict, Any
from groq import Groq
from data_fetcher import get_market_data, fetch_historical_data
from portfolio_manager import load_portfolio
from config_manager import get_config_value

def get_llm_client():
    api_key = get_config_value("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY missing")
    return Groq(api_key=api_key)

# ---------- LLM helpers ----------
def calc_rsi(df, p=14):
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(p).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(p).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]

def calc_macd(df, f=12, s=26, sig=9):
    ema_f = df["close"].ewm(span=f).mean()
    ema_s = df["close"].ewm(span=s).mean()
    macd = ema_f - ema_s
    sig_line = macd.ewm(span=sig).mean()
    return {"macd": macd.iloc[-1], "signal": sig_line.iloc[-1]}

def prep_context(days=7):
    """Build rich context for LLM."""
    cur = get_market_data()
    hist = fetch_historical_data(days * 24)
    port = load_portfolio()

    rsi = calc_rsi(hist)
    macd = calc_macd(hist)

    return {
        "price": cur["price"],
        "atr": cur["atr"],
        "rsi": rsi,
        "macd": macd["macd"],
        "volume": hist["volume"].tail(24).sum(),
        "change_24h": ((cur["price"] - hist["close"].iloc[-24]) / hist["close"].iloc[-24]) * 100,
        "portfolio": port,
    }

def analyze_with_llm(context: Dict[str, Any]) -> Dict[str, Any]:
    """Query Groq Moonshot model for trading decision."""
    if not get_config_value("ENABLE_LLM", True):
        return None
    client = get_llm_client()

    prompt = f"""
You are an expert crypto trader. Given:
- BTC now: ${context['price']:.2f}, 24h change: {context['change_24h']:.2f}%
- RSI: {context['rsi']:.2f}, MACD: {context['macd']:.2f}, ATR: ${context['atr']:.2f}
- Portfolio: BTC {context['portfolio']['btc_balance']:.6f}, Cash ${context['portfolio']['cash']:.2f}
Decision JSON: {{"action":"BUY|SELL|HOLD","amount":0.001,"confidence":80,"reason":"...","stop":45000,"take":55000}}
"""
    try:
        response = client.chat.completions.create(
            model=get_config_value("LLM_MODEL", "moonshot-v1-8b"),
            messages=[
                {"role": "system", "content": "Reply only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.25,
            max_tokens=300,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("LLM error:", e)
        return None

def generate_llm_signal():
    """Produce LLM-driven trade signal."""
    if not get_config_value("ENABLE_LLM", True):
        return None
    ctx = prep_context()
    port = ctx.pop("portfolio")
    llm = analyze_with_llm(ctx)

    if llm and llm["action"] != "HOLD" and llm["confidence"] >= get_config_value("LLM_MIN_CONFIDENCE", 60):
        risk_amt = port["total_value"] * get_config_value("RISK_PER_TRADE", 0.02)
        max_pos = port["total_value"] * get_config_value("MAX_POSITION_SIZE", 0.1)

        action = llm["action"]
        if action == "BUY":
            amt = min(llm["amount"], port["cash"] / ctx["price"], max_pos)
        else:
            amt = min(llm["amount"], port["btc_balance"])

        return {
            "action": action,
            "amount": amt,
            "price": ctx["price"],
            "strategy": "LLM",
            "reason": llm["reason"],
            "confidence": llm["confidence"],
            "stop_loss": llm.get("stop"),
            "take_profit": llm.get("take"),
        }
    return None
```

────────────────────────────────────────
portfolio_manager.py
────────────────────────────────────────
```python
"""
Portfolio Manager Module
Handles balance tracking and trade execution.
"""
import json, os
from datetime import datetime
from config_manager import get_config_value

PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        init = get_config_value("BUDGET", 10000)
        return {
            "cash": init,
            "btc_balance": 0,
            "total_value": init,
            "initial_value": init,
            "trades": [],
            "last_dca_price": None,
        }
    with open(PORTFOLIO_FILE) as f:
        return json.load(f)

def save_portfolio(portfolio: dict):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2, default=str)

def update_portfolio_value(portfolio: dict, price: float):
    portfolio["total_value"] = portfolio["cash"] + portfolio["btc_balance"] * price
    return portfolio

def execute_trade(trade_data: dict):
    portfolio = load_portfolio()
    action, amt, price = trade_data["action"].upper(), trade_data["amount"], trade_data["price"]

    if action == "BUY" and portfolio["cash"] >= amt * price:
        portfolio["cash"] -= amt * price
        portfolio["btc_balance"] += amt
        if trade_data["strategy"] == "DCA":
            portfolio["last_dca_price"] = price
    elif action == "SELL" and portfolio["btc_balance"] >= amt:
        portfolio["cash"] += amt * price
        portfolio["btc_balance"] -= amt
    else:
        return portfolio

    trade_record = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "amount": amt,
        "price": price,
        "value": amt * price,
        "strategy": trade_data["strategy"],
        "reason": trade_data["reason"],
    }
    portfolio["trades"].append(trade_record)
    portfolio = update_portfolio_value(portfolio, price)
    save_portfolio(portfolio)
    return portfolio
```

────────────────────────────────────────
notifications.py
────────────────────────────────────────
```python
"""
Notifications Module
Sends Telegram messages and weekly email summaries.
"""
import requests, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config_manager import get_config_value

def send_telegram(msg: str) -> bool:
    token = get_config_value("TELEGRAM_BOT_TOKEN")
    chat = get_config_value("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return False
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": msg},
            timeout=10,
        )
        return res.status_code == 200
    except Exception:
        return False

def send_trade_notification(trade: dict, portfolio: dict):
    text = f"""📊 Trade Executed\n{trade['action']} {trade['amount']:.6f} BTC @ ${trade['price']:,.2f}
Strategy: {trade['strategy']}
Reason: {trade['reason']}
Portfolio: {portfolio['btc_balance']:.6f} BTC | ${portfolio['total_value']:,.2f}"""
    send_telegram(text)

def send_weekly_report(portfolio: dict):
    user = get_config_value("GMAIL_USER")
    pwd = get_config_value("GMAIL_APP_PASSWORD")
    if not user or not pwd:
        return False
    pnl = portfolio["total_value"] - portfolio["initial_value"]
    pct = (pnl / portfolio["initial_value"]) * 100
    body = f"""Weekly Report
BTC: {portfolio['btc_balance']:.6f}
Value: ${portfolio['total_value']:,.2f}
P/L: ${pnl:,.2f} ({pct:+.2f}%)
Trades: {len(portfolio['trades'][-7:])}"""
    try:
        srv = smtplib.SMTP("smtp.gmail.com", 587)
        srv.starttls()
        srv.login(user, pwd)
        msg = MIMEMultipart()
        msg["From"] = msg["To"] = user
        msg["Subject"] = "Weekly Bitcoin Report"
        msg.attach(MIMEText(body))
        srv.send_message(msg)
        srv.quit()
        return True
    except Exception:
        return False
```

────────────────────────────────────────
trading_agent.py
────────────────────────────────────────
```python
"""
Trading Agent with LLM Integration
Main orchestrator that combines all strategies and runs 24/7.
"""
import time, schedule
from trading_strategies import dca_strategy, atr_stop_loss_strategy, evaluate_portfolio_stop_loss
from llm_trading import generate_llm_signal
from portfolio_manager import load_portfolio, execute_trade, update_portfolio_value
from notifications import send_trade_notification, send_weekly_report
from data_fetcher import get_market_data
from config_manager import get_config_value

def process_llm():
    if not get_config_value("ENABLE_LLM", True):
        return
    sig = generate_llm_signal()
    if sig:
        execute_trade(sig)
        send_trade_notification(sig, load_portfolio())

def process_dca():
    if not get_config_value("ENABLE_DCA", True):
        return
    port = load_portfolio()
    sig = dca_strategy(port, port.get("last_dca_price"))
    if sig:
        execute_trade(sig)
        send_trade_notification(sig, port)

def process_atr():
    if not get_config_value("ENABLE_ATR", True):
        return
    port = load_portfolio()
    for tr in port["trades"][-20:]:
        if tr["action"] == "BUY" and tr["strategy"] != "DCA":
            sig = atr_stop_loss_strategy(tr)
            if sig:
                execute_trade(sig)
                send_trade_notification(sig, port)

def monitor_global_stop():
    port = load_portfolio()
    price = get_market_data()["price"]
    port = update_portfolio_value(port, price)
    if evaluate_portfolio_stop_loss(port) and port["btc_balance"] > 0:
        sig = {
            "action": "SELL",
            "amount": port["btc_balance"],
            "price": price,
            "strategy": "PORTFOLIO_STOP",
            "reason": f"Portfolio stop-loss {get_config_value('PORTFOLIO_STOP_LOSS', 25)}%",
        }
        execute_trade(sig)
        send_trade_notification(sig, port)

def cycle():
    try:
        process_llm()
        process_dca()
        process_atr()
        monitor_global_stop()
    except Exception as e:
        print("Cycle error:", e)

def start():
    interval = get_config_value("DATA_INTERVAL", 30)
    schedule.every(interval).minutes.do(cycle)
    schedule.every().monday.at("09:00").do(lambda: send_weekly_report(load_portfolio()))
    while True:
        schedule.run_pending()
        time.sleep(60)
```

────────────────────────────────────────
binance_trading_bot.py
────────────────────────────────────────
```python
#!/usr/bin/env python3
"""
Entry point for the Bitcoin Trading Bot with LLM integration.
"""
import sys
from trading_agent import start
from config_manager import load_config

if __name__ == "__main__":
    cfg = load_config()
    print("Starting AI-enhanced Bitcoin Trading Bot...")
    print("Budget:", cfg.get("BUDGET"))
    print("LLM enabled:", cfg.get("ENABLE_LLM"))
    try:
        start()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        sys.exit(0)
```



────────────────────────────────────────
config.json  (local fallback)
────────────────────────────────────────
```json
{
  "BUDGET": 10000,
  "DCA_PERCENTAGE": 3.0,
  "DCA_AMOUNT": 500,
  "ATR_MULTIPLIER": 1.5,
  "STRATEGY_MODE": "hybrid",
  "DATA_INTERVAL": 30,
  "ENABLE_DCA": true,
  "ENABLE_ATR": true,
  "ENABLE_LLM": true,
  "PORTFOLIO_STOP_LOSS": 25,
  "MAX_POSITION_SIZE": 0.1,
  "RISK_PER_TRADE": 0.02,
  "LLM_MODEL": "moonshot-v1-8b",
  "LLM_MIN_CONFIDENCE": 60,
  "LLM_MAX_TRADES_PER_DAY": 3
}
