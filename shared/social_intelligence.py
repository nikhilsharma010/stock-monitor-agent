"""
Social Intelligence Module
Tracks Reddit sentiment and trending stocks for market intelligence.
"""

import praw
import logging
from datetime import datetime, timedelta
from collections import Counter
import re

logger = logging.getLogger(__name__)

class SocialIntelligence:
    """Handles social media sentiment tracking and trending stock detection."""
    
    def __init__(self, reddit_client_id=None, reddit_client_secret=None, reddit_user_agent=None):
        """Initialize Reddit API client."""
        self.reddit = None
        
        # Initialize Reddit client if credentials provided
        if reddit_client_id and reddit_client_secret and reddit_user_agent:
            try:
                self.reddit = praw.Reddit(
                    client_id=reddit_client_id,
                    client_secret=reddit_client_secret,
                    user_agent=reddit_user_agent
                )
                logger.info("Reddit API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Reddit client: {e}")
        else:
            logger.warning("Reddit credentials not provided. Social intelligence features will be limited.")
    
    def get_reddit_sentiment(self, ticker, limit=100):
        """
        Analyze Reddit sentiment for a ticker.
        Returns sentiment score (-1 to +1) and discussion themes.
        """
        if not self.reddit:
            return {
                'sentiment_score': 0,
                'mention_count': 0,
                'themes': [],
                'error': 'Reddit API not configured'
            }
        
        try:
            ticker = ticker.upper()
            subreddits = ['wallstreetbets', 'stocks', 'investing']
            
            mentions = []
            bullish_keywords = ['bullish', 'moon', 'calls', 'buy', 'long', 'rocket', '🚀', 'pump', 'gain']
            bearish_keywords = ['bearish', 'puts', 'sell', 'short', 'dump', 'crash', 'loss', 'bag']
            
            for sub_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(sub_name)
                    # Search for ticker mentions in last 24 hours
                    for post in subreddit.search(ticker, time_filter='day', limit=limit//len(subreddits)):
                        text = (post.title + ' ' + post.selftext).lower()
                        
                        # Count sentiment indicators
                        bullish_count = sum(1 for kw in bullish_keywords if kw in text)
                        bearish_count = sum(1 for kw in bearish_keywords if kw in text)
                        
                        mentions.append({
                            'text': post.title,
                            'score': post.score,
                            'bullish': bullish_count,
                            'bearish': bearish_count,
                            'url': post.url
                        })
                except Exception as e:
                    logger.error(f"Error searching r/{sub_name}: {e}")
            
            if not mentions:
                return {
                    'sentiment_score': 0,
                    'mention_count': 0,
                    'themes': [],
                    'top_posts': []
                }
            
            # Calculate weighted sentiment
            total_bullish = sum(m['bullish'] * (1 + m['score']/10) for m in mentions)
            total_bearish = sum(m['bearish'] * (1 + m['score']/10) for m in mentions)
            
            if total_bullish + total_bearish == 0:
                sentiment_score = 0
            else:
                sentiment_score = (total_bullish - total_bearish) / (total_bullish + total_bearish)
            
            # Extract top themes (most upvoted posts)
            top_posts = sorted(mentions, key=lambda x: x['score'], reverse=True)[:3]
            themes = [p['text'] for p in top_posts]
            
            return {
                'sentiment_score': round(sentiment_score, 2),
                'mention_count': len(mentions),
                'themes': themes,
                'top_posts': [{'title': p['text'], 'score': p['score'], 'url': p['url']} for p in top_posts]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {ticker}: {e}")
            return {
                'sentiment_score': 0,
                'mention_count': 0,
                'themes': [],
                'error': str(e)
            }
    
    def get_trending_stocks(self, limit=5):
        """
        Identify trending stocks on Reddit.
        Returns top tickers by mention frequency.
        """
        if not self.reddit:
            return []
        
        try:
            subreddits = ['wallstreetbets', 'stocks']
            ticker_pattern = re.compile(r'\b[A-Z]{1,5}\b')  # Match 1-5 letter uppercase words
            
            all_tickers = []
            
            for sub_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(sub_name)
                    for post in subreddit.hot(limit=50):
                        text = post.title + ' ' + post.selftext
                        tickers = ticker_pattern.findall(text)
                        # Filter out common false positives
                        filtered = [t for t in tickers if t not in ['THE', 'AND', 'FOR', 'ARE', 'YOU', 'NOT', 'BUT', 'CAN', 'ALL', 'NEW', 'GET', 'OUT', 'NOW', 'ONE', 'WAY', 'USE', 'HER', 'HIM', 'HIS', 'SHE', 'HAS', 'HAD', 'WAS', 'ITS']]
                        all_tickers.extend(filtered)
                except Exception as e:
                    logger.error(f"Error fetching from r/{sub_name}: {e}")
            
            # Count mentions
            ticker_counts = Counter(all_tickers)
            trending = ticker_counts.most_common(limit)
            
            return [{'ticker': t[0], 'mentions': t[1]} for t in trending]
            
        except Exception as e:
            logger.error(f"Error getting trending stocks: {e}")
            return []
