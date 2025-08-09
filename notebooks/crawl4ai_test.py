import asyncio
from crawl4ai import AsyncWebCrawler
import pandas as pd
from bs4 import BeautifulSoup
import re

async def scrape_bitcoin_historical():
    url = "https://www.investing.com/crypto/bitcoin/historical-data"
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        # Crawl with extended wait and interaction
        result = await crawler.arun(
            url=url,
            js_code="""
                // Wait for page to fully load
                await new Promise(r => setTimeout(r, 5000));
                
                // Look for and click date range or "Show more" buttons
                const buttons = document.querySelectorAll('button, a');
                for (let btn of buttons) {
                    if (btn.textContent.includes('Show more') || 
                        btn.textContent.includes('Load more') ||
                        btn.textContent.includes('Historical')) {
                        btn.click();
                        await new Promise(r => setTimeout(r, 2000));
                    }
                }
                
                // Scroll to load lazy content
                window.scrollTo(0, document.body.scrollHeight / 2);
                await new Promise(r => setTimeout(r, 2000));
                window.scrollTo(0, document.body.scrollHeight);
                await new Promise(r => setTimeout(r, 3000));
                
                // Look for the historical data table specifically
                const tables = document.querySelectorAll('table');
                for (let table of tables) {
                    const headers = table.querySelectorAll('th');
                    for (let header of headers) {
                        if (header.textContent.includes('Date') || 
                            header.textContent.includes('Price') ||
                            header.textContent.includes('Open')) {
                            // Found the right table, make it visible
                            table.scrollIntoView();
                            break;
                        }
                    }
                }
            """,
            wait_for="table",
            timeout=40000
        )
        
        if result.html:
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Find the correct table by looking for date patterns in the data
            all_tables = soup.find_all('table')
            print(f"\nFound {len(all_tables)} tables. Analyzing...")
            
            historical_data = []
            
            for i, table in enumerate(all_tables):
                rows = table.find_all('tr')
                if len(rows) > 5:  # Should have multiple data rows
                    # Check if this table has date-like content
                    sample_row = rows[1] if len(rows) > 1 else None
                    if sample_row:
                        cells = sample_row.find_all('td')
                        if cells:
                            first_cell = cells[0].get_text(strip=True)
                            # Check if first cell looks like a date
                            if any(month in first_cell for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                                print(f"✓ Table {i+1} appears to contain historical data")
                                
                                # Extract data from this table
                                for row in rows[1:]:  # Skip header
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
                                        # Verify this is price data (contains numbers)
                                        if any(char.isdigit() for char in row_data['Price']):
                                            historical_data.append(row_data)
                                
                                if historical_data:
                                    break  # Found the right table
            
            if historical_data:
                df = pd.DataFrame(historical_data)
                
                # Clean the data
                df['Date'] = df['Date'].str.replace('\n', ' ').str.strip()
                df['Price'] = df['Price'].str.replace(',', '').str.strip()
                df['Open'] = df['Open'].str.replace(',', '').str.strip()
                df['High'] = df['High'].str.replace(',', '').str.strip()
                df['Low'] = df['Low'].str.replace(',', '').str.strip()
                
                # Save to CSV
                df.to_csv("bitcoin_data_investing.com.csv", index=False)
                
                print(f"\n✅ Successfully extracted {len(df)} rows of historical data")
                print("\nFirst 5 rows:")
                print(df.head())
                print("\nLast 5 rows:")
                print(df.tail())
                
                return df
            else:
                print("\n❌ No historical price data found")
                
                # Debug: Save all table content
                print("\nSaving page content for debugging...")
                with open("page_debug.html", "w", encoding="utf-8") as f:
                    f.write(result.html)
                print("Page HTML saved to 'page_debug.html'")
                
                # Show what was found in tables
                for i, table in enumerate(all_tables[:3]):  # Check first 3 tables
                    print(f"\nTable {i+1} sample:")
                    rows = table.find_all('tr')[:3]  # First 3 rows
                    for row in rows:
                        cells = row.find_all(['th', 'td'])[:4]  # First 4 cells
                        print(" | ".join([cell.get_text(strip=True)[:20] for cell in cells]))
        
        return None

# Alternative: Use direct API-like request if available
async def scrape_with_custom_headers():
    print("\n[ALTERNATIVE METHOD] Trying with custom headers...")
    
    async with AsyncWebCrawler(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.investing.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        },
        verbose=True
    ) as crawler:
        result = await crawler.arun(
            url="https://www.investing.com/crypto/bitcoin/historical-data",
            js_code="""
                // Wait longer for anti-bot measures
                await new Promise(r => setTimeout(r, 8000));
                
                // Try to trigger data load
                document.body.style.zoom = '100%';
                window.dispatchEvent(new Event('resize'));
                await new Promise(r => setTimeout(r, 3000));
            """,
            wait_for="table",
            timeout=60000
        )
        
        if result.html:
            # Save for analysis
            with open("investing_page.html", "w", encoding="utf-8") as f:
                f.write(result.html)
            print("Full page saved to 'investing_page.html' for analysis")
            
            # Parse and look for data
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Look for any element containing price data
            price_elements = soup.find_all(text=re.compile(r'\$?\d{1,3},?\d{3,}'))
            if price_elements:
                print(f"Found {len(price_elements)} price-like values")
                print("Sample prices:", [elem.strip()[:30] for elem in price_elements[:5]])

if __name__ == "__main__":
    # Try main scraper
    df = asyncio.run(scrape_bitcoin_historical())
    
    # If failed, try alternative method
    if df is None:
        asyncio.run(scrape_with_custom_headers())
        print("\n⚠️ Check 'page_debug.html' and 'investing_page.html' to see what content was loaded")
        print("\nPossible issues:")
        print("1. The site may require login for historical data")
        print("2. Anti-bot protection blocking the scraper")
        print("3. Data loads via AJAX after page load")
        print("\nAlternative: Try using yfinance for Bitcoin data:")
        print("  pip install yfinance")
        print("  import yfinance as yf")
        print("  btc = yf.Ticker('BTC-USD')")
        print("  df = btc.history(period='1y')")