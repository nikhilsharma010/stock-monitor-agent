"""
Analyzer module for deep stock financials and AI commentary.
"""
import os
import requests
import time
from datetime import datetime, timedelta
import google.generativeai as genai
from utils import logger


class StockAnalyzer:
    """Handles financial analysis and LLM commentary for stocks."""
    
    def __init__(self, finnhub_api_key=None, gemini_api_key=None):
        self.finnhub_api_key = finnhub_api_key or os.getenv('FINNHUB_API_KEY')
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        self.finnhub_base_url = "https://finnhub.io/api/v1"
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not found. AI commentary will be disabled.")

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

    def get_price_history(self, ticker, days=15):
        """Fetch daily closing prices for the last N days."""
        try:
            end_time = int(time.time())
            start_time = int((datetime.now() - timedelta(days=days)).timestamp())
            
            url = f"{self.finnhub_base_url}/stock/candle"
            params = {
                'symbol': ticker,
                'resolution': 'D',
                'from': start_time,
                'to': end_time,
                'token': self.finnhub_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('s') != 'ok':
                return None
            
            # Format history
            history = []
            for i in range(len(data['c'])):
                dt = datetime.fromtimestamp(data['t'][i]).strftime('%Y-%m-%d')
                history.append({'date': dt, 'close': data['c'][i]})
            
            return history
        except Exception as e:
            logger.error(f"Error fetching history for {ticker}: {e}")
            return None

    def get_ai_commentary(self, ticker, metrics, history, news=None, question=None):
        """Generate AI commentary using Google Gemini."""
        if not self.model:
            return "AI commentary is currently disabled (missing API key)."
        
        try:
            # Prepare context for AI
            if history:
                history_str = "\n".join([f"{h['date']}: ${h['close']}" for h in history[-5:]])
            else:
                history_str = "Price history not available for this period."
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
                prompt = (
                    f"You are a seasoned financial analyst. Answer the following question about {ticker}.\n\n"
                    f"Context Data:\n{metrics_str}\n\nRecent Price Action:\n{history_str}\n{news_str}\n\n"
                    f"Question: {question}\n\n"
                    "Provide a precise, factual answer. If you are asked about competitors or business model, "
                    "use your internal knowledge but keep the answer grounded in the provided data where relevant."
                )
            else:
                prompt = (
                    f"You are a seasoned financial analyst. Provide a fundamental analysis for {ticker}.\n\n"
                    f"Financial Metrics:\n{metrics_str}\n\nRecent Price History (Last 5 days):\n{history_str}\n{news_str}\n"
                    "\nTask:\n"
                    "1. Summarize the company's current financial health.\n"
                    "2. Analyze recent price trends.\n"
                    "3. Give a clear 'Buy/Hold/Sell' recommendation with a 1-sentence justification.\n\n"
                    "Be professional, concise, and focused on data."
                )

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating AI commentary for {ticker}: {e}")
            return "⚠️ Failed to generate AI commentary."
