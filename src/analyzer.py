"""
Analyzer module for deep stock financials and AI commentary using Groq.
"""
import os
import requests
import time
from datetime import datetime
from groq import Groq
from utils import logger


class StockAnalyzer:
    """Handles financial analysis and LLM commentary for stocks."""
    
    def __init__(self, finnhub_api_key=None, groq_api_key=None):
        self.finnhub_api_key = finnhub_api_key or os.getenv('FINNHUB_API_KEY')
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        self.finnhub_base_url = "https://finnhub.io/api/v1"
        
        if self.groq_api_key:
            self.client = Groq(api_key=self.groq_api_key)
            self.model = "llama-3.1-70b-versatile" # High-quality available model
        else:
            self.client = None
            logger.warning("GROQ_API_KEY not found. AI commentary will be disabled.")

    def get_basic_financials(self, ticker):
        """Fetch basic financial metrics (P/E, Market Cap, etc.)."""
        try:
            url = f"{self.finnhub_base_url}/stock/metric"
            params = {
                'symbol': ticker,
                'metric': 'all',
                'token': self.finnhub_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('metric'):
                return None
            
            metrics = data['metric']
            return {
                'pe_ratio': metrics.get('peExclExtraTTM'),
                'market_cap': metrics.get('marketCapitalization'),
                '52_week_high': metrics.get('52WeekHigh'),
                '52_week_low': metrics.get('52WeekLow'),
                'beta': metrics.get('beta'),
                'ps_ratio': metrics.get('psTTM')
            }
        except Exception as e:
            logger.error(f"Error fetching financials for {ticker}: {e}")
            return None

    def get_stock_quote(self, ticker):
        """Fetch current stock price and daily change."""
        try:
            url = f"{self.finnhub_base_url}/quote"
            params = {
                'symbol': ticker,
                'token': self.finnhub_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('c'):  # Current price missing
                return None
            
            return {
                'current_price': data['c'],
                'change': data['d'],
                'percent_change': data['dp'],
                'high': data['h'],
                'low': data['l'],
                'open': data['o'],
                'previous_close': data['pc']
            }
        except Exception as e:
            logger.error(f"Error fetching quote for {ticker}: {e}")
            return None

    def get_ai_commentary(self, ticker, metrics, quote, news=None, question=None):
        """Generate AI commentary using Groq."""
        if not self.client:
            return "AI commentary is currently disabled (missing GROQ_API_KEY)."
        
        try:
            # Prepare context for AI
            if quote:
                price_context = (
                    f"Current Price: ${quote['current_price']}\n"
                    f"Today's Change: ${quote['change']} ({quote['percent_change']}%)\n"
                    f"Day's Range: ${quote['low']} - ${quote['high']}\n"
                    f"Previous Close: ${quote['previous_close']}"
                )
            else:
                price_context = "Current price action data not available."

            metrics_str = (
                f"P/E Ratio: {metrics['pe_ratio']}\n"
                f"Market Cap: {metrics['market_cap']}M\n"
                f"52-Week High: {metrics['52_week_high']}\n"
                f"52-Week Low: {metrics['52_week_low']}\n"
                f"Beta: {metrics['beta']}"
            )
            
            news_str = ""
            if news:
                news_str = "\nRecent News:\n" + "\n".join([f"- {n['headline']}" for n in news[:3]])

            # Prompt Construction
            if question:
                system_prompt = "You are a seasoned financial analyst. Provide precise, factual answers about stocks."
                user_prompt = (
                    f"Answer the following question about {ticker}.\n\n"
                    f"Context Data:\n{metrics_str}\n\nRecent Price Action:\n{price_context}\n{news_str}\n\n"
                    f"Question: {question}\n"
                )
            else:
                system_prompt = "You are a seasoned financial analyst. Be professional, concise, and focused on data."
                user_prompt = (
                    f"Provide a fundamental analysis for {ticker}.\n\n"
                    f"Financial Metrics:\n{metrics_str}\n\nRecent Price Action:\n{price_context}\n{news_str}\n"
                    "\nTask:\n"
                    "1. Summarize the company's current financial health.\n"
                    "2. Analyze recent price trends based on the day's movement and 52W range.\n"
                    "3. Give a clear 'Buy/Hold/Sell' recommendation with a 1-sentence justification.\n"
                )

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.2,
                max_tokens=600
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating AI commentary for {ticker}: {str(e)}")
            return f"⚠️ Failed to generate AI commentary with Groq: {str(e)}"
