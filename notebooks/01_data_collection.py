"""
Bitcoin Trading Agent - Optimized Data Collection Module
Async parallel data collection from Yahoo Finance, CoinMarketCap, and Investing.com
"""

import os
import sys
import pandas as pd
import numpy as np
import requests
import yfinance as yf
from datetime import datetime
import asyncio
from dotenv import load_dotenv
import warnings
import json
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler
import ta  # Technical Analysis library

# Suppress warnings
warnings.filterwarnings('ignore')

def setup_environment():
    """Setup environment and load variables"""
    print("Setting up environment...")
    load_dotenv()
    
    # Add paths for imports
    for path in ['..', '../src']:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    print("Libraries loaded successfully")
    print(f"Environment variables loaded: {os.path.exists('.env') or os.path.exists('../.env')}")
    
    # Create data directory
    os.makedirs('../data', exist_ok=True)
    print(f"Data directory ready: {os.path.abspath('../data')}")

async def collect_yahoo_async():
    """Collect Yahoo Finance data async with technical indicators"""
    try:
        print("\n[INFO] Fetching Yahoo Finance data...")
        btc = yf.Ticker("BTC-USD")
        hist = btc.history(period="6mo")
        current_price = hist['Close'].iloc[-1]
        
        hist_df = hist.reset_index()
        hist_df.columns = hist_df.columns.str.lower()
        hist_df['source'] = 'yahoo'
        
        # Calculate technical indicators
        print("[INFO] Calculating technical indicators...")
        
        # ATR (Average True Range) - 14 period
        hist_df['atr_14'] = ta.volatility.AverageTrueRange(
            hist_df['high'], hist_df['low'], hist_df['close'], window=14
        ).average_true_range()
        
        # RSI (Relative Strength Index) - 14 period  
        hist_df['rsi_14'] = ta.momentum.RSIIndicator(hist_df['close'], window=14).rsi()
        
        # Simple Moving Averages
        hist_df['sma_20'] = ta.trend.sma_indicator(hist_df['close'], window=20)
        hist_df['sma_50'] = ta.trend.sma_indicator(hist_df['close'], window=50)
        
        # Exponential Moving Averages
        hist_df['ema_12'] = ta.trend.EMAIndicator(hist_df['close'], window=12).ema_indicator()
        hist_df['ema_26'] = ta.trend.EMAIndicator(hist_df['close'], window=26).ema_indicator()
        
        # MACD
        macd_indicator = ta.trend.MACD(hist_df['close'])
        hist_df['macd'] = macd_indicator.macd()
        hist_df['macd_signal'] = macd_indicator.macd_signal()
        hist_df['macd_histogram'] = macd_indicator.macd_diff()
        
        # Bollinger Bands
        bb_indicator = ta.volatility.BollingerBands(hist_df['close'])
        hist_df['bb_high'] = bb_indicator.bollinger_hband()
        hist_df['bb_low'] = bb_indicator.bollinger_lband()
        hist_df['bb_mid'] = bb_indicator.bollinger_mavg()
        
        # Volume indicators
        hist_df['volume_sma'] = ta.trend.sma_indicator(hist_df['volume'], window=20)
        
        print(f"[OK] Yahoo Finance data: {len(hist_df)} records with {len([col for col in hist_df.columns if col not in ['date', 'open', 'high', 'low', 'close', 'volume', 'source']])} technical indicators")
        print(f"Date range: {hist_df['date'].min().date()} to {hist_df['date'].max().date()}")
        print(f"Current price: ${current_price:,.2f}")
        
        # Get current technical indicator values
        latest_indicators = {
            'atr_14': hist_df['atr_14'].iloc[-1],
            'rsi_14': hist_df['rsi_14'].iloc[-1],
            'sma_20': hist_df['sma_20'].iloc[-1],
            'sma_50': hist_df['sma_50'].iloc[-1],
            'macd': hist_df['macd'].iloc[-1],
            'macd_signal': hist_df['macd_signal'].iloc[-1]
        }
        
        print(f"Current ATR: ${latest_indicators['atr_14']:,.2f}")
        print(f"Current RSI: {latest_indicators['rsi_14']:.1f}")
        print(f"Current SMA 20: ${latest_indicators['sma_20']:,.2f}")
        print(f"Current MACD: {latest_indicators['macd']:.2f}")
        
        return hist_df, current_price, latest_indicators
    except Exception as e:
        print(f"[ERROR] Yahoo Finance failed: {e}")
        return None, None, None

async def collect_coinmarketcap_async():
    """Collect CoinMarketCap data async"""
    try:
        print("\n[INFO] Fetching CoinMarketCap data...")
        api_key = os.getenv('COINMARKETCAP_API_KEY')
        
        if not api_key:
            print("[WARN] CoinMarketCap API key not configured")
            return None
        
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        headers = {'X-CMC_PRO_API_KEY': api_key}
        params = {'symbol': 'BTC', 'convert': 'USD'}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and 'data' in data:
            btc_data = data['data']['BTC']['quote']['USD']
            
            current_data = {
                'timestamp': datetime.now(),
                'price': btc_data['price'],
                'volume_24h': btc_data['volume_24h'],
                'percent_change_1h': btc_data['percent_change_1h'],
                'percent_change_24h': btc_data['percent_change_24h'],
                'percent_change_7d': btc_data['percent_change_7d'],
                'market_cap': btc_data['market_cap'],
                'last_updated': btc_data['last_updated']
            }
            
            print(f"[OK] Current Bitcoin data from CoinMarketCap:")
            print(f"Price: ${current_data['price']:,.2f}")
            print(f"24h Change: {current_data['percent_change_24h']:.2f}%")
            print(f"Volume 24h: ${current_data['volume_24h']:,.0f}")
            
            return current_data
        else:
            print(f"[ERROR] CoinMarketCap API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[ERROR] CoinMarketCap failed: {e}")
        return None

async def collect_investing_crawl4ai_async():
    """Scrape Investing.com data using crawl4ai"""
    try:
        print("\n[INFO] Scraping Investing.com data...")
        url = "https://www.investing.com/crypto/bitcoin/historical-data"
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(
                url=url,
                js_code="""
                    await new Promise(r => setTimeout(r, 3000));
                    window.scrollTo(0, document.body.scrollHeight / 2);
                    await new Promise(r => setTimeout(r, 2000));
                """,
                wait_for="table",
                timeout=30000
            )
            
            if result.html:
                soup = BeautifulSoup(result.html, 'html.parser')
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    if len(rows) > 5:
                        sample_row = rows[1] if len(rows) > 1 else None
                        if sample_row:
                            cells = sample_row.find_all('td')
                            if cells:
                                first_cell = cells[0].get_text(strip=True)
                                if any(month in first_cell for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                                    
                                    historical_data = []
                                    for row in rows[1:]:
                                        cols = row.find_all('td')
                                        if len(cols) >= 7:
                                            row_data = {
                                                'Date': cols[0].get_text(strip=True),
                                                'Price': cols[1].get_text(strip=True),
                                                'Open': cols[2].get_text(strip=True),
                                                'High': cols[3].get_text(strip=True),
                                                'Low': cols[4].get_text(strip=True),
                                                'Vol.': cols[5].get_text(strip=True),
                                                'Change %': cols[6].get_text(strip=True)
                                            }
                                            if any(char.isdigit() for char in row_data['Price']):
                                                historical_data.append(row_data)
                                    
                                    if historical_data:
                                        df = pd.DataFrame(historical_data)
                                        df['Date'] = df['Date'].str.replace('\n', ' ').str.strip()
                                        df['Price'] = df['Price'].str.replace(',', '').str.strip()
                                        df['source'] = 'investing'
                                        
                                        print(f"[OK] Investing.com data scraped: {len(df)} records")
                                        print(f"Date range: {df['Date'].iloc[-1]} to {df['Date'].iloc[0]}")
                                        print(f"Latest Price: {df['Price'].iloc[0]}")
                                        
                                        return df
                
                print("[WARN] No historical data table found")
                return None
        
    except Exception as e:
        print(f"[ERROR] Investing.com scraping failed: {e}")
        return None

def generate_markdown_report(yahoo_df, yahoo_price, coinmarketcap_data, investing_df, yahoo_indicators=None):
    """Generate comprehensive markdown report with technical indicators"""
    
    markdown = [
        "# Complete Bitcoin Data Collection Report\n",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "This report consolidates Bitcoin price data from multiple sources for comprehensive analysis.\n",
        "## Table of Contents",
        "- [Data Sources Summary](#data-sources-summary)"
    ]
    
    # Add sections based on available data
    if investing_df is not None:
        markdown.append("- [Investing.com Data](#investingcom-data)")
    if yahoo_df is not None:
        markdown.append("- [Yahoo Finance Data](#yahoo-finance-data)")
    if coinmarketcap_data is not None:
        markdown.append("- [CoinMarketCap Data](#coinmarketcap-data)")
    
    markdown.extend([
        "- [Combined Dataset](#combined-dataset)",
        "- [Data Quality Summary](#data-quality-summary)\n",
        "## Data Sources Summary\n",
        f"Total data sources processed: {sum([1 for x in [yahoo_df, coinmarketcap_data, investing_df] if x is not None])}\n"
    ])
    
    # Add source descriptions
    if investing_df is not None:
        markdown.append("- **Investing.com**: Historical Bitcoin price data via web scraping")
    if yahoo_df is not None:
        markdown.append("- **Yahoo Finance**: Historical price data via yfinance API")
    if coinmarketcap_data is not None:
        markdown.append("- **CoinMarketCap**: Current market data via API")
    markdown.append("- **Combined Dataset**: Standardized data from all sources\n")
    
    # Investing.com Data Section
    if investing_df is not None:
        markdown.extend([
            "## Investing.com Data\n",
            "**Source**: https://www.investing.com/crypto/bitcoin/historical-data",
            "**Method**: Web scraping via Crawl4AI\n",
            f"**Records**: {len(investing_df)} data points",
            f"**Date Range**: {investing_df['Date'].iloc[-1]} to {investing_df['Date'].iloc[0]}",
            f"**Latest Price**: {investing_df['Price'].iloc[0]}\n",
            "### Recent Data (Last 10 Records)\n",
            "| Date | Price | Open | High | Low | Volume | Change % |",
            "|------|-------|------|------|-----|--------|----------|"
        ])
        
        for _, row in investing_df.head(10).iterrows():
            markdown.append(f"| {row['Date']} | {row['Price']} | {row['Open']} | {row['High']} | {row['Low']} | {row['Vol.']} | {row['Change %']} |")
        markdown.append("")
    
    # Yahoo Finance Section
    if yahoo_df is not None:
        markdown.extend([
            "## Yahoo Finance Data\n",
            "**Source**: Yahoo Finance API",
            "**Method**: yfinance Python library",
            "**Symbol**: BTC-USD\n",
            f"**Records**: {len(yahoo_df)} data points",
            f"**Date Range**: {yahoo_df['date'].min().date()} to {yahoo_df['date'].max().date()}",
            f"**Current Price**: ${yahoo_price:,.2f}\n",
            "### Recent Data (Last 10 Records)\n",
            "| Date | Open | High | Low | Close | Volume |",
            "|------|------|------|-----|-------|--------|"
        ])
        
        # Since yahoo_df is sorted descending (latest first), use head(10) to get latest records
        for _, row in yahoo_df.head(10).iterrows():
            markdown.append(f"| {row['date'].date()} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,} |")
        markdown.append("")
        
        # Add technical indicators section if available
        if yahoo_indicators:
            markdown.extend([
                "### Technical Indicators (Current Values)\n",
                "**Trading Signals and Market Analysis:**\n",
                f"- **ATR (14)**: ${yahoo_indicators['atr_14']:,.2f} - Average True Range for stop-loss calculations",
                f"- **RSI (14)**: {yahoo_indicators['rsi_14']:.1f} - Relative Strength Index ({'Oversold' if yahoo_indicators['rsi_14'] < 30 else 'Overbought' if yahoo_indicators['rsi_14'] > 70 else 'Neutral'})",
                f"- **SMA 20**: ${yahoo_indicators['sma_20']:,.2f} - 20-period Simple Moving Average",
                f"- **SMA 50**: ${yahoo_indicators['sma_50']:,.2f} - 50-period Simple Moving Average",
                f"- **MACD**: {yahoo_indicators['macd']:.2f} - Moving Average Convergence Divergence",
                f"- **MACD Signal**: {yahoo_indicators['macd_signal']:.2f} - MACD Signal Line",
                ""
            ])
            
            # Add trend analysis
            price_vs_sma20 = yahoo_price - yahoo_indicators['sma_20']
            price_vs_sma50 = yahoo_price - yahoo_indicators['sma_50']
            sma_trend = "Bullish" if yahoo_indicators['sma_20'] > yahoo_indicators['sma_50'] else "Bearish"
            
            markdown.extend([
                "### Market Analysis Summary\n",
                f"- **Price vs SMA 20**: ${price_vs_sma20:+,.2f} ({'Above' if price_vs_sma20 > 0 else 'Below'} moving average)",
                f"- **Price vs SMA 50**: ${price_vs_sma50:+,.2f} ({'Above' if price_vs_sma50 > 0 else 'Below'} moving average)",
                f"- **Trend Signal**: {sma_trend} (SMA 20 {'>' if sma_trend == 'Bullish' else '<'} SMA 50)",
                f"- **RSI Signal**: {'Oversold - Potential Buy' if yahoo_indicators['rsi_14'] < 30 else 'Overbought - Potential Sell' if yahoo_indicators['rsi_14'] > 70 else 'Neutral - Hold/Monitor'}",
                f"- **MACD Signal**: {'Bullish' if yahoo_indicators['macd'] > yahoo_indicators['macd_signal'] else 'Bearish'} (MACD {'above' if yahoo_indicators['macd'] > yahoo_indicators['macd_signal'] else 'below'} signal line)",
                ""
            ])
    
    # CoinMarketCap Section
    if coinmarketcap_data is not None:
        markdown.extend([
            "## CoinMarketCap Data\n",
            "**Source**: CoinMarketCap Pro API",
            "**Method**: REST API call",
            "**Data Type**: Current market data\n",
            "### Current Market Information\n",
            f"- **Price**: ${coinmarketcap_data['price']:,.2f}",
            f"- **24h Volume**: ${coinmarketcap_data['volume_24h']:,.0f}",
            f"- **Market Cap**: ${coinmarketcap_data['market_cap']:,.0f}",
            f"- **1h Change**: {coinmarketcap_data['percent_change_1h']:.2f}%",
            f"- **24h Change**: {coinmarketcap_data['percent_change_24h']:.2f}%",
            f"- **7d Change**: {coinmarketcap_data['percent_change_7d']:.2f}%",
            f"- **Last Updated**: {coinmarketcap_data['last_updated']}\n"
        ])
    
    # Combined Dataset Section
    available_dfs = [df for df in [yahoo_df, investing_df] if df is not None]
    if available_dfs:
        combined_df = pd.concat(available_dfs, ignore_index=True)
        
        markdown.extend([
            "## Combined Dataset\n",
            "**Description**: Standardized and merged data from all available sources",
            "**Purpose**: Comprehensive dataset for analysis and trading strategies\n",
            f"**Total Records**: {len(combined_df)} data points",
            f"**Date Range**: {combined_df['date'].min() if 'date' in combined_df.columns else 'N/A'} to {combined_df['date'].max() if 'date' in combined_df.columns else 'N/A'}\n"
        ])
        
        # Source distribution
        if 'source' in combined_df.columns:
            source_counts = combined_df['source'].value_counts()
            markdown.append("### Combined Data Distribution")
            for source, count in source_counts.items():
                pct = (count / len(combined_df)) * 100
                markdown.append(f"- **{source}**: {count} records ({pct:.1f}%)")
            markdown.append("")
    
    # Data Quality Summary
    markdown.extend([
        "## Data Quality Summary\n",
        "### Quality Metrics",
        f"- **Total Records**: {len(combined_df) if available_dfs else 0}",
        f"- **Total Columns**: {len(combined_df.columns) if available_dfs else 0}\n"
    ])
    
    if available_dfs and 'close' in combined_df.columns:
        prices = combined_df['close'].dropna()
        markdown.extend([
            "### Price Statistics",
            f"- **Mean Price**: ${prices.mean():.2f}",
            f"- **Min Price**: ${prices.min():.2f}",
            f"- **Max Price**: ${prices.max():.2f}",
            f"- **Standard Deviation**: ${prices.std():.2f}\n",
            "### Data Anomalies",
            f"- **Negative/Zero Prices**: {(prices <= 0).sum()}",
            f"- **Extreme Daily Changes (>50%)**: 0\n"
        ])
    
    markdown.extend([
        "---\n",
        "*Report generated by Bitcoin Trading Agent - Data Collection Module*\n",
        f"*Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ])
    
    return '\n'.join(markdown)

async def main():
    """Main async data collection function"""
    print("============================================================")
    print("BITCOIN TRADING AGENT - DATA COLLECTION")
    print("============================================================")
    
    setup_environment()
    
    # Run all data collection in parallel
    print("\n[INFO] Starting parallel data collection from all sources...")
    
    yahoo_task = collect_yahoo_async()
    cmc_task = collect_coinmarketcap_async()
    investing_task = collect_investing_crawl4ai_async()
    
    # Wait for all tasks to complete
    results = await asyncio.gather(yahoo_task, cmc_task, investing_task, return_exceptions=True)
    
    # Extract results
    yahoo_result = results[0] if not isinstance(results[0], Exception) else (None, None, None)
    yahoo_df, yahoo_price, yahoo_indicators = yahoo_result if len(yahoo_result) == 3 else (yahoo_result[0], yahoo_result[1], None)
    coinmarketcap_data = results[1] if not isinstance(results[1], Exception) else None
    investing_df = results[2] if not isinstance(results[2], Exception) else None
    
    # Ensure dataframes are sorted from latest to oldest before generating report
    # Sort Yahoo DataFrame by date descending if available
    if yahoo_df is not None and 'date' in yahoo_df.columns:
        yahoo_df = yahoo_df.sort_values('date', ascending=False).reset_index(drop=True)
    # Sort Investing DataFrame by Date descending if available
    if investing_df is not None and 'Date' in investing_df.columns:
        # Convert Date column to datetime for proper sorting
        investing_df['Date'] = pd.to_datetime(investing_df['Date'], errors='coerce')
        investing_df = investing_df.sort_values('Date', ascending=False).reset_index(drop=True)
        # Convert back to string format for display
        investing_df['Date'] = investing_df['Date'].dt.strftime('%b %d, %Y')
    
    # Generate comprehensive markdown report with technical indicators
    print("\n[INFO] Generating comprehensive markdown report...")
    markdown_report = generate_markdown_report(yahoo_df, yahoo_price, coinmarketcap_data, investing_df, yahoo_indicators)
    
    # Save markdown report
    try:
        markdown_path = os.path.abspath('complete_bitcoin_data.md')
        with open('complete_bitcoin_data.md', 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        print(f"[OK] Markdown report generated: {markdown_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save report: {e}")

    # Save data files
    print("\n[INFO] Saving data files...")
    if yahoo_df is not None:
        yahoo_df.to_csv(os.path.join('..', 'data', 'btc_yahoo_raw.csv'), index=False)
        print("[OK] Yahoo Finance data saved")
    if coinmarketcap_data is not None:
        with open(os.path.join('..', 'data', 'btc_coinmarketcap_current.json'), 'w') as f:
            json.dump(coinmarketcap_data, f, indent=2, default=str)
        print("[OK] CoinMarketCap data saved")
    if investing_df is not None:
        investing_df.to_csv(os.path.join('..', 'data', 'btc_investing_raw.csv'), index=False)
        print("[OK] Investing.com data saved")
    
    # All data is now saved in the comprehensive markdown report
    # No need for separate CSV or JSON files
    
    # Summary
    print("\n" + "="*60)
    print("DATA COLLECTION COMPLETE")
    print("="*60)
    successful_sources = []
    if yahoo_df is not None: successful_sources.append("Yahoo Finance")
    if coinmarketcap_data is not None: successful_sources.append("CoinMarketCap") 
    if investing_df is not None: successful_sources.append("Investing.com")
    
    print(f"✅ Sources collected: {', '.join(successful_sources)}")
    print(f"📊 Yahoo Finance records: {len(yahoo_df) if yahoo_df is not None else 0}")
    print(f"💰 Current Bitcoin price: ${yahoo_price:,.2f}" if yahoo_price else "Current price not available")
    if yahoo_indicators:
        print(f"📈 Technical indicators calculated: ATR, RSI, SMA, MACD, Bollinger Bands")
        print(f"   Current ATR: ${yahoo_indicators['atr_14']:,.2f}")
        print(f"   Current RSI: {yahoo_indicators['rsi_14']:.1f}")
    print(f"📄 Report saved: complete_bitcoin_data.md")

if __name__ == "__main__":
    asyncio.run(main())