"""
Bitcoin Trading Agent - Data Collection Module

This module handles data collection from multiple sources:
- Crawl4AI for Investing.com
- Yahoo Finance API
- CoinMarketCap API
"""

import os
import pandas as pd
import requests
import yfinance as yf
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DataCollector:
    """Main data collection class"""
    
    def __init__(self):
        self.sources = {
            'yahoo': YahooFinanceCollector(),
            'coinmarketcap': CoinMarketCapCollector(),
            'investing': InvestingCollector()
        }
    
    def collect_all_data(self, period='6mo'):
        """Collect data from all available sources"""
        data = {}
        
        for source_name, collector in self.sources.items():
            try:
                source_data = collector.get_data(period)
                if source_data is not None:
                    data[source_name] = source_data
                    logger.info(f"Successfully collected data from {source_name}")
                else:
                    logger.warning(f"No data from {source_name}")
            except Exception as e:
                logger.error(f"Error collecting from {source_name}: {e}")
        
        return data
    
    def get_current_price(self):
        """Get current Bitcoin price from best available source"""
        for source_name, collector in self.sources.items():
            try:
                price = collector.get_current_price()
                if price:
                    return price
            except Exception as e:
                logger.error(f"Error getting price from {source_name}: {e}")
        
        return None


class YahooFinanceCollector:
    """Yahoo Finance data collector"""
    
    def get_data(self, period='6mo'):
        """Get historical data from Yahoo Finance"""
        try:
            btc = yf.Ticker("BTC-USD")
            hist = btc.history(period=period)
            
            if not hist.empty:
                hist = hist.reset_index()
                hist.columns = [col.lower() for col in hist.columns]
                hist['source'] = 'yahoo'
                return hist
            
            return None
            
        except Exception as e:
            logger.error(f"Yahoo Finance error: {e}")
            return None
    
    def get_current_price(self):
        """Get current Bitcoin price"""
        try:
            btc = yf.Ticker("BTC-USD")
            info = btc.info
            return info.get('regularMarketPrice')
        except Exception as e:
            logger.error(f"Yahoo current price error: {e}")
            return None


class CoinMarketCapCollector:
    """CoinMarketCap API collector"""
    
    def __init__(self):
        self.api_key = os.getenv('COINMARKETCAP_API_KEY')
        self.base_url = 'https://pro-api.coinmarketcap.com/v1'
    
    def get_data(self, period=None):
        """Get current data from CoinMarketCap"""
        return self.get_current_data()
    
    def get_current_data(self):
        """Get current Bitcoin data from CoinMarketCap"""
        if not self.api_key or self.api_key == 'your_coinmarketcap_api_key_here':
            return None
        
        try:
            url = f'{self.base_url}/cryptocurrency/quotes/latest'
            headers = {
                'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': self.api_key,
            }
            params = {'symbol': 'BTC', 'convert': 'USD'}
            
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            if response.status_code == 200 and 'data' in data:
                btc_data = data['data']['BTC']['quote']['USD']
                return {
                    'price': btc_data['price'],
                    'volume_24h': btc_data['volume_24h'],
                    'percent_change_24h': btc_data['percent_change_24h'],
                    'market_cap': btc_data['market_cap'],
                    'timestamp': datetime.now()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"CoinMarketCap error: {e}")
            return None
    
    def get_current_price(self):
        """Get current Bitcoin price"""
        data = self.get_current_data()
        return data['price'] if data else None


class InvestingCollector:
    """Investing.com data collector using Crawl4AI"""
    
    async def get_data_async(self, period=None):
        """Get data using Crawl4AI (async)"""
        try:
            from crawl4ai import AsyncWebCrawler
            from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
            
            browser_config = BrowserConfig(headless=True, verbose=False)
            run_config = CrawlerRunConfig(
                word_count_threshold=10,
                exclude_external_links=True
            )
            
            url = "https://www.investing.com/crypto/bitcoin/historical-data"
            
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=url, config=run_config)
                
                if result.success:
                    return result.markdown
                else:
                    return None
                    
        except ImportError:
            logger.warning("Crawl4AI not installed")
            return None
        except Exception as e:
            logger.error(f"Crawl4AI error: {e}")
            return None
    
    def get_data(self, period=None):
        """Get data using fallback scraper"""
        return self._fallback_scraper()
    
    def _fallback_scraper(self):
        """Fallback scraper using requests + BeautifulSoup"""
        try:
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            url = "https://www.investing.com/crypto/bitcoin/historical-data"
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple table selectors
                selectors = [
                    'table[data-test="historical-data-table"]',
                    'table.historical-data-table',
                    'table.genTbl'
                ]
                
                table = None
                for selector in selectors:
                    table = soup.select_one(selector)
                    if table:
                        break
                
                if table:
                    return self._parse_table(table)
            
            return None
            
        except Exception as e:
            logger.error(f"Fallback scraper error: {e}")
            return None
    
    def _parse_table(self, table):
        """Parse HTML table to DataFrame"""
        try:
            rows = table.find_all('tr')[1:]  # Skip header
            data = []
            
            for row in rows[:50]:  # Limit to 50 recent records
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 6:
                    try:
                        date_text = cols[0].get_text(strip=True)
                        price = float(cols[1].get_text(strip=True).replace(',', '').replace('$', ''))
                        open_price = float(cols[2].get_text(strip=True).replace(',', '').replace('$', ''))
                        high = float(cols[3].get_text(strip=True).replace(',', '').replace('$', ''))
                        low = float(cols[4].get_text(strip=True).replace(',', '').replace('$', ''))
                        volume = cols[5].get_text(strip=True).replace(',', '')
                        
                        date_obj = pd.to_datetime(date_text, errors='coerce')
                        if pd.notna(date_obj):
                            data.append({
                                'date': date_obj,
                                'open': open_price,
                                'high': high,
                                'low': low,
                                'close': price,
                                'volume': volume,
                                'source': 'investing'
                            })
                    except (ValueError, IndexError):
                        continue
            
            return pd.DataFrame(data) if data else None
            
        except Exception as e:
            logger.error(f"Table parsing error: {e}")
            return None
    
    def get_current_price(self):
        """Get current price from scraped data"""
        data = self.get_data()
        if data is not None and not data.empty:
            return data['close'].iloc[0]  # Most recent price
        return None


# Utility functions
def standardize_dataframes(*dataframes, source_names=None):
    """Standardize and combine multiple dataframes"""
    if source_names is None:
        source_names = [f'source_{i}' for i in range(len(dataframes))]
    
    combined_data = []
    
    for df, source in zip(dataframes, source_names):
        if df is not None and not df.empty:
            df_copy = df.copy()
            
            # Ensure required columns
            required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
            
            # Map common column variations
            if 'price' in df_copy.columns and 'close' not in df_copy.columns:
                df_copy['close'] = df_copy['price']
            
            # Convert date
            if 'date' in df_copy.columns:
                df_copy['date'] = pd.to_datetime(df_copy['date'])
            
            # Add source
            df_copy['source'] = source
            
            # Select available columns
            available_cols = [col for col in required_cols if col in df_copy.columns]
            df_final = df_copy[available_cols + ['source']].copy()
            
            combined_data.append(df_final)
    
    if combined_data:
        final_df = pd.concat(combined_data, ignore_index=True)
        final_df = final_df.drop_duplicates(subset=['date', 'source'])
        final_df = final_df.sort_values('date').reset_index(drop=True)
        return final_df
    
    return None


def get_current_market_data():
    """Get comprehensive current market data"""
    collector = DataCollector()
    
    try:
        import ta
        
        # Get current data
        current_price = collector.get_current_price()
        if not current_price:
            return None
        
        # Get recent historical data for indicators
        yahoo_collector = YahooFinanceCollector()
        hist_data = yahoo_collector.get_data(period="30d")
        
        if hist_data is not None and not hist_data.empty:
            # Calculate technical indicators
            atr_14 = ta.volatility.average_true_range(
                hist_data['high'], hist_data['low'], hist_data['close'], window=14
            ).iloc[-1]
            
            rsi_14 = ta.momentum.rsi(hist_data['close'], window=14).iloc[-1]
            
            # Price change
            prev_close = hist_data['close'].iloc[-2]
            pct_change_1d = ((current_price - prev_close) / prev_close) * 100
            
            return {
                'timestamp': datetime.now(),
                'price': current_price,
                'atr_14': atr_14,
                'rsi_14': rsi_14,
                'pct_change_1d': pct_change_1d,
                'volume': hist_data['volume'].iloc[-1]
            }
        
        # Fallback without indicators
        return {
            'timestamp': datetime.now(),
            'price': current_price,
            'atr_14': 1000,  # Default ATR
            'rsi_14': 50,    # Neutral RSI
            'pct_change_1d': 0,
            'volume': 0
        }
        
    except Exception as e:
        logger.error(f"Current market data error: {e}")
        return None