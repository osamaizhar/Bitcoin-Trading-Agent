# 🚀 Getting Started Guide

This guide walks you through running the Bitcoin Trading Agent from start to finish.

## 📋 Prerequisites

1. ✅ **Python 3.9+** installed
2. ✅ **All API keys** obtained (see `API_SETUP_GUIDE.md`)
3. ✅ **.env file** configured with your keys
4. ✅ **Dependencies** installed (`pip install -r requirements.txt`)
5. ✅ **WhatsApp Web** logged in (for notifications)

---

## 🔄 Notebook Execution Sequence

Run the notebooks in **this exact order** for proper system setup:

### 1️⃣ Data Analysis Notebook
**File**: `notebooks/01_data_analysis.ipynb`

**Purpose**: 
- Collect Bitcoin price data from multiple sources
- Perform technical analysis (RSI, ATR, moving averages)
- Validate data collection systems

**What it does**:
- Tests Yahoo Finance, CoinMarketCap, and Investing.com connections
- Downloads historical Bitcoin data (6 months default)
- Calculates technical indicators
- Creates price charts and analysis
- Validates Crawl4AI web scraping

**Expected output**:
- Current Bitcoin price displayed
- Historical price charts
- Technical indicator plots (RSI, ATR, SMA)
- Data source status (✅/❌ for each API)

**Run time**: 2-3 minutes

---

### 2️⃣ Trading System Notebook  
**File**: `notebooks/02_trading_system.ipynb`

**Purpose**:
- Implement DCA and ATR trading strategies
- Test Coinbase API integration
- Simulate trading scenarios

**What it does**:
- Loads configuration from .env file
- Initializes DCA (Dollar-Cost Averaging) strategy
- Sets up ATR (Average True Range) stop-loss system
- Tests Coinbase API connectivity
- Runs trading simulations in paper mode
- Calculates position sizes and risk metrics

**Expected output**:
- Strategy configuration summary
- Simulated trade examples
- Risk management calculations
- Portfolio tracking demonstration
- Paper trading confirmations

**Run time**: 3-5 minutes

**⚠️ Safety Note**: Always verify `TRADING_MODE=paper` before running!

---

### 3️⃣ Bot Notifications Notebook
**File**: `notebooks/03_bot_notifications.ipynb`

**Purpose**:
- Set up WhatsApp and Gmail notification systems
- Run the main 24/7 trading bot
- Monitor real-time operations

**What it does**:
- Tests WhatsApp messaging to +923353015576
- Validates Gmail SMTP for weekly reports
- Starts continuous trading bot loop
- Monitors market conditions every 30 minutes
- Executes trades based on DCA/ATR triggers
- Sends real-time notifications

**Expected output**:
- WhatsApp test message received
- Email connectivity confirmation
- Trading bot status updates
- Live market monitoring
- Trade execution logs

**Run time**: Continuous (runs until stopped)

**🔴 IMPORTANT**: This starts the actual trading bot!

---

### 4️⃣ Live Dashboard Notebook
**File**: `notebooks/04_live_dashboard.ipynb`

**Purpose**:
- Real-time monitoring and control interface
- Interactive charts and performance metrics
- System health monitoring

**What it does**:
- Creates interactive Plotly dashboard
- Shows live Bitcoin price updates
- Displays portfolio performance
- Real-time trade activity feed
- System health indicators
- Strategy control panel

**Expected output**:
- Interactive web dashboard
- Auto-refreshing charts (30-second intervals)
- Portfolio value tracking
- Recent trades table
- Performance metrics

**Run time**: Continuous (dashboard stays active)

---

## 🏃‍♂️ Quick Start Commands

### Step 1: System Validation
```bash
# Navigate to project directory
cd "/home/osama/Desktop/Apziva Projects/Project 5/Bitcoin-Trading-Agent"

# Test all dependencies and API connections
python test_dependencies.py
```

### Step 2: Start Jupyter
```bash
# Start Jupyter notebook server
jupyter notebook

# Alternative: Use JupyterLab
jupyter lab
```

### Step 3: Run Notebooks Sequentially
1. Open `notebooks/01_data_analysis.ipynb` → Run All Cells
2. Open `notebooks/02_trading_system.ipynb` → Run All Cells  
3. Open `notebooks/03_bot_notifications.ipynb` → Run All Cells
4. Open `notebooks/04_live_dashboard.ipynb` → Run All Cells

---

## 🎯 What to Expect

### First Run (Data Analysis)
```
✅ Yahoo Finance      - Current BTC price: $43,245.67
✅ CoinMarketCap     - Current BTC price: $43,248.12
✅ Crawl4AI          - Library available
📊 Technical indicators calculated
📈 Price charts generated
```

### Trading System Test
```
📊 Configuration loaded from .env
💰 Budget: $1,000.00
📉 DCA Trigger: 3.0% price drop
🛡️ ATR Stop-Loss: 1.5x multiplier
🧪 Paper Trading Mode: ENABLED
✅ Coinbase API connected
```

### Bot Activation
```
🤖 Bitcoin Trading Bot Started
💰 Budget: $1,000.00
📊 Current Price: $43,245.67
⚙️ Paper Trading Mode Active
📱 WhatsApp notifications enabled to +923353015576
📧 Gmail reports configured
🔄 Checking market every 30 minutes...
```

### Dashboard Launch
```
🚀 Dashboard starting on http://localhost:8050
📊 Real-time monitoring active
🔄 Auto-refresh every 30 seconds
🎛️ Interactive controls enabled
```

---

## 📱 Notification Examples

### WhatsApp Messages You'll Receive:
```
🤖 BTC Bot Alert
14:30:25

🟢 DCA BUY EXECUTED
💰 $20.00 → 0.000463 BTC
📊 Price: $43,200.50
📝 Reason: 3.2% price drop
```

### Weekly Email Reports:
- HTML formatted performance summary
- Portfolio overview with charts
- Recent trades table
- Strategy configuration status
- AI-powered market insights (if Groq Cloud configured)

---

## ⚙️ Configuration Changes

### Modify Trading Parameters
Edit `.env` file and restart notebooks:
```bash
# Example changes
DCA_PERCENTAGE=5.0          # Trigger on 5% drops instead of 3%
ATR_MULTIPLIER=2.0          # Wider stop-losses
POSITION_SIZE_PCT=1.0       # Smaller position sizes
```

### Switch to Live Trading
```bash
# ⚠️ ONLY after thorough testing in paper mode!
TRADING_MODE=live
```

### Adjust Bot Timing
```bash
CYCLE_INTERVAL=3600         # Check every hour instead of 30 minutes
NOTIFICATION_RATE_LIMIT=60  # 1 minute between WhatsApp messages
```

---

## 🛠️ Troubleshooting

### Common Issues

1. **"API key not found" error**
   - Check `.env` file is in project root
   - Verify no extra spaces in API keys
   - Run `python test_dependencies.py`

2. **WhatsApp messages not sending**
   - Ensure WhatsApp Web is logged in
   - Check phone number format in .env
   - Verify PyWhatKit installation

3. **Gmail reports failing**
   - Use app password, not regular password
   - Enable 2-factor authentication first
   - Check Gmail security settings

4. **Coinbase API errors**
   - Verify API key permissions (View, Trade, Transfer)
   - Check account verification status
   - Ensure sufficient balance for trading

5. **Notebook crashes**
   - Restart Jupyter kernel
   - Check Python version compatibility
   - Run dependency test again

### Getting Help

1. **Check logs**: Look in `data/` directory for error logs
2. **Run diagnostics**: `python test_dependencies.py`
3. **Verify environment**: Check all .env variables are set
4. **Start fresh**: Restart all notebooks in sequence

---

## 🔒 Safety Reminders

### Before Going Live:
- [ ] ✅ Tested thoroughly in paper mode
- [ ] ✅ Received test WhatsApp messages  
- [ ] ✅ Verified email reports working
- [ ] ✅ Understood all strategy parameters
- [ ] ✅ Set appropriate budget limits
- [ ] ✅ Confirmed stop-loss mechanisms
- [ ] ✅ Reviewed recent market conditions

### Ongoing Monitoring:
- [ ] 📱 Monitor WhatsApp notifications
- [ ] 📧 Review weekly email reports
- [ ] 💻 Check dashboard regularly
- [ ] 📊 Track portfolio performance
- [ ] ⚙️ Adjust parameters as needed

---

## 📈 Success Metrics

### After 1 Week:
- Bot running continuously without crashes
- Receiving regular notifications
- Portfolio tracking accurately
- Strategy parameters working as expected

### After 1 Month:
- Consistent performance tracking
- Successful trade executions
- Risk management working effectively
- Comfortable with system operation

---

## 🎉 You're Ready!

Once you've successfully run all 4 notebooks and received your first WhatsApp notification, your Bitcoin Trading Agent is fully operational!

**Remember**: Start small, monitor closely, and adjust parameters based on market conditions and your risk tolerance.

Happy trading! 🚀📈