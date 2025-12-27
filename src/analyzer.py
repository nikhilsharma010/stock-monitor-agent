"""
Analyzer module for deep stock financials and AI commentary using Groq.
"""
import os
import requests
import logging
import time
from datetime import datetime, timedelta
from groq import Groq
from utils import logger


class StockAnalyzer:
    """Handles financial analysis and LLM commentary for stocks."""
    
    def _find_groq_key(self):
        """Ultra-resilient search for Groq API key in environment."""
        # 1. Explicit standard names
        for key in ['GROQ_API_KEY', 'GROQ_KEY']:
            val = os.getenv(key)
            if val: return val
            
        # 2. Case-insensitive fuzzy search
        for k, v in os.environ.items():
            k_up = k.upper()
            if 'GROQ' in k_up and 'KEY' in k_up:
                logger.info(f"StockAnalyzer: Found potential Groq key in env var '{k}'")
                return v
        return None

    def __init__(self, finnhub_api_key=None, groq_api_key=None):
        self.finnhub_api_key = finnhub_api_key or os.getenv('FINNHUB_API_KEY')
        self.groq_api_key = groq_api_key or self._find_groq_key()
        self.finnhub_base_url = "https://finnhub.io/api/v1"
        
        if self.groq_api_key:
            try:
                self.client = Groq(api_key=self.groq_api_key)
                self.model = "llama-3.3-70b-versatile"
                logger.info("StockAnalyzer: Groq client initialized successfully.")
            except Exception as e:
                self.client = None
                logger.error(f"StockAnalyzer: Error initializing Groq: {e}")
        else:
            self.client = None
            logger.warning("StockAnalyzer: No Groq key found in environment.")

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
                'debt_to_equity': 'N/A',
                'volume_avg_10d': 'N/A'
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
                    'debt_to_equity': m.get('totalDebt/totalEquityTTM', 'N/A'),
                    'volume_avg_10d': m.get('10DayAverageTradingVolume', 'N/A')
                })
            
            return result
        except Exception as e:
            logger.error(f"Error fetching financials for {ticker}: {e}")
            return result # Returns N/A template

    def get_performance_metrics(self, ticker):
        """Calculate multi-timeframe returns and current volume profiling."""
        try:
            # Get ~40 days of daily data to ensure we have 1 month of trading days
            end = int(time.time())
            start = end - (40 * 24 * 60 * 60)
            
            url = f"{self.finnhub_base_url}/stock/candle"
            params = {
                'symbol': ticker,
                'resolution': 'D',
                'from': start,
                'to': end,
                'token': self.finnhub_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            perf = {'5d_pct': 'N/A', '1m_pct': 'N/A', 'curr_vol': 'N/A'}
            
            if data.get('s') == 'ok' and len(data.get('c', [])) > 1:
                closes = data['c']
                vols = data['v']
                curr_price = closes[-1]
                
                # 5D Return (or max available)
                idx_5d = max(0, len(closes) - 6) # -1 is current, -6 is 5 days ago
                price_5d = closes[idx_5d]
                perf['5d_pct'] = ((curr_price / price_5d) - 1) * 100
                
                # 1M Return (approx 21 trading days)
                idx_1m = max(0, len(closes) - 22)
                price_1m = closes[idx_1m]
                perf['1m_pct'] = ((curr_price / price_1m) - 1) * 100
                
                # Current Volume (today's candle)
                perf['curr_vol'] = vols[-1]
            
            return perf
        except Exception as e:
            logger.error(f"Error calculating performance for {ticker}: {e}")
            return {'5d_pct': 'N/A', '1m_pct': 'N/A', 'curr_vol': 'N/A'}

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

    def get_ai_commentary(self, ticker, metrics, quote, news=None, question=None, profile=None, performance=None):
        """Generate Deep AI commentary using Groq."""
        # Dynamic re-check for key if missing
        if not self.client:
            self.groq_api_key = self._find_groq_key()
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
            price = quote.get('current_price', 'N/A')
            chg = quote.get('percent_change', 'N/A')
            price_context = f"Price: ${price} ({chg}%). "
            
            if performance:
                p5d = performance.get('5d_pct', 'N/A')
                p5d_str = f"{p5d:.2f}%" if isinstance(p5d, (int, float)) else str(p5d)
                p1m = performance.get('1m_pct', 'N/A')
                p1m_str = f"{p1m:.2f}%" if isinstance(p1m, (int, float)) else str(p1m)
                
                price_context += (
                    f"Performance: 5D({p5d_str}), 1M({p1m_str}). "
                    f"Volume: {performance['curr_vol']} vs 10D Avg: {metrics['volume_avg_10d']}."
                )
            
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
                    "2. MACRO CONTEXT: Consider industry trends or macro shifts (rates, regulation).\n"
                    "3. CONVICTION: Use volume and multi-timeframe returns to gauge momentum strength.\n"
                    "4. RICH FORMATTING: Use bold for headers and critical terms. Use italics for nuanced interpretations.\n"
                    "5. AESTHETICS: Use consistent emojis (e.g., 🔴 for risks, 📊 for data, 🏭 for industry).\n"
                    "6. STRICT BULLETS: Use only bullet points for all sections. No paragraphs.\n"
                    "7. ZERO HALLUCINATION: If a metric is 'N/A', do not interpret it. Say 'Insufficient Data'.\n"
                    "8. OPERATOR UX: Be concise. Max 200 words total."
                )
                user_prompt = (
                    f"Perform a 'Deep Intelligence' report for {ticker} over the last 60 days.\n\n"
                    f"Data: {metrics_str}\n{price_context}\n{news_context}\n\n"
                    "FORMATTING SPECIFICATION:\n"
                    "• 📝 <b>[SUMMARY]</b>: 1-2 bold bullets on the core narrative.\n"
                    "• ⚙️ <b>[DRIVERS]</b>: 2-3 bullets on fundamental catalysts.\n"
                    "• 🔴 <b>[RISKS]</b>: 2 bold bullets on critical red flags (<i>watch out for...</i>).\n"
                    "• 🏭 <b>[INDUSTRY]</b>: 1-2 bullets on sector-wide impacts.\n"
                    "• 🎯 <b>[OUTLOOK]</b>: What to watch in the next 30 days.\n"
                    "• ⭐ <b>[RATING]</b>: ⭐ ⭐ ⭐ <b>BUY/HOLD/SELL</b> - <i>Logic in italics.</i>"
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

    def get_ai_why_interpretation(self, ticker, metrics, quote, news=None, profile=None, performance=None):
        """Ultra-compressed interpretation of recent moves."""
        if not self.client:
            self.groq_api_key = self._find_groq_key()
            if self.groq_api_key:
                self.client = Groq(api_key=self.groq_api_key)
            else:
                return "AI analysis disabled."

        try:
            # High-density context for 'Why'
            price = quote.get('current_price', 'N/A')
            chg = quote.get('percent_change', 'N/A')
            p5d = performance.get('5d_pct', 'N/A') if performance else 'N/A'
            p5d_str = f"{p5d:+.2f}%" if isinstance(p5d, (int, float)) else str(p5d)
            
            headlines = [n['headline'] for n in news[:8]] if news else []
            news_str = "\n".join([f"- {h}" for h in headlines])
            
            industry = profile.get('finnhubIndustry', 'N/A') if profile else "N/A"

            system_prompt = (
                f"You are a World-Class Market Strategist. Analyze {ticker} ({industry}).\n"
                "TASK: Decode the narrative behind recent moves (1D to 30D).\n"
                "RULES: 1. Max 120 words. 2. Balanced view: Must show BOTH Bull and Bear factors. 3. Be direct."
            )
            user_prompt = (
                f"TICKER: {ticker}\n"
                f"RETURNS: 1D({chg:+.2f}%), 5D({p5d_str}), 1M({p1m_str})\n"
                f"NEWS/CONTEXT:\n{news_str}\n\n"
                "If news is thin, interpret price action vs. industry cycles or structural milestones (e.g. trials).\n\n"
                "FORMAT:\n"
                "🔍 <b>THE NARRATIVE</b>: [1-line summary]\n"
                "📈 <b>BULL CASE</b>: [1 bullet on positive drivers]\n"
                "📉 <b>BEAR CASE</b>: [1 bullet on risks/skepticism]\n"
                "⚖️ <b>STRATEGIC STANCE</b>: [1-line logic: Buy/Hold/Sell verdict]"
            )

            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.2,
                max_tokens=300
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in 'why' interpretation for {ticker}: {e}")
            return f"⚠️ Analysis failed: {e}"

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
