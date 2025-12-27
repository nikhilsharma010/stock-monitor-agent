"""
Main orchestrator for the# Stock Monitoring Agent - Deployment Trigger: Groq & Responsiveness Update
.
Coordinates stock monitoring, news fetching, and Telegram notifications.
"""
import os
import json
import time
import schedule
import threading
from datetime import datetime
from dotenv import load_dotenv

from stock_monitor import StockMonitor
from news_monitor import NewsMonitor
from telegram_notifier import TelegramNotifier
from bot_commands import TelegramBotHandler
from utils import CacheDB, generate_content_hash, logger


class StockMonitorAgent:
    """Main agent that orchestrates stock monitoring and notifications."""
    
    def __init__(self, config_path='config/stocks.json'):
        # Load environment variables
        load_dotenv()
        
        # Initialize components
        self.stock_monitor = StockMonitor()
        self.news_monitor = NewsMonitor()
        self.telegram = TelegramNotifier()
        self.bot_handler = TelegramBotHandler(config_path=config_path)
        self.cache = CacheDB()
        
        # Store config path for reloading
        self.config_path = config_path
        
        # Load configuration
        self.config = self._load_config(config_path)
        self.stocks = self.config.get('stocks', [])
        self.monitoring_config = self.config.get('monitoring', {})
        
        logger.info(f"Stock Monitor Agent initialized with {len(self.stocks)} stocks")
    
    def _load_config(self, config_path):
        """Load stocks configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            return {'stocks': [], 'monitoring': {}}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            return {'stocks': [], 'monitoring': {}}
    
    def check_stock_updates(self):
        """Check for stock price updates and send notifications."""
        logger.info("Checking stock updates...")
        
        for stock_config in self.stocks:
            if not stock_config.get('enabled', True):
                continue
            
            ticker = stock_config['ticker']
            company_name = stock_config.get('name', ticker)
            
            # Fetch stock data
            stock_data = self.stock_monitor.get_stock_data(ticker)
            
            if not stock_data:
                logger.warning(f"No data available for {ticker}")
                continue
            
            # Use company name from config or API
            company_name = stock_config.get('name') or stock_data.get('name', ticker)
            
            # Check if we should notify based on price change
            price_threshold = self.monitoring_config.get('price_change_threshold_percent', 5.0)
            current_change = stock_data.get('change_percent')
            change_percent = abs(current_change) if current_change is not None else 0
            
            if change_percent >= price_threshold:
                # Generate hash for deduplication
                content = f"{ticker}_price_{stock_data['current_price']:.2f}_{datetime.now().strftime('%Y-%m-%d')}"
                content_hash = generate_content_hash(content)
                
                if not self.cache.is_duplicate(content_hash):
                    # Send notification
                    self.telegram.send_stock_alert(
                        ticker=ticker,
                        company_name=company_name,
                        price=stock_data['current_price'],
                        change_percent=stock_data['change_percent']
                    )
                    
                    # Add to cache
                    self.cache.add_notification(
                        content_hash=content_hash,
                        ticker=ticker,
                        notification_type='price_alert',
                        title=f"Price: ${stock_data['current_price']:.2f}"
                    )
    
    def check_news_updates(self):
        """Check for news updates and send notifications."""
        logger.info("Checking news updates...")
        
        notify_all = self.monitoring_config.get('notify_all_news', True)
        
        for stock_config in self.stocks:
            if not stock_config.get('enabled', True):
                continue
            
            ticker = stock_config['ticker']
            company_name = stock_config.get('name', ticker)
            
            # Fetch news (last 24 hours)
            articles = self.news_monitor.get_company_news(ticker, days_back=1)
            
            if not articles:
                logger.info(f"No news for {ticker}")
                continue
            
            # Filter to recent news (last check interval)
            check_interval = self.monitoring_config.get('check_interval_minutes', 15)
            recent_articles = self.news_monitor.filter_recent_news(
                articles, 
                hours=check_interval / 60 * 2  # Check 2x the interval to avoid missing news
            )
            
            logger.info(f"Found {len(recent_articles)} recent articles for {ticker}")
            
            # Send notifications for new articles
            for article in recent_articles:
                # Generate hash for deduplication
                content_hash = generate_content_hash(
                    f"{ticker}_{article['headline']}_{article['datetime']}"
                )
                
                if not self.cache.is_duplicate(content_hash):
                    if notify_all:
                        # Send notification
                        self.telegram.send_news_alert(
                            ticker=ticker,
                            company_name=company_name,
                            headline=article['headline'],
                            summary=article.get('summary', 'No summary available')[:300],
                            url=article.get('url', ''),
                            source=article.get('source', '')
                        )
                        
                        # Add to cache
                        self.cache.add_notification(
                            content_hash=content_hash,
                            ticker=ticker,
                            notification_type='news',
                            title=article['headline'][:100]
                        )
                        
                        # Small delay to avoid rate limiting
                        time.sleep(1)
    
    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle."""
        logger.info("="*60)
        logger.info(f"Starting monitoring cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)
        
        try:
            # Reload config in case it was changed by commands
            self.config = self._load_config(self.config_path)
            self.stocks = self.config.get('stocks', [])
            self.monitoring_config = self.config.get('monitoring', {})
            
            # Check stock updates
            self.check_stock_updates()
            
            # Small delay between checks
            time.sleep(2)
            
            # Check news updates
            self.check_news_updates()
            
            # Cleanup old cache entries (weekly)
            if datetime.now().hour == 0:  # Run at midnight
                self.cache.cleanup_old_entries(days=7)
            
            logger.info("Monitoring cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error during monitoring cycle: {e}", exc_info=True)
    
    def start_scheduled_monitoring(self):
        """Start scheduled monitoring with configured interval."""
        
        logger.info("Starting scheduled monitoring")
        logger.info(f"Monitoring stocks: {', '.join([s['ticker'] for s in self.stocks if s.get('enabled', True)])}")
        
        # Send startup notification
        active_tickers = [s['ticker'] for s in self.stocks if s.get('enabled', True)]
        self.telegram.send_message(
            "🚀 <b>Stock Monitor is LIVE!</b>\n\n"
            f"Currently tracking: {', '.join(active_tickers)}\n"
            "Use /help to see all commands."
        )
        
        # Start bot command polling in a background thread for instant response
        bot_thread = threading.Thread(target=self.bot_handler.start_polling, daemon=True)
        bot_thread.start()
        
        # Run immediately on startup
        self.run_monitoring_cycle()
        
        # Schedule periodic checks - will be updated dynamically
        schedule.clear()
        interval_minutes = self.monitoring_config.get('check_interval_minutes', 15)
        schedule.every(interval_minutes).minutes.do(self.run_monitoring_cycle)
        
        logger.info(f"Scheduled checks every {interval_minutes} minutes")
        
        # Keep running
        try:
            last_interval = interval_minutes
            while True:
                schedule.run_pending()
                
                # Check if interval changed and reschedule if needed
                current_interval = self.monitoring_config.get('check_interval_minutes', 15)
                if current_interval != last_interval:
                    logger.info(f"Interval changed from {last_interval} to {current_interval} minutes - rescheduling")
                    schedule.clear()
                    schedule.every(current_interval).minutes.do(self.run_monitoring_cycle)
                    last_interval = current_interval
                    self.telegram.send_message(
                        f"⏱️ <b>Interval Updated</b>\n\n"
                        f"Now checking every {current_interval} minutes"
                    )
                
                time.sleep(1)  # Main loop sleep
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            self.telegram.send_message(
                "🛑 <b>Stock Monitor Agent Stopped</b>\n\n"
                "Monitoring has been paused."
            )


def main():
    """Main entry point."""
    print("="*60)
    print("Stock Monitor Agent with Telegram Notifications")
    print("="*60)
    print()
    
    # Load .env if it exists (local dev), but don't fail if missing (cloud dev)
    load_dotenv()
    
    # Required variables
    required_vars = ['FINNHUB_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        if not os.path.exists('.env'):
            print("No .env file found and system environment variables are not set.")
        return
    
    try:
        # Initialize and start agent
        agent = StockMonitorAgent()
        
        # Test Telegram connection
        if not agent.telegram.test_connection():
            print("❌ Failed to connect to Telegram. Please check your credentials.")
            return
        
        print("✅ All systems ready!")
        print()
        print("Starting monitoring...")
        print("Press Ctrl+C to stop")
        print()
        
        # Start scheduled monitoring
        agent.start_scheduled_monitoring()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease check your .env file and ensure all required variables are set.")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    main()
