"""
Telegram bot command handler for interactive stock management.
"""
import os
import json
import time
import requests
from datetime import datetime
from utils import logger
from analyzer import StockAnalyzer


class TelegramBotHandler:
    """Handles incoming Telegram commands for managing stocks and settings."""
    FINANCIAL_DISCLAIMER = "\n\n⚠️ <b>Disclaimer</b>: <i>This report is AI-generated for informational purposes only. Not financial advice. Always consult a certified professional before trading.</i>"

    BOT_HEADER = """
<b>ALPHA INTELLIGENCE v4.0</b>
────────────────────────
"""

    def __init__(self, bot_token=None, chat_id=None, config_path='config/stocks.json', cache=None, notifier=None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.config_path = config_path
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_update_id = 0
        from utils import CacheDB
        self.cache = cache or CacheDB()
        self.analyzer = StockAnalyzer()
        
        # Use existing notifier if provided, else create one
        if notifier:
            self.telegram_notifier = notifier
        else:
            from telegram_notifier import TelegramNotifier
            self.telegram_notifier = TelegramNotifier(bot_token=self.bot_token, chat_id=self.chat_id)
        
        # Identify bot and clear webhooks
        try:
            # Identify
            me_resp = requests.get(f"{self.api_url}/getMe", timeout=10)
            if me_resp.ok:
                bot_info = me_resp.json().get('result', {})
                self.bot_username = bot_info.get('username')
                self.bot_id = bot_info.get('id')
                logger.info(f"Bot authenticated as @{self.bot_username} (ID: {self.bot_id})")
            
            # Reset
            requests.get(f"{self.api_url}/deleteWebhook", timeout=10)
            
            # Sync update_id to current state - skip history
            resp = requests.get(f"{self.api_url}/getUpdates", params={'offset': -1, 'limit': 1}, timeout=10)
            if resp.ok:
                data = resp.json()
                result = data.get('result', [])
                if result:
                    # Set last_update_id to the most recent one to skip everything before now
                    self.last_update_id = result[0]['update_id']
                    logger.info(f"Synchronized update_id: {self.last_update_id} (History Skipped)")
                else:
                    logger.info("No existing updates found in history.")
            
            logger.info("Bot command handler: Startup sync complete.")
        except Exception as e:
            logger.error(f"Critical error during bot startup sync: {e}")
        
    def load_config(self):
        """Load current configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return None
    
    def save_config(self, config):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get_updates(self):
        """Get new messages from Telegram."""
        try:
            url = f"{self.api_url}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 30  # Long polling timeout
            }
            response = requests.get(url, params=params, timeout=35)
            response.raise_for_status()
            
            data = response.json()
            if data.get('ok') and data.get('result'):
                updates = data['result']
                if updates:
                    logger.info(f"Received {len(updates)} new updates from Telegram.")
                return updates
            return []
        except Exception as e:
            logger.debug(f"Error getting updates: {e}")
            return []
    
    def send_message(self, message, chat_id=None):
        """Send a message using the shared notifier."""
        if not message:
            return False
            
        try:
            # Use the more robust TelegramNotifier instance
            return self.telegram_notifier.send_message(message, chat_id=chat_id)
        except Exception as e:
            logger.error(f"Failed to send message via notifier proxy: {e}")
            return False
    
    def handle_add_stock(self, ticker, user_id):
        """Add a stock to user's personal watchlist."""
        ticker = ticker.upper().strip()
        if self.cache.add_to_watchlist(user_id, ticker):
            return f"✅ Added {ticker} to your watchlist!\nYou will now receive price and news alerts for this stock."
        else:
            return f"❌ Failed to add {ticker}. Try again later."
    
    def handle_remove_stock(self, ticker, user_id):
        """Remove a stock from user's personal watchlist."""
        ticker = ticker.upper().strip()
        if self.cache.remove_from_watchlist(user_id, ticker):
            return f"✅ Removed {ticker} from your watchlist."
        else:
            return f"❌ Failed to remove {ticker} or ticker not found."
    
    def handle_list_stocks(self, user_id):
        """List user's personal monitored stocks with interactive buttons."""
        tickers = self.cache.get_user_watchlist(user_id)
        
        if not tickers:
            return "📭 <b>Your Watchlist is Empty</b>\n\nUse /add TICKER to start monitoring stocks.", None
        
        message = "📊 <b>Your Personal Watchlist</b>\n\n"
        keyboard = {"inline_keyboard": []}
        
        for ticker in sorted(tickers):
            message += f"  • {ticker}\n"
            keyboard["inline_keyboard"].append([
                {"text": f"📈 {ticker} Chart", "callback_data": f"chart:{ticker}"},
                {"text": f"🧠 {ticker} Snap", "callback_data": f"snap:{ticker}"}
            ])
            
        message += "\n<i>Tap a button for instant deep intelligence.</i>"
        return message, json.dumps(keyboard)
    
    def handle_set_interval(self, minutes):
        """Set check interval in minutes."""
        config = self.load_config()
        if not config:
            return "❌ Failed to load configuration"
        
        try:
            minutes = int(minutes)
            if minutes < 1:
                return "❌ Interval must be at least 1 minute"
            if minutes > 1440:
                return "❌ Interval cannot exceed 24 hours (1440 minutes)"
            
            config['monitoring']['check_interval_minutes'] = minutes
            
            if self.save_config(config):
                return f"✅ Check interval set to {minutes} minutes\n\nChanges will take effect on next check cycle."
            else:
                return "❌ Failed to save configuration"
        except ValueError:
            return "❌ Invalid number. Please provide minutes as a number (e.g., /interval 5)"
    
    def handle_help(self):
        """Show help message with professional categorization."""
        return self.BOT_HEADER + """
<b>📊 MARKET INTELLIGENCE</b>
• /snapshot TICKER - Multi-timeframe deep report
• /chart TICKER - DMA + RSI technical visualization
• /why TICKER - Instant news narrative & drivers
• /compare T1 T2 - Strategic side-by-side analysis
• /ask <code>SYM Q</code> - Real-time financial Q&A

<b>🎯 STRATEGIC ADVISOR</b>
• /premarket - Personalized morning Alpha Brief
• /undervalued - AI-picked growth & value gems
• /sectors - Live Sector Rotation heat-map
• /risk - Map your investor DNA persona

<b>📈 WATCHLIST OPS</b>
• /add <code>SYM</code> - Register for automated monitoring
• /remove <code>SYM</code> - Unregister ticker
• /list - View your active terminals

<b>⚙️ SYSTEM</b>
• /status - Network & usage health
• /interval - Adjust scan frequency
• /start - Restart Concierge onboarding
• /donate - Support the Alpha Platform ☕️
"""
    
    def handle_donate(self):
        """Show donation information."""
        return """
☕️ <b>Support Stock Monitor Agent</b>

This platform is free and open-source, but running the AI models and infrastructure has costs. If you find this tool valuable, consider supporting its development!

<b>Ways to Support:</b>
• <a href="https://www.buymeacoffee.com/agenticai">Buy Me a Coffee</a>
• <a href="https://github.com/sponsors/nikhilsharma010">GitHub Sponsors</a>

<i>Your support helps keep the Deep Intelligence features fast and accessible for everyone!</i>
"""
    
    def handle_about(self):
        """Show comprehensive bot information with marketing copy and disclaimers."""
        return self.BOT_HEADER + """
🚀 <b>WELCOME TO ALPHA INTELLIGENCE</b>

Your AI-powered financial intelligence terminal that transforms market complexity into actionable insights.

────────────────────────
🎯 <b>WHAT WE DO</b>

Alpha Intelligence combines institutional-grade data analysis with cutting-edge AI to give you:

• <b>Deep Market Intelligence</b> - 60-day narrative tracking, technical analysis, and AI-powered insights
• <b>Social Sentiment</b> - Real-time Reddit tracking for trending stocks and market sentiment
• <b>Big Money Tracking</b> - Institutional ownership and insider trading intelligence
• <b>Personalized Advisor</b> - AI learns YOUR investment thesis and provides tailored recommendations
• <b>Pre-Market Alpha</b> - Daily sector rotation analysis and strategic briefings
• <b>Voice Interface</b> - Send voice notes, get instant AI analysis

────────────────────────
💡 <b>HOW TO GET THE MOST VALUE</b>

1. <b>Start with Onboarding</b>: Use <code>/start</code> to map your risk profile and interests
2. <b>Build Your Context</b>: Use <code>/note</code> to document your investment thesis and learnings
3. <b>Set Up Watchlists</b>: Add tickers with <code>/add</code> for automated monitoring
4. <b>Daily Routine</b>: Check <code>/premarket</code> for morning briefings and <code>/trending</code> for social buzz
5. <b>Deep Dives</b>: Use <code>/snapshot TICKER</code> for comprehensive analysis
6. <b>Get Recommendations</b>: Use <code>/recommend</code> for AI picks based on YOUR context

────────────────────────
⚠️ <b>IMPORTANT DISCLAIMERS</b>

🚨 <b>NOT FINANCIAL ADVICE</b>
All analysis, recommendations, and insights provided by this bot are for <b>informational and educational purposes only</b>. This is NOT financial, investment, or trading advice.

📊 <b>AI-GENERATED CONTENT</b>
All commentary is generated by AI models and may contain errors, biases, or outdated information. Always verify critical information independently.

👥 <b>DO YOUR OWN RESEARCH</b>
Never make investment decisions based solely on this bot. Consult with licensed financial professionals before making any investment decisions.

💸 <b>RISK WARNING</b>
Investing in stocks carries significant risk, including the potential loss of principal. Past performance does not guarantee future results.

🔒 <b>PRIVACY</b>
Your notes and context are stored securely and used only to personalize your experience. We never share your data with third parties.

────────────────────────
🔗 <b>GET STARTED</b>

Type <code>/help</code> to see all commands or <code>/start</code> to begin your personalized onboarding.

Built with ❤️ for serious market participants.
<i>Powered by Groq AI • yfinance • Reddit API</i>
"""
    
    def handle_status(self):
        """Show current status with clean sections."""
        config = self.load_config()
        if not config:
            return "❌ Failed to load configuration"
        
        active_stocks = self.cache.get_all_monitored_tickers()
        interval = config.get('monitoring', {}).get('check_interval_minutes', 15)
        threshold = config.get('monitoring', {}).get('price_change_threshold_percent', 0.5)
        metrics = self.cache.get_usage_metrics()
        
        return f"""
🖥 <b>SYSTEM TERMINAL STATUS</b>
────────────────────────
<b>📡 Monitoring Engine</b>
• Active Tickers: <code>{len(active_stocks)}</code>
• Frequency: <code>{interval} min</code>
• Threshold: <code>{threshold}%</code>

<b>👥 Platform Growth</b>
• Total Users: <code>{metrics.get('total_users', 0)}</code>
• Interactions: <code>{metrics.get('total_commands', 0)}</code>
• Daily Active: <code>{metrics.get('active_users_24h', 0)}</code>

☕️ Support the Platform: /donate
"""

    def handle_start(self, user_id, chat_id):
        """Handle /start with onboarding."""
        self.cache.set_user_step(user_id, 1)
        msg = (
            "🚀 <b>Welcome to the Alpha Intelligence Concierge!</b>\n\n"
            "Before we dive into the markets, let's map your <b>Financial DNA</b>.\n\n"
            "First, what is your <b>Risk Appetite?</b>"
        )
        # Use handle_risk to get the keyboard
        _, kb = self.handle_risk(chat_id)
        return msg, kb

    def handle_analyse(self, ticker, chat_id, user_id=None, skip_market_check=False):
        """Perform 60-day 'Deep Intelligence' analysis on a stock."""
        # Use chat_id as fallback for user_id
        u_id = user_id or chat_id
        ticker = ticker.upper().strip()
        
        # Check if ticker already has market suffix (skip if called from market selection callback)
        if not skip_market_check and not (ticker.endswith('.NS') or ticker.endswith('.BO')):
            # Show market selection buttons for ambiguous tickers
            msg = f"🌍 <b>Select Market for {ticker}</b>\n\nIs this an Indian or US stock?"
            keyboard = {"inline_keyboard": [
                [
                    {"text": "🇮🇳 India (NSE)", "callback_data": f"market:NSE:{ticker}"},
                    {"text": "🇺🇸 United States", "callback_data": f"market:US:{ticker}"}
                ]
            ]}
            return msg, json.dumps(keyboard)
        
        self.telegram_notifier.send_message(f"🔍 <b>Generating Deep Intelligence Report for {ticker}...</b>\nFetching 60 days of context and sector trends. Please wait.", chat_id=chat_id)
        
        try:
            # 1. Fetch Metrics
            metrics = self.analyzer.get_basic_financials(ticker)
            
            # 2. Fetch Quote
            quote = self.analyzer.get_stock_quote(ticker)
            
            # 3. Fetch Company Profile (New for Deep Intelligence)
            profile = self.analyzer.get_company_profile(ticker)
            
            # 4. Fetch 60 Days of News (Phase 3 Requirement)
            from news_monitor import NewsMonitor
            news_mon = NewsMonitor()
            news = news_mon.get_company_news(ticker, days_back=60)
            
            # 5. Fetch Performance Metrics (New for 5.1)
            performance = self.analyzer.get_performance_metrics(ticker)
            
            # 6. Fetch user risk profile (Phase 10)
            risk = self.cache.get_user_risk(u_id)
            
            # 7. Fetch Alpha Intel
            alpha_intel = self.analyzer.get_alpha_intelligence(ticker)
            
            # 8. Get AI Deep Commentary
            commentary = self.analyzer.get_ai_commentary(ticker, metrics, quote, news=news, profile=profile, performance=performance, alpha_intel=alpha_intel, risk_profile=risk)
            
            # Format report
            name = profile.get('name', ticker)
            industry = profile.get('finnhubIndustry', 'N/A')
            
            # Helper for indicators
            def get_dir(val):
                if isinstance(val, (int, float)):
                    return "🟢" if val > 0 else "🔴" if val < 0 else "⚪️"
                return "⚪️"

            m1d = get_dir(quote.get('percent_change', 0))
            m5d = get_dir(performance.get('5d_pct', 0))
            m1m = get_dir(performance.get('1m_pct', 0))
            
            # Format volume
            curr_vol = performance.get('curr_vol', 'N/A')
            vol_str = f"{curr_vol:,.0f}" if isinstance(curr_vol, (int, float)) else "N/A"
            avg_vol = metrics.get('volume_avg_10d', 'N/A')
            avg_vol_str = f"{avg_vol:,.0f}" if isinstance(avg_vol, (int, float)) else "N/A"

            p5d = performance.get('5d_pct', 'N/A')
            p5d_str = f"{p5d:+.2f}%" if isinstance(p5d, (int, float)) else "N/A"
            p1m = performance.get('1m_pct', 'N/A')
            p1m_str = f"{p1m:+.2f}%" if isinstance(p1m, (int, float)) else "N/A"

            chg1d = quote.get('percent_change', 'N/A')
            chg1d_str = f"{chg1d:+.2f}%" if isinstance(chg1d, (int, float)) else "N/A"
            curr_p = quote.get('current_price', 'N/A')
            curr_p_str = f"${curr_p:,.2f}" if isinstance(curr_p, (int, float)) else "N/A"

            report = (
                f"🧠 <b>OPERATOR SNAPSHOT: {ticker}</b>\n"
                f"<i>{name} | {industry}</i>\n"
                f"────────────────────────\n"
                f"📈 <b>MOMENTUM & SCALE</b>\n"
                f"<code>"
                f"Price:          {curr_p_str}\n"
                f"1D Performance: {m1d} {chg1d_str}\n"
                f"5D Performance: {m5d} {p5d_str}\n"
                f"1M Performance: {m1m} {p1m_str}\n"
                f"Market Cap:     {metrics['market_cap']}M"
                f"</code>\n\n"
                f"📊 <b>VOLUME CONVICTION</b>\n"
                f"<code>"
                f"Current Vol:    {vol_str}\n"
                f"10D Avg Vol:    {avg_vol_str}"
                f"</code>\n\n"
                f"💰 <b>CORE FUNDAMENTALS</b>\n"
                f"<code>"
                f"P/E Ratio:      {metrics['pe_ratio']}\n"
                f"Net Margin:     {metrics['net_margin']}%\n"
                f"Rev. Growth:    {metrics['revenue_growth']}%\n"
                f"ROIC:           {metrics['roic']}%"
                f"</code>\n\n"
                f"🐋 <b>BIG MONEY FOOTPRINT</b>\n"
                f"<code>"
                f"Inst. Held:     {alpha_intel['inst_held']}\n"
                f"Insider Held:   {alpha_intel['insider_held']}\n"
                f"Short Interest: {metrics['short_pct']}%\n"
                f"Short Ratio:    {metrics['short_ratio']}"
                f"</code>\n\n"
                f"🧠 <b>UNIFIED INTELLIGENCE</b>\n"
                f"{commentary}"
                f"{self.FINANCIAL_DISCLAIMER}\n"
                f"────────────────────────"
            )
            report += f"\n\n<b>🗓 EARNINGS PROXIMITY</b>\nNext Earnings: <code>{metrics.get('next_earnings')}</code> ({metrics.get('days_to_earnings')} days)"

            # Snapshot Footer with Buttons
            keyboard = {"inline_keyboard": [
                [
                    {"text": "📈 View Technical Chart", "callback_data": f"chart:{ticker}"},
                    {"text": "⚖️ Compare Ticker", "callback_data": f"prompt_compare:{ticker}"}
                ],
                [
                    {"text": "🏭 Industry Review", "callback_data": f"industry:{ticker}"}
                ]
            ]}

            # If called from callback (skip_market_check=True), send the message directly
            if skip_market_check:
                self.telegram_notifier.send_message(report, chat_id=chat_id, reply_markup=json.dumps(keyboard))
                return None, None  # Indicate message was sent
            else:
                # If called from command, return the message for the command handler to send
                return report, json.dumps(keyboard)
        except Exception as e:
            logger.error(f"Error in handle_analyse: {e}", exc_info=True)
            error_msg = f"❌ Failed to generate report: {str(e)}"
            if skip_market_check:
                self.telegram_notifier.send_message(error_msg, chat_id=chat_id)
                return None, None
            else:
                return error_msg, None

    def handle_ask(self, parts_text, chat_id, user_id=None):
        """Handle user questions about a stock."""
        u_id = user_id or chat_id
        parts = parts_text.split(maxsplit=1)
        if len(parts) < 2:
            return "❌ Usage: /ask TICKER QUESTION\nExample: /ask CCCC Who are their competitors?"
        
        ticker = parts[0].upper().strip()
        question = parts[1]
        
        self.telegram_notifier.send_message(f"🤔 <b>Consulting AI about {ticker}...</b>", chat_id=chat_id)
        
        # We try to get news too if possible for better context
        # But we don't have direct access to NewsMonitor here easily without passing it
        try:
            metrics = self.analyzer.get_basic_financials(ticker)
            quote = self.analyzer.get_stock_quote(ticker)
            profile = self.analyzer.get_company_profile(ticker)
            
            risk = self.cache.get_user_risk(u_id)
            alpha = self.analyzer.get_alpha_intelligence(ticker)
            
            answer = self.analyzer.get_ai_commentary(ticker, metrics, quote, question=question, profile=profile, alpha_intel=alpha, risk_profile=risk)
            return f"🤖 <b>AI Answer for {ticker}:</b>\n\n{answer}{self.FINANCIAL_DISCLAIMER}"
        except Exception as e:
            logger.error(f"Error in handle_ask: {e}", exc_info=True)
            return f"❌ Failed to get AI answer: {str(e)}"
    
    
    def handle_chart(self, args, chat_id, user_id=None):
        """Generate and send technical chart."""
        u_id = user_id or chat_id
        if not args:
            return "❌ Usage: /chart TICKER\nExample: /chart NVDA"
        
        ticker = args.upper().strip()
        self.telegram_notifier.send_message(f"📊 <b>Generating technical chart for {ticker}...</b>", chat_id=chat_id)
        
        try:
            chart_buf, tech_context = self.analyzer.get_stock_chart(ticker)
            if not chart_buf:
                return f"❌ Failed to generate chart for {ticker}.\nReason: {tech_context or 'Internal Error'}"
            
            # Fetch AI technical insights
            insights = self.analyzer.get_ai_technical_insights(ticker, tech_context)
            
            # Use telegram_notifier.send_photo
            caption = (
                f"📈 <b>Technical Analysis: {ticker}</b>\n"
                f"────────────────────────\n"
                f"{insights}\n\n"
                f"<i>Indicators: DMA 20/50/200 + RSI(14)</i>"
            )
            
            success = self.telegram_notifier.send_photo(
                chart_buf, 
                caption=caption,
                chat_id=chat_id
            )
            
            if not success:
                return "❌ Failed to send chart image. Please try again."
            
            return None # Message sent via send_photo
            
        except Exception as e:
            logger.error(f"Error in handle_chart for {ticker}: {e}", exc_info=True)
            return f"❌ Error: {str(e)}"

    def handle_compare(self, args, chat_id, user_id=None):
        """Compare two stock tickers."""
        u_id = user_id or chat_id
        tickers = args.upper().strip().split()
        if len(tickers) < 2:
            return "❌ Usage: /compare TICKER1 TICKER2\nExample: /compare AAPL MSFT"
        
        t1, t2 = tickers[0], tickers[1]
        self.telegram_notifier.send_message(f"⚖️ <b>Comparing {t1} vs {t2}...</b>\nGathering data and AI comparison. This will take a moment.", chat_id=chat_id)
        
        try:
            # Gather data for both
            m1 = self.analyzer.get_basic_financials(t1)
            q1 = self.analyzer.get_stock_quote(t1)
            
            m2 = self.analyzer.get_basic_financials(t2)
            q2 = self.analyzer.get_stock_quote(t2)
            
            # Use analyzer to get comparison commentary
            commentary = self.analyzer.get_ai_comparison(t1, m1, q1, t2, m2, q2)
            
            report = (
                f"⚖️ <b>COMPARISON: {t1} vs {t2}</b>\n"
                f"────────────────────────\n"
                f"<b>📊 DATA GRID</b>\n"
                f"<code>"
                f"METRIC      {t1:<8} {t2:<8}\n"
                f"PRICE       {q1['current_price']:<8.2f} {q2['current_price']:<8.2f}\n"
                f"CHG%        {q1['percent_change']:<8.2f} {q2['percent_change']:<8.2f}\n"
                f"P/E         {str(m1['pe_ratio']):<8} {str(m2['pe_ratio']):<8}\n"
                f"CAP(M)      {str(m1['market_cap']):<8} {str(m2['market_cap']):<8}"
                f"</code>\n\n"
                f"<b>💡 AI VERDICT</b>\n"
                f"{commentary}\n"
                f"────────────────────────"
            )
            return report
            
        except Exception as e:
            logger.error(f"Error in handle_compare: {e}")
            return f"❌ Failed to compare stocks: {str(e)}"
    
    def handle_debug(self):
        """Show diagnostic information."""
        from dotenv import load_dotenv
        load_dotenv() 
        
        lines = ["🔎 <b>System Debug Information</b>\n"]
        
        # 1. Check Core Bot Keys
        tg_token = os.getenv('TELEGRAM_BOT_TOKEN')
        tg_status = "✅ Found" if tg_token else "❌ Missing"
        lines.append(f"• Telegram Token: {tg_status}")
        
        # 2. Check Finnhub
        fh_key = os.getenv('FINNHUB_API_KEY')
        fh_status = "✅ Found" if fh_key else "❌ Missing"
        lines.append(f"• Finnhub API Key: {fh_status}")
        
        # 3. Check Groq (Integrated Search)
        groq_key = self.analyzer.groq_api_key
        if groq_key:
            # Mask key for safety
            masked = f"{groq_key[:5]}...{groq_key[-4:]}"
            lines.append(f"• Groq AI Engine: ✅ Active ({masked})")
        else:
            lines.append("• Groq AI Engine: ❌ Missing (Check GROQ_API_KEY)")

        lines.append(f"\n<b>Bot Status:</b>")
        lines.append(f"• Model Ready: {'✅ Yes' if self.analyzer.client else '❌ No'}")
        lines.append(f"• Multi-User DB: ✅ Connected")
        lines.append(f"• Server Time: {datetime.now().strftime('%H:%M:%S')}")
        
        return "\n".join(lines)
    
    def process_command(self, message_text, user_id, chat_id):
        """Process a command message."""
        try:
            parts = message_text.strip().split(maxsplit=1)
            raw_command = parts[0].lower()
            # Handle commands with bot username (e.g., /help@MyBot)
            command = raw_command.split('@')[0]
            args = parts[1] if len(parts) > 1 else ''
            
            if command == '/start':
                return self.handle_start(user_id, chat_id)
            elif command == '/help':
                return self.handle_help(), None
            elif command == '/add':
                if not args:
                    return "❌ Usage: /add TICKER\nExample: /add AAPL", None
                return self.handle_add_stock(args, user_id), None
            elif command == '/remove':
                if not args:
                    return "❌ Usage: /remove TICKER\nExample: /remove BYND", None
                return self.handle_remove_stock(args, user_id), None
            elif command == '/list':
                return self.handle_list_stocks(user_id)
            elif command == '/interval':
                if not args:
                    return "❌ Usage: /interval MINUTES\nExample: /interval 5"
                return self.handle_set_interval(args), None
            elif command == '/status':
                return self.handle_status(), None
            elif command == '/snapshot' or command == '/analyse' or command == '/analyze' or command == '/why':
                if not args:
                    cmd_name = command[1:]
                    return f"❌ Usage: /{cmd_name} TICKER\nExample: /{cmd_name} AAPL", None
                return self.handle_analyse(args, chat_id, user_id)
            elif command == '/chart':
                return self.handle_chart(args, chat_id, user_id), None
            elif command == '/ask':
                if not args:
                    return "❌ Usage: /ask TICKER QUESTION\nExample: /ask CCCC What does this company do?", None
                return self.handle_ask(args, chat_id, user_id), None
            elif command == '/compare':
                return self.handle_compare(args, chat_id, user_id), None
            elif command == '/debug':
                return self.handle_debug(), None
            elif command == '/ping':
                return "🏓 <b>Pong!</b> Bot is online and responsive.", None
            elif command == '/undervalued' or command == '/alpha' or command == '/discovery':
                return self.handle_undervalued(chat_id), None
            elif command == '/risk':
                return self.handle_risk(chat_id, user_id)
            elif command == '/premarket':
                return self.handle_premarket(chat_id, user_id), None
            elif command == '/sectors':
                return self.handle_sectors(), None
            elif command == '/donate':
                return self.handle_donate(), None
            elif command == '/about' or command == '/info':
                return self.handle_about(), None
            else:
                return f"❌ Unknown command: {command}\n\nUse /help to see available commands", None
        except Exception as e:
            logger.error(f"Error processing command {message_text}: {e}", exc_info=True)
            return f"❌ An internal error occurred while processing your command: {str(e)}"
    
    def handle_callback_query(self, callback_query):
        """Process inline button clicks."""
        dq_id = callback_query.get('id')
        data = callback_query.get('data', '')
        chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
        user_id = callback_query.get('from', {}).get('id')
        
        # Answer immediately to stop spinner
        requests.post(f"{self.api_url}/answerCallbackQuery", json={'callback_query_id': dq_id})
        
        if not data: return
        
        action, ticker = data.split(':', 1) if ':' in data else (data, '')
        
        # Handle market selection callbacks
        if action == 'market':
            # Format: market:NSE:TICKER or market:US:TICKER
            parts = data.split(':', 2)
            if len(parts) == 3:
                _, market, base_ticker = parts
                # Apply market suffix
                if market == 'NSE':
                    resolved_ticker = f"{base_ticker}.NS"
                    flag = "🇮🇳"
                elif market == 'BSE':
                    resolved_ticker = f"{base_ticker}.BO"
                    flag = "🇮🇳"
                else:  # US
                    resolved_ticker = base_ticker
                    flag = "🇺🇸"
                
                # Execute the original command with resolved ticker
                # Skip market check since we just resolved it
                # handle_analyse will send the analysis message directly, so we don't need to send it again
                self.handle_analyse(resolved_ticker, chat_id, user_id, skip_market_check=True)
            return
        
        if action == 'chart':
            self.handle_chart(ticker, chat_id)
        elif action == 'snap':
            # handle_analyse returns tuple (msg, kb_json), we need to send it
            msg, kb = self.handle_analyse(ticker, chat_id, user_id)
            self.telegram_notifier.send_message(msg, chat_id=chat_id, reply_markup=kb)
        elif action == 'industry':
            report = self.analyzer.get_industry_analysis(ticker)
            self.telegram_notifier.send_message(report + self.FINANCIAL_DISCLAIMER, chat_id=chat_id)
        elif action == 'setrisk':
            # ticker here is the risk profile name
            success = self.cache.set_user_risk(chat_id, ticker)
            
            # Phase 11 Onboarding Logic
            state = self.cache.get_user_state(user_id)
            if state['step'] == 1:
                self.cache.set_user_step(user_id, 2)
                self.telegram_notifier.send_message(
                    f"✅ <b>Risk Strategy Locked: {ticker}</b>\n\n"
                    "Next, tell me which <b>Sectors or Themes</b> interest you? (e.g. AI, Clean Energy, SaaS, Chipmakers)\n\n"
                    "<i>Just type your interests below:</i>", 
                    chat_id=chat_id
                )
            elif success:
                self.telegram_notifier.send_message(f"✅ <b>Risk Profile set to: {ticker}</b>\nFuture reports will be tailored to this strategy.", chat_id=chat_id)
            else:
                self.telegram_notifier.send_message("❌ Failed to update risk profile.", chat_id=chat_id)
        elif action == 'prompt_compare':
            self.telegram_notifier.send_message(f"🔍 <b>To compare {ticker}</b>, type: <code>/compare {ticker} TICKER2</code>", chat_id=chat_id)

    def handle_onboarding_interests(self, user_id, chat_id, text):
        """Finalize onboarding with interests."""
        self.cache.set_user_interests(user_id, text)
        self.cache.set_user_step(user_id, 0)
        
        self.telegram_notifier.send_message("🤵‍♂️ <b>Mapping your Financial DNA...</b>", chat_id=chat_id)
        
        state = self.cache.get_user_state(user_id)
        summary = self.analyzer.get_persona_summary(state['risk'], state['interests'])
        
        report = (
            f"🤝 <b>WELCOME TO ALPHA INTELLIGENCE</b>\n\n"
            f"{summary}\n\n"
            "────────────────────────\n"
            "🚀 <b>QUICK START GUIDE:</b>\n"
            "• Use <code>/snapshot TICKER</code> for deep analysis.\n"
            "• Use <code>/premarket</code> for your morning brief.\n"
            "• Use <code>/undervalued</code> to find new plays.\n"
            "• 🎙 <b>Tip:</b> Try sending a voice note!"
        )
        self.telegram_notifier.send_message(report, chat_id=chat_id)

    def handle_undervalued(self, chat_id):
        """Find and display undervalued stock picks."""
        self.telegram_notifier.send_message("🔍 <b>Searching Alpha List for undervalued gems...</b>\nAnalyzing growth vs valuation metrics. Please wait.", chat_id=chat_id)
        try:
            report = self.analyzer.get_undervalued_picks()
            return f"💎 <b>ALPHA DISCOVERY: Top Undervalued Picks</b>\n\n{report}{self.FINANCIAL_DISCLAIMER}"
        except Exception as e:
            logger.error(f"Error in handle_undervalued: {e}")
            return "❌ Alpha Discovery failed. Please try again."

    def handle_risk(self, chat_id, user_id=None):
        """Allow user to select their risk profile."""
        u_id = user_id or chat_id
        current = self.cache.get_user_risk(u_id)
        msg = f"🛡️ <b>RISK PROFILING</b>\nYour current profile is: <b>{current}</b>\n\nSelect a strategy to tailor AI reports:"
        keyboard = {"inline_keyboard": [
            [
                {"text": "🚀 Degen (Aggressive)", "callback_data": "setrisk:Degen"},
                {"text": "⚖️ Balanced (Moderate)", "callback_data": "setrisk:Moderate"}
            ],
            [
                {"text": "🏦 Builder (Conservative)", "callback_data": "setrisk:Builder"}
            ]
        ]}
        return msg, json.dumps(keyboard)

    def handle_premarket(self, chat_id, user_id=None):
        """Generate pre-market briefing."""
        u_id = user_id or chat_id
        risk = self.cache.get_user_risk(u_id)
        wl = self.cache.get_user_watchlist(u_id)
        self.telegram_notifier.send_message("☕️ <b>Brewing your Pre-Market Alpha Briefing...</b>\nAnalyzing global sector rotation and your watchlist. Please wait.", chat_id=chat_id)
        report = self.analyzer.get_pre_market_briefing(risk_profile=risk, watchlist=wl)
        return f"📍 <b>PRE-MARKET ALPHA: The Institutional Brief</b>\n\n{report}{self.FINANCIAL_DISCLAIMER}"

    def handle_sectors(self):
        """Display sector rotation performance."""
        trends = self.analyzer.get_sector_trends()
        if not trends: return "❌ Failed to fetch sector data."
        
        lines = [self.BOT_HEADER + "<b>🏁 SECTOR ROTATION TERMINAL</b>\n"]
        lines.append("<code>")
        lines.append(f"{'SECTOR':<18} {'CHG%':>8}")
        lines.append("─" * 27)
        for t in trends:
            lines.append(f"{t['name']:<18} {t['change']:>+7.2f}%")
        lines.append("</code>")
        return "\n".join(lines)

    def handle_voice(self, message):
        """Transcribe and process voice messages."""
        chat_id = message['chat'].get('id')
        user_id = message.get('from', {}).get('id')
        voice = message.get('voice')
        if not voice: return
        
        file_id = voice['file_id']
        self.telegram_notifier.send_message("🎙️ <b>Processing Voice Signal...</b>", chat_id=chat_id)
        
        try:
            # 1. Get file path
            resp = requests.get(f"{self.api_url}/getFile", params={'file_id': file_id})
            file_path = resp.json()['result']['file_path']
            file_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
            
            # 2. Download
            audio_data = requests.get(file_url).content
            file_name = f"voice_{file_id}.oga"
            with open(file_name, 'wb') as f:
                f.write(audio_data)
            
            # 3. Transcribe via Groq
            if not self.analyzer.client:
                return "❌ AI Transcription offline."
            
            with open(file_name, 'rb') as audio_file:
                transcription = self.analyzer.client.audio.transcriptions.create(
                    file=(file_name, audio_file.read()),
                    model="whisper-large-v3",
                    response_format="text",
                )
            
            # Clean up
            if os.path.exists(file_name): os.remove(file_name)
            
            trans_text = str(transcription).strip()
            self.telegram_notifier.send_message(f"📝 <b>Transcribed:</b> \"{trans_text}\"", chat_id=chat_id)
            
            # 4. Route to handle_ask if it looks like a ticker query
            # We assume any voice note for now is a question for the AI analyst
            # Or we can try to find a ticker in the text
            words = trans_text.upper().split()
            potential_ticker = None
            for w in words:
                if len(w) <= 5 and w.isalpha():
                    # Check if it's a known ticker or just use it
                    potential_ticker = w
                    break
            
            if potential_ticker:
                response = self.handle_ask(f"{potential_ticker} {trans_text}", chat_id)
                self.telegram_notifier.send_message(response, chat_id=chat_id)
            else:
                self.telegram_notifier.send_message("🔬 <b>AI Insight:</b> I couldn't identify a specific ticker in your message. Try mentioning a symbol like 'AAPL' or 'NVDA'.", chat_id=chat_id)
                
        except Exception as e:
            logger.error(f"Voice processing failed: {e}")
            self.telegram_notifier.send_message(f"❌ Voice processing failed: {str(e)}", chat_id=chat_id)

    def check_and_handle_commands(self):
        """Check for new commands and callback queries."""
        updates = self.get_updates()
        
        for update in updates:
            current_update_id = update['update_id']
            self.last_update_id = current_update_id
            
            # Handle Callback Queries (Buttons)
            if 'callback_query' in update:
                self.handle_callback_query(update['callback_query'])
                continue

            if 'message' not in update:
                continue
            
            message = update['message']
            chat_id = message['chat'].get('id')
            user = message.get('from', {})
            user_id = user.get('id')
            username = user.get('username', 'N/A')
            
            if 'voice' in message:
                self.handle_voice(message)
                continue

            if 'text' not in message:
                continue
            
            text = message['text']
            
            # Handle Group Mentions
            if message['chat']['type'] in ['group', 'supergroup']:
                if not text.startswith('/') and f"@{self.bot_username}" not in text:
                    continue # Ignore normal chatter in groups
            
            if not text.startswith('/'):
                # Phase 11: Check if in onboarding
                state = self.cache.get_user_state(user_id)
                if state['step'] == 2:
                    self.handle_onboarding_interests(user_id, chat_id, text)
                    continue

                # Process as natural language if it doesn't start with / but in DM
                if message['chat']['type'] == 'private':
                    # Find a ticker and route to /ask
                    words = text.upper().split()
                    ticker = None
                    for w in words:
                        if len(w) <= 5 and w.isalpha():
                            ticker = w
                            break
                    if ticker:
                        resp = self.handle_ask(f"{ticker} {text}", chat_id)
                        self.telegram_notifier.send_message(resp, chat_id=chat_id)
                    else:
                        self.telegram_notifier.send_message("🤖 I'm here! Tell me a ticker (e.g., AAPL) or ask a question.", chat_id=chat_id)
                continue
            
            logger.info(f"📥 COMMAND RECEIVED: '{text}' from @{username} (Chat: {chat_id})")
            
            try:
                first_name = user.get('first_name', 'N/A')
                parts = text.strip().split(maxsplit=1)
                cmd_name = parts[0].lower()
                cmd_args = parts[1] if len(parts) > 1 else ''
                self.cache.log_user_command(user_id, username, first_name, cmd_name, cmd_args)
                
                # Process and Reply
                response, reply_markup = self.process_command(text, user_id, chat_id)
                if response:
                    self.telegram_notifier.send_message(response, chat_id=chat_id, reply_markup=reply_markup)
                    logger.info(f"📤 REPLY SENT to @{username}")
            except Exception as e:
                logger.error(f"Error processing command '{text}': {e}", exc_info=True)
                self.telegram_notifier.send_message(f"❌ Sorry, an error occurred: {str(e)}", chat_id=chat_id)

    def start_polling(self):
        """Start a continuous loop to check for commands."""
        logger.info("Bot command polling started (Background Thread)")
        while True:
            try:
                self.check_and_handle_commands()
                time.sleep(1) # Poll more frequently for buttons
            except Exception as e:
                logger.error(f"Error in bot polling loop: {e}")
                time.sleep(5)
