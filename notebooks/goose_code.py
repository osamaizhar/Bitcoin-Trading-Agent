# config_manager.py
"""
Configuration Manager Module
[... docstring ...]
"""
import json, os, time, gspread
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
load_dotenv()


_config_cache = None
_last_update = None

def load_config():
    """Load configuration from Google Sheets or local JSON fallback."""
    global _config_cache, _last_update
    if _config_cache and _last_update and datetime.now() - _last_update < timedelta(hours=1):
        return _config_cache
    
    config = {}
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        creds = Credentials.from_service_account_file(os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json'), scopes=scopes)
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(os.getenv('GOOGLE_SHEET_ID'))
        data = spreadsheet.worksheet("config").get_all_records()
        
        for row in data:
            key, value = row['key'], row['value']
            if value.lower() in ['true', 'false']: value = value.lower() == 'true'
            elif value.isdigit(): value = int(value)
            elif value.replace('.', '').isdigit(): value = float(value)
            config[key] = value
    except:
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except:
            config = {'BUDGET': 10000, 'DCA_PERCENTAGE': 3.0, 'DCA_AMOUNT': 500, 'ATR_MULTIPLIER': 1.5, 'STRATEGY_MODE': 'hybrid', 'DATA_INTERVAL': 30, 'ENABLE_DCA': True, 'ENABLE_ATR': True, 'ENABLE_LLM': True, 'PORTFOLIO_STOP_LOSS': 25, 'MAX_POSITION_SIZE': 0.1, 'RISK_PER_TRADE': 0.02}
    
    config.update({
        'BINANCE_API_KEY': os.getenv('BINANCE_API_KEY'), 'BINANCE_SECRET_KEY': os.getenv('BINANCE_SECRET_KEY'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'), 'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'GMAIL_USER': os.getenv('GMAIL_USER'), 'GMAIL_APP_PASSWORD': os.getenv('GMAIL_APP_PASSWORD')
    })
    
    _config_cache = config
    _last_update = datetime.now()
    return config

def get_config_value(key, default=None):
    """Get a specific configuration value."""
    return load_config().get(key, default)


# Test code (keep commented):
if __name__ == "__main__":
    print("Testing config_manager...")
    config = load_config()
    print("Available config keys:", list(config.keys()))
    print("DCA_AMOUNT:", get_config_value('DCA_AMOUNT', 500))
    print("BINANCE_API_KEY exists:", bool(get_config_value('BINANCE_API_KEY')))


# ===================================================================================
# data_fetcher.py
"""
Data Fetcher Module
[... docstring ...]
"""
import ccxt, pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Test code (keep commented):
# if __name__ == "__main__":
#     print("Testing data_fetcher...")
#     try:
#         price = fetch_btc_price()
#         print(f"Current BTC price: ${price}")
#         
#         data = get_market_data()
#         print(f"BTC: ${data['price']}")
#         print(f"ATR: ${data['atr']:.2f}")
#         print(f"Data shape: {data['df'].shape}")
#     except Exception as e:
#         print("Error:", str(e))

def get_binance_client():
    """Create and return authenticated Binance client."""
    from config_manager import get_config_value
    return ccxt.binance({'apiKey': get_config_value('BINANCE_API_KEY'), 'secret': get_config_value('BINANCE_SECRET_KEY'), 'enableRateLimit': True})

def fetch_btc_price():
    """Fetch current BTC/USDT price."""
    exchange = get_binance_client()
    return exchange.fetch_ticker('BTC/USDT')['last']

def fetch_historical_data(limit=100):
    """Fetch historical OHLCV data."""
    exchange = get_binance_client()
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def calculate_atr(df, period=14):
    """Calculate Average True Range indicator."""
    df = df.copy()
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = np.abs(df['high'] - df['close'].shift())
    df['low_close'] = np.abs(df['low'] - df['close'].shift())
    df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['atr'] = df['tr'].rolling(window=period).mean()
    return df['atr'].iloc[-1]

def get_market_data():
    """Get complete market data package."""
    df = fetch_historical_data()
    return {'price': df['close'].iloc[-1], 'atr': calculate_atr(df), 'df': df}

# ===================================================================================
# trading_strategies.py
"""
Trading Strategies Module
[... docstring ...]
"""
import numpy as np
from datetime import datetime
from data_fetcher import get_market_data
from config_manager import get_config_value

# Test code (keep commented):
# if __name__ == "__main__":
#     print("Testing trading_strategies...")
#     portfolio = {'initial_value': 10000, 'total_value': 9500}
#     last_buy = 50000
#     
#     # Test DCA
#     trade = dca_strategy(portfolio, last_buy)
#     print("DCA trade:", trade)
#     
#     # Test ATR stop loss
#     test_trade = {'entry_price': 50000, 'amount': 0.001, 'strategy': 'TEST'}
#     stop_loss = atr_stop_loss_strategy(test_trade)
#     print("Stop loss:", stop_loss)
#     
#     # Test portfolio stop loss
#     should_stop = evaluate_portfolio_stop_loss(portfolio)
#     print("Portfolio stop loss:", should_stop)

def should_trigger_dca(last_buy_price, current_price):
    """Check if DCA should trigger based on price drop."""
    price_drop = ((last_buy_price - current_price) / last_buy_price) * 100
    return price_drop >= get_config_value('DCA_PERCENTAGE', 3.0)

def calculate_atr_stop_loss(entry_price, atr, multiplier=None):
    """Calculate ATR-based stop-loss price."""
    if multiplier is None: multiplier = get_config_value('ATR_MULTIPLIER', 1.5)
    return entry_price - (atr * multiplier)

def dca_strategy(portfolio, last_buy_price=None):
    """Execute Dollar-Cost Averaging strategy."""
    if not get_config_value('ENABLE_DCA', True): return None
    
    market_data = get_market_data()
    if last_buy_price is None or should_trigger_dca(last_buy_price, market_data['price']):
        dca_amount = get_config_value('DCA_AMOUNT', 500)
        return {'action': 'BUY', 'amount': dca_amount / market_data['price'], 'price': market_data['price'], 'strategy': 'DCA', 'reason': f'Price dropped {get_config_value("DCA_PERCENTAGE", 3)}%'}

def atr_stop_loss_strategy(trade):
    """Check if ATR stop-loss should trigger."""
    if not get_config_value('ENABLE_ATR', True): return None
    
    market_data = get_market_data()
    stop_loss_price = calculate_atr_stop_loss(trade['entry_price'], market_data['atr'])
    
    if market_data['price'] <= stop_loss_price:
        return {'action': 'SELL', 'amount': trade['amount'], 'price': market_data['price'], 'strategy': 'ATR_STOP_LOSS', 'reason': f'Stop loss triggered at {stop_loss_price:.2f}'}

def evaluate_portfolio_stop_loss(portfolio):
    """Check if portfolio-level stop-loss should trigger."""
    return portfolio['total_value'] <= portfolio['initial_value'] * (1 - get_config_value('PORTFOLIO_STOP_LOSS', 25)/100)

# ===================================================================================
# portfolio_manager.py
"""
Portfolio Manager Module
[... docstring ...]
"""
import json, os
from datetime import datetime
from config_manager import get_config_value

# Test code (keep commented):
# if __name__ == "__main__":
#     print("Testing portfolio_manager...")
#     portfolio = load_portfolio()
#     print("Initial portfolio:", portfolio)
#     
#     # Test buy
#     trade = {'action': 'BUY', 'amount': 0.001, 'price': 50000, 'strategy': 'TEST', 'reason': 'Test buy'}
#     portfolio = execute_trade(trade)
#     print("After buy:", portfolio['btc_balance'], portfolio['cash'])
#     
#     # Test sell
#     trade = {'action': 'SELL', 'amount': 0.0005, 'price': 51000, 'strategy': 'TEST', 'reason': 'Test sell'}
#     portfolio = execute_trade(trade)
#     print("After sell:", portfolio['btc_balance'], portfolio['cash'])

PORTFOLIO_FILE = 'portfolio.json'

def load_portfolio():
    """Load current portfolio state from file."""
    if not os.path.exists(PORTFOLIO_FILE):
        initial_budget = get_config_value('BUDGET', 10000)
        return {'cash': initial_budget, 'btc_balance': 0, 'total_value': initial_budget, 'initial_value': initial_budget, 'trades': [], 'last_dca_price': None}
    
    with open(PORTFOLIO_FILE, 'r') as f:
        return json.load(f)

def save_portfolio(portfolio):
    """Save portfolio state to file."""
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2, default=str)

def update_portfolio_value(portfolio, current_price):
    """Update portfolio value based on current BTC price."""
    portfolio['total_value'] = portfolio['cash'] + (portfolio['btc_balance'] * current_price)
    return portfolio

def execute_trade(trade_data):
    """Execute a trade and update portfolio."""
    portfolio = load_portfolio()
    action, amount, price = trade_data['action'].upper(), trade_data['amount'], trade_data['price']
    
    if action == 'BUY' and portfolio['cash'] >= amount * price:
        portfolio['cash'] -= amount * price
        portfolio['btc_balance'] += amount
        if trade_data['strategy'] == 'DCA': portfolio['last_dca_price'] = price
    
    elif action == 'SELL' and portfolio['btc_balance'] >= amount:
        portfolio['cash'] += amount * price
        portfolio['btc_balance'] -= amount
    
    trade_record = {'timestamp': datetime.now().isoformat(), 'action': action, 'amount': amount, 'price': price, 'value': amount * price, 'strategy': trade_data['strategy'], 'reason': trade_data['reason']}
    portfolio['trades'].append(trade_record)
    portfolio = update_portfolio_value(portfolio, price)
    save_portfolio(portfolio)
    return portfolio

# ===================================================================================
# notifications.py
"""
Notifications Module
[... docstring ...]
"""
import requests, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config_manager import get_config_value

# Test code (keep commented):
# if __name__ == "__main__":
#     print("Testing notifications...")
#     test_trade = {'action': 'BUY', 'amount': 0.001, 'price': 50000, 'value': 50, 'strategy': 'TEST', 'reason': 'Test'}
#     test_portfolio = {'btc_balance': 0.001, 'total_value': 10050}
#     
#     # Test Telegram (will fail without credentials)
#     success = send_trade_notification(test_trade, test_portfolio)
#     print("Telegram notification sent:", success)
#     
#     # Test email (will fail without credentials)
#     success = send_weekly_report(test_portfolio)
#     print("Email report sent:", success)

def send_telegram_message(message):
    """Send message via Telegram bot."""
    token = get_config_value('TELEGRAM_BOT_TOKEN')
    chat_id = get_config_value('TELEGRAM_CHAT_ID')
    if not token or not chat_id: return False
    
    try:
        response = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={'chat_id': chat_id, 'text': message})
        return response.status_code == 200
    except: return False

def send_trade_notification(trade, portfolio):
    """Send trade notification via Telegram."""
    message = f"""📊 Trade Executed\n\nAction: {trade['action']}\nAmount: {trade['amount']:.6f} BTC\nPrice: ${trade['price']:,.2f}\nValue: ${trade['value']:,.2f}\nStrategy: {trade['strategy']}\nReason: {trade['reason']}\n\nPortfolio: {portfolio['btc_balance']:.6f} BTC | ${portfolio['total_value']:,.2f}"""
    send_telegram_message(message)

def send_weekly_report(portfolio):
    """Send weekly portfolio report via email."""
    gmail_user = get_config_value('GMAIL_USER')
    gmail_password = get_config_value('GMAIL_APP_PASSWORD')
    if not gmail_user or not gmail_password: return False
    
    profit_loss = portfolio['total_value'] - portfolio['initial_value']
    profit_loss_pct = (profit_loss / portfolio['initial_value']) * 100
    
    message = f"""Weekly Bitcoin Trading Report\n\nPortfolio Summary:\n- BTC Balance: {portfolio['btc_balance']:.6f}\n- Total Value: ${portfolio['total_value']:,.2f}\n- Initial Investment: ${portfolio['initial_value']:,.2f}\n- P/L: ${profit_loss:,.2f} ({profit_loss_pct:+.2f}%)\n\nTrades This Week: {len(portfolio['trades'][-7:])}"""
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        msg = MIMEMultipart()
        msg['From'] = msg['To'] = gmail_user
        msg['Subject'] = 'Weekly Bitcoin Trading Report'
        msg.attach(MIMEText(message, 'plain'))
        server.send_message(msg)
        server.quit()
        return True
    except: return False

# ===================================================================================
# trading_agent.py
"""
Trading Agent Module
[... docstring ...]
"""
import time, schedule
from trading_strategies import dca_strategy, atr_stop_loss_strategy, evaluate_portfolio_stop_loss
from portfolio_manager import load_portfolio, execute_trade, update_portfolio_value
from notifications import send_trade_notification, send_weekly_report
from data_fetcher import get_market_data
from config_manager import get_config_value

# Test code (keep commented):
# if __name__ == "__main__":
#     print("Testing trading_agent...")
#     print("Running single trading cycle...")
#     run_trading_cycle()
#     
#     # Test portfolio monitoring
#     portfolio = load_portfolio()
#     print("Portfolio value:", portfolio['total_value'])
#     print("Should stop loss:", evaluate_portfolio_stop_loss(portfolio))

def process_dca_strategy():
    """Process DCA strategy based on market conditions."""
    if not get_config_value('ENABLE_DCA', True): return
    portfolio = load_portfolio()
    trade = dca_strategy(portfolio, portfolio.get('last_dca_price'))
    if trade:
        portfolio = execute_trade(trade)
        send_trade_notification(trade, portfolio)

def process_atr_strategy():
    """Process ATR stop-loss strategy for active positions."""
    if not get_config_value('ENABLE_ATR', True): return
    portfolio = load_portfolio()
    for trade in portfolio['trades'][-20:]:
        if trade['action'] == 'BUY' and trade['strategy'] != 'DCA':
            stop_loss = atr_stop_loss_strategy(trade)
            if stop_loss:
                portfolio = execute_trade(stop_loss)
                send_trade_notification(stop_loss, portfolio)

def monitor_portfolio():
    """Monitor portfolio for stop-loss conditions."""
    portfolio = load_portfolio()
    market_data = get_market_data()
    portfolio = update_portfolio_value(portfolio, market_data['price'])
    
    if evaluate_portfolio_stop_loss(portfolio) and portfolio['btc_balance'] > 0:
        trade = {'action': 'SELL', 'amount': portfolio['btc_balance'], 'price': market_data['price'], 'strategy': 'PORTFOLIO_STOP', 'reason': f'Portfolio stop-loss triggered ({get_config_value("PORTFOLIO_STOP_LOSS", 25)}%)'}
        portfolio = execute_trade(trade)
        send_trade_notification(trade, portfolio)

def run_trading_cycle():
    """Run one complete trading cycle."""
    try:
        process_dca_strategy()
        process_atr_strategy()
        monitor_portfolio()
    except Exception as e:
        print(f"Trading error: {e}")

def start_trading():
    """Start the trading agent."""
    interval = get_config_value('DATA_INTERVAL', 30)
    schedule.every(interval).minutes.do(run_trading_cycle)
    schedule.every().monday.at("09:00").do(lambda: send_weekly_report(load_portfolio()))
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# ===================================================================================
# binance_trading_bot.py
"""
Binance Trading Bot - Main Entry Point
[... docstring ...]
"""
import sys
from trading_agent import start_trading
from config_manager import load_config

# Test code (keep commented):
# if __name__ == "__main__":
#     print("Testing complete system...")
#     config = load_config()
#     print("Config loaded successfully")
#     print("Testing modules...")
#     
#     # Test each module
#     try:
#         from config_manager import load_config
#         print("✓ config_manager")
#         from data_fetcher import get_market_data
#         print("✓ data_fetcher")
#         from trading_strategies import dca_strategy
#         print("✓ trading_strategies")
#         from portfolio_manager import load_portfolio
#         print("✓ portfolio_manager")
#         from notifications import send_telegram_message
#         print("✓ notifications")
#         print("All modules imported successfully!")
#     except Exception as e:
#         print("Import error:", str(e))
#     
#     # Uncomment to run actual trading:
#     # start_trading()

if __name__ == "__main__":
    print("Starting Bitcoin Trading Bot...")
    config = load_config()
    print(f"Initial budget: ${config.get('BUDGET', 10000)}")
    print(f"Strategy mode: {config.get('STRATEGY_MODE', 'hybrid')}")
    
    try:
        start_trading()
    except KeyboardInterrupt:
        print("\nTrading bot stopped by user")
        sys.exit(0)
