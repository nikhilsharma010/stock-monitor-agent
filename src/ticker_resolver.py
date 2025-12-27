"""
Smart Ticker Resolver
Automatically detects and resolves tickers for both US and Indian markets.
"""

import yfinance as yf
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TickerResolver:
    """Resolves tickers across US and Indian markets with automatic detection."""
    
    def __init__(self):
        """Initialize resolver with cache."""
        self.cache = {}  # {ticker: (resolved_ticker, market, timestamp)}
        self.cache_duration = timedelta(hours=24)
    
    def resolve_ticker(self, ticker):
        """
        Automatically resolve ticker to correct market.
        Returns: (resolved_ticker, market) where market is 'US', 'NSE', 'BSE', or None
        
        Examples:
            'AAPL' -> ('AAPL', 'US')
            'RELIANCE' -> ('RELIANCE.NS', 'NSE')
            'TCS' -> ('TCS.NS', 'NSE')
        """
        ticker = ticker.upper().strip()
        
        # Check cache first
        if ticker in self.cache:
            cached_ticker, market, timestamp = self.cache[ticker]
            if datetime.now() - timestamp < self.cache_duration:
                return cached_ticker, market
        
        # If already has suffix, validate and return
        if ticker.endswith('.NS'):
            if self._validate_ticker(ticker):
                self._cache_result(ticker, ticker, 'NSE')
                return ticker, 'NSE'
        elif ticker.endswith('.BO'):
            if self._validate_ticker(ticker):
                self._cache_result(ticker, ticker, 'BSE')
                return ticker, 'BSE'
        
        # Try US market first (most common for international users)
        if self._validate_ticker(ticker):
            self._cache_result(ticker, ticker, 'US')
            return ticker, 'US'
        
        # Try NSE (National Stock Exchange - most liquid Indian exchange)
        nse_ticker = f"{ticker}.NS"
        if self._validate_ticker(nse_ticker):
            self._cache_result(ticker, nse_ticker, 'NSE')
            return nse_ticker, 'NSE'
        
        # Try BSE (Bombay Stock Exchange - backup)
        bse_ticker = f"{ticker}.BO"
        if self._validate_ticker(bse_ticker):
            self._cache_result(ticker, bse_ticker, 'BSE')
            return bse_ticker, 'BSE'
        
        # Not found in any market
        logger.warning(f"Ticker {ticker} not found in US, NSE, or BSE")
        return None, None
    
    def _validate_ticker(self, ticker):
        """Check if ticker exists by attempting to fetch basic info."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            # Check if we got valid data (has at least symbol or shortName)
            return 'symbol' in info or 'shortName' in info
        except Exception as e:
            logger.debug(f"Ticker {ticker} validation failed: {e}")
            return False
    
    def _cache_result(self, original_ticker, resolved_ticker, market):
        """Cache successful resolution."""
        self.cache[original_ticker] = (resolved_ticker, market, datetime.now())
    
    def get_market_info(self, ticker):
        """
        Get market information for a ticker.
        Returns dict with market, currency, flag, and formatting info.
        """
        resolved_ticker, market = self.resolve_ticker(ticker)
        
        if market == 'US':
            return {
                'market': 'US',
                'currency': 'USD',
                'symbol': '$',
                'flag': '🇺🇸',
                'exchange': 'NASDAQ/NYSE',
                'resolved_ticker': resolved_ticker
            }
        elif market in ['NSE', 'BSE']:
            return {
                'market': market,
                'currency': 'INR',
                'symbol': '₹',
                'flag': '🇮🇳',
                'exchange': market,
                'resolved_ticker': resolved_ticker
            }
        else:
            return {
                'market': 'UNKNOWN',
                'currency': 'USD',
                'symbol': '$',
                'flag': '🌐',
                'exchange': 'Unknown',
                'resolved_ticker': ticker
            }
    
    def format_currency(self, amount, market):
        """Format currency based on market."""
        if market in ['NSE', 'BSE']:
            # Indian formatting with lakhs/crores
            return self._format_inr(amount)
        else:
            # US formatting
            return f"${amount:,.2f}" if isinstance(amount, (int, float)) else amount
    
    def _format_inr(self, amount):
        """Format amount in Indian numbering system (lakhs/crores)."""
        if not isinstance(amount, (int, float)):
            return amount
        
        if amount >= 10000000:  # 1 crore
            return f"₹{amount/10000000:.2f}Cr"
        elif amount >= 100000:  # 1 lakh
            return f"₹{amount/100000:.2f}L"
        else:
            return f"₹{amount:,.2f}"
    
    def clear_cache(self):
        """Clear the ticker resolution cache."""
        self.cache = {}
        logger.info("Ticker resolver cache cleared")

# Global instance
resolver = TickerResolver()
