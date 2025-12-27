"""
Analyzer module for deep stock financials and AI commentary using Groq.
"""
import os
import requests
import logging
import time
from datetime import datetime, timedelta
import io
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg') # Headless support
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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
        """Fetch high-density financial metrics using yfinance."""
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
        try:
            symbol = yf.Ticker(ticker)
            info = symbol.info
            
            # Formatting helper
            def fmt(val, multiplier=1, suffix="", is_pct=False):
                if val is None or val == 'N/A': return 'N/A'
                try:
                    v = float(val) * multiplier
                    if is_pct: return f"{v:.1f}%"
                    if v > 1e9: return f"{v/1e9:.1f}B"
                    if v > 1e6: return f"{v/1e6:.1f}M"
                    return f"{v:.2f}{suffix}"
                except: return 'N/A'

            result.update({
                'pe_ratio': fmt(info.get('trailingPE')),
                'market_cap': fmt(info.get('marketCap')),
                '52_week_high': fmt(info.get('fiftyTwoWeekHigh')),
                '52_week_low': fmt(info.get('fiftyTwoWeekLow')),
                'beta': fmt(info.get('beta')),
                'ps_ratio': fmt(info.get('priceToSalesTrailing12Months')),
                'net_margin': fmt(info.get('profitMargins'), 100),
                'operating_margin': fmt(info.get('operatingMargins'), 100),
                'revenue_growth': fmt(info.get('revenueGrowth'), 100),
                'eps_growth': fmt(info.get('earningsGrowth'), 100),
                'roic': fmt(info.get('returnOnAssets'), 100), # Using ROA as high-confidence proxy
                'debt_to_equity': fmt(info.get('debtToEquity')),
                'volume_avg_10d': fmt(info.get('averageVolume10days'))
            })
            return result
        except Exception as e:
            logger.error(f"Error fetching yfinance financials for {ticker}: {e}")
            return result

    def get_performance_metrics(self, ticker):
        """Calculate multi-timeframe returns using yfinance."""
        perf = {'5d_pct': 'N/A', '1m_pct': 'N/A', 'curr_vol': 'N/A'}
        try:
            symbol = yf.Ticker(ticker)
            df = symbol.history(period="1mo")
            
            if df.empty or len(df) < 2:
                return perf
            
            closes = df['Close'].tolist()
            vols = df['Volume'].tolist()
            curr_price = closes[-1]
            
            # 5D Return
            if len(closes) >= 6:
                price_5d = closes[-6]
                perf['5d_pct'] = ((curr_price / price_5d) - 1) * 100
                
            # 1M Return
            price_1m = closes[0]
            perf['1m_pct'] = ((curr_price / price_1m) - 1) * 100
            
            # Current Volume
            perf['curr_vol'] = vols[-1]
            
            return perf
        except Exception as e:
            logger.error(f"Error calculating yfinance performance for {ticker}: {e}")
            return perf

    def get_company_profile(self, ticker):
        """Fetch company profile using yfinance."""
        try:
            symbol = yf.Ticker(ticker)
            info = symbol.info
            return {
                'name': info.get('longName', ticker),
                'finnhubIndustry': info.get('industry', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'description': info.get('longBusinessSummary', 'N/A'),
                'website': info.get('website', 'N/A')
            }
        except Exception as e:
            logger.error(f"Error fetching yfinance profile for {ticker}: {e}")
            return {}

    def get_stock_quote(self, ticker):
        """Fetch current stock price and change using yfinance."""
        try:
            symbol = yf.Ticker(ticker)
            # Fast way to get current price for most stocks
            info = symbol.info
            curr = info.get('currentPrice')
            prev = info.get('previousClose')
            
            if curr is None:
                # Fallback to history for 1 day
                df = symbol.history(period="2d")
                if df.empty: return None
                curr = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2] if len(df) > 1 else curr
            
            change = curr - prev
            pct_change = (change / prev) * 100 if prev else 0
            
            return {
                'current_price': curr,
                'change': change,
                'percent_change': pct_change,
                'high': info.get('dayHigh', curr),
                'low': info.get('dayLow', curr),
                'open': info.get('open', curr),
                'previous_close': prev
            }
        except Exception as e:
            logger.error(f"Error fetching yfinance quote for {ticker}: {e}")
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
                    "TASK: Perform a 'Unified Intelligence' analysis (Macro context + Recent 'Why').\n"
                    "CORE RULES:\n"
                    "1. BALANCED PERSPECTIVE: You must provide both Bull and Bear cases.\n"
                    "2. NARRATIVE DRIVEN: Analyze the 30-day window. If news is thin, interpret moves vs. industry benchmarks or clinical/product cycles (e.g. Phase 2 trials).\n"
                    "3. RICH FORMATTING: Use bold for headers. Use only bullet points.\n"
                    "4. OPERATOR UX: Be direct. Max 200 words."
                )
                user_prompt = (
                    f"Perform a 'Deep Intelligence' report for {ticker} over the last 60 days.\n\n"
                    f"Data: {metrics_str}\n{price_context}\n{news_context}\n\n"
                    "FORMATTING SPECIFICATION:\n"
                    "• 🔍 <b>THE NARRATIVE</b>: 1-line summary of the core market story.\n"
                    "• 📈 <b>BULL CASE</b>: 2 bullets on positive catalysts/upside drivers.\n"
                    "• 📉 <b>BEAR CASE</b>: 2 bullets on critical red flags/risks (<i>skepticism</i>).\n"
                    "• 🏭 <b>INDUSTRY CONTEXT</b>: 1-2 bullets on sector-wide impacts.\n"
                    "• ⭐ <b>STRATEGIC STANCE</b>: ⭐ ⭐ ⭐ <b>BUY/HOLD/SELL</b> - <i>1-sentence tactical logic.</i>"
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

    def get_stock_chart(self, ticker, days=180):
        """Generate a technical chart with DMA and RSI overlays using yfinance."""
        try:
            # 1. Fetch historical data via yfinance (Reliable Alternate)
            symbol = yf.Ticker(ticker)
            # 6 months is roughly 180 days
            df = symbol.history(period="6mo")
            
            if df.empty:
                logger.error(f"yfinance returned empty data for {ticker}")
                return None, f"No data found for symbol '{ticker}'. It might be invalid or delisted."
            
            # 2. Extract and format (yfinance already returns a clean DataFrame)
            # Ensure index is datetime
            df.index = pd.to_datetime(df.index)
            
            # 3. Calculate Indicators
            df['DMA20'] = df['Close'].rolling(window=20).mean()
            df['DMA50'] = df['Close'].rolling(window=50).mean()
            df['DMA200'] = df['Close'].rolling(window=200).mean()
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # 4. Plotting
            plt.style.use('dark_background')
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
            fig.subplots_adjust(hspace=0.05)
            
            # Subplot 1: Price and DMAs
            ax1.plot(df.index, df['Close'], color='#1f77b4', label='Close Price', linewidth=1.5, alpha=0.8)
            ax1.plot(df.index, df['DMA20'], color='#2ca02c', label='20-Day SMA', linewidth=1, alpha=0.9)
            ax1.plot(df.index, df['DMA50'], color='#ff7f0e', label='50-Day SMA', linewidth=1, alpha=0.9)
            if not df['DMA200'].isnull().all():
                ax1.plot(df.index, df['DMA200'], color='#d62728', label='200-Day SMA', linewidth=1, alpha=0.9)
            
            ax1.set_title(f"Technical Analysis: {ticker}", fontsize=16, fontweight='bold', pad=20)
            ax1.set_ylabel("Price (USD)", fontsize=12)
            ax1.legend(loc='best', frameon=False)
            ax1.grid(True, alpha=0.2)
            
            # Subplot 2: RSI
            ax2.plot(df.index, df['RSI'], color='#9467bd', label='RSI (14)', linewidth=1.2)
            ax2.axhline(70, color='red', linestyle='--', alpha=0.5, linewidth=0.8)
            ax2.axhline(30, color='green', linestyle='--', alpha=0.5, linewidth=0.8)
            ax2.fill_between(df.index, 30, 70, color='#9467bd', alpha=0.1)
            ax2.set_ylabel("RSI", fontsize=12)
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.2)
            
            # Formatting Date Axis
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            fig.autofmt_xdate()
            
            # 5. Extract Context for AI Insights
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            tech_context = {
                'price': latest['Close'],
                'dma20': latest['DMA20'],
                'dma50': latest['DMA50'],
                'dma200': latest['DMA200'],
                'rsi': latest['RSI'],
                'trend_1d': ((latest['Close'] / prev['Close']) - 1) * 100 if len(df) > 1 else 0
            }

            # 6. Export to Buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)
            
            return buf, tech_context
            
        except Exception as e:
            logger.error(f"Error generating yfinance chart for {ticker}: {e}")
            plt.close('all')
            return None, f"Data fetch error: {str(e)}"

    def get_ai_technical_insights(self, ticker, context):
        """Generate a concise AI interpretation of technical signals."""
        if not self.client: return "AI technical analysis is currently unavailable."
        
        try:
            # Prepare readable context
            p = context['price']
            d20 = context['dma20']
            d50 = context['dma50']
            d200 = context['dma200']
            rsi = context['rsi']
            
            system_prompt = (
                "You are a Chartered Market Technician (CMT). "
                "Analyze the provided technical data and give a high-density, professional interpretation. "
                "Rules: 1. Max 80 words. 2. Use bullet points. 3. Focus on trend and momentum signals."
            )
            
            data_str = (
                f"Ticker: {ticker}\n"
                f"Price: ${p:.2f}\n"
                f"DMA20: {f'{d20:.2f}' if pd.notnull(d20) else 'N/A'}\n"
                f"DMA50: {f'{d50:.2f}' if pd.notnull(d50) else 'N/A'}\n"
                f"DMA200: {f'{d200:.2f}' if pd.notnull(d200) else 'N/A'}\n"
                f"RSI(14): {f'{rsi:.1f}' if pd.notnull(rsi) else 'N/A'}"
            )
            
            user_prompt = f"Data:\n{data_str}\n\nProvide the 'Technical Verdict' (Trend, Support/Resistance, and Momentum)."

            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.2,
                max_tokens=250
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating technical insights for {ticker}: {e}")
            return "⚠️ Technical interpretation failed."
