"""
Quick test script to send a sample notification.
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.telegram_notifier import TelegramNotifier
from src.stock_monitor import StockMonitor

load_dotenv()

# Initialize
telegram = TelegramNotifier()
stock_monitor = StockMonitor()

print("Fetching current stock data and sending test notification...")

# Get CCCC data
cccc_data = stock_monitor.get_stock_data('CCCC')
if cccc_data:
    telegram.send_stock_alert(
        ticker='CCCC',
        company_name=cccc_data.get('name', 'C4 Therapeutics'),
        price=cccc_data['current_price'],
        change_percent=cccc_data['change_percent']
    )
    print(f"✅ Sent CCCC alert: ${cccc_data['current_price']:.2f} ({cccc_data['change_percent']:+.2f}%)")

# Get BYND data
bynd_data = stock_monitor.get_stock_data('BYND')
if bynd_data:
    telegram.send_stock_alert(
        ticker='BYND',
        company_name=bynd_data.get('name', 'Beyond Meat'),
        price=bynd_data['current_price'],
        change_percent=bynd_data['change_percent']
    )
    print(f"✅ Sent BYND alert: ${bynd_data['current_price']:.2f} ({bynd_data['change_percent']:+.2f}%)")

print("\n✅ Test notifications sent! Check your Telegram.")
