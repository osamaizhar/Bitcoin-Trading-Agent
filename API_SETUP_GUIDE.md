# 🔑 API Keys Setup Guide

This guide provides step-by-step instructions for obtaining all the API keys needed for the Bitcoin Trading Agent.

## 🚨 IMPORTANT SECURITY NOTES

- **NEVER share your API keys** with anyone
- **Start with paper trading** mode to test everything safely
- **Enable 2FA** on all financial accounts
- **Use strong, unique passwords**
- **Monitor your accounts** regularly for unauthorized activity

---

## 1. 🏦 Coinbase Advanced Trade API (REQUIRED for Live Trading)

### Purpose
Execute actual Bitcoin buy/sell orders

### Steps to Get API Keys

1. **Create Account & Verify**
   - Go to [coinbase.com](https://coinbase.com)
   - Sign up or log in to your account
   - Complete identity verification if not done

2. **Access Coinbase Advanced Trade**
   - Visit [pro.coinbase.com](https://pro.coinbase.com) or click "Advanced Trade" in main Coinbase

3. **Create API Key**
   - Click your profile icon → Settings
   - Go to "API" section
   - Click "New API Key"

4. **Configure Permissions**
   - ✅ **View** - Read account info and balances
   - ✅ **Trade** - Place buy/sell orders
   - ✅ **Transfer** - Move funds (if needed)
   - ❌ Avoid giving unnecessary permissions

5. **Security Settings**
   - Add your IP address to whitelist (recommended)
   - Set passphrase if required
   - Save the API Key and Secret immediately

6. **Copy to .env file**
   ```bash
   COINBASE_API_KEY=your_actual_api_key_here
   COINBASE_API_SECRET=your_actual_secret_here
   ```

### 💰 Funding Your Account
- Transfer funds to your Coinbase account
- Ensure you have USD balance for trading
- Start small for testing!

---

## 2. 📧 Gmail App Password (REQUIRED for Email Reports)

### Purpose
Send weekly HTML performance reports

### Steps to Get App Password

1. **Enable 2-Step Verification**
   - Go to [myaccount.google.com](https://myaccount.google.com)
   - Security → 2-Step Verification
   - Follow setup if not already enabled

2. **Generate App Password**
   - Still in Security section
   - Scroll to "App passwords"
   - Click "App passwords"

3. **Create New App Password**
   - Select app: "Mail"
   - Select device: "Other (custom name)"
   - Name it: "Bitcoin Trading Bot"
   - Click "Generate"

4. **Copy 16-Character Password**
   - Google will show a 16-character password
   - Copy this immediately (won't be shown again)
   - This is NOT your regular Gmail password

5. **Add to .env file**
   ```bash
   GMAIL_EMAIL=your_email@gmail.com
   GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
   ```

### 📨 What You'll Receive
- Weekly reports every Monday at 9 AM
- Portfolio performance summaries
- Recent trades overview
- Strategy configuration status

---

## 3. 💹 CoinMarketCap API (OPTIONAL - Backup Price Data)

### Purpose
Alternative Bitcoin price source for redundancy

### Steps to Get API Key

1. **Create Account**
   - Visit [coinmarketcap.com/api](https://coinmarketcap.com/api)
   - Sign up for free account

2. **Access Developer Portal**
   - Go to "My Account" → "API"
   - Click "Create new API Key"

3. **Choose Plan**
   - **Basic Plan (Free)**: 10,000 calls/month
   - Perfect for this bot's needs

4. **Copy API Key**
   - Copy your API key from the dashboard

5. **Add to .env file**
   ```bash
   COINMARKETCAP_API_KEY=your_cmc_api_key_here
   ```

### 📊 Free Plan Limits
- 10,000 API calls per month
- Basic cryptocurrency data
- Sufficient for price monitoring

---

## 4. 📊 Google Sheets API (OPTIONAL - Dynamic Configuration)

### Purpose
Change trading parameters without editing code

### Steps to Set Up

1. **Create Google Cloud Project**
   - Go to [console.cloud.google.com](https://console.cloud.google.com)
   - Create new project or select existing

2. **Enable Google Sheets API**
   - In project dashboard → "Enable APIs and Services"
   - Search for "Google Sheets API"
   - Click "Enable"

3. **Create Service Account**
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Name: "Bitcoin Trading Bot"
   - Description: "API access for trading bot configuration"

4. **Download JSON Key**
   - Click on created service account
   - Go to "Keys" tab
   - "Add Key" → "Create new key" → JSON
   - Download and save securely

5. **Create Configuration Spreadsheet**
   - Create new Google Sheet
   - Name first tab "Config"
   - Add headers: Parameter | Value | Description
   - Share sheet with service account email (from JSON file)

6. **Add to .env file**
   ```bash
   GOOGLE_SHEETS_SERVICE_ACCOUNT=/path/to/service-account.json
   GOOGLE_SHEETS_ID=your_sheet_id_from_url
   ```

### 📋 Sample Configuration Sheet

| Parameter | Value | Description |
|-----------|-------|-------------|
| budget | 1000 | Total trading budget in USD |
| dca_percentage | 3.0 | DCA trigger percentage drop |
| atr_multiplier | 1.5 | ATR stop-loss multiplier |
| trading_mode | paper | paper/live trading mode |

---

## 5. 🤖 Groq Cloud API (OPTIONAL - AI Market Insights with Llama 3.3 70B)

### Purpose
Generate AI-powered market analysis and insights using Llama 3.3 70B Versatile model

### Steps to Get API Key

1. **Create Groq Cloud Account**
   - Visit [console.groq.com](https://console.groq.com)
   - Sign up or log in

2. **Access API Keys**
   - Go to "API Keys" section in the console
   - Free tier available with generous limits
   - No credit card required for basic usage

3. **Create API Key**
   - Click "Create API Key"
   - Name it: "Bitcoin Trading Bot"
   - Copy the key immediately (starts with gsk_)

4. **Add to .env file**
   ```bash
   GROQ_API_KEY=gsk_your_groq_api_key_here
   ```

### 💸 Cost Considerations
- Free tier with generous limits
- Fast inference with Llama 3.3 70B model
- No billing alerts needed for basic usage

---

## 6. 📱 WhatsApp Setup (Automatic via PyWhatKit)

### Purpose
Instant trade notifications to +923353015576

### Requirements

1. **WhatsApp Web Login**
   - Must be logged into WhatsApp Web on the server
   - PyWhatKit opens browser tabs to send messages
   - Keep session active

2. **Phone Number**
   - Currently hardcoded to +923353015576
   - Rate limited to prevent spam (30-second intervals)

### What You'll Receive
- 🟢 DCA buy notifications
- 🔴 Stop-loss alerts
- 📊 Daily/weekly summaries
- ⚠️ Error notifications

---

## 🧪 Testing Your Setup

### 1. Run Dependency Test
```bash
python test_dependencies.py
```

### 2. Check Each API Connection
```bash
# Test in Python
python -c "
import yfinance as yf
btc = yf.Ticker('BTC-USD')
print(f'BTC Price: ${btc.info[\"regularMarketPrice\"]:,.2f}')
"
```

### 3. Validate Environment
```bash
# Check if .env file is loaded
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('Budget:', os.getenv('DEFAULT_BUDGET'))
print('Mode:', os.getenv('TRADING_MODE'))
"
```

---

## 🚀 Getting Started Checklist

- [ ] ✅ Created Coinbase account and got API keys
- [ ] ✅ Generated Gmail app password
- [ ] ✅ Updated .env file with all keys
- [ ] ✅ Ran `python test_dependencies.py` successfully
- [ ] ✅ Verified TRADING_MODE is set to "paper"
- [ ] ✅ WhatsApp Web is logged in (for notifications)
- [ ] ✅ Tested basic Bitcoin price retrieval
- [ ] ✅ Ready to run notebooks in sequence

---

## 🆘 Need Help?

1. **Check test_dependencies.py output** for specific issues
2. **Verify API key format** - no extra spaces or characters
3. **Ensure .env file is in project root directory**
4. **Start with paper trading** mode for safety
5. **Check API documentation** if getting authentication errors

## 🔒 Security Best Practices

1. **Never commit .env file** to git (already in .gitignore)
2. **Use read-only API keys** where possible
3. **Set IP restrictions** on API keys when available
4. **Monitor account activity** regularly
5. **Rotate API keys** periodically
6. **Start with small amounts** for testing
7. **Keep backups** of important configurations

Ready to start trading? Run the notebooks in order: 01 → 02 → 03 → 04! 🚀