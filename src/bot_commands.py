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
                logger.info(f"Bot authenticated as @{bot_info.get('username')} (ID: {bot_info.get('id')})")
            
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
        """List user's personal monitored stocks."""
        tickers = self.cache.get_user_watchlist(user_id)
        
        if not tickers:
            return "📭 <b>Your Watchlist is Empty</b>\n\nUse /add TICKER to start monitoring stocks."
        
        message = "📊 <b>Your Personal Watchlist</b>\n\n"
        for ticker in sorted(tickers):
            message += f"  • {ticker}\n"
        
        message += "\nUse /analyse TICKER for deep insights!"
        return message
    
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
        return """
👨‍💻 <b>STOCK MONITOR COMMAND CENTER</b>
────────────────────────
<b>📊 Analysis & Insights</b>
• /analyse <code>SYM</code> - AI Deep Intelligence
• /compare <code>S1 S2</code> - Side-by-side verdict
• /ask <code>SYM Q</code> - Financial Q&A

<b>📈 Watchlist Management</b>
• /add <code>SYM</code> - Add to private watchlist
• /remove <code>SYM</code> - Stop monitoring
• /list - View your stocks

<b>⚙️ System & Support</b>
• /status - Health & Usage metrics
• /interval <code>MIN</code> - Set check frequency
• /ping - Diagnostic test
• /donate - Support independent AI ☕️
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

    def handle_analyse(self, ticker, chat_id):
        """Perform 60-day 'Deep Intelligence' analysis on a stock."""
        ticker = ticker.upper().strip()
        self.send_message(f"🔍 <b>Generating Deep Intelligence Report for {ticker}...</b>\nFetching 60 days of context and sector trends. Please wait.", chat_id=chat_id)
        
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
            
            # 5. Get AI Deep Commentary
            commentary = self.analyzer.get_ai_commentary(ticker, metrics, quote, news=news, profile=profile)
            
            # Format report
            name = profile.get('name', ticker)
            industry = profile.get('finnhubIndustry', 'N/A')
            sector = profile.get('finnhubSector', 'N/A')
            
            report = (
                f"🧠 <b>OPERATOR SNAPSHOT: {ticker}</b>\n"
                f"<i>{name} | {industry}</i>\n"
                f"────────────────────────\n"
                f"📊 <b>PERFORMANCE & SCALE</b>\n"
                f"<code>"
                f"Price:  ${quote['current_price']:,.2f} ({quote['percent_change']:+.2f}%)\n"
                f"Cap:    {metrics['market_cap']}M\n"
                f"Range:  ${metrics['52_week_low']} - ${metrics['52_week_high']}\n"
                f"P/E:    {metrics['pe_ratio']}"
                f"</code>\n\n"
                f"💰 <b>CORE FUNDAMENTALS</b>\n"
                f"<code>"
                f"Rev. Growth: {metrics['revenue_growth']}\n"
                f"Net Margin:  {metrics['net_margin']}\n"
                f"ROIC:        {metrics['roic']}\n"
                f"Debt/Equity: {metrics['debt_to_equity']}"
                f"</code>\n\n"
                f"⚡️ <b>FIRST-PRINCIPLES ANALYSIS</b>\n"
                f"{commentary}\n"
                f"────────────────────────"
            )
            return report
            
        except Exception as e:
            logger.error(f"Crash in handle_analyse: {e}", exc_info=True)
            return f"❌ Analysis failed: {str(e)}"

    def handle_ask(self, parts_text, chat_id):
        """Handle user questions about a stock."""
        parts = parts_text.split(maxsplit=1)
        if len(parts) < 2:
            return "❌ Usage: /ask TICKER QUESTION\nExample: /ask CCCC Who are their competitors?"
        
        ticker = parts[0].upper().strip()
        question = parts[1]
        
        self.send_message(f"🤔 <b>Consulting AI about {ticker}...</b>", chat_id=chat_id)
        
        # We try to get news too if possible for better context
        # But we don't have direct access to NewsMonitor here easily without passing it
        try:
            metrics = self.analyzer.get_basic_financials(ticker)
            quote = self.analyzer.get_stock_quote(ticker)
            profile = self.analyzer.get_company_profile(ticker)
            
            answer = self.analyzer.get_ai_commentary(ticker, metrics, quote, question=question, profile=profile)
            return f"🤖 <b>AI Answer for {ticker}:</b>\n\n{answer}"
        except Exception as e:
            logger.error(f"Error in handle_ask: {e}", exc_info=True)
            return f"❌ Failed to get AI answer: {str(e)}"
    
    def handle_compare(self, args, chat_id):
        """Compare two stock tickers."""
        tickers = args.upper().strip().split()
        if len(tickers) < 2:
            return "❌ Usage: /compare TICKER1 TICKER2\nExample: /compare AAPL MSFT"
        
        t1, t2 = tickers[0], tickers[1]
        self.send_message(f"⚖️ <b>Comparing {t1} vs {t2}...</b>\nGathering data and AI comparison. This will take a moment.", chat_id=chat_id)
        
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
        load_dotenv() # Refresh just in case
        
        vars_to_check = ['FINNHUB_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'GROQ_API_KEY', 'GROQ_KEY']
        lines = ["🔎 <b>System Debug Information</b>\n"]
        
        for var in vars_to_check:
            val = os.getenv(var)
            status = "✅ Found" if val else "❌ Missing"
            masked = f"{val[:5]}...{val[-4:]}" if val and len(val) > 10 else "N/A"
            lines.append(f"• {var}: {status} ({masked})")
            
        # Search for similar named keys
        all_keys = os.environ.keys()
        similar = [k for k in all_keys if 'GROQ' in k or 'KEY' in k]
        if similar:
            lines.append(f"\nPotential Matches Found: {', '.join(similar)}")
            
        lines.append(f"\nModel Initialized: {'✅ Yes' if self.analyzer.client else '❌ No'}")
        lines.append(f"Process ID: {os.getpid()}")
        lines.append(f"Server Time: {datetime.now().strftime('%H:%M:%S')}")
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
                return self.handle_help()
            elif command == '/help':
                return self.handle_help()
            elif command == '/add':
                if not args:
                    return "❌ Usage: /add TICKER\nExample: /add AAPL"
                return self.handle_add_stock(args, user_id)
            elif command == '/remove':
                if not args:
                    return "❌ Usage: /remove TICKER\nExample: /remove BYND"
                return self.handle_remove_stock(args, user_id)
            elif command == '/list':
                return self.handle_list_stocks(user_id)
            elif command == '/interval':
                if not args:
                    return "❌ Usage: /interval MINUTES\nExample: /interval 5"
                return self.handle_set_interval(args)
            elif command == '/status':
                return self.handle_status()
            elif command == '/analyse' or command == '/analyze' or command == '/snapshot':
                if not args:
                    return "❌ Usage: /snapshot TICKER\nExample: /snapshot AAPL"
                return self.handle_analyse(args, chat_id)
            elif command == '/ask':
                if not args:
                    return "❌ Usage: /ask TICKER QUESTION\nExample: /ask CCCC What does this company do?"
                return self.handle_ask(args, chat_id)
            elif command == '/compare':
                return self.handle_compare(args, chat_id)
            elif command == '/debug':
                return self.handle_debug()
            elif command == '/ping':
                return "🏓 <b>Pong!</b> Bot is online and responsive."
            elif command == '/donate':
                return self.handle_donate()
            else:
                return f"❌ Unknown command: {command}\n\nUse /help to see available commands"
        except Exception as e:
            logger.error(f"Error processing command {message_text}: {e}", exc_info=True)
            return f"❌ An internal error occurred while processing your command: {str(e)}"
    
    def check_and_handle_commands(self):
        """Check for new commands and handle them with strict state tracking."""
        updates = self.get_updates()
        
        for update in updates:
            # Update state immediately to mark as received
            current_update_id = update['update_id']
            self.last_update_id = current_update_id
            
            if 'message' not in update:
                continue
            
            message = update['message']
            chat_id = message['chat'].get('id')
            user = message.get('from', {})
            user_id = user.get('id')
            username = user.get('username', 'N/A')
            
            # Only process text messages
            if 'text' not in message:
                continue
            
            text = message['text']
            if not text.startswith('/'):
                continue
            
            logger.info(f"📥 COMMAND RECEIVED: '{text}' from @{username} (Chat: {chat_id})")
            
            try:
                # Log for analytics
                first_name = user.get('first_name', 'N/A')
                parts = text.strip().split(maxsplit=1)
                cmd_name = parts[0].lower()
                cmd_args = parts[1] if len(parts) > 1 else ''
                self.cache.log_user_command(user_id, username, first_name, cmd_name, cmd_args)
                
                # Process and Reply
                response = self.process_command(text, user_id, chat_id)
                if response:
                    self.send_message(response, chat_id=chat_id)
                    logger.info(f"📤 REPLY SENT to @{username}")
            except Exception as e:
                logger.error(f"Error processing command '{text}': {e}", exc_info=True)
                self.send_message(f"❌ Sorry, an error occurred: {str(e)}", chat_id=chat_id)
    def start_polling(self):
        """Start a continuous loop to check for commands (for background thread)."""
        logger.info("Bot command polling started (Background Thread)")
        count = 0
        while True:
            try:
                count += 1
                if count % 10 == 0:  # Heartbeat every ~5 mins (assuming 30s long polling)
                    logger.info("Bot polling heartbeat: background thread is alive and listening.")
                self.check_and_handle_commands()
            except Exception as e:
                logger.error(f"Error in bot polling loop: {e}")
                import time
                time.sleep(5)  # Wait before retrying on error
