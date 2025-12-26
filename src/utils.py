"""
Utility functions for the stock monitoring agent.
"""
import sqlite3
import logging
import hashlib
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class CacheDB:
    """SQLite database for tracking sent notifications to avoid duplicates."""
    
    def __init__(self, db_path='data/cache.db'):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sent_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                ticker TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                title TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def is_duplicate(self, content_hash):
        """Check if content has already been sent."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id FROM sent_notifications WHERE content_hash = ?',
            (content_hash,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def add_notification(self, content_hash, ticker, notification_type, title=''):
        """Add a sent notification to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''INSERT INTO sent_notifications 
                   (content_hash, ticker, notification_type, title) 
                   VALUES (?, ?, ?, ?)''',
                (content_hash, ticker, notification_type, title)
            )
            
            conn.commit()
            conn.close()
            logger.info(f"Added notification to cache: {ticker} - {notification_type}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Duplicate notification attempted: {content_hash}")
            return False
    
    def cleanup_old_entries(self, days=7):
        """Remove entries older than specified days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''DELETE FROM sent_notifications 
               WHERE sent_at < datetime('now', '-' || ? || ' days')''',
            (days,)
        )
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up {deleted} old entries from cache")
        return deleted


def generate_content_hash(content):
    """Generate a hash for content to check for duplicates."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def format_price_change(change_percent):
    """Format price change with emoji indicator."""
    if change_percent > 0:
        return f"📈 +{change_percent:.2f}%"
    elif change_percent < 0:
        return f"📉 {change_percent:.2f}%"
    else:
        return f"➡️ {change_percent:.2f}%"


def truncate_text(text, max_length=200):
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
