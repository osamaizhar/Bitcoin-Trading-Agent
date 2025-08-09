# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Bitcoin Trading Agent that implements Dollar-Cost Averaging (DCA) and ATR-based stop-loss strategies with real-time notifications. The system is built using Python and operates through Jupyter notebooks with supporting modules.

## Core Architecture

### Main Components

**Jupyter Notebooks (Primary Interface):**
- `notebooks/01_data_collection.ipynb` - Enhanced data collection from multiple sources (Yahoo Finance, CoinGecko, Binance, CoinMarketCap, Investing.com with anti-bot protection)
- `notebooks/02_trading_system.ipynb` - DCA strategy implementation with Coinbase integration
- `notebooks/02_binance_trading_system.ipynb` - Alternative Binance-based trading system
- `notebooks/03_bot_notifications.ipynb` - WhatsApp notifications and Gmail reports system
- `notebooks/03_binance_bot_notifications.ipynb` - Binance-specific bot notifications
- `notebooks/04_live_dashboard.ipynb` - Real-time monitoring dashboard
- `notebooks/04_binance_live_dashboard.ipynb` - Binance-specific real-time dashboard

**Python Modules (src/):**
- `src/data_collector.py` - Enhanced multi-source Bitcoin data collection with 5 data sources, retry logic, and anti-bot measures
- `src/trading_engine.py` - Core trading logic (DCA strategy, ATR stop-loss, risk management)
- `src/notifications.py` - WhatsApp alerts via PyWhatKit and HTML email reports
- `src/config_manager.py` - Configuration management with Google Sheets integration

### Key Trading Strategies

**DCA (Dollar-Cost Averaging):**
- Triggers on 3% price drops (configurable)
- Uses 2% of budget per trade
- RSI oversold conditions (≤30) also trigger purchases
- Includes portfolio tracking and P&L calculations

**ATR Stop-Loss System:**
- Dynamic stop-loss based on Average True Range (ATR)
- 1.5x ATR multiplier (configurable)
- Trailing stops that adjust with market volatility
- Position management with entry/exit tracking

**Risk Management:**
- Maximum 25% portfolio drawdown protection
- Budget exhaustion prevention
- Rate limiting for notifications (30-second intervals)
- Paper trading mode by default

## Development Commands

### Setup and Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Test system setup and dependencies
python test_dependencies.py

# Alternative: Use Poetry
poetry install
```

### Environment Configuration
Required environment variables in `.env`:
```bash
# Trading Configuration
DEFAULT_BUDGET=1000
DCA_PERCENTAGE=3.0
ATR_MULTIPLIER=1.5
TRADING_MODE=paper

# API Keys
COINBASE_API_KEY=your_coinbase_api_key
COINBASE_API_SECRET=your_coinbase_secret
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password

# Notifications (WhatsApp number is hardcoded to +923353015576)
WHATSAPP_PHONE_NUMBER=+923353015576

# Optional APIs (CoinGecko and Binance are free and don't require keys)
COINMARKETCAP_API_KEY=your_cmc_key
GOOGLE_SHEETS_SERVICE_ACCOUNT=path/to/service_account.json
GROQ_API_KEY=your_groq_key

# Data Source Priority (automatic failover)
# 1. Yahoo Finance (primary)
# 2. CoinGecko (free API)
# 3. Binance Public API (free)  
# 4. CoinMarketCap (requires API key)
# 5. Investing.com (scraping fallback)
```

### Development Tools
```bash
# Format code (Poetry development dependencies)
black src/ test_dependencies.py
flake8 src/ test_dependencies.py

# Run tests (if pytest is configured)
pytest

# Install development dependencies
poetry install --with dev
```

### Running the System
```bash
# Start Jupyter notebook server
jupyter notebook

# Run notebooks in sequence:
# 1. 01_data_collection.ipynb (data collection & analysis)  
# 2. 02_trading_system.ipynb or 02_binance_trading_system.ipynb (trading strategy testing)
# 3. 03_bot_notifications.ipynb or 03_binance_bot_notifications.ipynb (24/7 bot with notifications)
# 4. 04_live_dashboard.ipynb or 04_binance_live_dashboard.ipynb (real-time monitoring)

# Validate system before deployment
python test_dependencies.py
```

## Technology Stack

### Core Dependencies
- **pandas, numpy** - Data manipulation and analysis
- **yfinance** - Yahoo Finance API for Bitcoin price data
- **ta** - Technical analysis indicators (RSI, ATR, SMA, etc.)
- **requests** - HTTP requests for API calls
- **pywhatkit** - WhatsApp instant messaging (uses WhatsApp Web)
- **smtplib** - Gmail SMTP for email reports

### Optional/Advanced Dependencies
- **crawl4ai** v0.2.x - Modern async web scraping for Investing.com (version mismatch with docs)
- **ccxt** - Cryptocurrency exchange integration (Binance, Coinbase Pro)
- **pycoingecko** - CoinGecko API client (free Bitcoin data)
- **beautifulsoup4** - HTML parsing for web scraping
- **fake-useragent** - User agent rotation for anti-bot detection
- **requests-html** - Enhanced requests with JavaScript support
- **lxml** - Fast XML/HTML parsing
- **google-api-python-client** - Google Sheets configuration management
- **groq** - LLM-powered market insights with Llama 3.3 70B
- **jupyter** - Notebook interface for interactive development
- **matplotlib, seaborn** - Data visualization and charting

### Development Dependencies (Poetry)
- **pytest** - Testing framework
- **black** - Code formatting
- **flake8** - Code linting and style checking

### Notification Systems
- **WhatsApp**: Instant trade alerts to +923353015576 using PyWhatKit
- **Gmail**: Weekly HTML reports with charts and performance summaries
- **Rate limiting**: 30-second intervals between WhatsApp messages

## Development Workflow

### Making Changes to Trading Logic
1. Modify parameters in `.env` file or Google Sheets (if configured)
2. Test changes in `02_trading_system.ipynb` with paper trading
3. Validate notifications in `03_bot_notifications.ipynb`
4. Monitor real-time updates in `04_live_dashboard.ipynb`

### Adding New Data Sources
1. Extend `DataCollector` class in `src/data_collector.py`
2. Implement data source interface with `get_data()` and `get_current_price()` methods
3. Add error handling and fallback mechanisms
4. Test integration in `01_data_analysis.ipynb`

### Modifying Trading Strategies
1. Update strategy classes in `src/trading_engine.py`
2. Implement new trigger conditions in `should_trigger_dca()` or similar methods
3. Add risk management checks in `RiskManager` class
4. Test thoroughly in paper trading mode

## Important Considerations

### Security
- API keys are stored in `.env` file (never commit to repository)
- WhatsApp requires WhatsApp Web to be logged in on deployment server
- Gmail requires app password, not regular password
- Paper trading mode is enabled by default for safety

### Performance
- System checks market conditions every 30 minutes
- Multiple data sources provide redundancy (Yahoo Finance primary, others as fallback)
- Technical indicators calculated on 30-day rolling windows
- Notification rate limiting prevents spam

### Deployment
- Designed for cloud deployment (DigitalOcean, AWS, etc.)
- Uses virtual environment located in `env/` directory
- Project includes comprehensive dependency testing via `test_dependencies.py`
- No Docker configuration found - runs natively in Python environment
- Supports both Poetry (pyproject.toml) and pip (requirements.txt) dependency management
- Dual exchange support: Coinbase and Binance implementations available

### Error Handling
- Graceful degradation when data sources fail
- Comprehensive logging throughout all modules
- WhatsApp and email error notifications
- Trading continues even if individual components fail

## Common Development Tasks

### Testing New Features
1. Always start with paper trading mode (`TRADING_MODE=paper`)
2. Run `python test_dependencies.py` to verify system health
3. Test individual components in respective notebooks
4. Monitor logs in `data/` directory for errors

### Debugging Issues
1. Check `test_dependencies.py` output for missing dependencies or API issues
2. Verify `.env` file configuration
3. Check WhatsApp Web login status on deployment server
4. Review notebook outputs for error messages
5. Monitor trading logs for execution details

### Performance Optimization
1. Adjust cycle intervals in bot configuration (default: 30 minutes)
2. Optimize technical indicator calculations for faster execution
3. Use caching for frequently accessed data
4. Consider async operations for improved performance