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
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY') or os.getenv('GROQ_KEY')
        self.finnhub_base_url = "https://finnhub.io/api/v1"
        
        # Super-debug: Log all env keys
        all_keys = list(os.environ.keys())
        logger.debug(f"StockAnalyzer Init: All Env Keys: {all_keys}")
        
        if self.groq_api_key:
            self.client = Groq(api_key=self.groq_api_key)
            self.model = "llama-3.3-70b-versatile" # Updated to newest supported model
            logger.info("StockAnalyzer: Groq client initialized successfully.")
        else:
            self.client = None
            logger.warning("StockAnalyzer: GROQ_API_KEY not found during initialization.")

    def get_basic_financials(self, ticker):
        """Fetch high-density financial metrics (Margins, Growth, Efficiency)."""
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
            
            # Expanded N/A template
            result = {
                'pe_ratio': 'N/A',
                'market_cap': 'N/A',
                '52_week_high': 'N/A',
                '52_week_low': 'N/A',
                'beta': 'N/A',
                'ps_ratio': 'N/A',
                'net_margin': 'N/A',
                'operating_margin': 'N/A',
                'revenue_growth': 'N/A',
                'eps_growth': 'N/A',
                'roic': 'N/A',
                'debt_to_equity': 'N/A'
            }
            
            if data.get('metric'):
                m = data['metric']
                result.update({
                    'pe_ratio': m.get('peExclExtraTTM', 'N/A'),
                    'market_cap': m.get('marketCapitalization', 'N/A'),
                    '52_week_high': m.get('52WeekHigh', 'N/A'),
                    '52_week_low': m.get('52WeekLow', 'N/A'),
                    'beta': m.get('beta', 'N/A'),
                    'ps_ratio': m.get('psTTM', 'N/A'),
                    'net_margin': m.get('netProfitMarginTTM', 'N/A'),
                    'operating_margin': m.get('operatingMarginTTM', 'N/A'),
                    'revenue_growth': m.get('revenueGrowthYoy', 'N/A'),
                    'eps_growth': m.get('epsGrowthYoy', 'N/A'),
                    'roic': m.get('roicTTM', 'N/A'),
                    'debt_to_equity': m.get('totalDebt/totalEquityTTM', 'N/A')
                })
            
            return result
        except Exception as e:
            logger.error(f"Error fetching financials for {ticker}: {e}")
            return result # Returns N/A template

    def get_company_profile(self, ticker):
        """Fetch company profile (Industry, Sector, Description)."""
        try:
            url = f"{self.finnhub_base_url}/stock/profile2"
            params = {
                'symbol': ticker,
                'token': self.finnhub_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching profile for {ticker}: {e}")
            return {}

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

    def get_ai_commentary(self, ticker, metrics, quote, news=None, question=None, profile=None):
        """Generate Deep AI commentary using Groq."""
        # Dynamic re-check for key if missing
        if not self.client:
            self.groq_api_key = os.getenv('GROQ_API_KEY') or os.getenv('GROQ_KEY')
            if self.groq_api_key:
                try:
                    self.client = Groq(api_key=self.groq_api_key)
                    self.model = "llama-3.3-70b-versatile"
                    logger.info("StockAnalyzer: Late-initialized Groq client.")
                except Exception as e:
                    logger.error(f"Failed to late-init Groq: {e}")
            else:
                return "AI commentary is currently disabled (missing GROQ_API_KEY)."
        
        try:
            # Context Preparation
            price_context = f"Price: ${quote['current_price']} ({quote['percent_change']}%)" if quote else "Price N/A"
            industry = profile.get('finnhubIndustry', 'Unknown Industry') if profile else "Unknown Industry"
            
            metrics_str = (
                f"P/E: {metrics['pe_ratio']}, Market Cap: {metrics['market_cap']}M, "
                f"52W Range: {metrics['52_week_low']} - {metrics['52_week_high']}"
            )
            
            news_context = ""
            if news:
                # Take up to 8 representative headlines for the last 60 days
                headlines = [n['headline'] for n in news[:10]]
                news_context = "\nRecent 60-Day News Headlines:\n" + "\n".join([f"- {h}" for h in headlines])

            if question:
                system_prompt = (
                    f"You are a Senior Equity Analyst. Industry: {industry}. "
                    "Use a First-Principles approach: Break everything down to logical drivers. "
                    "Always use bullet points. Keep answers objective and grounded."
                )
                user_prompt = f"Stock: {ticker}\nMetrics: {metrics_str}\n{price_context}\n{news_context}\n\nQuestion: {question}"
            else:
                system_prompt = (
                    f"You are a Senior Strategic Advisor. Industry: {industry}.\n"
                    "CORE RULES:\n"
                    "1. FIRST PRINCIPLES: Analyze the narrative based on structural drivers, not just price.\n"
                    "2. MACRO CONTEXT: Consider how industry-wide trends or macro shifts (rates, regulation) impact this specific ticker.\n"
                    "3. STRICT BULLETS: Use only bullet points for all sections. No paragraphs.\n"
                    "4. ZERO HALLUCINATION: If a metric is 'N/A', do not interpret it. Say 'Insufficient Data'.\n"
                    "5. OPERATOR UX: Be concise. Max 180 words total."
                )
                user_prompt = (
                    f"Perform a 'Deep Intelligence' report for {ticker} over the last 60 days.\n\n"
                    f"Data: {metrics_str}\n{price_context}\n{news_context}\n\n"
                    "FORMAT:\n"
                    "• [SUMMARY] Primary 60-day narrative.\n"
                    "• [DRIVERS] List 2-3 key fundamental/market drivers.\n"
                    "• [RISKS] Critical red flags or things to watch out for.\n"
                    "• [INDUSTRY] Major sector/macro developments impacting {ticker}.\n"
                    "• [OUTLOOK] What to watch in the next 30 days.\n"
                    "• [RATING] ⭐ ⭐ ⭐ [BUY/HOLD/SELL] - 1-sentence logic."
                )

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.3, # Slightly higher for more "insightful" connections
                max_tokens=1000
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating AI deep commentary for {ticker}: {str(e)}")
            return f"⚠️ AI deep analysis failed: {str(e)}"

    def get_ai_comparison(self, t1, m1, q1, t2, m2, q2):
        """Generate a side-by-side AI comparison of two stocks."""
        if not self.client:
            return "AI comparison is currently disabled (missing GROQ_API_KEY)."
        
        try:
            comparison_context = f"""
Stock 1: {t1}
- P/E: {m1['pe_ratio']}
- Market Cap: {m1['market_cap']}M
- Price: ${q1['current_price']} ({q1['percent_change']}%)
- 52W Range: ${m1['52_week_low']} - ${m1['52_week_high']}

Stock 2: {t2}
- P/E: {m2['pe_ratio']}
- Market Cap: {m2['market_cap']}M
- Price: ${q2['current_price']} ({q2['percent_change']}%)
- 52W Range: ${m2['52_week_low']} - ${m2['52_week_high']}
"""
            system_prompt = (
                "You are a world-class equity researcher. Compare two stocks using First-Principles logic. "
                "Use bullet points only. Zero speculation on missing data."
            )
            user_prompt = f"""
Compare the following two stocks based on the data provided:
{comparison_context}

FORMAT:
• [VALUATION] Bulleted comparison.
• [POSITION] Structural industry standing.
• [VERDICT] 🏆 WINNER: [TICKER] - 1-sentence logic.
"""
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.2,
                max_tokens=800
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in AI comparison: {e}")
            return f"⚠️ AI Comparison failed: {str(e)}"
