"""
Telegram notification service for sending stock alerts.
"""
import os
import requests
from utils import logger


class TelegramNotifier:
    """Sends notifications via Telegram Bot API."""
    
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found.")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        logger.info("Telegram notifier initialized")
    
    def send_message(self, message, chat_id=None, parse_mode='HTML', reply_markup=None):
        """
        Send a message via Telegram.
        
        Args:
            message: Text message to send
            chat_id: Optional recipient chat ID (falls back to default)
            parse_mode: 'HTML' or 'Markdown' for formatting
            reply_markup: Optional InlineKeyboardMarkup or similar
        """
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            logger.error("No chat_id provided and no default chat_id set.")
            return False

        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                'chat_id': target_chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': False
            }
            if reply_markup:
                payload['reply_markup'] = reply_markup
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Message sent successfully via Telegram")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def send_stock_alert(self, ticker, company_name, price, change_percent, news_count=0, chat_id=None):
        """
        Send a stock price alert.
        
        Args:
            ticker: Stock ticker symbol
            company_name: Company name
            price: Current stock price
            change_percent: Price change percentage
            news_count: Number of news items
            chat_id: Optional recipient chat ID
        """
        emoji = "📈" if change_percent > 0 else "📉" if change_percent < 0 else "➡️"
        
        message = f"""
🔔 <b>Stock Update: {ticker}</b>

<b>{company_name}</b>
💰 Price: ${price:.2f}
{emoji} Change: {change_percent:+.2f}%
"""
        
        if news_count > 0:
            message += f"📰 News Items: {news_count}\n"
        
        return self.send_message(message, chat_id=chat_id)
    
    def send_news_alert(self, ticker, company_name, headline, summary, url, source='', chat_id=None):
        """
        Send a news alert.
        
        Args:
            ticker: Stock ticker symbol
            company_name: Company name
            headline: News headline
            summary: News summary
            url: Article URL
            source: News source
            chat_id: Optional recipient chat ID
        """
        message = f"""
📰 <b>News Alert: {ticker}</b>

<b>{company_name}</b>

<b>{headline}</b>

{summary}
"""
        
        if source:
            message += f"\n📌 Source: {source}\n"
        
        if url:
            message += f'\n🔗 <a href="{url}">Read more</a>'
        
        return self.send_message(message, chat_id=chat_id)

    def send_anomaly_alert(self, ticker, company_name, alert_text, chat_id=None):
        """Send a high-conviction anomaly alert (Volume/Earnings)."""
        message = f"""
🚦 <b>PRO INTELLIGENCE ALERT: {ticker}</b>

<b>{company_name}</b>
{alert_text}

<i>Use /snapshot {ticker} for deep analysis.</i>
"""
        return self.send_message(message, chat_id=chat_id)
    
    def send_photo(self, photo_bytes, caption=None, chat_id=None):
        """
        Send a photo via Telegram.
        
        Args:
            photo_bytes: Bytes object or file-like object containing the image
            caption: Optional caption for the photo
            chat_id: Optional recipient chat ID
        """
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            logger.error("No chat_id provided for send_photo.")
            return False

        try:
            url = f"{self.api_url}/sendPhoto"
            files = {'photo': ('chart.png', photo_bytes, 'image/png')}
            data = {'chat_id': target_chat_id}
            if caption:
                data['caption'] = caption
                data['parse_mode'] = 'HTML'
                
            response = requests.post(url, data=data, files=files, timeout=20)
            response.raise_for_status()
            
            logger.info("Photo sent successfully via Telegram")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram photo: {e}")
            return False
    
    def test_connection(self):
        """Test the Telegram bot connection."""
        try:
            url = f"{self.api_url}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_name = bot_info['result']['username']
                logger.info(f"✅ Telegram bot connected: @{bot_name}")
                return True
            else:
                logger.error("❌ Telegram bot connection failed")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Telegram connection test failed: {e}")
            return False


# Test function for standalone execution
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing Telegram Notifier...")
    
    try:
        notifier = TelegramNotifier()
        
        # Test connection
        if notifier.test_connection():
            # Send test message
            success = notifier.send_message(
                "🤖 <b>Stock Monitor Agent</b>\n\n"
                "✅ Connection successful!\n"
                "Your stock monitoring agent is ready."
            )
            
            if success:
                print("✅ Test message sent successfully!")
            else:
                print("❌ Failed to send test message")
        else:
            print("❌ Connection test failed")
            
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease set up your .env file with:")
        print("  TELEGRAM_BOT_TOKEN=your_bot_token")
        print("  TELEGRAM_CHAT_ID=your_chat_id")
