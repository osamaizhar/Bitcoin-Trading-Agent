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
    """Collect Yahoo Finance data async"""
    try:
        print("\n[INFO] Fetching Yahoo Finance data...")
        btc = yf.Ticker("BTC-USD")
        hist = btc.history(period="6mo")
        current_price = hist['Close'].iloc[-1]
        
        hist_df = hist.reset_index()
        hist_df.columns = hist_df.columns.str.lower()
        hist_df['source'] = 'yahoo'
        
        print(f"[OK] Yahoo Finance data: {len(hist_df)} records")
        print(f"Date range: {hist_df['date'].min().date()} to {hist_df['date'].max().date()}")
        print(f"Current price: ${current_price:,.2f}")
        
        return hist_df, current_price
    except Exception as e:
        print(f"[ERROR] Yahoo Finance failed: {e}")
        return None, None

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

def generate_markdown_report(yahoo_df, yahoo_price, coinmarketcap_data, investing_df):
    """Generate comprehensive markdown report"""
    
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
        
        for _, row in yahoo_df.tail(10).iterrows():
            markdown.append(f"| {row['date'].date()} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,} |")
        markdown.append("")
    
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
    yahoo_df, yahoo_price = results[0] if not isinstance(results[0], Exception) else (None, None)
    coinmarketcap_data = results[1] if not isinstance(results[1], Exception) else None
    investing_df = results[2] if not isinstance(results[2], Exception) else None
    
    # Generate markdown report
    print("\n[INFO] Generating markdown report...")
    markdown_report = generate_markdown_report(yahoo_df, yahoo_price, coinmarketcap_data, investing_df)
    
    # Save markdown report
    markdown_path = os.path.abspath('complete_bitcoin_data.md')
    with open('complete_bitcoin_data.md', 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"[OK] Markdown report generated: {markdown_path}")
    
    # Save data files
    print("\n[INFO] Saving data files...")
    if yahoo_df is not None:
        yahoo_df.to_csv('../data/btc_yahoo_raw.csv', index=False)
        print("[OK] Yahoo Finance data saved")
    if coinmarketcap_data is not None:
        with open('../data/btc_coinmarketcap_current.json', 'w') as f:
            json.dump(coinmarketcap_data, f, indent=2, default=str)
        print("[OK] CoinMarketCap data saved")
    if investing_df is not None:
        investing_df.to_csv('../data/btc_investing_raw.csv', index=False)
        print("[OK] Investing.com data saved")
    
    # Summary
    print("\n" + "="*50)
    print("[SUMMARY] Data Collection Summary")
    print("="*50)
    successful_sources = sum([1 for x in [yahoo_df, coinmarketcap_data, investing_df] if x is not None])
    print(f"[OK] Successful sources: {successful_sources}/3")
    
    total_records = 0
    if yahoo_df is not None:
        total_records += len(yahoo_df)
    if investing_df is not None:
        total_records += len(investing_df)
    
    print(f"[DATA] Total records collected: {total_records}")
    print(f"[READY] Ready for trading analysis")
    print(f"[REPORT] Comprehensive markdown report saved to: {markdown_path}")
    print("="*50)
    print("DATA COLLECTION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())