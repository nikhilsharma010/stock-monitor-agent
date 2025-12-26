"""
Stock data monitor using Finnhub API.
"""
import os
import requests
from utils import logger


class StockMonitor:
    """Fetches stock data from Finnhub API."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('FINNHUB_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Finnhub API key not found. "
                "Set FINNHUB_API_KEY environment variable."
            )
        
        self.base_url = "https://finnhub.io/api/v1"
        logger.info("Stock monitor initialized with Finnhub API")
    
    def get_quote(self, ticker):
        """
        Get current stock quote.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            dict: Stock quote data or None if failed
        """
        try:
            url = f"{self.base_url}/quote"
            params = {
                'symbol': ticker,
                'token': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Finnhub returns: c (current), d (change), dp (percent change), 
            # h (high), l (low), o (open), pc (previous close)
            if data.get('c') is not None:
                logger.info(f"Fetched quote for {ticker}: ${data['c']:.2f}")
                return {
                    'ticker': ticker,
                    'current_price': data['c'],
                    'change': data.get('d', 0),
                    'change_percent': data.get('dp', 0),
                    'high': data.get('h', 0),
                    'low': data.get('l', 0),
                    'open': data.get('o', 0),
                    'previous_close': data.get('pc', 0)
                }
            else:
                logger.warning(f"No data returned for {ticker}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch quote for {ticker}: {e}")
            return None
    
    def get_company_profile(self, ticker):
        """
        Get company profile information.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            dict: Company profile or None if failed
        """
        try:
            url = f"{self.base_url}/stock/profile2"
            params = {
                'symbol': ticker,
                'token': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data:
                logger.info(f"Fetched profile for {ticker}: {data.get('name', 'Unknown')}")
                return {
                    'ticker': ticker,
                    'name': data.get('name', ticker),
                    'industry': data.get('finnhubIndustry', 'N/A'),
                    'market_cap': data.get('marketCapitalization', 0),
                    'logo': data.get('logo', ''),
                    'weburl': data.get('weburl', '')
                }
            else:
                logger.warning(f"No profile data for {ticker}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch profile for {ticker}: {e}")
            return None
    
    def get_stock_data(self, ticker):
        """
        Get combined stock data (quote + profile).
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            dict: Combined stock data or None if failed
        """
        quote = self.get_quote(ticker)
        profile = self.get_company_profile(ticker)
        
        if quote and profile:
            return {**quote, **profile}
        elif quote:
            # If profile fails, still return quote with ticker as name
            quote['name'] = ticker
            return quote
        else:
            return None


# Test function for standalone execution
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing Stock Monitor...")
    
    try:
        monitor = StockMonitor()
        
        # Test with CCCC and BYND
        for ticker in ['CCCC', 'BYND']:
            print(f"\n{'='*50}")
            print(f"Fetching data for {ticker}...")
            print('='*50)
            
            data = monitor.get_stock_data(ticker)
            
            if data:
                print(f"✅ {data.get('name', ticker)}")
                print(f"   Price: ${data['current_price']:.2f}")
                print(f"   Change: {data['change_percent']:+.2f}%")
                print(f"   High: ${data.get('high', 0):.2f}")
                print(f"   Low: ${data.get('low', 0):.2f}")
                if data.get('industry'):
                    print(f"   Industry: {data['industry']}")
            else:
                print(f"❌ Failed to fetch data for {ticker}")
                
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease set up your .env file with:")
        print("  FINNHUB_API_KEY=your_api_key")
