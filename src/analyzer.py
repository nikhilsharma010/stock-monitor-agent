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

# Optional matplotlib import for chart generation
try:
    import matplotlib
    matplotlib.use('Agg')  # Headless support
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib not available - chart generation will be disabled")

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

    CORE_ALPHA_LIST = ['NVDA', 'TSLA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'NFLX', 'AMD', 'AVGO', 'ASML', 'PLTR', 'SNOW', 'MDB', 'CRWD', 'ZS', 'PANW', 'NET', 'DDOG', 'OKTA']
    SECTOR_ETFS = {
        'XLK': 'Technology', 'XLF': 'Financials', 'XLV': 'Health Care', 
        'XLE': 'Energy', 'XLY': 'Consumer Disc', 'XLI': 'Industrials', 
        'XLC': 'Communication', 'XLB': 'Materials', 'XLU': 'Utilities', 
        'XLP': 'Consumer Staples'
    }

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
                'volume_avg_10d': fmt(info.get('averageVolume10days')),
                'short_pct': fmt(info.get('shortPercentOfFloat'), 100),
                'short_ratio': fmt(info.get('shortRatio'))
            })
            
            # Add Earnings proximity
            earnings_date, days_to = self.get_earnings_info(ticker)
            result['next_earnings'] = earnings_date
            result['days_to_earnings'] = days_to
            
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

    def get_ai_commentary(self, ticker, metrics, quote, news=None, question=None, profile=None, performance=None, alpha_intel=None, risk_profile='Moderate'):
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

            intel_context = ""
            if alpha_intel:
                intel_context = (
                    f"\nBIG MONEY INTEL:\n"
                    f"- Institutional Held: {alpha_intel['insider_held']}\n"
                    f"- Institutional Held: {alpha_intel['inst_held']}\n"
                    f"- Top Holders: {', '.join(alpha_intel['top_holders'])}\n"
                    f"- Short % of Float: {metrics.get('short_pct', 'N/A')}\n"
                )
                if alpha_intel['recent_insider_trades']:
                    trades = [f"{t['type']} ({t['shares']} shares) on {t['date']}" for t in alpha_intel['recent_insider_trades']]
                    intel_context += f"- Recent Insider Trades: {'; '.join(trades)}\n"

            if question:
                system_prompt = (
                    f"You are a Senior Equity Analyst. Industry: {industry}. "
                    "Use a First-Principles approach: Break everything down to logical drivers. "
                    "Always use bullet points. Keep answers objective and grounded."
                )
                user_prompt = f"Stock: {ticker}\nMetrics: {metrics_str}\n{price_context}\n{news_context}\n{intel_context}\n\nQuestion: {question}"
            else:
                system_prompt = (
                    f"You are a Senior Strategic Advisor. Industry: {industry}.\n"
                    "TASK: Perform a 'Unified Intelligence' analysis (Macro context + Recent 'Why').\n"
                    "CORE RULES:\n"
                    "1. BALANCED PERSPECTIVE: You must provide both Bull and Bear cases.\n"
                    f"2. RISK PROFILE: The user is a '{risk_profile}' investor. Tailor the advice accordingly.\n"
                    "3. NARRATIVE DRIVEN: Analyze the 30-day window.\n"
                    "4. RICH FORMATTING: Use bold for headers. Use only bullet points.\n"
                    "5. OPERATOR UX: Be direct. Max 200 words."
                )
                user_prompt = (
                    f"Perform a 'Deep Intelligence' report for {ticker}.\n\n"
                    f"Data: {metrics_str}\n{price_context}\n{news_context}\n{intel_context}\n\n"
                    "FORMATTING SPECIFICATION:\n"
                    "• 🔍 <b>THE NARRATIVE</b>: 1-line summary of the core market story.\n"
                    "• 📈 <b>BULL CASE</b>: 2 bullets on positive catalysts/upside drivers.\n"
                    "• 📉 <b>BEAR CASE</b>: 2 bullets on critical red flags/risks.\n"
                    "• 🐋 <b>BIG MONEY</b>: Interpretation of institutional/insider activity.\n"
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
        if not MATPLOTLIB_AVAILABLE:
            logger.warning(f"Chart generation requested for {ticker} but matplotlib is not available")
            return None, "Chart generation is not available - matplotlib not installed"
        
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
        """Generate a concise, explainable, and actionable technical analysis."""
        if not self.client: return "AI technical analysis is currently unavailable."
        
        try:
            p = context['price']
            d20 = context['dma20']
            d50 = context['dma50']
            d200 = context['dma200']
            rsi = context['rsi']
            
            system_prompt = (
                "You are an Elite Proprietary Trader & Market Technician.\n"
                "TASK: Analyze the provided technical data with high 'Explainability' and 'Actionability'.\n"
                "RULES:\n"
                "1. EXPLAIN THE WHY: Don't just list values. Explain what they imply for price psychology.\n"
                "2. BE ACTIONABLE: Provide a specific tactical level or outlook (e.g., 'Watch for a bounce at $X').\n"
                "3. FORMAT: Use the 3 specific headers below. Max 120 words. Use bolding."
            )
            
            data_str = (
                f"Ticker: {ticker}\n"
                f"Current Price: ${p:.2f}\n"
                f"Indicators: DMA20({d20:.2f}), DMA50({d50:.2f}), DMA200({d200:.2f}), RSI(14)={rsi:.1f}"
            )
            
            user_prompt = (
                f"DATA:\n{data_str}\n\n"
                "REQUIRED FORMAT:\n"
                "• 🛰️ <b>THE SIGNAL</b>: [Identify dominant trend/pattern]\n"
                "• 🧠 <b>EXPLAINABILITY</b>: [Explain WHY this matters for the stock's physics]\n"
                "• ⚡ <b>ACTIONABLE STRATEGY</b>: [Specific tactical entry/support or risk management level]"
            )

            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.2,
                max_tokens=400
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating explainable insights for {ticker}: {e}")
            return "⚠️ Technical interpretation failed."

    def get_earnings_info(self, ticker):
        """Fetch next earnings date and days until it occurs."""
        try:
            symbol = yf.Ticker(ticker)
            calendar = symbol.calendar
            if not calendar or 'Earnings Date' not in calendar:
                return "Unknown", 999
            
            e_dates = calendar['Earnings Date']
            if not e_dates:
                return "Unknown", 999
            
            next_e = e_dates[0]
            if hasattr(next_e, 'date'):
                next_e = next_e.date()
                
            today = datetime.now().date()
            diff = (next_e - today).days
            
            return next_e.strftime('%Y-%m-%d'), diff
        except Exception as e:
            logger.error(f"Error fetching earnings for {ticker}: {e}")
            return "Unknown", 999

    def check_volume_anomaly(self, metrics, performance):
        """Detect if current volume is a significant anomaly (>2x 10D avg)."""
        try:
            curr_vol = performance.get('curr_vol', 0)
            avg_vol = metrics.get('volume_avg_10d')
            
            if not curr_vol or avg_vol == 'N/A':
                return None
            
            # Convert human-readable avg_vol (e.g. 175.0M) back to number
            multiplier = 1
            if isinstance(avg_vol, str):
                if 'B' in avg_vol: multiplier = 1e9
                elif 'M' in avg_vol: multiplier = 1e6
                elif 'K' in avg_vol: multiplier = 1e3
                avg_num = float(avg_vol.replace('B','').replace('M','').replace('K','')) * multiplier
            else:
                avg_num = float(avg_vol)
                
            if curr_vol > (2.0 * avg_num):
                ratio = curr_vol / avg_num
                return f"🚀 <b>VOLUME ANOMALY</b>: Trading at {ratio:.1f}x normal volume. Strong buyer/seller conviction detected."
            
            return None
        except Exception as e:
            logger.error(f"Error checking volume anomaly: {e}")
            return None

    def get_alpha_intelligence(self, ticker):
        """Fetch Big Money footprint (Insider & Institutional)."""
        intel = {
            'insider_held': 'N/A',
            'inst_held': 'N/A',
            'top_holders': [],
            'recent_insider_trades': []
        }
        try:
            symbol = yf.Ticker(ticker)
            
            # 1. Ownership Percentages
            major_holders = symbol.major_holders
            if not major_holders is None and not major_holders.empty:
                if 'Value' in major_holders.columns:
                    if 'insidersPercentHeld' in major_holders.index:
                        val = major_holders.loc['insidersPercentHeld', 'Value']
                        if pd.notnull(val):
                            intel['insider_held'] = f"{val * 100:.1f}%"
                    if 'institutionsPercentHeld' in major_holders.index:
                        val = major_holders.loc['institutionsPercentHeld', 'Value']
                        if pd.notnull(val):
                            intel['inst_held'] = f"{val * 100:.1f}%"

            # 2. Top Institutional Holders
            inst_holders = symbol.institutional_holders
            if not inst_holders is None and not inst_holders.empty:
                # Columns: Holder, Shares, Date Reported, % Out, Value
                for _, row in inst_holders.head(3).iterrows():
                    intel['top_holders'].append(f"{row['Holder'][:15]} ({row['pctChange'] * 100:+.1f}%)")

            # 3. Recent Insider Transactions
            insider = symbol.insider_transactions
            if not insider is None and not insider.empty:
                # Filter for non-zero values and recent dates if possible
                # Columns: Shares, Value, Text, Transaction, Start Date
                for _, row in insider.head(3).iterrows():
                    text = row['Text'] if pd.notnull(row['Text']) else "Trade"
                    intel['recent_insider_trades'].append({
                        'date': str(row['Start Date']),
                        'type': text,
                        'shares': row['Shares']
                    })

            return intel
        except Exception as e:
            logger.error(f"Error fetching alpha intel for {ticker}: {e}")
            return intel

    def get_industry_peers(self, ticker):
        """Use AI to identify 3-4 top direct competitors."""
        if not self.client: return []
        try:
            profile = self.get_company_profile(ticker)
            ind = profile.get('finnhubIndustry', 'N/A')
            
            system_prompt = "You are a Bloomberg Terminal data provider. Respond ONLY with a comma-separated list of 3-4 stock tickers that are the closest direct competitors/peers to the given ticker."
            user_prompt = f"Ticker: {ticker}\nIndustry: {ind}"
            
            completion = self.client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                model=self.model,
                temperature=0.1,
                max_tokens=50
            )
            peers_str = completion.choices[0].message.content.strip()
            # Clean up: remove dots, spaces, uppercase
            peers = [p.strip().upper().replace('.','') for p in peers_str.split(',')]
            return [p for p in peers if p != ticker][:4]
        except Exception as e:
            logger.error(f"Error getting peers for {ticker}: {e}")
            return []

    def get_industry_analysis(self, ticker):
        """Build a comparison table vs peers."""
        try:
            peers = self.get_industry_peers(ticker)
            if not peers: return "⚠️ Industry peer data unavailable."
            
            # Fetch data for main ticker
            m_main = self.get_basic_financials(ticker)
            q_main = self.get_stock_quote(ticker)
            
            lines = [f"🏭 <b>INDUSTRY BENCHMARK: {ticker} vs Peers</b>\n"]
            lines.append("<code>")
            lines.append(f"{'TICKER':<8} {'P/E':<8} {'MARGIN':<8} {'REV_G':<8}")
            
            def add_row(t, m):
                pe = str(m.get('pe_ratio', 'N/A'))[:6]
                margin = str(m.get('net_margin', 'N/A'))[:6]
                growth = str(m.get('revenue_growth', 'N/A'))[:6]
                lines.append(f"{t:<8} {pe:<8} {margin:<8}% {growth:<8}%")

            add_row(f"*{ticker}", m_main)
            
            for p in peers:
                m_peer = self.get_basic_financials(p)
                add_row(p, m_peer)
            
            lines.append("</code>")
            
            # Add AI Context
            context = f"Comparing {ticker} vs rivals {', '.join(peers)}. Focus on relative valuation and efficiency."
            ai_verdict = self.get_ai_commentary(ticker, m_main, q_main, question=context)
            
            return "\n".join(lines) + f"\n\n<b>⚖️ RELATIVE VERDICT</b>\n{ai_verdict}"
        except Exception as e:
            logger.error(f"Error in industry analysis for {ticker}: {e}")
            return f"❌ Industry analysis failed: {str(e)}"

    def get_undervalued_picks(self):
        """Analyze Alpha List for undervalued opportunities."""
        if not self.client: return "AI Discovery is offline."
        try:
            # Picking 5 from Alpha List at random to analyze
            import random
            sample = random.sample(self.CORE_ALPHA_LIST, 5)
            
            candidates = []
            for t in sample:
                m = self.get_basic_financials(t)
                q = self.get_stock_quote(t)
                # Simple logic: Growth > 15% and P/E < 35 (very basic, AI will refine)
                candidates.append({'ticker': t, 'metrics': m, 'quote': q})

            system_prompt = (
                "You are an Institutional Value & Growth Strategist.\n"
                "TASK: Identify the TOP 2 'Best Buys' from the provided list.\n"
                "RULES: 1. Use <b>bold</b> for Tickers and Headers.\n"
                "2. Provide a 'Thesis' for each pick.\n"
                "3. Use a structured, information-dense layout.\n"
                "4. Be authoritative and precise."
            )
            
            data_summary = "<code>\n"
            data_summary += f"{'TKN':<6} {'P/E':>6} {'GROWTH':>8} {'PRICE':>8}\n"
            data_summary += "─" * 30 + "\n"
            for c in candidates:
                pe = f"{c['metrics']['pe_ratio']}" if c['metrics']['pe_ratio'] != 'N/A' else 'N/A'
                gr = f"{c['metrics']['revenue_growth']}%" if c['metrics']['revenue_growth'] != 'N/A' else 'N/A'
                data_summary += f"{c['ticker']:<6} {pe:>6} {gr:>8} {c['quote']['current_price']:>8.2f}\n"
            data_summary += "</code>"
            
            completion = self.client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": data_summary}],
                model=self.model,
                temperature=0.2,
                max_tokens=400
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in undervalued picks: {e}")
            return "❌ Alpha Discovery failed."

    def get_sector_trends(self):
        """Fetch daily performance for all major sectors."""
        trends = []
        try:
            tickers_str = " ".join(self.SECTOR_ETFS.keys())
            data = yf.download(tickers_str, period="2d", group_by='ticker', progress=False)
            
            for ticker, name in self.SECTOR_ETFS.items():
                if ticker in data:
                    t_data = data[ticker]
                    if len(t_data) >= 2:
                        curr = t_data['Close'].iloc[-1]
                        prev = t_data['Close'].iloc[-2]
                        chg = ((curr / prev) - 1) * 100
                        trends.append({'ticker': ticker, 'name': name, 'change': chg})
            
            return sorted(trends, key=lambda x: x['change'], reverse=True)
        except Exception as e:
            logger.error(f"Error fetching sector trends: {e}")
            return []

    def get_pre_market_briefing(self, risk_profile='Moderate', watchlist=None):
        """Generate a high-impact Pre-Market Alpha Briefing."""
        if not self.client: return "AI Advisor is offline."
        try:
            trends = self.get_sector_trends()
            top_sector = trends[0] if trends else {'name': 'Unknown', 'change': 0}
            bottom_sector = trends[-1] if trends else {'name': 'Unknown', 'change': 0}
            
            sector_context = "\n".join([f"- {t['name']}: {t['change']:+.2f}%" for t in trends])
            
            # Watchlist context if any
            wl_str = "None"
            if watchlist:
                wl_str = ", ".join(watchlist[:10])

            system_prompt = (
                "You are an Institutional Level Alpha Advisor.\n"
                f"USER PROFILE: {risk_profile} Investor.\n"
                "TASK: Provide a Pre-Market 'Strategic Briefing'.\n"
                "STRUCTURE:\n"
                "1. 🏛️ STATE OF THE MARKET: Briefly interpret sector rotation.\n"
                "2. 🏹 TACTICAL OPS: High-momentum setups for today.\n"
                "3. 💎 STRATEGIC WEALTH: Structural trends for long-term compounding.\n"
                "RULES: Use bold headers. Use bullet points. Be high-velocity and expert-toned."
            )
            
            user_prompt = (
                f"Sector Trends (Last 24h):\n{sector_context}\n\n"
                f"User Watchlist: {wl_str}\n\n"
                "Provide the Pre-Market Alpha Briefing."
            )
            
            completion = self.client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                model=self.model,
                temperature=0.3,
                max_tokens=500
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in pre-market briefing: {e}")
            return "❌ Pre-Market briefing generation failed."

    def get_persona_summary(self, risk_profile, interests):
        """Generate a personalized AI greeting for onboarding."""
        if not self.client: return "AI Advisor is offline."
        try:
            system_prompt = (
                "You are an Institutional Concierge for an elite stock analysis bot.\n"
                "TASK: Generate a concise, welcoming personality summary for a new user.\n"
                "RULES: 1. Address their Risk Profile and Interests specifically.\n"
                "2. Tell them exactly how best to use this bot (e.g. commands they should use).\n"
                "3. Keep it under 150 words. Be professional but high-energy."
            )
            
            user_prompt = f"User Profile: {risk_profile} Investor interested in {interests}."
            
            completion = self.client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                model=self.model,
                temperature=0.4,
                max_tokens=300
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in persona summary: {e}")
            return "✅ Onboarding Complete! Start by typing /help to see all commands."
