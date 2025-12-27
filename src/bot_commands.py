"""
Telegram bot command handler for interactive stock management.
"""
import os
import json
import requests
from utils import logger
from analyzer import StockAnalyzer


class TelegramBotHandler:
    """Handles incoming Telegram commands for managing stocks and settings."""
    
    def __init__(self, bot_token=None, chat_id=None, config_path='config/stocks.json'):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.config_path = config_path
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_update_id = 0
        self.analyzer = StockAnalyzer()
        
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
                return data['result']
            return []
        except Exception as e:
            logger.debug(f"Error getting updates: {e}")
            return []
    
    def send_message(self, text):
        """Send a message to the user."""
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def handle_add_stock(self, ticker):
        """Add a stock to monitoring list."""
        config = self.load_config()
        if not config:
            return "❌ Failed to load configuration"
        
        ticker = ticker.upper().strip()
        
        # Check if already exists
        for stock in config['stocks']:
            if stock['ticker'] == ticker:
                if stock.get('enabled', True):
                    return f"ℹ️ {ticker} is already being monitored"
                else:
                    stock['enabled'] = True
                    self.save_config(config)
                    return f"✅ Re-enabled monitoring for {ticker}"
        
        # Add new stock
        config['stocks'].append({
            'ticker': ticker,
            'name': ticker,
            'enabled': True
        })
        
        if self.save_config(config):
            return f"✅ Added {ticker} to monitoring list!\n\nChanges will take effect on next check cycle."
        else:
            return "❌ Failed to save configuration"
    
    def handle_remove_stock(self, ticker):
        """Remove a stock from monitoring list."""
        config = self.load_config()
        if not config:
            return "❌ Failed to load configuration"
        
        ticker = ticker.upper().strip()
        
        for stock in config['stocks']:
            if stock['ticker'] == ticker:
                stock['enabled'] = False
                if self.save_config(config):
                    return f"✅ Disabled monitoring for {ticker}\n\nChanges will take effect on next check cycle."
                else:
                    return "❌ Failed to save configuration"
        
        return f"❌ {ticker} not found in monitoring list"
    
    def handle_list_stocks(self):
        """List all monitored stocks."""
        config = self.load_config()
        if not config:
            return "❌ Failed to load configuration"
        
        active = [s for s in config['stocks'] if s.get('enabled', True)]
        disabled = [s for s in config['stocks'] if not s.get('enabled', True)]
        
        message = "📊 <b>Monitored Stocks</b>\n\n"
        
        if active:
            message += "<b>Active:</b>\n"
            for stock in active:
                message += f"  • {stock['ticker']} - {stock.get('name', stock['ticker'])}\n"
        
        if disabled:
            message += "\n<b>Disabled:</b>\n"
            for stock in disabled:
                message += f"  • {stock['ticker']} - {stock.get('name', stock['ticker'])}\n"
        
        interval = config.get('monitoring', {}).get('check_interval_minutes', 15)
        threshold = config.get('monitoring', {}).get('price_change_threshold_percent', 0.5)
        
        message += f"\n⏱️ Check interval: {interval} minutes"
        message += f"\n📈 Price threshold: {threshold}%"
        
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
        """Show help message."""
        return """
🤖 <b>Stock Monitor Bot</b>

<b>Commands:</b>
• /add TICKER - Track a stock
• /remove TICKER - Stop tracking
• /list - Show monitored stocks
• /analyse TICKER - AI Analysis & Rating
• /ask TICKER QUESTION - Ask AI anything
• /status - Show agent status
• /interval MIN - Set check interval
"""
    
    def handle_status(self):
        """Show current status."""
        config = self.load_config()
        if not config:
            return "❌ Failed to load configuration"
        
        active_stocks = [s for s in config['stocks'] if s.get('enabled', True)]
        interval = config.get('monitoring', {}).get('check_interval_minutes', 15)
        threshold = config.get('monitoring', {}).get('price_change_threshold_percent', 0.5)
        
        return f"""
📊 <b>Agent Status</b>

🔹 Monitoring: {len(active_stocks)} stocks
🔹 Check interval: {interval} minutes
🔹 Price threshold: {threshold}%
🔹 News alerts: {'All news' if config.get('monitoring', {}).get('notify_all_news', True) else 'Major only'}

Use /list to see all stocks
"""

    def handle_analyse(self, ticker):
        """Perform fundamental analysis on a stock."""
        ticker = ticker.upper().strip()
        self.send_message(f"🔍 <b>Analyzing {ticker}...</b>\nFetching financials and AI commentary. This may take a moment.")
        
        metrics = self.analyzer.get_basic_financials(ticker)
        history = self.analyzer.get_price_history(ticker)
        
        if not metrics or not history:
            return f"❌ Failed to fetch data for {ticker}. Please verify the ticker."
        
        # Get AI commentary
        commentary = self.analyzer.get_ai_commentary(ticker, metrics, history)
        
        # Format metrics summary
        summary = (
            f"📊 <b>Fundamental Data: {ticker}</b>\n\n"
            f"💰 P/E Ratio: {metrics['pe_ratio'] or 'N/A'}\n"
            f"🏦 Market Cap: {metrics['market_cap'] or 'N/A'}M\n"
            f"📏 P/S Ratio: {metrics['ps_ratio'] or 'N/A'}\n"
            f"📈 52W High: ${metrics['52_week_high'] or 'N/A'}\n"
            f"📉 52W Low: ${metrics['52_week_low'] or 'N/A'}\n"
            f"🎲 Beta: {metrics['beta'] or 'N/A'}\n\n"
            f"<b>🧠 AI Analysis:</b>\n{commentary}"
        )
        return summary

    def handle_ask(self, parts_text):
        """Handle user questions about a stock."""
        parts = parts_text.split(maxsplit=1)
        if len(parts) < 2:
            return "❌ Usage: /ask TICKER QUESTION\nExample: /ask CCCC Who are their competitors?"
        
        ticker = parts[0].upper().strip()
        question = parts[1]
        
        self.send_message(f"🤔 <b>Consulting AI about {ticker}...</b>")
        
        metrics = self.analyzer.get_basic_financials(ticker)
        history = self.analyzer.get_price_history(ticker)
        
        # We try to get news too if possible for better context
        # But we don't have direct access to NewsMonitor here easily without passing it
        # Let's stick to metrics and history for now, or fetch news inside analyzer
        
        answer = self.analyzer.get_ai_commentary(ticker, metrics, history, question=question)
        return f"🤖 <b>AI Answer for {ticker}:</b>\n\n{answer}"
    
    def process_command(self, message_text):
        """Process a command message."""
        parts = message_text.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ''
        
        if command == '/start':
            return self.handle_help()
        elif command == '/help':
            return self.handle_help()
        elif command == '/add':
            if not args:
                return "❌ Usage: /add TICKER\nExample: /add AAPL"
            return self.handle_add_stock(args)
        elif command == '/remove':
            if not args:
                return "❌ Usage: /remove TICKER\nExample: /remove BYND"
            return self.handle_remove_stock(args)
        elif command == '/list':
            return self.handle_list_stocks()
        elif command == '/interval':
            if not args:
                return "❌ Usage: /interval MINUTES\nExample: /interval 5"
            return self.handle_set_interval(args)
        elif command == '/status':
            return self.handle_status()
        elif command == '/analyse' or command == '/analyze':
            if not args:
                return "❌ Usage: /analyse TICKER\nExample: /analyse AAPL"
            return self.handle_analyse(args)
        elif command == '/ask':
            if not args:
                return "❌ Usage: /ask TICKER QUESTION\nExample: /ask CCCC What does this company do?"
            return self.handle_ask(args)
        else:
            return f"❌ Unknown command: {command}\n\nUse /help to see available commands"
    
    def check_and_handle_commands(self):
        """Check for new commands and handle them."""
        updates = self.get_updates()
        
        for update in updates:
            self.last_update_id = update['update_id']
            
            if 'message' not in update:
                continue
            
            message = update['message']
            
            # Only process messages from the configured chat
            if str(message['chat']['id']) != str(self.chat_id):
                continue
            
            # Only process text messages
            if 'text' not in message:
                continue
            
            text = message['text']
            
            # Only process commands (starting with /)
            if not text.startswith('/'):
                continue
            
            logger.info(f"Processing command: {text}")
            response = self.process_command(text)
            self.send_message(response)
    def start_polling(self):
        """Start a continuous loop to check for commands (for background thread)."""
        logger.info("Bot command polling started (Background Thread)")
        while True:
            try:
                self.check_and_handle_commands()
            except Exception as e:
                logger.error(f"Error in bot polling loop: {e}")
                import time
                time.sleep(5)  # Wait before retrying on error
