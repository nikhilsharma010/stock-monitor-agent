"""
News monitor using Finnhub News API.
"""
import os
import requests
from datetime import datetime, timedelta
from utils import logger, truncate_text


class NewsMonitor:
    """Fetches company news from Finnhub API."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('FINNHUB_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Finnhub API key not found. "
                "Set FINNHUB_API_KEY environment variable."
            )
        
        self.base_url = "https://finnhub.io/api/v1"
        logger.info("News monitor initialized with Finnhub API")
    
    def get_company_news(self, ticker, days_back=1):
        """
        Get company news for a specific ticker.
        
        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to look back for news
        
        Returns:
            list: List of news articles
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            url = f"{self.base_url}/company-news"
            params = {
                'symbol': ticker,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'token': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            articles = response.json()
            
            if articles:
                logger.info(f"Fetched {len(articles)} news articles for {ticker}")
                
                # Format articles
                formatted_articles = []
                for article in articles:
                    formatted_articles.append({
                        'ticker': ticker,
                        'headline': article.get('headline', 'No headline'),
                        'summary': article.get('summary', ''),
                        'source': article.get('source', 'Unknown'),
                        'url': article.get('url', ''),
                        'datetime': article.get('datetime', 0),
                        'image': article.get('image', ''),
                        'category': article.get('category', 'general')
                    })
                
                # Sort by datetime (most recent first)
                formatted_articles.sort(key=lambda x: x['datetime'], reverse=True)
                
                return formatted_articles
            else:
                logger.info(f"No news found for {ticker}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch news for {ticker}: {e}")
            return []
    
    def get_market_news(self, category='general'):
        """
        Get general market news.
        
        Args:
            category: News category (general, forex, crypto, merger)
        
        Returns:
            list: List of news articles
        """
        try:
            url = f"{self.base_url}/news"
            params = {
                'category': category,
                'token': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            articles = response.json()
            
            if articles:
                logger.info(f"Fetched {len(articles)} market news articles")
                return articles[:10]  # Limit to 10 most recent
            else:
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch market news: {e}")
            return []
    
    def filter_recent_news(self, articles, hours=24):
        """
        Filter articles to only include those from the last N hours.
        
        Args:
            articles: List of article dictionaries
            hours: Number of hours to look back
        
        Returns:
            list: Filtered articles
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        recent = [
            article for article in articles 
            if article.get('datetime', 0) >= cutoff_timestamp
        ]
        
        logger.info(f"Filtered to {len(recent)} articles from last {hours} hours")
        return recent


# Test function for standalone execution
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing News Monitor...")
    
    try:
        monitor = NewsMonitor()
        
        # Test with CCCC and BYND
        for ticker in ['CCCC', 'BYND']:
            print(f"\n{'='*60}")
            print(f"Fetching news for {ticker}...")
            print('='*60)
            
            articles = monitor.get_company_news(ticker, days_back=7)
            
            if articles:
                print(f"✅ Found {len(articles)} articles\n")
                
                # Show first 3 articles
                for i, article in enumerate(articles[:3], 1):
                    timestamp = datetime.fromtimestamp(article['datetime'])
                    print(f"{i}. {article['headline']}")
                    print(f"   Source: {article['source']}")
                    print(f"   Date: {timestamp.strftime('%Y-%m-%d %H:%M')}")
                    if article['summary']:
                        print(f"   Summary: {truncate_text(article['summary'], 100)}")
                    print(f"   URL: {article['url']}")
                    print()
            else:
                print(f"❌ No news found for {ticker}")
                
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease set up your .env file with:")
        print("  FINNHUB_API_KEY=your_api_key")
