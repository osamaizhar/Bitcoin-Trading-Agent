# ⚡ Quick Setup & Validation Commands

This is your rapid-fire setup guide with all the essential commands to get your Bitcoin Trading Agent running.

## 🚀 30-Second Setup

```bash
# 1. Navigate to project
cd "/home/osama/Desktop/Apziva Projects/Project 5/Bitcoin-Trading-Agent"

# 2. Install dependencies  
pip install -r requirements.txt

# 3. Test everything
python test_dependencies.py

# 4. Start Jupyter
jupyter notebook
```

Then run notebooks: **01 → 02 → 03 → 04**

---

## 🔧 Essential Validation Commands

### Test Bitcoin Price Fetching
```bash
python -c "
import yfinance as yf
btc = yf.Ticker('BTC-USD')
print(f'✅ BTC Price: \${btc.info[\"regularMarketPrice\"]:,.2f}')
"
```

### Verify Environment Variables
```bash
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('Budget:', os.getenv('DEFAULT_BUDGET', 'NOT SET'))
print('Mode:', os.getenv('TRADING_MODE', 'NOT SET'))
print('DCA:', os.getenv('DCA_PERCENTAGE', 'NOT SET'))
"
```

### Test CoinMarketCap API (if configured)
```bash
python -c "
import os, requests
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('COINMARKETCAP_API_KEY')
if api_key and api_key != 'your_coinmarketcap_api_key_here':
    try:
        response = requests.get(
            'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest',
            headers={'X-CMC_PRO_API_KEY': api_key},
            params={'symbol': 'BTC', 'convert': 'USD'},
            timeout=10
        )
        data = response.json()
        price = data['data']['BTC']['quote']['USD']['price']
        print(f'✅ CoinMarketCap BTC: \${price:,.2f}')
    except Exception as e:
        print(f'❌ CoinMarketCap Error: {e}')
else:
    print('⚠️ CoinMarketCap API key not configured')
"
```

### Test Gmail Connection
```bash
python -c "
import os, smtplib
from dotenv import load_dotenv
load_dotenv()
email = os.getenv('GMAIL_EMAIL')
password = os.getenv('GMAIL_APP_PASSWORD')
if email and password:
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        server.quit()
        print('✅ Gmail SMTP connection successful')
    except Exception as e:
        print(f'❌ Gmail Error: {e}')
else:
    print('⚠️ Gmail credentials not configured')
"
```

### Check Technical Analysis Libraries
```bash
python -c "
import ta, pandas as pd, numpy as np
# Create sample data
prices = pd.Series(np.random.randn(30).cumsum() + 50000)
highs = prices + np.random.rand(30) * 1000
lows = prices - np.random.rand(30) * 1000
# Test indicators
rsi = ta.momentum.rsi(prices)
atr = ta.volatility.average_true_range(highs, lows, prices)
print(f'✅ RSI calculation: {rsi.iloc[-1]:.1f}')
print(f'✅ ATR calculation: {atr.iloc[-1]:.2f}')
"
```

---

## 📋 Pre-Flight Checklist

Run these commands and ensure all show ✅:

```bash
# Complete system check
python test_dependencies.py
```

**Expected output**:
```
✅ pandas               - Data manipulation and analysis
✅ numpy                - Numerical computing  
✅ yfinance             - Yahoo Finance data
✅ ta                   - Technical analysis indicators
✅ pywhatkit            - WhatsApp notifications
✅ DEFAULT_BUDGET       - Default trading budget
✅ TRADING_MODE         - Trading mode
✅ Yahoo Finance        - Current BTC price: $43,245.67
✅ Technical Analysis   - RSI, ATR, SMA calculations working
🎯 OVERALL STATUS: ✅ READY FOR DEPLOYMENT
```

---

## 🛠️ Quick Fixes for Common Issues

### Fix 1: Missing Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Fix 2: .env File Not Loading
```bash
# Check file exists
ls -la .env

# Verify content format (no spaces around =)
head -5 .env
```

### Fix 3: Jupyter Not Starting
```bash
# Install Jupyter if missing
pip install jupyter

# Alternative: Use JupyterLab
pip install jupyterlab
jupyter lab
```

### Fix 4: API Key Format Issues
```bash
# Check for extra spaces/characters
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('COINBASE_API_KEY', '')
print(f'Length: {len(key)}, Starts with: {key[:10]}...')
"
```

### Fix 5: WhatsApp Not Working
- Ensure WhatsApp Web is logged in
- Check default browser opens correctly
- Verify phone number format: +923353015576

---

## 🚨 Emergency Commands

### Stop All Notebooks
```bash
# Ctrl+C in terminal, or:
pkill -f jupyter
```

### Reset to Paper Trading
```bash
# Edit .env file
sed -i 's/TRADING_MODE=live/TRADING_MODE=paper/' .env
```

### Check Running Processes
```bash
ps aux | grep jupyter
ps aux | grep python
```

### Clear Jupyter Cache
```bash
jupyter --paths
rm -rf ~/.jupyter/runtime/*
```

---

## 🔄 Quick Restart Sequence

If something goes wrong, use this sequence:

```bash
# 1. Stop everything
pkill -f jupyter

# 2. Verify environment
python test_dependencies.py

# 3. Restart Jupyter
jupyter notebook

# 4. Run notebooks in order: 01 → 02 → 03 → 04
```

---

## 📊 Monitor Bot Health

### Check if Bot is Running
```bash
# Look for active Python processes
ps aux | grep python | grep -v grep
```

### View Recent Logs
```bash
# Check data directory for logs
ls -la data/
tail -f data/*.log  # If log files exist
```

### Quick Portfolio Check
```bash
python -c "
from src.data_collector import get_current_market_data
data = get_current_market_data()
if data:
    print(f'Current BTC: \${data[\"price\"]:,.2f}')
    print(f'RSI: {data[\"rsi_14\"]:.1f}')
    print(f'ATR: \${data[\"atr_14\"]:.2f}')
else:
    print('❌ Unable to fetch market data')
"
```

---

## 🎯 Success Indicators

### ✅ System Ready When You See:
- All dependencies test pass
- Bitcoin price fetching works
- .env variables loaded correctly
- Jupyter starts without errors
- First notebook runs completely

### ✅ Bot Working When You See:
- WhatsApp test message received
- Email test successful
- "Trading cycle started" messages
- Dashboard showing live data
- No error messages in notebook outputs

### ✅ Trading Active When You See:
- Market monitoring logs every 30 minutes
- Actual buy/sell notifications (if triggered)
- Portfolio value tracking
- Stop-loss monitoring active

---

## 🔗 Quick Links

- **Full Setup Guide**: `API_SETUP_GUIDE.md`
- **Detailed Instructions**: `GETTING_STARTED.md`
- **Architecture Guide**: `CLAUDE.md`
- **Project Overview**: `PROJECT_SUMMARY.md`

---

## 🆘 Need Help?

1. **Run**: `python test_dependencies.py`
2. **Check**: All API keys in `.env` file
3. **Verify**: TRADING_MODE is set to "paper"
4. **Ensure**: WhatsApp Web is logged in
5. **Confirm**: Sufficient balance in Coinbase (for live mode)

**Ready to trade? Your Bitcoin bot is just 4 notebook runs away!** 🚀