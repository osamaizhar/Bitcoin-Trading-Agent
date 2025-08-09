"""
Bitcoin Trading Agent - Modular Data Collection

This module provides individual callable functions for Bitcoin data collection
from multiple sources with proper error handling and path management.
"""

import os
import sys
import pandas as pd
import numpy as np
import requests
import yfinance as yf
from datetime import datetime, timedelta
import asyncio
import json
import warnings
from typing import Dict, List, Optional, Tuple, Any

warnings.filterwarnings('ignore')

# =============================================================================
# 1. SETUP AND CONFIGURATION FUNCTIONS
# =============================================================================

def setup_environment() -> Dict[str, Any]:
    """
    Setup environment variables, paths, and imports.
    
    Returns:
        dict: Environment setup status and configuration
    """
    try:
        from dotenv import load_dotenv
        
        # Load environment variables
        env_loaded = load_dotenv()
        
        # Fix Python path for imports
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        src_path = os.path.join(project_root, 'src')
        
        # Add paths to sys.path if they exist
        paths_added = []
        if os.path.exists(src_path):
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
                paths_added.append(src_path)
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
                paths_added.append(project_root)
        else:
            # Fallback paths
            fallback_paths = ['../src', '..']
            for path in fallback_paths:
                if path not in sys.path:
                    sys.path.insert(0, path)
                    paths_added.append(path)
        
        # Check for environment file existence
        env_files = ['../.env', '.env', '../.env']
        env_file_exists = any(os.path.exists(f) for f in env_files)
        
        config = {
            'env_loaded': env_loaded,
            'paths_added': paths_added,
            'env_file_exists': env_file_exists,
            'project_root': project_root,
            'src_path': src_path,
            'current_dir': current_dir
        }
        
        print("✅ Environment setup completed successfully")
        print(f"📁 Environment file found: {env_file_exists}")
        print(f"🔧 Python paths added: {len(paths_added)} paths")
        
        return config
        
    except Exception as e:
        print(f"❌ Environment setup failed: {e}")
        return {
            'env_loaded': False,
            'paths_added': [],
            'env_file_exists': False,
            'error': str(e)
        }

def create_data_directories(base_path: str = "..") -> Dict[str, str]:
    """
    Create necessary data directories.
    
    Args:
        base_path: Base path for data directory
        
    Returns:
        dict: Created directory paths
    """
    try:
        data_dir = os.path.join(base_path, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Create subdirectories if needed
        subdirs = ['raw', 'processed', 'enhanced']
        created_dirs = {'data': data_dir}
        
        for subdir in subdirs:
            subdir_path = os.path.join(data_dir, subdir)
            os.makedirs(subdir_path, exist_ok=True)
            created_dirs[subdir] = subdir_path
        
        print(f"✅ Data directories created: {data_dir}")
        return created_dirs
        
    except Exception as e:
        print(f"❌ Failed to create data directories: {e}")
        return {'error': str(e)}

def load_configuration() -> Dict[str, Any]:
    """
    Load and validate configuration settings.
    
    Returns:
        dict: Configuration settings and API availability
    """
    config = {
        'apis': {},
        'settings': {},
        'available_sources': []
    }
    
    try:
        # Check API keys
        api_keys = {
            'coinmarketcap': os.getenv('COINMARKETCAP_API_KEY'),
            'groq': os.getenv('GROQ_API_KEY'),
            'gmail': os.getenv('GMAIL_APP_PASSWORD'),
            'whatsapp_phone': os.getenv('WHATSAPP_PHONE_NUMBER')
        }
        
        config['apis'] = api_keys
        
        # Determine available sources
        if api_keys['coinmarketcap'] and api_keys['coinmarketcap'] != 'your_coinmarketcap_api_key_here':
            config['available_sources'].append('coinmarketcap')
        
        if api_keys['groq'] and api_keys['groq'] != 'your_groq_key':
            config['available_sources'].append('investing_crawl4ai')
        
        # Yahoo Finance and basic scraping are always available
        config['available_sources'].extend(['yahoo_finance', 'investing_scraper'])
        
        # Settings
        config['settings'] = {
            'default_period': '6mo',
            'retry_attempts': 3,
            'timeout_seconds': 30
        }
        
        print(f"✅ Configuration loaded - {len(config['available_sources'])} data sources available")
        
        return config
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        config['error'] = str(e)
        return config

# =============================================================================
# 2. DATA COLLECTION FUNCTIONS  
# =============================================================================

def collect_enhanced_data(period: str = '6mo', data_dir: str = '../data') -> Dict[str, Any]:
    """
    Try to collect data using enhanced DataCollector from src module.
    
    Args:
        period: Time period for data collection
        data_dir: Directory to save data files
        
    Returns:
        dict: Collection results with data and metadata
    """
    result = {
        'success': False,
        'data': None,
        'sources_successful': [],
        'sources_failed': [],
        'current_price': None,
        'error': None
    }
    
    # Multiple import strategies
    collector = None
    enhanced_available = False
    
    print("🔄 Attempting to load Enhanced DataCollector...")
    
    # Strategy 1: Direct import
    try:
        from data_collector import DataCollector
        print("✅ Imported DataCollector directly")
        enhanced_available = True
    except ImportError as e1:
        print(f"⚠️ Direct import failed: {e1}")
        
        # Strategy 2: Module import
        try:
            from src.data_collector import DataCollector
            print("✅ Imported DataCollector from src module")
            enhanced_available = True
        except ImportError as e2:
            print(f"⚠️ src module import failed: {e2}")
            
            # Strategy 3: Path manipulation
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)
                src_path = os.path.join(project_root, 'src')
                if src_path not in sys.path:
                    sys.path.insert(0, src_path)
                
                from data_collector import DataCollector
                print("✅ Imported DataCollector with path manipulation")
                enhanced_available = True
            except ImportError as e3:
                print(f"⚠️ All import strategies failed:")
                print(f"  - Direct: {e1}")
                print(f"  - Module: {e2}")
                print(f"  - Path: {e3}")
                result['error'] = f"Import failed: {e1}, {e2}, {e3}"
                return result
    
    if not enhanced_available:
        result['error'] = "Enhanced DataCollector not available"
        return result
    
    try:
        # Initialize collector
        collector = DataCollector()
        
        print(f"Available sources: {list(collector.sources.keys())}")
        
        # Collect data from all sources
        all_data = collector.collect_all_data(period=period)
        
        print(f"\n📊 Enhanced Data Collection Results:")
        for source, data in all_data.items():
            if data is not None and not data.empty:
                print(f"✅ {source}: {len(data)} records")
                # Save individual source data
                data.to_csv(f'{data_dir}/btc_{source}_enhanced.csv', index=False)
                result['sources_successful'].append(source)
            else:
                print(f"❌ {source}: No data")
                result['sources_failed'].append(source)
        
        # Get current price
        result['current_price'] = collector.get_current_price()
        if result['current_price']:
            print(f"\n💰 Current BTC Price: ${result['current_price']:,.2f}")
        
        # Combine successful sources
        if result['sources_successful']:
            try:
                # Try to import standardize function
                standardize_func = None
                try:
                    from data_collector import standardize_dataframes
                    standardize_func = standardize_dataframes
                except ImportError:
                    try:
                        from src.data_collector import standardize_dataframes
                        standardize_func = standardize_dataframes
                    except ImportError:
                        print("⚠️ Using local standardize function")
                        standardize_func = _local_standardize_dataframes
                
                successful_dfs = [all_data[source] for source in result['sources_successful']]
                combined_data = standardize_func(*successful_dfs, source_names=result['sources_successful'])
                
                if combined_data is not None:
                    print(f"✅ Combined Dataset: {len(combined_data)} records")
                    print(f"Sources: {combined_data['source'].unique()}")
                    combined_data.to_csv(f'{data_dir}/btc_enhanced_combined.csv', index=False)
                    result['data'] = combined_data
                    result['success'] = True
            
            except Exception as combine_error:
                print(f"⚠️ Error combining data: {combine_error}")
                result['error'] = f"Combination failed: {combine_error}"
        
        return result
        
    except Exception as e:
        print(f"❌ Enhanced DataCollector runtime error: {e}")
        result['error'] = f"Runtime error: {e}"
        return result

def collect_coinmarketcap_data() -> Dict[str, Any]:
    """
    Fetch current Bitcoin data from CoinMarketCap API.
    
    Returns:
        dict: API response data and metadata
    """
    result = {
        'success': False,
        'data': None,
        'error': None
    }
    
    try:
        api_key = os.getenv('COINMARKETCAP_API_KEY')
        
        if not api_key or api_key == 'your_coinmarketcap_api_key_here':
            result['error'] = "CoinMarketCap API key not configured"
            print("⚠️ CoinMarketCap API key not configured")
            return result
        
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {'symbol': 'BTC', 'convert': 'USD'}
        headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': api_key}
        
        response = requests.get(url, headers=headers, params=parameters, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and 'data' in data:
            btc_data = data['data']['BTC']
            quote = btc_data['quote']['USD']
            
            result['data'] = {
                'timestamp': datetime.now().isoformat(),
                'price': quote['price'],
                'volume_24h': quote['volume_24h'],
                'percent_change_1h': quote['percent_change_1h'],
                'percent_change_24h': quote['percent_change_24h'],
                'percent_change_7d': quote['percent_change_7d'],
                'market_cap': quote['market_cap'],
                'last_updated': quote['last_updated']
            }
            result['success'] = True
            
            print("✅ CoinMarketCap data collected successfully")
            print(f"Price: ${result['data']['price']:,.2f}")
            print(f"24h Change: {result['data']['percent_change_24h']:.2f}%")
            
        else:
            result['error'] = f"API error: {data}"
            print(f"❌ CoinMarketCap API error: {data}")
        
        return result
        
    except Exception as e:
        result['error'] = f"Request failed: {e}"
        print(f"❌ Error fetching CoinMarketCap data: {e}")
        return result

def collect_yahoo_data(period: str = '6mo') -> Dict[str, Any]:
    """
    Fetch Bitcoin data from Yahoo Finance.
    
    Args:
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
    Returns:
        dict: Yahoo Finance data and metadata
    """
    result = {
        'success': False,
        'data': None,
        'current_price': None,
        'error': None
    }
    
    try:
        btc_ticker = yf.Ticker("BTC-USD")
        hist_data = btc_ticker.history(period=period)
        
        if not hist_data.empty:
            # Reset index and standardize columns
            hist_data = hist_data.reset_index()
            hist_data.columns = [col.lower() for col in hist_data.columns]
            hist_data['date'] = hist_data['date'].dt.strftime('%Y-%m-%d')
            hist_data['price'] = hist_data['close']
            
            # Get current price
            try:
                info = btc_ticker.info
                current_price = info.get('regularMarketPrice', hist_data['close'].iloc[-1])
            except:
                current_price = hist_data['close'].iloc[-1]
            
            result['data'] = hist_data
            result['current_price'] = current_price
            result['success'] = True
            
            print(f"✅ Yahoo Finance data: {len(hist_data)} records")
            print(f"Date range: {hist_data['date'].iloc[0]} to {hist_data['date'].iloc[-1]}")
            print(f"Current price: ${current_price:,.2f}")
            
        else:
            result['error'] = "No data returned from Yahoo Finance"
            print("❌ No data returned from Yahoo Finance")
        
        return result
        
    except Exception as e:
        result['error'] = f"Yahoo Finance error: {e}"
        print(f"❌ Error fetching Yahoo Finance data: {e}")
        return result

async def collect_investing_data_crawl4ai() -> Dict[str, Any]:
    """
    Scrape Bitcoin historical data from Investing.com using Crawl4AI.
    
    Returns:
        dict: Scraped data and metadata
    """
    result = {
        'success': False,
        'data': None,
        'error': None
    }
    
    try:
        # Check if required modules are available
        from crawl4ai import AsyncWebCrawler
        from crawl4ai.extraction_strategy import LLMExtractionStrategy, LLMConfig
        
        groq_key = os.getenv('GROQ_API_KEY')
        if not groq_key or groq_key == 'your_groq_key':
            result['error'] = "Groq API key not configured for Crawl4AI"
            return result
        
        url = "https://www.investing.com/crypto/bitcoin/historical-data"
        
        extraction_strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider="groq",
                api_token=groq_key,
                model="llama-3.3-70b-versatile"
            ),
            instruction="""
            Extract the historical Bitcoin price data from the table. 
            Return a JSON array with objects containing:
            - date: The date in YYYY-MM-DD format
            - price: The closing price as a number
            - open: The opening price as a number  
            - high: The highest price as a number
            - low: The lowest price as a number
            - volume: The volume as a number
            - change_pct: The percentage change as a number
            """
        )
        
        async with AsyncWebCrawler(verbose=True) as crawler:
            crawl_result = await crawler.arun(
                url=url,
                extraction_strategy=extraction_strategy,
                css_selector=".historical-data-table, table[data-test='historical-data-table']",
                wait_for="css:.historical-data-table",
                timeout=30000
            )
            
            if crawl_result.extracted_content:
                try:
                    # Parse the extracted JSON data
                    data = json.loads(crawl_result.extracted_content)
                    if data and len(data) > 0:
                        result['data'] = pd.DataFrame(data)
                        result['success'] = True
                        print(f"✅ Crawl4AI data: {len(result['data'])} records")
                    else:
                        result['error'] = "No data extracted from Investing.com"
                except json.JSONDecodeError:
                    result['error'] = "Failed to parse extracted data as JSON"
            else:
                result['error'] = "No content extracted from Investing.com"
        
        return result
        
    except ImportError as e:
        result['error'] = f"Crawl4AI not available: {e}"
        return result
    except Exception as e:
        result['error'] = f"Crawl4AI scraping failed: {e}"
        return result

def collect_investing_data_fallback() -> Dict[str, Any]:
    """
    Fallback method using requests + BeautifulSoup for Investing.com.
    
    Returns:
        dict: Scraped data and metadata
    """
    result = {
        'success': False,
        'data': None,
        'error': None
    }
    
    try:
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        url = "https://www.investing.com/crypto/bitcoin/historical-data"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find historical data table
            table = soup.find('table', {'data-test': 'historical-data-table'})
            if not table:
                table = soup.find('table', class_='historical-data-table')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                data = []
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        try:
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
                        except (ValueError, IndexError):
                            continue  # Skip malformed rows
                
                if data:
                    result['data'] = pd.DataFrame(data)
                    result['success'] = True
                    print(f"✅ Investing.com fallback: {len(data)} records")
                else:
                    result['error'] = "No valid data rows found in table"
            else:
                result['error'] = "Historical data table not found"
        else:
            result['error'] = f"HTTP error: {response.status_code}"
        
        return result
        
    except ImportError:
        result['error'] = "BeautifulSoup not available for fallback scraping"
        return result
    except Exception as e:
        result['error'] = f"Fallback scraping failed: {e}"
        return result

# =============================================================================
# 3. DATA PROCESSING AND QUALITY CHECK FUNCTIONS
# =============================================================================

def standardize_data_sources(*dataframes, source_names=None, data_dir='../data') -> Dict[str, Any]:
    """
    Standardize and combine Bitcoin data from multiple sources.
    
    Args:
        dataframes: Variable number of DataFrame arguments
        source_names: List of source names for each DataFrame
        data_dir: Directory to save combined data
        
    Returns:
        dict: Combined data results and metadata
    """
    result = {
        'success': False,
        'data': None,
        'sources_processed': [],
        'error': None
    }
    
    try:
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
                result['sources_processed'].append(source)
                print(f"✅ Processed {len(df_final)} records from {source}")
            else:
                print(f"⚠️ No data available from {source}")
        
        if combined_data:
            # Combine all dataframes
            final_df = pd.concat(combined_data, ignore_index=True)
            
            # Remove duplicates based on date and source
            final_df = final_df.drop_duplicates(subset=['date', 'source'])
            
            # Sort by date
            final_df = final_df.sort_values('date').reset_index(drop=True)
            
            result['data'] = final_df
            result['success'] = True
            
            # Save combined data
            output_file = os.path.join(data_dir, 'btc_combined_standardized.csv')
            final_df.to_csv(output_file, index=False)
            
            print(f"\n✅ Combined dataset: {len(final_df)} total records")
            print(f"Date range: {final_df['date'].min()} to {final_df['date'].max()}")
            print(f"Sources: {final_df['source'].unique()}")
            
        else:
            result['error'] = "No valid data sources to combine"
        
        return result
        
    except Exception as e:
        result['error'] = f"Standardization failed: {e}"
        print(f"❌ Failed to standardize data sources: {e}")
        return result

def perform_data_quality_checks(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Comprehensive data quality assessment.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        dict: Quality assessment results
    """
    result = {
        'success': False,
        'quality_score': 0,
        'issues': [],
        'summary': {},
        'error': None
    }
    
    try:
        if df is None or df.empty:
            result['error'] = "No data to check"
            return result
        
        print("🔍 Data Quality Assessment")
        print("="*50)
        
        # Basic info
        shape = df.shape
        date_range = (df['date'].min(), df['date'].max()) if 'date' in df.columns else None
        total_days = (date_range[1] - date_range[0]).days if date_range else 0
        
        print(f"📊 Dataset Shape: {shape}")
        if date_range:
            print(f"📅 Date Range: {date_range[0]} to {date_range[1]}")
            print(f"🔢 Total Days: {total_days} days")
        
        # Missing values analysis
        print("\n🔍 Missing Values:")
        missing_summary = df.isnull().sum()
        missing_issues = 0
        
        for col, missing in missing_summary.items():
            if missing > 0:
                pct = (missing / len(df)) * 100
                print(f"  {col}: {missing} ({pct:.1f}%)")
                result['issues'].append(f"Missing {col}: {missing} ({pct:.1f}%)")
                missing_issues += 1
            else:
                print(f"  {col}: ✅ No missing values")
        
        # Data types
        print("\n📋 Data Types:")
        for col, dtype in df.dtypes.items():
            print(f"  {col}: {dtype}")
        
        # Price statistics and anomalies
        if 'close' in df.columns:
            print("\n💰 Price Statistics:")
            price_stats = df['close'].describe()
            for stat, value in price_stats.items():
                print(f"  {stat}: ${value:,.2f}")
            
            # Price anomaly checks
            print("\n⚠️ Price Anomaly Checks:")
            
            # Check for negative prices
            negative_prices = (df['close'] <= 0).sum()
            print(f"  Negative/Zero prices: {negative_prices}")
            if negative_prices > 0:
                result['issues'].append(f"Negative/zero prices: {negative_prices}")
            
            # Check for extreme price changes (>50% in one day)
            df_sorted = df.sort_values('date') if 'date' in df.columns else df
            price_changes = df_sorted['close'].pct_change().abs()
            extreme_changes = (price_changes > 0.5).sum()
            print(f"  Extreme daily changes (>50%): {extreme_changes}")
            
            if extreme_changes > 0:
                result['issues'].append(f"Extreme price changes: {extreme_changes}")
                extreme_dates = df_sorted[price_changes > 0.5]['date'].tolist()
                print(f"    Dates with extreme changes: {extreme_dates[:5]}")
        
        # Duplicate checks
        print("\n🔄 Duplicate Checks:")
        if 'date' in df.columns:
            date_duplicates = df['date'].duplicated().sum()
            print(f"  Duplicate dates: {date_duplicates}")
            if date_duplicates > 0:
                result['issues'].append(f"Duplicate dates: {date_duplicates}")
        
        # Source distribution
        if 'source' in df.columns:
            print("\n📈 Data Source Distribution:")
            source_counts = df['source'].value_counts()
            for source, count in source_counts.items():
                pct = (count / len(df)) * 100
                print(f"  {source}: {count} records ({pct:.1f}%)")
        
        # Calculate quality score (0-100)
        quality_score = 100
        quality_score -= min(missing_issues * 10, 30)  # Deduct for missing data
        quality_score -= min(len(result['issues']) * 5, 50)  # Deduct for other issues
        
        result['quality_score'] = max(quality_score, 0)
        result['summary'] = {
            'shape': shape,
            'missing_values': missing_summary.to_dict(),
            'date_range': date_range,
            'price_stats': price_stats.to_dict() if 'close' in df.columns else None,
            'total_issues': len(result['issues'])
        }
        result['success'] = True
        
        print(f"\n🏆 Data Quality Score: {result['quality_score']}/100")
        
        return result
        
    except Exception as e:
        result['error'] = f"Quality check failed: {e}"
        print(f"❌ Data quality assessment failed: {e}")
        return result

def save_data_files(data_dict: Dict[str, pd.DataFrame], data_dir: str = '../data') -> Dict[str, Any]:
    """
    Save collected data to CSV files with proper naming.
    
    Args:
        data_dict: Dictionary with source names as keys and DataFrames as values
        data_dir: Directory to save files
        
    Returns:
        dict: Save operation results
    """
    result = {
        'success': False,
        'files_saved': [],
        'files_failed': [],
        'error': None
    }
    
    try:
        os.makedirs(data_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for source_name, df in data_dict.items():
            if df is not None and not df.empty:
                try:
                    filename = f'btc_{source_name}_{timestamp}.csv'
                    filepath = os.path.join(data_dir, filename)
                    df.to_csv(filepath, index=False)
                    result['files_saved'].append(filepath)
                    print(f"✅ Saved {source_name}: {filepath}")
                except Exception as file_error:
                    result['files_failed'].append(f"{source_name}: {file_error}")
                    print(f"❌ Failed to save {source_name}: {file_error}")
            else:
                result['files_failed'].append(f"{source_name}: No data to save")
        
        if result['files_saved']:
            result['success'] = True
            print(f"\n📁 Saved {len(result['files_saved'])} files to {data_dir}")
        else:
            result['error'] = "No files were saved successfully"
        
        return result
        
    except Exception as e:
        result['error'] = f"Save operation failed: {e}"
        print(f"❌ Failed to save data files: {e}")
        return result

# =============================================================================
# 4. SUMMARY AND REPORTING FUNCTIONS  
# =============================================================================

def generate_collection_summary(collection_results: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Generate comprehensive summary of data collection results.
    
    Args:
        collection_results: Dictionary containing results from each collection function
        
    Returns:
        dict: Complete collection summary
    """
    summary = {
        'timestamp': datetime.now().isoformat(),
        'sources_attempted': list(collection_results.keys()),
        'sources_successful': [],
        'sources_failed': [],
        'total_records': 0,
        'date_range': None,
        'files_created': [],
        'errors': {},
        'quality_summary': None,
        'recommendations': []
    }
    
    try:
        # Analyze each collection result
        all_data = []
        
        for source, result in collection_results.items():
            if result.get('success', False) and result.get('data') is not None:
                summary['sources_successful'].append(source)
                data = result['data']
                if not data.empty:
                    all_data.append(data)
                    summary['total_records'] += len(data)
            else:
                summary['sources_failed'].append(source)
                if result.get('error'):
                    summary['errors'][source] = result['error']
        
        # Calculate overall date range
        if all_data:
            all_dates = []
            for df in all_data:
                if 'date' in df.columns:
                    all_dates.extend(df['date'].tolist())
            
            if all_dates:
                summary['date_range'] = [
                    min(all_dates).isoformat() if hasattr(min(all_dates), 'isoformat') else str(min(all_dates)),
                    max(all_dates).isoformat() if hasattr(max(all_dates), 'isoformat') else str(max(all_dates))
                ]
        
        # Generate recommendations
        success_rate = len(summary['sources_successful']) / len(summary['sources_attempted']) * 100
        
        if success_rate < 50:
            summary['recommendations'].append("Low success rate - check API keys and network connectivity")
        
        if summary['total_records'] == 0:
            summary['recommendations'].append("No data collected - verify API access and retry")
        
        if len(summary['sources_successful']) == 1:
            summary['recommendations'].append("Only one data source successful - consider backup options")
        
        return summary
        
    except Exception as e:
        summary['error'] = f"Summary generation failed: {e}"
        return summary

def print_collection_results(summary: Dict[str, Any]) -> None:
    """
    Print formatted collection results.
    
    Args:
        summary: Collection summary dictionary
    """
    try:
        print("\n📋 Data Collection Summary")
        print("="*50)
        
        total_attempted = len(summary.get('sources_attempted', []))
        total_successful = len(summary.get('sources_successful', []))
        
        print(f"✅ Successful sources: {total_successful}/{total_attempted}")
        
        if summary.get('sources_successful'):
            print("  📊 Successful:")
            for source in summary['sources_successful']:
                print(f"    - {source}")
        
        if summary.get('sources_failed'):
            print("  ❌ Failed:")
            for source in summary['sources_failed']:
                error = summary.get('errors', {}).get(source, 'Unknown error')
                print(f"    - {source}: {error}")
        
        print(f"\n📊 Total records collected: {summary.get('total_records', 0)}")
        
        if summary.get('date_range'):
            print(f"📅 Date range: {summary['date_range'][0]} to {summary['date_range'][1]}")
        
        if summary.get('files_created'):
            print(f"📁 Files created: {len(summary['files_created'])}")
        
        ready_for_analysis = summary.get('total_records', 0) > 0
        print(f"🏁 Ready for analysis: {'✅' if ready_for_analysis else '❌'}")
        
        if summary.get('recommendations'):
            print("\n💡 Recommendations:")
            for rec in summary['recommendations']:
                print(f"  - {rec}")
        
        if ready_for_analysis:
            print("\n🎯 Next step: Run analysis functions or trading strategy development")
        
    except Exception as e:
        print(f"❌ Error printing results: {e}")

def save_collection_summary(summary: Dict[str, Any], data_dir: str = '../data') -> bool:
    """
    Save collection summary to JSON file.
    
    Args:
        summary: Collection summary dictionary
        data_dir: Directory to save summary
        
    Returns:
        bool: Success status
    """
    try:
        os.makedirs(data_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(data_dir, f'collection_summary_{timestamp}.json')
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"✅ Summary saved to: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save summary: {e}")
        return False

# =============================================================================
# 5. MAIN ORCHESTRATION FUNCTIONS
# =============================================================================

def run_individual_source(source_name: str, **kwargs) -> Dict[str, Any]:
    """
    Run data collection for a specific source.
    
    Args:
        source_name: Name of the data source ('yahoo', 'coinmarketcap', etc.)
        **kwargs: Additional arguments for the collection function
        
    Returns:
        dict: Collection result
    """
    print(f"\n🔄 Running data collection for: {source_name}")
    
    try:
        if source_name.lower() == 'yahoo' or source_name.lower() == 'yahoo_finance':
            period = kwargs.get('period', '6mo')
            return collect_yahoo_data(period=period)
            
        elif source_name.lower() == 'coinmarketcap':
            return collect_coinmarketcap_data()
            
        elif source_name.lower() == 'investing_crawl4ai':
            # This requires async execution
            return asyncio.run(collect_investing_data_crawl4ai())
            
        elif source_name.lower() == 'investing_fallback':
            return collect_investing_data_fallback()
            
        elif source_name.lower() == 'enhanced':
            period = kwargs.get('period', '6mo')
            data_dir = kwargs.get('data_dir', '../data')
            return collect_enhanced_data(period=period, data_dir=data_dir)
            
        else:
            return {
                'success': False,
                'error': f"Unknown source: {source_name}",
                'available_sources': ['yahoo', 'coinmarketcap', 'investing_crawl4ai', 'investing_fallback', 'enhanced']
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f"Failed to run {source_name}: {e}"
        }

def run_full_collection(period: str = '6mo', data_dir: str = '../data', 
                       sources: List[str] = None) -> Dict[str, Any]:
    """
    Execute complete data collection pipeline.
    
    Args:
        period: Time period for historical data
        data_dir: Directory for output files
        sources: List of sources to collect from (None = all available)
        
    Returns:
        dict: Complete collection results
    """
    print("🚀 Starting full Bitcoin data collection pipeline...")
    
    # Setup environment
    print("\n1️⃣ Setting up environment...")
    env_config = setup_environment()
    
    # Create directories
    print("\n2️⃣ Creating data directories...")
    dirs_created = create_data_directories(os.path.dirname(data_dir))
    
    # Load configuration
    print("\n3️⃣ Loading configuration...")
    config = load_configuration()
    
    # Determine sources to use
    if sources is None:
        sources = ['yahoo', 'coinmarketcap', 'investing_fallback', 'enhanced']
    
    available_sources = config.get('available_sources', [])
    sources_to_run = [s for s in sources if any(avail in s for avail in available_sources)]
    
    print(f"\n4️⃣ Collecting data from {len(sources_to_run)} sources...")
    
    # Collect data from each source
    collection_results = {}
    
    for source in sources_to_run:
        try:
            result = run_individual_source(source, period=period, data_dir=data_dir)
            collection_results[source] = result
        except Exception as e:
            collection_results[source] = {'success': False, 'error': str(e)}
    
    # Standardize and combine successful results
    print("\n5️⃣ Processing and standardizing data...")
    
    successful_dfs = []
    successful_sources = []
    
    for source, result in collection_results.items():
        if result.get('success') and result.get('data') is not None:
            successful_dfs.append(result['data'])
            successful_sources.append(source)
    
    combined_result = None
    if successful_dfs:
        combined_result = standardize_data_sources(*successful_dfs, 
                                                 source_names=successful_sources, 
                                                 data_dir=data_dir)
    
    # Perform quality checks
    print("\n6️⃣ Performing data quality checks...")
    quality_result = None
    if combined_result and combined_result.get('success'):
        quality_result = perform_data_quality_checks(combined_result['data'])
    
    # Generate summary
    print("\n7️⃣ Generating collection summary...")
    summary = generate_collection_summary(collection_results)
    if quality_result:
        summary['quality_summary'] = quality_result
    
    # Save results
    print("\n8️⃣ Saving results...")
    
    # Save individual files
    data_to_save = {}
    for source, result in collection_results.items():
        if result.get('success') and result.get('data') is not None:
            data_to_save[source] = result['data']
    
    if data_to_save:
        save_result = save_data_files(data_to_save, data_dir)
        summary['files_created'] = save_result.get('files_saved', [])
    
    # Save summary
    save_collection_summary(summary, data_dir)
    
    # Print results
    print_collection_results(summary)
    
    return {
        'summary': summary,
        'collection_results': collection_results,
        'combined_data': combined_result,
        'quality_check': quality_result,
        'environment': env_config,
        'configuration': config
    }

# =============================================================================
# 6. HELPER FUNCTIONS
# =============================================================================

def _local_standardize_dataframes(*dataframes, source_names=None):
    """
    Local version of standardize_dataframes function.
    
    Args:
        dataframes: Variable number of DataFrame arguments
        source_names: List of source names for each DataFrame
        
    Returns:
        pd.DataFrame: Combined and standardized DataFrame
    """
    if source_names is None:
        source_names = [f'source_{i}' for i in range(len(dataframes))]
    
    combined_data = []
    
    for df, source in zip(dataframes, source_names):
        if df is not None and not df.empty:
            df_copy = df.copy()
            
            # Ensure we have required columns
            required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
            
            # Map common column variations
            if 'price' in df_copy.columns and 'close' not in df_copy.columns:
                df_copy['close'] = df_copy['price']
            
            # Convert date to datetime if needed
            if 'date' in df_copy.columns:
                df_copy['date'] = pd.to_datetime(df_copy['date'])
            
            # Add source column
            df_copy['source'] = source
            
            # Select available columns
            available_cols = [col for col in required_cols if col in df_copy.columns]
            df_final = df_copy[available_cols + ['source']].copy()
            
            combined_data.append(df_final)
    
    if combined_data:
        # Combine all dataframes
        final_df = pd.concat(combined_data, ignore_index=True)
        # Remove duplicates and sort
        final_df = final_df.drop_duplicates(subset=['date', 'source'])
        final_df = final_df.sort_values('date').reset_index(drop=True)
        return final_df
    else:
        return None

def get_available_sources() -> List[str]:
    """
    Get list of all available data sources.
    
    Returns:
        list: Available source names
    """
    return ['yahoo', 'coinmarketcap', 'investing_crawl4ai', 'investing_fallback', 'enhanced']

def validate_period(period: str) -> bool:
    """
    Validate if the period string is valid for Yahoo Finance.
    
    Args:
        period: Time period string
        
    Returns:
        bool: True if valid period
    """
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    return period in valid_periods

# =============================================================================
# 7. EXAMPLE USAGE AND TESTING
# =============================================================================

def example_usage():
    """
    Example usage of the modular data collection functions.
    """
    print("🔍 Bitcoin Data Collection - Example Usage")
    print("="*60)
    
    # Example 1: Setup environment
    print("\n1. Setup Environment:")
    env_config = setup_environment()
    print(f"Environment setup success: {env_config.get('env_loaded', False)}")
    
    # Example 2: Collect from single source
    print("\n2. Collect from Yahoo Finance:")
    yahoo_result = run_individual_source('yahoo', period='1mo')
    print(f"Yahoo collection success: {yahoo_result.get('success', False)}")
    
    # Example 3: Collect from CoinMarketCap
    print("\n3. Collect from CoinMarketCap:")
    cmc_result = run_individual_source('coinmarketcap')
    print(f"CoinMarketCap success: {cmc_result.get('success', False)}")
    
    # Example 4: Run full collection pipeline
    print("\n4. Run Full Collection Pipeline:")
    full_result = run_full_collection(period='1mo', data_dir='../data')
    
    return {
        'environment': env_config,
        'yahoo': yahoo_result,
        'coinmarketcap': cmc_result,
        'full_collection': full_result
    }

if __name__ == "__main__":
    """
    Run example usage when script is executed directly.
    """
    print("🚀 Running Bitcoin Data Collection Module...")
    
    # You can uncomment the line below to run example usage:
    # example_results = example_usage()
    
    print("\n📚 Available Functions:")
    print("="*40)
    print("Setup Functions:")
    print("  - setup_environment()")
    print("  - create_data_directories()")
    print("  - load_configuration()")
    
    print("\nData Collection Functions:")
    print("  - collect_yahoo_data(period='6mo')")
    print("  - collect_coinmarketcap_data()")
    print("  - collect_investing_data_crawl4ai()")
    print("  - collect_investing_data_fallback()")
    print("  - collect_enhanced_data()")
    
    print("\nProcessing Functions:")
    print("  - standardize_data_sources()")
    print("  - perform_data_quality_checks()")
    print("  - save_data_files()")
    
    print("\nOrchestration Functions:")
    print("  - run_individual_source(source_name)")
    print("  - run_full_collection(period, data_dir, sources)")
    
    print("\n💡 Example Usage:")
    print("from data_collection_modular import *")
    print("")
    print("# Collect Yahoo Finance data")
    print("yahoo_result = run_individual_source('yahoo', period='6mo')")
    print("")
    print("# Run full collection pipeline")
    print("full_result = run_full_collection(period='6mo', data_dir='../data')")
    print("")
    print("# Check data quality")
    print("if full_result['combined_data'] and full_result['combined_data']['success']:")
    print("    quality = perform_data_quality_checks(full_result['combined_data']['data'])")
    print("    print(f'Quality Score: {quality[\"quality_score\"]}/100')")
    
    print("\n✅ Module ready for use!")