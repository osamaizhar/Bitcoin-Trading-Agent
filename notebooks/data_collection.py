"""
Bitcoin Trading Agent - Data Collection Module

This module handles comprehensive Bitcoin data collection from multiple sources:
- Investing.com Bitcoin historical data (via CSV)
- CoinMarketCap API for current prices  
- Yahoo Finance as backup
- Enhanced DataCollector with multiple sources
- Fallback web scraping methods

The script is organized into modular functions for better maintainability.
"""

import os
import sys
import pandas as pd
import numpy as np
import requests
import yfinance as yf
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv
import warnings
import json
from bs4 import BeautifulSoup

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

def setup_environment():
    """
    Setup environment, load variables, and configure Python paths
    
    Returns:
        dict: Environment configuration status
    """
    print("Setting up environment...")
    
    # Load environment variables
    load_dotenv()
    
    # Fix Python path for imports - use absolute path
    current_dir = os.path.dirname(os.path.abspath(''))
    project_root = os.path.dirname(current_dir) if os.path.basename(current_dir) == 'notebooks' else current_dir
    src_path = os.path.join(project_root, 'src')
    
    # Add both possible paths to ensure imports work
    if os.path.exists(src_path):
        sys.path.insert(0, src_path)
        sys.path.insert(0, project_root)
    else:
        # Fallback paths 
        sys.path.insert(0, '../src')
        sys.path.insert(0, '..')
    
    env_status = {
        'env_loaded': os.path.exists('../.env') or os.path.exists('.env'),
        'paths_added': [p for p in sys.path[:3]],
        'project_root': project_root,
        'src_path': src_path
    }
    
    print("Libraries loaded successfully")
    print(f"Environment variables loaded: {env_status['env_loaded']}")
    print(f"Python paths added: {env_status['paths_added']}")
    
    return env_status

def setup_data_directory():
    """
    Create data directory if it doesn't exist
    
    Returns:
        str: Path to data directory
    """
    data_dir = '../data'
    os.makedirs(data_dir, exist_ok=True)
    print(f"Data directory ready: {os.path.abspath(data_dir)}")
    return data_dir

def collect_enhanced_data():
    """
    Try to collect data using Enhanced DataCollector with multiple sources
    
    Returns:
        dict: Results from enhanced data collection
    """
    print("\n[INFO] Using Enhanced DataCollector with Multiple Sources...")
    
    results = {
        'enhanced_available': False,
        'successful_sources': [],
        'all_data': {},
        'combined_data': None,
        'current_price': None
    }
    
    # Multiple import strategies to handle different path configurations
    collector = None
    enhanced_available = False
    
    # Strategy 1: Try direct import from data_collector
    try:
        from data_collector import DataCollector
        print("Imported DataCollector directly")
        enhanced_available = True
    except ImportError as e1:
        print(f"[WARN] Direct import failed: {e1}")
        
        # Strategy 2: Try import from src.data_collector
        try:
            from src.data_collector import DataCollector
            print("Imported DataCollector from src module")
            enhanced_available = True
        except ImportError as e2:
            print(f"[WARN] src module import failed: {e2}")
            
            # Strategy 3: Try with sys.path manipulation
            try:
                project_root = os.path.dirname(os.path.abspath('.'))
                src_path = os.path.join(project_root, 'src')
                if src_path not in sys.path:
                    sys.path.insert(0, src_path)
                
                from data_collector import DataCollector
                print("Imported DataCollector with path manipulation")
                enhanced_available = True
            except ImportError as e3:
                print(f"[WARN] All import strategies failed:")
                print(f"  - Direct: {e1}")
                print(f"  - Module: {e2}")  
                print(f"  - Path: {e3}")
                enhanced_available = False
    
    results['enhanced_available'] = enhanced_available
    
    # If enhanced collector is available, try to use it
    if enhanced_available:
        try:
            # Initialize enhanced data collector
            collector = DataCollector()
            
            print(f"Available sources: {list(collector.sources.keys())}")
            
            # Try collecting data from all sources
            all_data = collector.collect_all_data(period='6mo')
            
            print(f"\n[DATA] Enhanced Data Collection Results:")
            successful_sources = []
            for source, data in all_data.items():
                if data is not None and not data.empty:
                    print(f"{source}: {len(data)} records")
                    # Save individual source data
                    data.to_csv(f'../data/btc_{source}_enhanced.csv', index=False)
                    successful_sources.append(source)
                else:
                    print(f"{source}: No data")
            
            results['successful_sources'] = successful_sources
            results['all_data'] = all_data
            
            # Get current price from best source
            current_price = collector.get_current_price()
            if current_price:
                print(f"\n[PRICE] Current BTC Price from enhanced collector: ${current_price:,.2f}")
                results['current_price'] = current_price
            else:
                print("\n[WARN] Could not get current price from enhanced collector")
                
            # Combine successful sources
            if successful_sources:
                try:
                    # Try to import standardize_dataframes function
                    try:
                        from data_collector import standardize_dataframes
                    except ImportError:
                        try:
                            from src.data_collector import standardize_dataframes
                        except ImportError:
                            print("[WARN] Could not import standardize_dataframes, using local function")
                            # Define local version if import fails
                            def standardize_dataframes(*dataframes, source_names=None):
                                if source_names is None:
                                    source_names = [f'source_{i}' for i in range(len(dataframes))]
                                
                                combined_data = []
                                for df, source in zip(dataframes, source_names):
                                    if df is not None and not df.empty:
                                        df_copy = df.copy()
                                        df_copy['source'] = source
                                        combined_data.append(df_copy)
                                
                                if combined_data:
                                    return pd.concat(combined_data, ignore_index=True)
                                return None
                    
                    successful_dfs = [all_data[source] for source in successful_sources]
                    enhanced_combined = standardize_dataframes(*successful_dfs, source_names=successful_sources)
                    
                    if enhanced_combined is not None:
                        print(f"\nEnhanced Combined Dataset: {len(enhanced_combined)} records")
                        print(f"Sources: {enhanced_combined['source'].unique()}")
                        enhanced_combined.to_csv('../data/btc_enhanced_combined.csv', index=False)
                        results['combined_data'] = enhanced_combined
                        
                except Exception as combine_error:
                    print(f"[WARN] Error combining enhanced data: {combine_error}")
                    
        except Exception as collector_error:
            print(f"[ERROR] Enhanced DataCollector runtime error: {collector_error}")
            print("Falling back to original scraping methods...")
            enhanced_available = False
    else:
        print("[ERROR] Enhanced DataCollector not available")
        print("Falling back to original scraping methods...")
    
    return results

def collect_investing_data():
    """
    Collect Bitcoin data from Investing.com CSV file
    
    Returns:
        pd.DataFrame: Investing.com data or None if not available
    """
    print("\n[INFO] Loading Investing.com data from CSV...")
    
    investing_csv_path = '../bitcoin_data_investing.com.csv'
    
    try:
        if os.path.exists(investing_csv_path):
            investing_df = pd.read_csv(investing_csv_path)
            print(f"[OK] Investing.com data loaded: {len(investing_df)} records")
            print(f"Date range: {investing_df['Date'].iloc[-1]} to {investing_df['Date'].iloc[0]}")
            
            # Save to data directory
            investing_df.to_csv('../data/btc_investing_raw.csv', index=False)
            return investing_df
        else:
            print(f"[WARN] Investing.com CSV not found at: {investing_csv_path}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error loading Investing.com data: {str(e)}")
        return None

def collect_fallback_scraping_data():
    """
    Fallback method using requests + BeautifulSoup if all else fails
    
    Returns:
        pd.DataFrame: Scraped data or None if failed
    """
    print("\n[INFO] Trying fallback scraping method...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        url = "https://www.investing.com/crypto/bitcoin/historical-data"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the historical data table
            table = soup.find('table', {'data-test': 'historical-data-table'})
            if not table:
                table = soup.find('table', class_='historical-data-table')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                
                data = []
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        date_str = cols[0].text.strip()
                        price = cols[1].text.replace(',', '').replace('$', '').strip()
                        open_price = cols[2].text.replace(',', '').replace('$', '').strip()
                        high = cols[3].text.replace(',', '').replace('$', '').strip()
                        low = cols[4].text.replace(',', '').replace('$', '').strip()
                        volume = cols[5].text.replace(',', '').strip()
                        
                        data.append({
                            'date': date_str,
                            'price': float(price) if price else None,
                            'open': float(open_price) if open_price else None,
                            'high': float(high) if high else None,
                            'low': float(low) if low else None,
                            'volume': volume
                        })
                
                if data:
                    df = pd.DataFrame(data)
                    print(f"[OK] Fallback method successful: {len(df)} records")
                    return df
            
    except Exception as e:
        print(f"[ERROR] Fallback scraper error: {str(e)}")
        
    print("[ERROR] Fallback scraping method also failed")
    return None

def collect_coinmarketcap_data():
    """
    Fetch current Bitcoin data from CoinMarketCap API
    
    Returns:
        dict: Current market data or None if not available
    """
    print("\n[INFO] Fetching CoinMarketCap data...")
    
    api_key = os.getenv('COINMARKETCAP_API_KEY')
    
    if not api_key or api_key == 'your_coinmarketcap_api_key_here':
        print("[WARN] CoinMarketCap API key not configured")
        return None
    
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': 'BTC',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    
    try:
        response = requests.get(url, headers=headers, params=parameters, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and 'data' in data:
            btc_data = data['data']['BTC']
            quote = btc_data['quote']['USD']
            
            current_data = {
                'timestamp': datetime.now().isoformat(),
                'price': quote['price'],
                'volume_24h': quote['volume_24h'],
                'percent_change_1h': quote['percent_change_1h'],
                'percent_change_24h': quote['percent_change_24h'],
                'percent_change_7d': quote['percent_change_7d'],
                'market_cap': quote['market_cap'],
                'last_updated': quote['last_updated']
            }
            
            print("[OK] Current Bitcoin data from CoinMarketCap:")
            print(f"Price: ${current_data['price']:,.2f}")
            print(f"24h Change: {current_data['percent_change_24h']:.2f}%")
            print(f"Volume 24h: ${current_data['volume_24h']:,.0f}")
            print(f"Market Cap: ${current_data['market_cap']:,.0f}")
            
            return current_data
        else:
            print(f"[ERROR] CoinMarketCap API error: {data}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error fetching CoinMarketCap data: {str(e)}")
        return None

def collect_yahoo_finance_data(period='6mo'):
    """
    Fetch Bitcoin data from Yahoo Finance
    
    Args:
        period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
    Returns:
        tuple: (DataFrame, current_price) or (None, None) if failed
    """
    print("\n[INFO] Fetching Yahoo Finance data...")
    
    try:
        btc_ticker = yf.Ticker("BTC-USD")
        hist_data = btc_ticker.history(period=period)
        
        if not hist_data.empty:
            # Reset index to get date as column
            hist_data = hist_data.reset_index()
            
            # Rename columns to match our standard format
            hist_data.columns = [col.lower() for col in hist_data.columns]
            hist_data['date'] = hist_data['date'].dt.strftime('%Y-%m-%d')
            hist_data['price'] = hist_data['close']
            
            # Get current info
            info = btc_ticker.info
            current_price = info.get('regularMarketPrice', hist_data['close'].iloc[-1])
            
            print(f"[OK] Yahoo Finance data: {len(hist_data)} records")
            print(f"Date range: {hist_data['date'].iloc[0]} to {hist_data['date'].iloc[-1]}")
            print(f"Current price: ${current_price:,.2f}")
            print(f"Latest close: ${hist_data['close'].iloc[-1]:,.2f}")
            
            # Save Yahoo data
            hist_data.to_csv('../data/btc_yahoo_raw.csv', index=False)
            
            return hist_data, current_price
        else:
            print("[ERROR] No data returned from Yahoo Finance")
            return None, None
            
    except Exception as e:
        print(f"[ERROR] Error fetching Yahoo Finance data: {str(e)}")
        return None, None

def standardize_and_combine_data(*dataframes, source_names=None):
    """
    Standardize and combine Bitcoin data from multiple sources
    
    Args:
        *dataframes: Variable number of DataFrames to combine
        source_names (list): Names for each source
        
    Returns:
        pd.DataFrame: Combined standardized data or None if no data
    """
    print("\n[INFO] Standardizing and combining data...")
    
    if source_names is None:
        source_names = [f'source_{i}' for i in range(len(dataframes))]
    
    combined_data = []
    
    for df, source in zip(dataframes, source_names):
        if df is not None and not df.empty:
            # Create a copy to avoid modifying original
            df_copy = df.copy()
            
            # Ensure we have required columns
            required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
            
            # Map common column variations
            if 'price' in df_copy.columns and 'close' not in df_copy.columns:
                df_copy['close'] = df_copy['price']
            
            # Convert date to datetime if it's not already
            if 'date' in df_copy.columns:
                df_copy['date'] = pd.to_datetime(df_copy['date'])
            
            # Add source column
            df_copy['source'] = source
            
            # Select and reorder columns
            available_cols = [col for col in required_cols if col in df_copy.columns]
            df_final = df_copy[available_cols + ['source']].copy()
            
            combined_data.append(df_final)
            print(f"Processed {len(df_final)} records from {source}")
        else:
            print(f"[WARN] No data available from {source}")
    
    if combined_data:
        # Combine all dataframes
        final_df = pd.concat(combined_data, ignore_index=True)
        
        # Remove duplicates based on date and source
        final_df = final_df.drop_duplicates(subset=['date', 'source'])
        
        # Sort by date
        final_df = final_df.sort_values('date').reset_index(drop=True)
        
        print(f"\n[OK] Combined dataset: {len(final_df)} total records")
        print(f"Date range: {final_df['date'].min()} to {final_df['date'].max()}")
        print(f"Sources: {final_df['source'].unique()}")
        
        # Save combined data
        final_df.to_csv('../data/btc_combined_raw.csv', index=False)
        
        return final_df
    else:
        print("[ERROR] No data sources available")
        return None

def perform_data_quality_analysis(df):
    """
    Comprehensive data quality assessment
    
    Args:
        df (pd.DataFrame): DataFrame to analyze
        
    Returns:
        dict: Quality assessment report
    """
    print("\n[ANALYSIS] Data Quality Assessment")
    print("="*50)
    
    if df is None or df.empty:
        print("[ERROR] No data to check")
        return None
    
    # Basic info
    print(f"[DATA] Dataset Shape: {df.shape}")
    print(f"[DATE] Date Range: {df['date'].min()} to {df['date'].max()}")
    print(f"Total Days: {(df['date'].max() - df['date'].min()).days} days")
    
    # Missing values
    print("\n[ANALYSIS] Missing Values:")
    missing_summary = df.isnull().sum()
    for col, missing in missing_summary.items():
        if missing > 0:
            pct = (missing / len(df)) * 100
            print(f"  {col}: {missing} ({pct:.1f}%)")
        else:
            print(f"  {col}: No missing values")
    
    # Data types
    print("\n[SUMMARY] Data Types:")
    for col, dtype in df.dtypes.items():
        print(f"  {col}: {dtype}")
    
    # Price statistics
    price_stats = None
    if 'close' in df.columns:
        print("\n[PRICE] Price Statistics:")
        price_stats = df['close'].describe()
        for stat, value in price_stats.items():
            print(f"  {stat}: ${value:,.2f}")
        
        # Price anomalies
        print("\nPrice Anomaly Checks:")
        
        # Check for negative prices
        negative_prices = (df['close'] <= 0).sum()
        print(f"  Negative/Zero prices: {negative_prices}")
        
        # Check for extreme price changes (>50% in one day)
        df_sorted = df.sort_values('date')
        price_changes = df_sorted['close'].pct_change().abs()
        extreme_changes = (price_changes > 0.5).sum()
        print(f"  Extreme daily changes (>50%): {extreme_changes}")
        
        if extreme_changes > 0:
            extreme_dates = df_sorted[price_changes > 0.5]['date'].tolist()
            print(f"    Dates with extreme changes: {extreme_dates[:5]}")
    
    # Duplicate checks
    print("\nDuplicate Checks:")
    date_duplicates = df['date'].duplicated().sum()
    print(f"  Duplicate dates: {date_duplicates}")
    
    # Source distribution
    if 'source' in df.columns:
        print("\nData Source Distribution:")
        source_counts = df['source'].value_counts()
        for source, count in source_counts.items():
            pct = (count / len(df)) * 100
            print(f"  {source}: {count} records ({pct:.1f}%)")
    
    return {
        'shape': df.shape,
        'missing_values': missing_summary.to_dict(),
        'date_range': (df['date'].min(), df['date'].max()),
        'price_stats': price_stats.to_dict() if price_stats is not None else None,
        'anomalies': {
            'negative_prices': negative_prices if 'close' in df.columns else 0,
            'extreme_changes': extreme_changes if 'close' in df.columns else 0
        }
    }

def generate_markdown_report(investing_df=None, yahoo_df=None, yahoo_current=None, 
                           cmc_data=None, enhanced_combined=None, combined_btc_data=None, quality_report=None):
    """
    Generate a comprehensive markdown report with all collected Bitcoin data
    
    Args:
        investing_df: Investing.com DataFrame
        yahoo_df: Yahoo Finance DataFrame  
        yahoo_current: Current price from Yahoo
        cmc_data: CoinMarketCap data dict
        enhanced_combined: Enhanced multi-source data
        combined_btc_data: Combined dataset
        quality_report: Data quality report
        
    Returns:
        str: Markdown content
    """
    print("\n[INFO] Generating markdown report...")
    
    markdown_content = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Header
    markdown_content.append("# Complete Bitcoin Data Collection Report")
    markdown_content.append(f"\nGenerated on: {timestamp}\n")
    markdown_content.append("This report consolidates Bitcoin price data from multiple sources for comprehensive analysis.\n")
    
    # Table of Contents
    markdown_content.append("## Table of Contents")
    markdown_content.append("- [Data Sources Summary](#data-sources-summary)")
    
    sources_added = []
    
    # Check for Investing.com data from CSV
    investing_csv_path = '../bitcoin_data_investing.com.csv'
    if os.path.exists(investing_csv_path) or investing_df is not None:
        sources_added.append("investing")
        markdown_content.append("- [Investing.com Data](#investingcom-data)")
    
    if yahoo_df is not None:
        sources_added.append("yahoo")
        markdown_content.append("- [Yahoo Finance Data](#yahoo-finance-data)")
    
    if cmc_data is not None:
        sources_added.append("coinmarketcap")
        markdown_content.append("- [CoinMarketCap Data](#coinmarketcap-data)")
    
    if enhanced_combined is not None:
        sources_added.append("enhanced")
        markdown_content.append("- [Enhanced Multi-Source Data](#enhanced-multi-source-data)")
    
    if combined_btc_data is not None:
        sources_added.append("combined")
        markdown_content.append("- [Combined Dataset](#combined-dataset)")
    
    markdown_content.append("- [Data Quality Summary](#data-quality-summary)\n")
    
    # Data Sources Summary
    markdown_content.append("## Data Sources Summary")
    markdown_content.append(f"\nTotal data sources processed: {len(sources_added)}\n")
    
    for source in sources_added:
        if source == "investing":
            markdown_content.append("- **Investing.com**: Historical Bitcoin price data via web scraping")
        elif source == "yahoo":
            markdown_content.append("- **Yahoo Finance**: Historical price data via yfinance API")
        elif source == "coinmarketcap":
            markdown_content.append("- **CoinMarketCap**: Current market data via API")
        elif source == "enhanced":
            markdown_content.append("- **Enhanced DataCollector**: Multi-source aggregated data")
        elif source == "combined":
            markdown_content.append("- **Combined Dataset**: Standardized data from all sources")
    
    markdown_content.append("")
    
    # Investing.com Data
    if os.path.exists(investing_csv_path) or investing_df is not None:
        markdown_content.append("## Investing.com Data")
        markdown_content.append("\n**Source**: https://www.investing.com/crypto/bitcoin/historical-data")
        markdown_content.append("**Method**: Web scraping via Crawl4AI\n")
        
        try:
            if investing_df is None:
                investing_df_md = pd.read_csv(investing_csv_path)
            else:
                investing_df_md = investing_df
                
            markdown_content.append(f"**Records**: {len(investing_df_md)} data points")
            markdown_content.append(f"**Date Range**: {investing_df_md.iloc[:, 0].iloc[-1]} to {investing_df_md.iloc[:, 0].iloc[0]}")
            markdown_content.append(f"**Latest Price**: {investing_df_md.iloc[:, 1].iloc[0]}\n")
            
            markdown_content.append("### Recent Data (Last 10 Records)")
            markdown_content.append("\n| Date | Price | Open | High | Low | Volume | Change % |")
            markdown_content.append("|------|-------|------|------|-----|--------|----------|")
            
            for _, row in investing_df_md.head(10).iterrows():
                row_values = [str(val) for val in row.values[:7]]  # Take first 7 columns
                while len(row_values) < 7:
                    row_values.append("")
                markdown_content.append(f"| {' | '.join(row_values)} |")
            
            markdown_content.append("")
        except Exception as e:
            markdown_content.append(f"**Error**: Error reading Investing.com data: {str(e)}\n")
    
    # Yahoo Finance Data
    if yahoo_df is not None:
        markdown_content.append("## Yahoo Finance Data")
        markdown_content.append("\n**Source**: Yahoo Finance API")
        markdown_content.append("**Method**: yfinance Python library")
        markdown_content.append(f"**Symbol**: BTC-USD\n")
        
        markdown_content.append(f"**Records**: {len(yahoo_df)} data points")
        markdown_content.append(f"**Date Range**: {yahoo_df['date'].iloc[0]} to {yahoo_df['date'].iloc[-1]}")
        if yahoo_current:
            markdown_content.append(f"**Current Price**: ${yahoo_current:,.2f}\n")
        
        markdown_content.append("### Recent Data (Last 10 Records)")
        markdown_content.append("\n| Date | Open | High | Low | Close | Volume |")
        markdown_content.append("|------|------|------|-----|-------|--------|")
        
        for _, row in yahoo_df.tail(10).iterrows():
            markdown_content.append(f"| {row['date']} | ${row['open']:,.2f} | ${row['high']:,.2f} | ${row['low']:,.2f} | ${row['close']:,.2f} | {row['volume']:,} |")
        
        markdown_content.append("")
    
    # CoinMarketCap Data
    if cmc_data is not None:
        markdown_content.append("## CoinMarketCap Data")
        markdown_content.append("\n**Source**: CoinMarketCap Pro API")
        markdown_content.append("**Method**: REST API call")
        markdown_content.append("**Data Type**: Current market data\n")
        
        markdown_content.append("### Current Market Information")
        markdown_content.append(f"\n- **Price**: ${cmc_data['price']:,.2f}")
        markdown_content.append(f"- **24h Volume**: ${cmc_data['volume_24h']:,.0f}")
        markdown_content.append(f"- **Market Cap**: ${cmc_data['market_cap']:,.0f}")
        markdown_content.append(f"- **1h Change**: {cmc_data['percent_change_1h']:.2f}%")
        markdown_content.append(f"- **24h Change**: {cmc_data['percent_change_24h']:.2f}%")
        markdown_content.append(f"- **7d Change**: {cmc_data['percent_change_7d']:.2f}%")
        markdown_content.append(f"- **Last Updated**: {cmc_data['last_updated']}\n")
    
    # Enhanced Multi-Source Data
    if enhanced_combined is not None:
        markdown_content.append("## Enhanced Multi-Source Data")
        markdown_content.append("\n**Source**: Enhanced DataCollector")
        markdown_content.append("**Method**: Multiple API sources with failover")
        markdown_content.append("**Description**: Aggregated data from multiple sources for reliability\n")
        
        markdown_content.append(f"**Total Records**: {len(enhanced_combined)} data points")
        markdown_content.append(f"**Date Range**: {enhanced_combined['date'].min()} to {enhanced_combined['date'].max()}")
        
        if 'source' in enhanced_combined.columns:
            source_counts = enhanced_combined['source'].value_counts()
            markdown_content.append("\n### Data Distribution by Source")
            for source, count in source_counts.items():
                markdown_content.append(f"- **{source}**: {count} records ({count/len(enhanced_combined)*100:.1f}%)")
        
        markdown_content.append("")
    
    # Combined Dataset
    if combined_btc_data is not None:
        markdown_content.append("## Combined Dataset")
        markdown_content.append("\n**Description**: Standardized and merged data from all available sources")
        markdown_content.append("**Purpose**: Comprehensive dataset for analysis and trading strategies\n")
        
        markdown_content.append(f"**Total Records**: {len(combined_btc_data)} data points")
        markdown_content.append(f"**Date Range**: {combined_btc_data['date'].min()} to {combined_btc_data['date'].max()}")
        
        if 'source' in combined_btc_data.columns:
            source_counts = combined_btc_data['source'].value_counts()
            markdown_content.append("\n### Combined Data Distribution")
            for source, count in source_counts.items():
                markdown_content.append(f"- **{source}**: {count} records ({count/len(combined_btc_data)*100:.1f}%)")
        
        markdown_content.append("")
    
    # Data Quality Summary
    markdown_content.append("## Data Quality Summary")
    
    if quality_report is not None:
        markdown_content.append("\n### Quality Metrics")
        markdown_content.append(f"- **Total Records**: {quality_report['shape'][0]}")
        markdown_content.append(f"- **Total Columns**: {quality_report['shape'][1]}")
        
        if quality_report['missing_values']:
            markdown_content.append("\n### Missing Values")
            for col, missing in quality_report['missing_values'].items():
                if missing > 0:
                    pct = (missing / quality_report['shape'][0]) * 100
                    markdown_content.append(f"- **{col}**: {missing} missing ({pct:.1f}%)")
        
        if quality_report['price_stats']:
            markdown_content.append("\n### Price Statistics")
            stats = quality_report['price_stats']
            markdown_content.append(f"- **Mean Price**: ${stats['mean']:,.2f}")
            markdown_content.append(f"- **Min Price**: ${stats['min']:,.2f}")
            markdown_content.append(f"- **Max Price**: ${stats['max']:,.2f}")
            markdown_content.append(f"- **Standard Deviation**: ${stats['std']:,.2f}")
        
        if quality_report['anomalies']:
            markdown_content.append("\n### Data Anomalies")
            anomalies = quality_report['anomalies']
            markdown_content.append(f"- **Negative/Zero Prices**: {anomalies['negative_prices']}")
            markdown_content.append(f"- **Extreme Daily Changes (>50%)**: {anomalies['extreme_changes']}")
    
    markdown_content.append("\n---")
    markdown_content.append(f"\n*Report generated by Bitcoin Trading Agent - Data Collection Module*")
    markdown_content.append(f"\n*Timestamp: {timestamp}*")
    
    return "\n".join(markdown_content)

def save_data_files(collection_summary):
    """
    Save collection summary and other data files
    
    Args:
        collection_summary (dict): Summary of data collection results
    """
    print("\n[INFO] Saving data files...")
    
    # Save collection summary
    with open('../data/collection_summary.json', 'w') as f:
        json.dump(collection_summary, f, indent=2, default=str)
    
    print("Data files saved successfully")

def display_summary(collection_summary):
    """
    Display collection summary to console
    
    Args:
        collection_summary (dict): Summary of data collection results
    """
    print("\n" + "="*50)
    print("[SUMMARY] Data Collection Summary")
    print("="*50)
    print(f"[OK] Successful sources: {len(collection_summary['sources_successful'])}/{len(collection_summary['sources_attempted'])}")
    print(f"[DATA] Total records collected: {collection_summary['total_records']}")
    print(f"[FILES] Files created: {len(collection_summary['files_created'])}")
    print(f"[READY] Ready for EDA: {'Yes' if collection_summary['total_records'] > 0 else 'No'}")

    if collection_summary['total_records'] > 0:
        print(f"\n[DATE] Date range: {collection_summary['date_range'][0]} to {collection_summary['date_range'][1]}")
        print("\n[NEXT] Next step: Run notebook 02_eda_analysis.ipynb for exploratory data analysis")
    else:
        print("\n[ERROR] No data collected - check API keys and network connectivity")

    print("\n[REPORT] Comprehensive markdown report saved to: complete_bitcoin_data.md")

def main():
    """
    Main function to orchestrate the entire data collection process
    """
    print("="*60)
    print("BITCOIN TRADING AGENT - DATA COLLECTION")
    print("="*60)
    
    # Setup environment and directories
    env_status = setup_environment()
    data_dir = setup_data_directory()
    
    # Initialize collection summary
    collection_summary = {
        'timestamp': datetime.now().isoformat(),
        'sources_attempted': ['investing.com', 'coinmarketcap', 'yahoo_finance'],
        'sources_successful': [],
        'total_records': 0,
        'date_range': None,
        'files_created': [],
        'quality_report': None
    }
    
    # Collect data from all sources
    enhanced_results = collect_enhanced_data()
    investing_df = collect_investing_data()
    cmc_data = collect_coinmarketcap_data()
    yahoo_df, yahoo_current = collect_yahoo_finance_data()
    
    # If enhanced data collection failed, try fallback scraping
    if not enhanced_results['enhanced_available'] or not enhanced_results['successful_sources']:
        fallback_df = collect_fallback_scraping_data()
        if fallback_df is not None:
            investing_df = fallback_df  # Use fallback data as investing data
    
    # Prepare data for combination
    available_dfs = []
    source_names = []
    
    if investing_df is not None:
        available_dfs.append(investing_df)
        source_names.append('investing')
        collection_summary['sources_successful'].append('investing.com')
        collection_summary['files_created'].append('btc_investing_raw.csv')
    
    if yahoo_df is not None:
        available_dfs.append(yahoo_df)
        source_names.append('yahoo')
        collection_summary['sources_successful'].append('yahoo_finance')
        collection_summary['files_created'].append('btc_yahoo_raw.csv')
    
    if cmc_data is not None:
        collection_summary['sources_successful'].append('coinmarketcap')
    
    # Combine and standardize data
    combined_btc_data = None
    if available_dfs:
        combined_btc_data = standardize_and_combine_data(*available_dfs, source_names=source_names)
        
        if combined_btc_data is not None:
            collection_summary['total_records'] = len(combined_btc_data)
            collection_summary['date_range'] = [
                combined_btc_data['date'].min().isoformat(),
                combined_btc_data['date'].max().isoformat()
            ]
            collection_summary['files_created'].append('btc_combined_raw.csv')
    
    # Perform data quality analysis
    quality_report = None
    if combined_btc_data is not None:
        quality_report = perform_data_quality_analysis(combined_btc_data)
        collection_summary['quality_report'] = quality_report
    elif enhanced_results.get('combined_data') is not None:
        quality_report = perform_data_quality_analysis(enhanced_results['combined_data'])
        collection_summary['quality_report'] = quality_report
    else:
        print("\n[WARN] No combined data available for quality checks")
    
    # Generate comprehensive markdown report
    markdown_report = generate_markdown_report(
        investing_df=investing_df,
        yahoo_df=yahoo_df,
        yahoo_current=yahoo_current,
        cmc_data=cmc_data,
        enhanced_combined=enhanced_results.get('combined_data'),
        combined_btc_data=combined_btc_data,
        quality_report=quality_report
    )
    
    # Save markdown report
    with open('complete_bitcoin_data.md', 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print("[OK] Markdown report generated: complete_bitcoin_data.md")
    
    # Save data files and display summary
    save_data_files(collection_summary)
    display_summary(collection_summary)
    
    print("\n" + "="*60)
    print("DATA COLLECTION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()