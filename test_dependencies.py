#!/usr/bin/env python3
"""
Bitcoin Trading Agent - Dependency Test Script

This script tests all required dependencies and validates the system setup.
Run this before deploying the trading bot.
"""

import sys
import os
import importlib
from datetime import datetime

def test_import(module_name, description="", required=True):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name:<20} - {description}")
        return True
    except ImportError as e:
        status = "❌" if required else "⚠️"
        req_text = "REQUIRED" if required else "OPTIONAL"
        print(f"{status} {module_name:<20} - {description} [{req_text}]")
        if required:
            print(f"   Error: {e}")
        return False

def test_environment_variables():
    """Test environment variable configuration"""
    print("\n🔧 Testing Environment Variables:")
    
    required_vars = [
        ('COINBASE_API_KEY', 'Coinbase API key for trading'),
        ('COINBASE_API_SECRET', 'Coinbase API secret'),
        ('GMAIL_EMAIL', 'Gmail email for reports'),
        ('GMAIL_APP_PASSWORD', 'Gmail app password'),
        ('DEFAULT_BUDGET', 'Default trading budget'),
        ('DCA_PERCENTAGE', 'DCA trigger percentage'),
        ('ATR_MULTIPLIER', 'ATR stop-loss multiplier')
    ]
    
    optional_vars = [
        ('COINMARKETCAP_API_KEY', 'CoinMarketCap API key'),
        ('GOOGLE_SHEETS_SERVICE_ACCOUNT', 'Google Sheets service account file'),
        ('GOOGLE_SHEETS_ID', 'Google Sheets ID'),
        ('GROQ_API_KEY', 'Groq Cloud API key for LLM features')
    ]
    
    required_count = 0
    for var, desc in required_vars:
        value = os.getenv(var)
        if value and value != f'your_{var.lower()}_here':
            print(f"✅ {var:<30} - {desc}")
            required_count += 1
        else:
            print(f"❌ {var:<30} - {desc} [REQUIRED]")
    
    optional_count = 0
    for var, desc in optional_vars:
        value = os.getenv(var)
        if value and value != f'your_{var.lower()}_here':
            print(f"✅ {var:<30} - {desc}")
            optional_count += 1
        else:
            print(f"⚠️ {var:<30} - {desc} [OPTIONAL]")
    
    return required_count, len(required_vars)

def test_data_sources():
    """Test data source connectivity"""
    print("\n📊 Testing Data Sources:")
    
    success_count = 0
    
    # Test Yahoo Finance
    try:
        import yfinance as yf
        btc = yf.Ticker("BTC-USD")
        info = btc.info
        price = info.get('regularMarketPrice')
        if price:
            print(f"✅ Yahoo Finance      - Current BTC price: ${price:,.2f}")
            success_count += 1
        else:
            print("❌ Yahoo Finance      - No price data available")
    except Exception as e:
        print(f"❌ Yahoo Finance      - Error: {e}")
    
    # Test CoinMarketCap
    api_key = os.getenv('COINMARKETCAP_API_KEY')
    if api_key and api_key != 'your_coinmarketcap_api_key_here':
        try:
            import requests
            url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
            headers = {'X-CMC_PRO_API_KEY': api_key}
            params = {'symbol': 'BTC', 'convert': 'USD'}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                price = data['data']['BTC']['quote']['USD']['price']
                print(f"✅ CoinMarketCap     - Current BTC price: ${price:,.2f}")
                success_count += 1
            else:
                print(f"❌ CoinMarketCap     - API error: {response.status_code}")
        except Exception as e:
            print(f"❌ CoinMarketCap     - Error: {e}")
    else:
        print("⚠️ CoinMarketCap     - API key not configured [OPTIONAL]")
    
    # Test Crawl4AI
    try:
        from crawl4ai import AsyncWebCrawler
        print("✅ Crawl4AI          - Library available")
        success_count += 1
    except ImportError:
        print("⚠️ Crawl4AI          - Not installed [OPTIONAL]")
    except Exception as e:
        print(f"❌ Crawl4AI          - Error: {e}")
    
    return success_count

def test_notifications():
    """Test notification systems"""
    print("\n📱 Testing Notifications:")
    
    success_count = 0
    
    # Test PyWhatKit
    try:
        import pywhatkit
        print("✅ PyWhatKit         - Library available for WhatsApp")
        success_count += 1
    except ImportError:
        print("❌ PyWhatKit         - Not installed [REQUIRED for WhatsApp]")
    except Exception as e:
        print(f"❌ PyWhatKit         - Error: {e}")
    
    # Test Gmail SMTP
    email = os.getenv('GMAIL_EMAIL')
    password = os.getenv('GMAIL_APP_PASSWORD')
    
    if email and password:
        try:
            import smtplib
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email, password)
            server.quit()
            print("✅ Gmail SMTP        - Authentication successful")
            success_count += 1
        except Exception as e:
            print(f"❌ Gmail SMTP        - Authentication failed: {e}")
    else:
        print("⚠️ Gmail SMTP        - Credentials not configured")
    
    return success_count

def test_technical_indicators():
    """Test technical analysis libraries"""
    print("\n📈 Testing Technical Analysis:")
    
    success_count = 0
    
    try:
        import ta
        import pandas as pd
        import numpy as np
        
        # Create sample data
        dates = pd.date_range('2023-01-01', periods=30)
        prices = np.random.randn(30).cumsum() + 50000
        df = pd.DataFrame({
            'close': prices,
            'high': prices + np.random.rand(30) * 1000,
            'low': prices - np.random.rand(30) * 1000,
            'volume': np.random.randint(1000, 10000, 30)
        })
        
        # Test indicators
        rsi = ta.momentum.rsi(df['close'])
        atr = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
        sma = ta.trend.sma_indicator(df['close'])
        
        if not rsi.isnull().all() and not atr.isnull().all():
            print("✅ Technical Analysis - RSI, ATR, SMA calculations working")
            success_count += 1
        else:
            print("❌ Technical Analysis - Indicator calculations failed")
            
    except Exception as e:
        print(f"❌ Technical Analysis - Error: {e}")
    
    return success_count

def test_project_structure():
    """Test project file structure"""
    print("\n📁 Testing Project Structure:")
    
    required_files = [
        '.env',
        'requirements.txt',
        'pyproject.toml',
        'notebooks/01_data_analysis.ipynb',
        'notebooks/02_trading_system.ipynb', 
        'notebooks/03_bot_notifications.ipynb',
        'src/__init__.py',
        'src/data_collector.py',
        'src/trading_engine.py',
        'src/notifications.py',
        'src/config_manager.py'
    ]
    
    success_count = 0
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file:<40} - Found")
            success_count += 1
        else:
            print(f"❌ {file:<40} - Missing")
    
    # Check data directory
    if not os.path.exists('data'):
        os.makedirs('data')
        print("✅ data/                                 - Created")
        success_count += 1
    else:
        print("✅ data/                                 - Exists")
        success_count += 1
    
    return success_count, len(required_files) + 1

def main():
    """Run all tests"""
    print("🤖 BITCOIN TRADING AGENT - DEPENDENCY TEST")
    print("=" * 50)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python Version: {sys.version}")
    
    # Test core dependencies
    print("\n📦 Testing Core Dependencies:")
    
    core_deps = [
        ('pandas', 'Data manipulation and analysis'),
        ('numpy', 'Numerical computing'),
        ('requests', 'HTTP requests'),
        ('python-dotenv', 'Environment variable management'),  
        ('yfinance', 'Yahoo Finance data'),
        ('ta', 'Technical analysis indicators'),
        ('schedule', 'Task scheduling'),
        ('pywhatkit', 'WhatsApp notifications'),
        ('google-auth', 'Google API authentication', False),
        ('googleapiclient', 'Google API client', False),
        ('crawl4ai', 'Web scraping', False),
        ('groq', 'Groq Cloud API', False)
    ]
    
    core_success = 0
    core_required = 0
    
    for dep in core_deps:
        module_name = dep[0]
        description = dep[1]
        required = dep[2] if len(dep) > 2 else True
        
        if test_import(module_name, description, required):
            if required:
                core_success += 1
        if required:
            core_required += 1
    
    # Test environment variables
    env_success, env_required = test_environment_variables()
    
    # Test data sources
    data_success = test_data_sources()
    
    # Test notifications
    notification_success = test_notifications()
    
    # Test technical indicators
    ta_success = test_technical_indicators()
    
    # Test project structure
    structure_success, structure_required = test_project_structure()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY:")
    print(f"  Core Dependencies:    {core_success}/{core_required} ({'✅' if core_success == core_required else '❌'})")
    print(f"  Environment Variables: {env_success}/{env_required} ({'✅' if env_success >= env_required - 2 else '❌'})")
    print(f"  Data Sources:         {data_success}/3 ({'✅' if data_success >= 1 else '❌'})")
    print(f"  Notifications:        {notification_success}/2 ({'✅' if notification_success >= 1 else '❌'})")
    print(f"  Technical Analysis:   {ta_success}/1 ({'✅' if ta_success == 1 else '❌'})")
    print(f"  Project Structure:    {structure_success}/{structure_required} ({'✅' if structure_success == structure_required else '❌'})")
    
    # Overall status
    critical_tests = [
        core_success == core_required,
        env_success >= env_required - 2,  # Allow 2 missing optional vars
        data_success >= 1,  # At least one data source
        notification_success >= 1,  # At least one notification method
        ta_success == 1,  # Technical analysis working
        structure_success == structure_required  # All files present
    ]
    
    all_critical_passed = all(critical_tests)
    
    print(f"\n🎯 OVERALL STATUS: {'✅ READY FOR DEPLOYMENT' if all_critical_passed else '❌ NEEDS ATTENTION'}")
    
    if not all_critical_passed:
        print("\n⚠️ ISSUES TO RESOLVE:")
        if core_success != core_required:
            print("  • Install missing required Python packages")
        if env_success < env_required - 2:
            print("  • Configure missing environment variables in .env")
        if data_success < 1:
            print("  • Fix data source connectivity issues")
        if notification_success < 1:
            print("  • Configure at least one notification method")
        if ta_success != 1:
            print("  • Fix technical analysis library issues")
        if structure_success != structure_required:
            print("  • Ensure all required project files are present")
    else:
        print("\n🚀 NEXT STEPS:")
        print("  1. Update .env with your actual API keys")
        print("  2. Test WhatsApp notifications manually")
        print("  3. Run a few trading cycles in paper mode")
        print("  4. Deploy to production environment")
        print("  5. Monitor logs and performance")
    
    return 0 if all_critical_passed else 1

if __name__ == "__main__":
    sys.exit(main())